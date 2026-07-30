"""
安卓桌面宠物闹钟 - 完全修复版 V3.6.2
修复内存泄漏、定时器清理和状态持久化问题
修复非重复闹钟重复触发bug（添加触发标记）
修复睡眠动画被心情系统覆盖bug
修复窗口大小和标签布局问题
V3.6.2: 修复多个动画回调叠加bug、简化input_filter、版本号统一、on_start定时器初始化、内容输入长度限制
"""

import os
import json
import gc
from datetime import datetime, timedelta
from kivy.app import App
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.switch import Switch
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.graphics import Color, Ellipse, RoundedRectangle
from kivy.properties import NumericProperty, ListProperty, BooleanProperty
from kivy.config import Config
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp
from plyer import notification
from plyer import vibrator
import time

# 导入新增功能模块
from pet_mood import PetMoodSystem
from weather import WeatherAPI
from calendar_integration import CalendarIntegration

# ⚠️ Config.set('graphics', ...) 在 Kivy 2.3+ 中已被废弃且在 App 构建前调用无效
# Android 悬浮窗透明度已在 init_app_window() 中通过 Window.clearcolor 设置
# Config.set('graphics', 'background_color', '0,0,0,0')


# ==================== 跨平台资源路径辅助函数 ====================
def get_data_dir():
    """获取应用数据目录(兼容 Android 和桌面)"""
    try:
        app = App.get_running_app()
        if app:
            return app.user_data_dir
    except Exception:
        pass
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(filename, fallback_dir=''):
    """获取资源文件的跨平台路径

    优先级:
    1. 应用数据目录(Android上正确)
    2. 当前工作目录
    3. 回退目录
    """
    # 先在应用数据目录查找
    data_dir = get_data_dir()
    if data_dir:
        path = os.path.join(data_dir, filename)
        if os.path.exists(path):
            return path

    # 再在当前工作目录查找
    if os.path.exists(filename):
        return filename

    # 再在脚本目录查找
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, filename)
    if os.path.exists(path):
        return path

    # 最后在回退目录查找
    if fallback_dir and os.path.exists(os.path.join(fallback_dir, filename)):
        return os.path.join(fallback_dir, filename)

    # 返回原始文件名(让调用方处理不存在的情况)
    return filename


def get_config_path(filename):
    """获取配置文件的跨平台路径(可写)"""
    try:
        app = App.get_running_app()
        if app:
            return os.path.join(app.user_data_dir, filename)
    except Exception:
        pass
    return filename  # 回退到当前目录


# ==================== 颜色主题 ====================
CUTE_COLORS = {
    'primary': get_color_from_hex('#FF8FB1'),
    'secondary': get_color_from_hex('#B5EAEA'),
    'accent': get_color_from_hex('#FFE194'),
    'purple': get_color_from_hex('#D4A5FF'),
    'coral': get_color_from_hex('#FF9A8B'),
    'background': get_color_from_hex('#FFF5F7'),
    'text': get_color_from_hex('#5A4A4A'),
    'white': (1, 1, 1, 1),
    'shadow': (0, 0, 0, 0.15),
    'success': (0.3, 0.8, 0.3, 1),
    'error': (1, 0.3, 0.3, 1),
    'warning': (1.0, 0.7, 0.1, 1),
}

# 默认配置
DEFAULT_PET_SETTINGS = {
    'size': 160,
    'opacity': 1.0,
    'sleep_start_hour': 22,
    'sleep_end_hour': 7,
}

DEFAULT_ALARM_SETTINGS = {
    'snooze_duration': 5,
    'max_snooze_count': 3,
    'vibrate': True,
    'sound_enabled': True,
    'volume': 0.8,
    'banner_time': 5,
}

# ==================== 横幅部件 ====================
class CuteBanner(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.95, None)
        self.height = dp(80)
        self.pos_hint = {'center_x': 0.5, 'top': 0.98}
        self.opacity = 0
        self.hide_event = None

        with self.canvas.before:
            Color(*CUTE_COLORS['shadow'])
            self.shadow_rect = RoundedRectangle(
                pos=(self.x + dp(3), self.y - dp(3)),
                size=self.size,
                radius=[dp(20)]
            )
            Color(*CUTE_COLORS['primary'])
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(20)]
            )

        self.bind(pos=self.update_bg, size=self.update_bg)

        content_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(5))
        self.title_label = Label(
            text='⏰ 闹钟提醒',
            font_size=sp(22),
            bold=True,
            color=CUTE_COLORS['white'],
            size_hint_y=0.45
        )
        content_layout.add_widget(self.title_label)

        self.content_label = Label(
            text='时间到了!',
            font_size=sp(16),
            color=CUTE_COLORS['white'],
            size_hint_y=0.55
        )
        content_layout.add_widget(self.content_label)
        self.add_widget(content_layout)

    def update_bg(self, *args):
        self.shadow_rect.pos = (self.x + dp(3), self.y - dp(3))
        self.shadow_rect.size = self.size
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def show(self, title, content, duration=5):
        self.title_label.text = f"⏰ {title}"
        self.content_label.text = content

        if self.hide_event:
            self.hide_event.cancel()

        anim = Animation(opacity=1, duration=0.3, t='out_quad')
        anim.start(self)
        self.hide_event = Clock.schedule_once(lambda dt: self.hide(), duration)

    def hide(self):
        if self.hide_event:
            self.hide_event.cancel()
            self.hide_event = None
        anim = Animation(opacity=0, duration=0.3, t='in_quad')
        anim.start(self)

    def cleanup(self):
        if self.hide_event:
            self.hide_event.cancel()
            self.hide_event = None


# ==================== 睡眠气泡 ====================
class SleepBubble(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(40), dp(40))
        self.opacity = 0
        self.current_anim = None

        with self.canvas:
            Color(1, 1, 1, 0.8)
            self.bubble = Ellipse(pos=self.pos, size=self.size)

        self.bind(pos=self.update_bubble, size=self.update_bubble)

        self.label = Label(
            text='Z',
            font_size=sp(20),
            bold=True,
            color=(0.4, 0.4, 0.6, 1),
            pos=self.pos,
            size=self.size
        )
        self.add_widget(self.label)

    def update_bubble(self, *args):
        self.bubble.pos = self.pos
        self.bubble.size = self.size
        self.label.pos = self.pos
        self.label.size = self.size

    def float_up(self):
        if self.current_anim:
            self.current_anim.cancel(self)

        start_y = self.y  # 先捕获起始位置（此时 opacity 仍为 1.0）
        self.opacity = 0  # 再设置为透明，避免闪烁

        anim = Animation(opacity=0.8, duration=0.5)
        anim &= Animation(y=start_y + dp(60), duration=2, t='out_quad')
        anim &= Animation(x=self.x + dp(10), duration=2, t='in_out_sine')

        def on_complete(*args):
            self.hide()

        anim.bind(on_complete=on_complete)
        self.current_anim = anim
        anim.start(self)

    def hide(self):
        if self.current_anim:
            self.current_anim.cancel(self)
        Animation(opacity=0, duration=0.3).start(self)

    def cleanup(self):
        if self.current_anim:
            self.current_anim.cancel(self)
            self.current_anim = None


# ==================== 宠物部件 ====================
class CutePet(Widget):
    pet_size = NumericProperty(160)
    pet_opacity = NumericProperty(1.0)
    scale = NumericProperty(1.0)
    rotation = NumericProperty(0)
    is_dragging = BooleanProperty(False)
    drag_start_pos = ListProperty([0, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (self.pet_size, self.pet_size)
        # 宠物在悬浮窗内的相对位置(用于拖拽)
        self._pet_offset_x = 0
        self._pet_offset_y = 0
        # 拖拽时记录起点
        self._drag_touch_start_x = 0
        self._drag_touch_start_y = 0
        self._drag_pet_start_x = 0
        self._drag_pet_start_y = 0

        self.pet_image = None
        self.pet_body = None
        self.shadow = None
        self.highlight = None
        self.sleep_bubbles = []
        self.current_animation = None
        self.bubble_timer = None
        self.is_sleeping = False
        self.is_excited = False
        self.touch_start_time = 0
        self.last_click_time = 0
        self.click_count = 0

        # 新增功能系统
        self.mood_system = PetMoodSystem()
        self.weather_api = WeatherAPI()
        self.calendar = CalendarIntegration()
        self.current_mood = 'normal'
        self.current_weather = None
        self.next_calendar_event = None

        # 定时器引用(用于 cleanup)
        self.mood_update_event = None
        self.weather_update_event = None
        self.calendar_update_event = None

        # 宠物状态更新由 DesktopPetAlarmApp 的定时器统一管理
        # CutePet 中不创建独立定时器，避免重复调度
        # 相关定时器引用保留但初始化为 None，待 App 层统一创建
        self.mood_update_event = None
        self.weather_update_event = None
        self.calendar_update_event = None

        # 天气城市配置(默认北京)
        self.weather_city = 'Beijing'

        # 🚨 修复:睡眠动画被心情系统覆盖bug
        # 标记宠物是否处于用户手动触发的睡眠模式（该模式下不响应心情动画切换）
        self._manual_sleep_mode = False

        # 🚨 修复:excited_animation多次点击防重复标志（初始化为False）
        self._excited_callback_registered = False
        self._sleep_callback_registered = False  # 🚨 修复:start_sleep_animation防重复标志
        self._happy_callback_registered = False  # 🚨 修复:start_happy_animation防重复标志

        # bubble_timer 将在 draw_cute_pet 末尾创建，此处不提前调度
        # 修复Bug：避免 bubble_timer 双重调度
        
        self.load_settings()

        # 加载宠物持久化状态(新功能)
        loaded_mood = self.mood_system.load_state()
        self.current_mood = loaded_mood if loaded_mood else 'normal'  # 同步当前心情状态

        self.draw_cute_pet()
        Clock.schedule_once(lambda dt: self.start_cute_idle(), 0.5)
        # bubble_timer 在 draw_cute_pet 末尾调度（避免双重调度）

    def draw_cute_pet(self):
        image_files = ['pet.png', 'pet_default.png', 'assets/pet.png']
        for img_file in image_files:
            path = resource_path(img_file)
            if os.path.exists(path):
                self.pet_image = Image(
                    source=path,
                    size=self.size,
                    pos=self.pos,
                    allow_stretch=True,
                    keep_ratio=True
                )
                self.add_widget(self.pet_image)
                # bubble_timer 在图片加载成功后才调度（避免重复调度）
                self.bubble_timer = Clock.schedule_interval(self.spawn_sleep_bubble, 3)
                return

        self.draw_default_pet()

    def draw_default_pet(self):
        with self.canvas:
            Color(*CUTE_COLORS['shadow'])
            self.shadow = Ellipse(
                pos=(self.x + dp(5), self.y - dp(5)),
                size=self.size
            )
            Color(*CUTE_COLORS['primary'])
            self.pet_body = Ellipse(pos=self.pos, size=self.size)
            Color(1, 1, 1, 0.3)
            highlight_size = (self.pet_size * 0.4, self.pet_size * 0.25)
            self.highlight = Ellipse(
                pos=(self.x + self.pet_size * 0.2, self.y + self.pet_size * 0.6),
                size=highlight_size
            )

        self.bind(pos=self.update_pet, size=self.update_pet)

        for i in range(3):
            bubble = SleepBubble()
            bubble.pos = (
                self.x + self.pet_size + dp(10) + i * dp(15),
                self.y + self.pet_size * 0.7 + i * dp(10)
            )
            self.sleep_bubbles.append(bubble)
            self.add_widget(bubble)

        # 🔥 修复Bug:draw_default_pet() 也需要创建气泡定时器
        # 否则当没有 pet.png 图片时，睡眠气泡动画永远不会触发
        self.bubble_timer = Clock.schedule_interval(self.spawn_sleep_bubble, 3)

    def update_pet(self, *args):
        if self.pet_body and self.shadow and self.highlight:
            self.shadow.pos = (self.x + dp(5), self.y - dp(5))
            self.shadow.size = self.size
            self.pet_body.pos = self.pos
            self.pet_body.size = self.size

            highlight_size = (self.pet_size * 0.4, self.pet_size * 0.25)
            self.highlight.pos = (
                self.x + self.pet_size * 0.2,
                self.y + self.pet_size * 0.6
            )
            self.highlight.size = highlight_size

        if self.pet_image:
            self.pet_image.pos = self.pos
            self.pet_image.size = self.size

        for i, bubble in enumerate(self.sleep_bubbles):
            bubble.pos = (
                self.x + self.pet_size + dp(10) + i * dp(15),
                self.y + self.pet_size * 0.7 + i * dp(10)
            )

    def spawn_sleep_bubble(self, dt):
        if self.is_sleeping:
            for bubble in self.sleep_bubbles:
                if bubble.opacity < 0.1:
                    bubble.float_up()
                    break

    def cancel_current_animation(self):
        if self.current_animation:
            self.current_animation.cancel(self)
            self.current_animation = None
        # 🚨 修复:取消动画时重置所有回调标志，确保下次动画能正常触发回调
        self._happy_callback_registered = False
        self._sleep_callback_registered = False
        self._excited_callback_registered = False

    def start_cute_idle(self):
        self.cancel_current_animation()
        self.is_excited = False
        # 立即捕获当前位置作为动画基准(避免 self.y 在动画过程中变化导致跳跃)
        base_y = self.y
        base_x = self.x

        def create_idle_animation():
            if self.is_excited or self.is_sleeping:
                return
            # 再次获取当前位置确保同步
            current_y = self.y

            breathe_in = Animation(scale=1.05, duration=1.2, t='in_out_sine')
            breathe_out = Animation(scale=1.0, duration=1.2, t='in_out_sine')
            sway_left = Animation(rotation=-3, duration=1.2, t='in_out_sine')
            sway_right = Animation(rotation=3, duration=1.2, t='in_out_sine')
            float_up = Animation(y=current_y + dp(8), duration=1.5, t='in_out_sine')
            float_down = Animation(y=current_y, duration=1.5, t='in_out_sine')

            anim = (breathe_in & sway_left & float_up) + (breathe_out & sway_right & float_down)
            anim.repeat = True
            self.current_animation = anim
            anim.start(self)

        create_idle_animation()

    def start_sleep_animation(self, manual=False):
        """
        睡眠动画
        Args:
            manual: True=用户手动触发（锁定睡眠状态，不被心情动画覆盖）
                   False=自动触发（可被心情动画覆盖）
        """
        self.cancel_current_animation()
        self.is_sleeping = True
        self._sleep_callback_registered = False  # 🚨 修复:重置回调标志，防止多次调用叠加
        # 🚨 修复:睡眠动画被心情系统覆盖bug
        # 只有用户手动触发的睡眠才标记锁定，自动睡眠不锁定
        if manual:
            self._manual_sleep_mode = True
        # 立即捕获当前位置作为动画基准
        base_y = self.y

        anim = Animation(scale=0.85, opacity=0.6, rotation=0, duration=1, t='out_quad')

        def start_breathing(*args):
            if self.is_sleeping and not self._sleep_callback_registered:
                self._sleep_callback_registered = True
                current_y = self.y  # 重新获取当前位置
                breathe_in = Animation(opacity=0.5, scale=0.83, duration=2, t='in_out_sine')
                breathe_out = Animation(opacity=0.7, scale=0.87, duration=2, t='in_out_sine')
                anim = breathe_in + breathe_out
                anim.repeat = True
                self.current_animation = anim
                anim.start(self)

        anim.bind(on_complete=start_breathing)
        self.current_animation = anim
        anim.start(self)

    def wake_up_animation(self):
        self.cancel_current_animation()
        self.is_sleeping = False
        self._manual_sleep_mode = False  # 🚨 修复:退出用户手动睡眠模式
        # 立即捕获当前位置作为动画基准
        base_y = self.y

        anim1 = Animation(scale=1.2, rotation=10, opacity=1, duration=0.15, t='out_quad')
        anim2 = Animation(scale=0.9, rotation=-10, duration=0.1, t='in_quad')
        anim3 = Animation(scale=1.15, rotation=5, duration=0.1, t='out_quad')
        anim4 = Animation(scale=1.0, rotation=0, duration=0.15, t='in_out_quad')
        jump_up = Animation(y=base_y + dp(30), duration=0.15, t='out_quad')
        jump_down = Animation(y=base_y, duration=0.25, t='bounce_out')

        anim = (anim1 & jump_up) + (anim2 & jump_down) + anim3 + anim4
        anim.bind(on_complete=lambda *args: self.start_cute_idle())
        self.current_animation = anim
        anim.start(self)

    def excited_animation(self):
        """宠物兴奋时的动画 - 快速摇摆和跳跃"""
        self.cancel_current_animation()
        self.is_excited = True
        # 🚨 修复:多次点击excited_animation会叠加on_complete回调导致start_cute_idle重复执行
        self._excited_callback_registered = False
        base_y = self.y
        base_x = self.x

        seq = None
        for i in range(5):
            left = Animation(rotation=-15, duration=0.08, t='out_quad')
            right = Animation(rotation=15, duration=0.08, t='out_quad')
            jump = Animation(y=base_y + dp(15), duration=0.08, t='out_quad')
            fall = Animation(y=base_y, duration=0.08, t='in_quad')

            step = (left & jump) + (right & fall)
            if seq is None:
                seq = step
            else:
                seq += step

        seq += Animation(rotation=0, scale=1.0, duration=0.2, t='out_quad')

        def on_complete(*args):
            self.is_excited = False
            if not self._excited_callback_registered:
                self._excited_callback_registered = True
                self.start_cute_idle()

        seq.bind(on_complete=on_complete)
        self.current_animation = seq
        seq.start(self)

    def cute_click_animation(self):
        anim1 = Animation(scale_x=1.15, scale_y=0.85, duration=0.08, t='out_quad')
        anim2 = Animation(scale_x=0.95, scale_y=1.05, duration=0.1, t='out_quad')
        anim3 = Animation(scale_x=1.02, scale_y=0.98, duration=0.08, t='in_out_quad')
        anim4 = Animation(scale_x=1.0, scale_y=1.0, duration=0.08, t='in_out_quad')
        (anim1 + anim2 + anim3 + anim4).start(self)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.is_dragging = True
            self.touch_start_time = time.time()
            self._drag_touch_start_x = touch.x
            self._drag_touch_start_y = touch.y
            self._drag_pet_start_x = self.x
            self._drag_pet_start_y = self.y
            self.cute_click_animation()
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.is_dragging:
            dx = touch.x - self._drag_touch_start_x
            dy = touch.y - self._drag_touch_start_y

            new_x = self._drag_pet_start_x + dx
            new_y = self._drag_pet_start_y + dy

            # 限制在合理范围内(防止拖出屏幕太远)
            from kivy.core.window import Window
            screen_w = Window.width if Window.width > 0 else 1920
            screen_h = Window.height if Window.height > 0 else 1080
            pet_size = int(self.pet_size)
            margin = 20

            new_x = max(-margin, min(new_x, screen_w - pet_size + margin))
            new_y = max(-margin, min(new_y, screen_h - pet_size + margin))

            # 直接移动宠物部件位置(在FloatLayout内自由移动)
            self.pos = (new_x, new_y)

            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.is_dragging:
            self.is_dragging = False

            touch_duration = time.time() - self.touch_start_time
            dx = abs(touch.x - self._drag_touch_start_x)
            dy = abs(touch.y - self._drag_touch_start_y)

            # 保存拖拽结束后的位置
            self._pet_offset_x = self.x
            self._pet_offset_y = self.y

            if dx < 10 and dy < 10 and touch_duration < 0.4:
                self.handle_click()
            elif touch_duration >= 0.4:
                self.on_long_press()

            return True
        return super().on_touch_up(touch)

    def handle_click(self):
        current_time = time.time()
        time_since_last = current_time - self.last_click_time

        if time_since_last < 0.35:
            self.click_count += 1
        else:
            self.click_count = 1

        self.last_click_time = current_time

        # 始终重置计数，防止延迟回调和后续点击混淆
        # 用户连续操作后，计数归零，等待下一轮判断
        if self.click_count == 1:
            # 修复: 捕获 click_count 值避免闭包问题
            saved_count = self.click_count
            Clock.schedule_once(lambda dt, cc=saved_count: self._delayed_click(cc), 0.2)
            self.click_count = 0  # 立即归零，后续点击重新计数
        elif self.click_count == 2:
            self.on_double_click()
            self.click_count = 0
        elif self.click_count >= 3:
            self.on_triple_click()
            self.click_count = 0

    def _delayed_click(self, saved_count):
        """延迟点击处理(使用捕获的值)"""
        if saved_count == 1:
            self.on_pet_click()

    def on_pet_click(self):
        """宠物单击处理：弹出主菜单"""
        app = App.get_running_app()
        if app:
            app.show_main_menu()

    def on_double_click(self):
        self.excited_animation()
        app = App.get_running_app()
        if app:
            Clock.schedule_once(lambda dt: app.show_main_menu(), 0.3)

    def on_triple_click(self):
        app = App.get_running_app()
        if app:
            app.show_timer_dialog()

    def on_long_press(self):
        app = App.get_running_app()
        if app:
            app.show_quick_menu()

    def on_scale(self, instance, value):
        new_size = self.pet_size * value
        self.size = (new_size, new_size)
        if self.pet_image:
            self.pet_image.size = self.size

    def cleanup(self):
        self.cancel_current_animation()
        if self.bubble_timer:
            self.bubble_timer.cancel()
            self.bubble_timer = None
        for bubble in self.sleep_bubbles:
            bubble.cleanup()
        # 取消定时器以防止内存泄漏
        if self.mood_update_event:
            self.mood_update_event.cancel()
            self.mood_update_event = None
        if self.weather_update_event:
            self.weather_update_event.cancel()
            self.weather_update_event = None
        if self.calendar_update_event:
            self.calendar_update_event.cancel()
            self.calendar_update_event = None

    def start_happy_animation(self):
        self._happy_callback_registered = False  # 🚨 修复:重置回调标志在cancel之前，避免cancel后旧标志残留导致回调跳过
        self.cancel_current_animation()
        # 使用宠物自身位置基准
        base_y = self.y

        # 快乐的摇摆动画
        sway_left = Animation(rotation=-8, duration=0.8, t='in_out_sine')
        sway_right = Animation(rotation=8, duration=0.8, t='in_out_sine')
        jump_up = Animation(y=base_y + dp(15), duration=0.3, t='out_quad')
        jump_down = Animation(y=base_y, duration=0.3, t='bounce_out')

        anim = (sway_left & jump_up) + (sway_right & jump_down)
        anim.repeat = True

        def on_repeat(*args):
            if self._happy_callback_registered:
                return
            self._happy_callback_registered = True
            self.start_cute_idle()

        anim.bind(on_complete=on_repeat)
        self.current_animation = anim
        anim.start(self)

    def start_sleepy_animation(self):
        self.cancel_current_animation()
        self.is_sleeping = True
        # 使用宠物自身位置基准
        base_y = self.y

        # 困倦的缓慢移动
        sway_left = Animation(rotation=-3, duration=2.5, t='in_out_sine')
        sway_right = Animation(rotation=3, duration=2.5, t='in_out_sine')
        float_up = Animation(y=base_y + dp(5), duration=3, t='in_out_sine')
        float_down = Animation(y=base_y, duration=3, t='in_out_sine')

        anim = (sway_left & float_up) + (sway_right & float_down)
        anim.repeat = True
        self.current_animation = anim
        anim.start(self)

    def start_excited_animation(self):
        """宠物兴奋动画 - 与 excited_animation 相同,但基于自身位置"""
        self.cancel_current_animation()
        self.is_excited = True
        # 使用宠物自身位置基准(而非窗口位置)
        base_y = self.y

        # 兴奋的快速旋转和跳动
        seq = None
        for i in range(3):
            left = Animation(rotation=-20, duration=0.05, t='out_quad')
            right = Animation(rotation=20, duration=0.05, t='out_quad')
            jump = Animation(y=base_y + dp(25), duration=0.05, t='out_quad')
            fall = Animation(y=base_y, duration=0.05, t='in_quad')

            step = (left & jump) + (right & fall)
            if seq is None:
                seq = step
            else:
                seq += step

        seq += Animation(rotation=0, duration=0.1, t='out_quad')

        def on_complete(*args):
            self.is_excited = False
            self.start_cute_idle()

        seq.bind(on_complete=on_complete)
        self.current_animation = seq
        seq.start(self)

    def start_angry_animation(self):
        self.cancel_current_animation()
        # 使用宠物自身位置基准
        base_y = self.y

        # 生气的小幅度抖动
        vibrate_left = Animation(rotation=-5, duration=0.1, t='out_quad')
        vibrate_right = Animation(rotation=5, duration=0.1, t='out_quad')

        anim = vibrate_left + vibrate_right
        anim.repeat = True
        self.current_animation = anim
        anim.start(self)


# ==================== 按钮样式 ====================
class CuteButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = CUTE_COLORS['primary']
        self.color = CUTE_COLORS['white']
        self.font_size = sp(16)
        self.bold = True


# ==================== 闹钟管理类 ====================
class AlarmClock:
    def __init__(self):
        self.alarms = []
        self.next_alarm = None
        self.alarm_check_event = None
        self.snooze_alarms = {}
        # 🚨 修复:非重复闹钟重复触发bug - 添加已触发标记集合
        # 用于记录今天已触发过的非重复闹钟ID，防止60秒轮询间隔内重复触发
        self._triggered_today = set()
        self._last_check_date = datetime.now().date()  # 🚨 Fix: 初始化时设置当前日期，避免跨会话状态残留
        # 🚨 修复:闹钟ID使用自增计数器替代len(self.alarms)
        # 避免删除闹钟后新添加的闹钟获得已删除闹钟的ID导致冲突
        self._alarm_id_counter = 0
        self._batch_mode = False  # 批量添加时暂停调度
        self.settings = self.load_settings()
        self.load_alarms()
        self.schedule_next_alarm()

    def load_settings(self):
        try:
            config_path = get_config_path('alarm_settings.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载设置失败: {e}")
        return DEFAULT_ALARM_SETTINGS.copy()

    def save_settings(self):
        try:
            config_path = get_config_path('alarm_settings.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置失败: {e}")

    def add_alarm(self, hour, minute, label="闹钟", content="时间到了!",
                  repeat_days=None, enabled=True):
        alarm = {
            'id': self._alarm_id_counter,
        }
        self._alarm_id_counter += 1
        alarm.update({
            'hour': hour,
            'minute': minute,
            'label': label,
            'content': content,
            'repeat_days': repeat_days or [],
            'enabled': enabled,
            'snooze_count': 0,
            'max_snooze': self.settings.get('max_snooze_count', 3)
        })
        self.alarms.append(alarm)
        self.save_alarms()
        if not self._batch_mode:
            self.schedule_next_alarm()
        return alarm

    def batch_add_alarms(self, alarm_text):
        self._batch_mode = True  # 先暂停调度
        added_count = 0
        error_count = 0

        alarm_entries = alarm_text.strip().split(';')
        for entry in alarm_entries:
            entry = entry.strip()
            if not entry:
                continue

            parts = [part.strip() for part in entry.split(',')]
            if len(parts) < 3:
                error_count += 1
                continue

            try:
                label = parts[0]
                time_str = parts[1]
                content = ','.join(parts[2:])

                if ':' in time_str:
                    hour, minute = map(int, time_str.split(':'))
                else:
                    raise ValueError("时间格式错误")

                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    error_count += 1
                    continue

                # 手动构建闹钟避免重复 schedule_next_alarm
                alarm = {
                    'id': self._alarm_id_counter,
                }
                self._alarm_id_counter += 1
                alarm.update({
                    'hour': hour,
                    'minute': minute,
                    'label': label,
                    'content': content,
                    'repeat_days': [],
                    'enabled': True,
                    'snooze_count': 0,
                    'max_snooze': self.settings.get('max_snooze_count', 3)
                })
                self.alarms.append(alarm)
                added_count += 1
            except Exception as e:
                print(f"解析错误: {entry} - {e}")
                error_count += 1

        self.save_alarms()
        self._batch_mode = False
        self.schedule_next_alarm()  # 批量添加完成后一次性调度

        return added_count, error_count

    def remove_alarm(self, alarm_id):
        # 清理关联的贪睡闹钟
        if alarm_id in self.snooze_alarms:
            del self.snooze_alarms[alarm_id]
        self.alarms = [a for a in self.alarms if a['id'] != alarm_id]
        # 重要：不重新编号！snooze_alarms 和其他地方可能引用了旧ID
        # 闹钟ID使用自增方式，删除后ID会空缺，下次add_alarm会填补
        self.save_alarms()
        self.schedule_next_alarm()

    def toggle_alarm(self, alarm_id, enabled):
        for alarm in self.alarms:
            if alarm['id'] == alarm_id:
                alarm['enabled'] = enabled
                break
        self.save_alarms()
        self.schedule_next_alarm()

    def update_alarm(self, alarm_id, hour=None, minute=None, label=None,
                     content=None, repeat_days=None):
        for alarm in self.alarms:
            if alarm['id'] == alarm_id:
                if hour is not None:
                    alarm['hour'] = hour
                if minute is not None:
                    alarm['minute'] = minute
                if label is not None:
                    alarm['label'] = label
                if content is not None:
                    alarm['content'] = content
                if repeat_days is not None:
                    alarm['repeat_days'] = repeat_days
                # 编辑闹钟时清除该闹钟的贪睡闹钟,防止时间已变更但贪睡闹钟仍用旧时间
                if alarm_id in self.snooze_alarms:
                    del self.snooze_alarms[alarm_id]
                alarm['snooze_count'] = 0
                break
        self.save_alarms()
        self.schedule_next_alarm()

    def snooze_alarm(self, alarm_id):
        for alarm in self.alarms:
            if alarm['id'] == alarm_id:
                if alarm['snooze_count'] < alarm['max_snooze']:
                    alarm['snooze_count'] += 1
                    snooze_minutes = self.settings.get('snooze_duration', 5)
                    snooze_time = datetime.now() + timedelta(minutes=snooze_minutes)
                    self.snooze_alarms[alarm_id] = snooze_time
                    return True, snooze_minutes
                else:
                    alarm['snooze_count'] = 0
                    return False, 0
        return False, 0

    def stop_alarm(self, alarm_id):
        for alarm in self.alarms:
            if alarm['id'] == alarm_id:
                alarm['snooze_count'] = 0
                if alarm_id in self.snooze_alarms:
                    del self.snooze_alarms[alarm_id]
                break

    def schedule_next_alarm(self):
        now = datetime.now()
        next_alarm_time = None
        next_alarm = None

        # 🚨 修复:triggered_alarms NameError
        # triggered_alarms 用于追踪本次检查中已触发的贪睡闹钟,避免重复触发
        triggered_alarms = []
        for alarm_id, snooze_time in list(self.snooze_alarms.items()):
            # 检查贪睡时间是否已到
            if snooze_time <= now:
                # 找到对应的闹钟配置
                for alarm in self.alarms:
                    if alarm['id'] == alarm_id:
                        # 检查该闹钟在今天是重复闹钟，如果是则需验证星期
                        if alarm['repeat_days'] and now.weekday() not in alarm['repeat_days']:
                            break  # 今天不是重复日，跳过（保留 snooze_alarms 供明天用）
                        # 触发闹钟
                        if alarm['id'] not in self._triggered_today:
                            triggered_alarms.append(alarm)
                            self._triggered_today.add(alarm['id'])
                        # 清除该贪睡闹钟
                        del self.snooze_alarms[alarm_id]
                        break
                continue
            if next_alarm_time is None or snooze_time < next_alarm_time:
                next_alarm_time = snooze_time
                for alarm in self.alarms:
                    if alarm['id'] == alarm_id:
                        next_alarm = alarm
                        break

        for alarm in self.alarms:
            if not alarm['enabled']:
                continue

            alarm_time = now.replace(
                hour=alarm['hour'],
                minute=alarm['minute'],
                second=0,
                microsecond=0
            )

            if alarm_time <= now:
                alarm_time += timedelta(days=1)

            if alarm['repeat_days']:
                while alarm_time.weekday() not in alarm['repeat_days']:
                    alarm_time += timedelta(days=1)

            if next_alarm_time is None or alarm_time < next_alarm_time:
                next_alarm_time = alarm_time
                next_alarm = alarm

        self.next_alarm = {
            'time': next_alarm_time,
            'alarm': next_alarm
        }

        app = App.get_running_app()
        # 修复Bug:改为每60秒轮询检查所有闹钟
        # 旧逻辑只调度到下一个闹钟时间,如果app在那之前被Android杀死,闹钟永远不会触发
        # 新逻辑确保即使app被杀死重启,每次启动时 schedule_next_alarm 也会重新建立60秒轮询
        if app:
            # 取消旧的调度
            if self.alarm_check_event:
                self.alarm_check_event.cancel()
            # 建立稳定的60秒轮询
            self.alarm_check_event = Clock.schedule_interval(
                lambda dt: self.check_alarms(),
                60.0  # 每60秒检查一次所有闹钟
            )

    def check_alarms(self):
        now = datetime.now()
        triggered_alarms = []

        # 每天0点重置触发记录
        today = now.date()
        if hasattr(self, '_last_check_date') and self._last_check_date != today:
            self._triggered_today.clear()
        self._last_check_date = today

        # 处理贪睡闹钟
        for alarm_id, snooze_time in list(self.snooze_alarms.items()):
            if now > snooze_time:
                for alarm in self.alarms:
                    if alarm['id'] == alarm_id:
                        triggered_alarms.append(alarm)
                        if alarm_id in self.snooze_alarms:
                            del self.snooze_alarms[alarm_id]
                        break

        # 处理常规闹钟
        for alarm in self.alarms:
            if not alarm['enabled']:
                continue

            # 计算闹钟的下一次触发时间
            alarm_time_today = now.replace(hour=alarm['hour'], minute=alarm['minute'], second=0, microsecond=0)
            
            # 计算距离闹钟触发还有多少秒（可以为负数）
            seconds_until = (alarm_time_today - now).total_seconds()
            
            # 如果今天的闹钟时间已过（秒数为负），检查是否是重复闹钟需要推到明天
            if seconds_until < -30:
                # 今天的闹钟已经错过了（超过30秒窗口），不触发
                continue
            
            if seconds_until <= 30:
                # 在30秒触发窗口内
                if not alarm['repeat_days']:
                    # 非重复闹钟
                    if alarm['id'] not in self._triggered_today:
                        triggered_alarms.append(alarm)
                        alarm['enabled'] = False
                        self._triggered_today.add(alarm['id'])
                elif now.weekday() in alarm['repeat_days']:
                    # 重复闹钟：每天只触发一次
                    if alarm['id'] not in self._triggered_today:
                        triggered_alarms.append(alarm)
                        self._triggered_today.add(alarm['id'])

        app = App.get_running_app()
        if app:
            for alarm in triggered_alarms:
                app.trigger_alarm(alarm)

    def save_alarms(self):
        try:
            config_path = get_config_path('alarms.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.alarms, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存闹钟失败: {e}")

    def load_alarms(self):
        try:
            config_path = get_config_path('alarms.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.alarms = json.load(f)
            # 🚨 修复:load_alarms 后更新 _alarm_id_counter，确保新闹钟ID不与已加载的冲突
            if self.alarms:
                self._alarm_id_counter = max(a['id'] for a in self.alarms) + 1
        except Exception as e:
            print(f"加载闹钟失败: {e}")
            self.alarms = []

    def export_alarms(self, filepath):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.alarms, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出闹钟失败: {e}")
            return False

    def cleanup(self):
        """清理闹钟资源，防止内存泄漏（App退出时调用）"""
        if self.alarm_check_event:
            self.alarm_check_event.cancel()
            self.alarm_check_event = None
        # 清理所有已触发标记
        self._triggered_today.clear()


# ==================== 计时器管理类 ====================
class TimerManager:
    def __init__(self):
        self.timers = []
        self.timer_check_event = None
        self._timer_id_counter = 0  # 🚨 Fix: 使用自增ID避免与已删除计时器ID冲突
        self.start_checking()

    def add_timer(self, minutes, seconds=0, label="计时器"):
        total_seconds = minutes * 60 + seconds
        timer = {
            'id': self._timer_id_counter,  # 🚨 Fix: 使用自增ID
            'label': label,
            'total_seconds': total_seconds,
            'remaining': total_seconds,
            'running': True,
            'created_at': datetime.now()
        }
        self._timer_id_counter += 1  # 🚨 Fix: 自增计数器
        self.timers.append(timer)
        return timer

    def remove_timer(self, timer_id):
        self.timers = [t for t in self.timers if t['id'] != timer_id]

    def toggle_timer(self, timer_id):
        for timer in self.timers:
            if timer['id'] == timer_id:
                timer['running'] = not timer['running']
                break

    def start_checking(self):
        self.timer_check_event = Clock.schedule_interval(self.check_timers, 1)

    def check_timers(self, dt):
        triggered_timers = []  # 先收集要触发的计时器,避免迭代中修改导致RuntimeError
        for timer in self.timers[:]:  # 复制列表避免迭代中修改问题
            if timer['running'] and timer['remaining'] > 0:
                timer['remaining'] -= 1

                if timer['remaining'] <= 0:
                    timer['running'] = False
                    triggered_timers.append(timer)

        # 统一触发(触发回调中可能调用remove_timer修改self.timers)
        for timer in triggered_timers:
            self.trigger_timer(timer)

    def trigger_timer(self, timer):
        app = App.get_running_app()
        if app:
            app.trigger_timer_alarm(timer)
        # 统一移除已完成的计时器
        self.timers = [t for t in self.timers if t['id'] != timer['id']]

    def get_active_timers(self):
        return [t for t in self.timers if t['remaining'] > 0]

    def format_time(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def cleanup(self):
        if self.timer_check_event:
            self.timer_check_event.cancel()
            self.timer_check_event = None


# ==================== 对话框类 ====================
class CutePopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background = ''
        self.background_color = (0, 0, 0, 0.5)
        self.title_color = CUTE_COLORS['text']
        self.title_size = sp(20)
        self.separator_color = CUTE_COLORS['primary']


class AlarmDialog(CutePopup):
    def __init__(self, alarm_manager, app=None, alarm_id=None, **kwargs):
        super().__init__(**kwargs)
        self.alarm_manager = alarm_manager
        self.alarm_id = alarm_id
        self.app = app  # 🚨 修复:传入 app 引用用于显示反馈横幅

        self.title = '✏️ 编辑闹钟' if alarm_id is not None else '➕ 新建闹钟'
        self.size_hint = (0.9, 0.8)

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        time_layout = BoxLayout(orientation='horizontal', size_hint_y=0.12, spacing=dp(10))
        time_layout.add_widget(Label(text='⏰ 时间:', size_hint_x=0.25, font_size=sp(16), color=CUTE_COLORS['text']))
        self.hour_spinner = Spinner(
            text='08',
            values=[f'{i:02d}' for i in range(24)],
            size_hint_x=0.3,
            background_color=CUTE_COLORS['secondary']
        )
        time_layout.add_widget(self.hour_spinner)
        time_layout.add_widget(Label(text=':', size_hint_x=0.1, font_size=sp(24), color=CUTE_COLORS['text']))
        self.minute_spinner = Spinner(
            text='00',
            values=[f'{i:02d}' for i in range(60)],
            size_hint_x=0.3,
            background_color=CUTE_COLORS['secondary']
        )
        time_layout.add_widget(self.minute_spinner)
        layout.add_widget(time_layout)

        label_layout = BoxLayout(orientation='horizontal', size_hint_y=0.12, spacing=dp(10))
        label_layout.add_widget(Label(text='🏷️ 名称:', size_hint_x=0.25, font_size=sp(16), color=CUTE_COLORS['text']))
        self.label_input = TextInput(
            text='闹钟',
            multiline=False,
            size_hint_x=0.75,
            font_size=sp(16),
            background_color=CUTE_COLORS['background']
        )
        label_layout.add_widget(self.label_input)
        layout.add_widget(label_layout)

        content_layout = BoxLayout(orientation='horizontal', size_hint_y=0.18, spacing=dp(10))
        content_layout.add_widget(Label(text='📝 内容:', size_hint_x=0.25, font_size=sp(16), color=CUTE_COLORS['text']))
        self.content_input = TextInput(
            text='时间到了!',
            multiline=True,
            size_hint_x=0.75,
            font_size=sp(14),
            background_color=CUTE_COLORS['background'],
            hint_text='闹钟内容（选填）',
            input_filter=lambda text, _: text[:99]
        )
        content_layout.add_widget(self.content_input)
        layout.add_widget(content_layout)

        layout.add_widget(Label(text='📅 重复:', size_hint_y=0.08, font_size=sp(16), color=CUTE_COLORS['text']))
        days_layout = GridLayout(cols=7, rows=1, size_hint_y=0.12, spacing=dp(5))
        self.day_checks = []
        days = ['一', '二', '三', '四', '五', '六', '日']
        for day in days:
            day_box = BoxLayout(orientation='vertical', spacing=dp(2))
            day_box.add_widget(Label(text=day, size_hint_y=0.4, font_size=sp(12), color=CUTE_COLORS['text']))
            check = CheckBox(size_hint_y=0.6)
            self.day_checks.append(check)
            day_box.add_widget(check)
            days_layout.add_widget(day_box)
        layout.add_widget(days_layout)

        quick_repeat_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=dp(5))
        quick_repeat_layout.add_widget(Label(text='⚡ 快捷:', size_hint_x=0.15, font_size=sp(14), color=CUTE_COLORS['text']))

        for text, days_set in [('一次', []), ('每天', list(range(7))), ('工作日', list(range(5))), ('周末', [5, 6])]:
            btn = Button(
                text=text,
                size_hint_x=0.2,
                font_size=sp(12),
                background_color=CUTE_COLORS['accent']
            )
            btn.bind(on_press=lambda inst, ds=days_set: self.set_repeat_days(ds))
            quick_repeat_layout.add_widget(btn)

        layout.add_widget(quick_repeat_layout)

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=dp(15))

        cancel_btn = CuteButton(text='❌ 取消')
        cancel_btn.bind(on_press=self.dismiss)
        button_layout.add_widget(cancel_btn)

        save_btn = CuteButton(text='✅ 保存')
        save_btn.bind(on_press=self.save_alarm)
        button_layout.add_widget(save_btn)

        if alarm_id is not None:
            delete_btn = CuteButton(text='🗑️ 删除')
            delete_btn.background_color = CUTE_COLORS['coral']
            delete_btn.bind(on_press=self.delete_alarm)
            button_layout.add_widget(delete_btn)

        layout.add_widget(button_layout)
        self.content = layout

        if alarm_id is not None:
            self.load_alarm_data()

    def set_repeat_days(self, days):
        for i, check in enumerate(self.day_checks):
            check.active = i in days

    def load_alarm_data(self):
        for alarm in self.alarm_manager.alarms:
            if alarm['id'] == self.alarm_id:
                self.hour_spinner.text = f"{alarm['hour']:02d}"
                self.minute_spinner.text = f"{alarm['minute']:02d}"
                self.label_input.text = alarm['label']
                self.content_input.text = alarm.get('content', '时间到了!')

                if alarm['repeat_days']:
                    for i, check in enumerate(self.day_checks):
                        check.active = (i in alarm['repeat_days'])
                break

    def save_alarm(self, instance):
        try:
            hour = int(self.hour_spinner.text)
            minute = int(self.minute_spinner.text)
            label = self.label_input.text.strip() or '闹钟'
            # 🚨 修复:使用 validate_alarm_label 确保标签长度合理（函数已存在但未调用）
            from resources import validate_alarm_label
            valid, _ = validate_alarm_label(label)
            if not valid:
                label = label[:20]  # 超长时截断而非拒绝，避免用户困惑
            content = self.content_input.text.strip()
            if not content:
                content = '时间到了!'

            repeat_days = [i for i, check in enumerate(self.day_checks) if check.active]

            if self.alarm_id is not None:
                self.alarm_manager.update_alarm(
                    self.alarm_id, hour, minute, label, content, repeat_days
                )
                action_text = '✅ 闹钟已更新'
            else:
                self.alarm_manager.add_alarm(
                    hour, minute, label, content, repeat_days, True
                )
                action_text = '✅ 闹钟已添加'
            # 🚨 修复:保存成功后通过横幅通知用户，提升用户体验
            if self.app:
                self.app.banner.show(action_text, f'{label} ({hour:02d}:{minute:02d})', 3)
            else:
                Clock.schedule_once(
                    lambda dt: print(f'{action_text}: {label} ({hour:02d}:{minute:02d})'), 0.1
                )
            self.dismiss()
        except ValueError:
            # 静默失败用户体验差,改为提示(但由于是 Spinner 选择,理论上不会触发)
            print("闹钟保存失败:时间格式错误")

    def delete_alarm(self, instance):
        if self.alarm_id is not None:
            self.alarm_manager.remove_alarm(self.alarm_id)
            self.dismiss()


class BatchAddDialog(CutePopup):
    def __init__(self, alarm_manager, **kwargs):
        super().__init__(**kwargs)
        self.alarm_manager = alarm_manager
        self.title = '➕ 批量添加闹钟'
        self.size_hint = (0.9, 0.8)

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        instructions = Label(
            text='📋 格式:闹钟名,时间,具体内容\n💡 示例:起床,08:00,该起床了\n📝 多个闹钟用分号分隔',
            size_hint_y=0.15,
            halign='left',
            valign='middle',
            font_size=sp(14),
            color=CUTE_COLORS['text']
        )
        instructions.bind(size=instructions.setter('text_size'))
        layout.add_widget(instructions)

        example_text = '起床,08:00,该起床了;午餐,12:30,记得吃饭;午休,13:00,休息一会;下班,18:00,下班时间到了;睡觉,22:30,早点休息'

        self.text_input = TextInput(
            text=example_text,
            multiline=True,
            size_hint_y=0.5,
            font_size=sp(14),
            background_color=CUTE_COLORS['background']
        )
        layout.add_widget(self.text_input)

        self.result_label = Label(
            text='',
            size_hint_y=0.1,
            color=CUTE_COLORS['success'],
            font_size=sp(14)
        )
        layout.add_widget(self.result_label)

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=dp(15))

        cancel_btn = CuteButton(text='❌ 取消')
        cancel_btn.bind(on_press=self.dismiss)
        button_layout.add_widget(cancel_btn)

        add_btn = CuteButton(text='➕ 添加')
        add_btn.bind(on_press=self.batch_add)
        button_layout.add_widget(add_btn)

        layout.add_widget(button_layout)
        self.content = layout

    def batch_add(self, instance):
        text = self.text_input.text.strip()
        if not text:
            self.result_label.text = '⚠️ 请输入闹钟数据'
            self.result_label.color = CUTE_COLORS['error']
            return

        added_count, error_count = self.alarm_manager.batch_add_alarms(text)

        if added_count > 0:
            self.result_label.text = f'✅ 成功添加 {added_count} 个闹钟'
            self.result_label.color = CUTE_COLORS['success']
            if error_count > 0:
                self.result_label.text += f',⚠️ {error_count} 个格式错误'
            Clock.schedule_once(lambda dt: self.dismiss(), 2)
        else:
            self.result_label.text = '❌ 未添加任何闹钟,请检查格式'
            self.result_label.color = CUTE_COLORS['error']


class TimerDialog(CutePopup):
    def __init__(self, timer_manager, **kwargs):
        super().__init__(**kwargs)
        self.timer_manager = timer_manager
        self.title = '⏱️ 倒计时'
        self.size_hint = (0.85, 0.7)
        self.update_timer_event = None  # 必须先初始化,避免 on_dismiss 时引用不存在

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        time_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=dp(10))
        time_layout.add_widget(Label(text='⏱️ 分钟:', size_hint_x=0.3, font_size=sp(16), color=CUTE_COLORS['text']))
        self.minute_input = TextInput(
            text='5',
            multiline=False,
            input_filter='int',
            size_hint_x=0.7,
            font_size=sp(16),
            background_color=CUTE_COLORS['background']
        )
        time_layout.add_widget(self.minute_input)
        layout.add_widget(time_layout)

        sec_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=dp(10))
        sec_layout.add_widget(Label(text='⏱️ 秒:', size_hint_x=0.3, font_size=sp(16), color=CUTE_COLORS['text']))
        self.sec_input = TextInput(
            text='0',
            multiline=False,
            input_filter='int',
            size_hint_x=0.7,
            font_size=sp(16),
            background_color=CUTE_COLORS['background']
        )
        sec_layout.add_widget(self.sec_input)
        layout.add_widget(sec_layout)

        label_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=dp(10))
        label_layout.add_widget(Label(text='🏷️ 标签:', size_hint_x=0.3, font_size=sp(16), color=CUTE_COLORS['text']))
        self.label_input = TextInput(
            text='计时器',
            multiline=False,
            size_hint_x=0.7,
            font_size=sp(16),
            background_color=CUTE_COLORS['background']
        )
        label_layout.add_widget(self.label_input)
        layout.add_widget(label_layout)

        layout.add_widget(Label(text='📋 活动计时器:', size_hint_y=0.08, font_size=sp(16), color=CUTE_COLORS['text']))

        scroll = ScrollView(size_hint_y=0.3)
        self.timer_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.timer_list.bind(minimum_height=self.timer_list.setter('height'))
        scroll.add_widget(self.timer_list)
        layout.add_widget(scroll)

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=dp(15))

        cancel_btn = CuteButton(text='❌ 关闭')
        cancel_btn.bind(on_press=self.dismiss)
        button_layout.add_widget(cancel_btn)

        add_btn = CuteButton(text='▶️ 开始计时')
        add_btn.bind(on_press=self.add_timer)
        button_layout.add_widget(add_btn)

        layout.add_widget(button_layout)
        self.content = layout

        self.update_timer_event = Clock.schedule_interval(self.update_timer_list, 1)
        self.update_timer_list(0)

    def on_dismiss(self):
        if self.update_timer_event:
            self.update_timer_event.cancel()
            self.update_timer_event = None
        super().on_dismiss()

    def add_timer(self, instance):
        try:
            minutes = int(self.minute_input.text.strip() or '0')
            seconds = int(self.sec_input.text.strip() or '0')

            if minutes < 0 or seconds < 0:
                self.minute_input.text = '0'
                self.sec_input.text = '0'
                return

            # 🚨 修复:TimerDialog输入框无上限校验，允许输入极大值导致计时器行为异常
            if minutes > 999:
                minutes = 999
                self.minute_input.text = '999'
            if seconds > 59:
                seconds = 59
                self.sec_input.text = '59'

            if minutes == 0 and seconds == 0:
                return

            label = self.label_input.text.strip() or '计时器'
            self.timer_manager.add_timer(minutes, seconds, label)
            self.update_timer_list(0)

            # 清空输入框
            self.minute_input.text = '5'
            self.sec_input.text = '0'
        except ValueError:
            self.minute_input.text = '0'
            self.sec_input.text = '0'

    def update_timer_list(self, dt):
        self.timer_list.clear_widgets()

        for timer in self.timer_manager.get_active_timers():
            item = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))

            time_text = self.timer_manager.format_time(timer['remaining'])
            label = Label(
                text=f"{timer['label']}: {time_text}",
                size_hint_x=0.6,
                font_size=sp(14),
                color=CUTE_COLORS['text']
            )
            item.add_widget(label)

            toggle_btn = Button(
                text='⏸️' if timer['running'] else '▶️',
                size_hint_x=0.2,
                font_size=sp(14),
                background_color=CUTE_COLORS['secondary']
            )
            toggle_btn.bind(on_press=lambda inst, t=timer: self.toggle_timer(t))
            item.add_widget(toggle_btn)

            del_btn = Button(
                text='🗑️',
                size_hint_x=0.2,
                font_size=sp(14),
                background_color=CUTE_COLORS['coral']
            )
            del_btn.bind(on_press=lambda inst, t=timer: self.delete_timer(t))
            item.add_widget(del_btn)

            self.timer_list.add_widget(item)

    def toggle_timer(self, timer):
        self.timer_manager.toggle_timer(timer['id'])
        self.update_timer_list(0)

    def delete_timer(self, timer):
        self.timer_manager.remove_timer(timer['id'])
        self.update_timer_list(0)


class QuickMenu(CutePopup):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.title = '⚡ 快捷操作'
        self.size_hint = (0.75, 0.55)

        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        btn_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=0.7)

        buttons = [
            ('➕ 新建闹钟', self.new_alarm, CUTE_COLORS['primary']),
            ('⏱️ 倒计时', self.show_timer, CUTE_COLORS['secondary']),
            ('⚙️ 设置', self.show_settings, CUTE_COLORS['purple']),
            ('😴 睡眠模式', self.toggle_sleep, CUTE_COLORS['accent']),
        ]

        for text, callback, color in buttons:
            btn = CuteButton(text=text)
            btn.background_color = color
            btn.bind(on_press=callback)
            btn_layout.add_widget(btn)

        layout.add_widget(btn_layout)

        close_btn = CuteButton(text='❌ 关闭', size_hint_y=0.2)
        close_btn.bind(on_press=self.dismiss)
        layout.add_widget(close_btn)

        self.content = layout

    def new_alarm(self, instance):
        self.dismiss()
        dialog = AlarmDialog(self.app.alarm_manager, self.app)
        dialog.open()

    def show_timer(self, instance):
        self.dismiss()
        self.app.show_timer_dialog()

    def show_settings(self, instance):
        self.dismiss()
        settings = SettingsDialog(self.app)
        settings.open()

    def toggle_sleep(self, instance):
        self.dismiss()
        was_sleeping = self.app.pet.is_sleeping
        if was_sleeping:
            self.app.pet.wake_up_animation()
        else:
            self.app.pet.start_sleep_animation(manual=True)  # 🚨 修复:标记为用户手动睡眠
        # 🚨 修复:关闭旧菜单后重建，确保下次打开时标题反映最新睡眠状态
        # QuickMenu 的标题在 __init__ 中确定，toggle 后需重建才能更新标题
        try:
            self.app.root.remove_widget(self._quick_menu)
        except Exception:
            pass
        self._quick_menu = QuickMenu(self.app)
        self._quick_menu.open()



class MainMenu(CutePopup):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.title = '🐾 宠物闹钟'
        self.size_hint = (0.95, 0.9)

        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        self.time_label = Label(
            text=self.get_current_time(),
            font_size=sp(32),
            size_hint_y=0.12,
            bold=True,
            color=CUTE_COLORS['primary']
        )
        main_layout.add_widget(self.time_label)

        self.next_alarm_label = Label(
            text=self.get_next_alarm_text(),
            font_size=sp(16),
            size_hint_y=0.08,
            color=CUTE_COLORS['text']
        )
        main_layout.add_widget(self.next_alarm_label)

        alarm_list_label = Label(text='📋 闹钟列表:', size_hint_y=0.06, font_size=sp(16), color=CUTE_COLORS['text'])
        main_layout.add_widget(alarm_list_label)

        scroll = ScrollView(size_hint_y=0.45)
        self.alarm_list_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5)
        )
        self.alarm_list_layout.bind(minimum_height=self.alarm_list_layout.setter('height'))
        scroll.add_widget(self.alarm_list_layout)
        main_layout.add_widget(scroll)

        button_layout = GridLayout(cols=2, rows=3, size_hint_y=0.3, spacing=dp(10), padding=dp(5))

        buttons = [
            ('➕ 新建闹钟', self.show_new_alarm_dialog),
            ('📥 批量添加', self.show_batch_add_dialog),
            ('⏱️ 倒计时', self.show_timer_dialog),
            ('💾 导出闹钟', self.export_alarms),
            ('⚙️ 设置', self.show_settings),
            ('❌ 关闭', self.dismiss),
        ]

        for text, callback in buttons:
            btn = CuteButton(text=text)
            btn.bind(on_press=callback)
            button_layout.add_widget(btn)

        main_layout.add_widget(button_layout)
        self.content = main_layout

        self.update_timer_event = Clock.schedule_interval(self.update_time, 1)
        self.update_alarm_list()

    def on_dismiss(self):
        if self.update_timer_event:
            self.update_timer_event.cancel()
            self.update_timer_event = None
        super().on_dismiss()

    def get_current_time(self):
        now = datetime.now()
        return now.strftime("%H:%M:%S")

    def get_next_alarm_text(self):
        next_alarm = self.app.alarm_manager.next_alarm
        if next_alarm and next_alarm['alarm']:
            alarm = next_alarm['alarm']
            alarm_time = next_alarm['time']
            time_str = alarm_time.strftime("%H:%M")
            days_str = ""
            if alarm['repeat_days']:
                days = ["一", "二", "三", "四", "五", "六", "日"]
                day_names = [days[i] for i in alarm['repeat_days']]
                days_str = f" ({'、'.join(day_names)})"
            return f"⏰ 下一个: {time_str}{days_str} - {alarm['label']}"
        return "📭 没有设置闹钟"

    def update_time(self, dt):
        self.time_label.text = self.get_current_time()
        self.next_alarm_label.text = self.get_next_alarm_text()

    def update_alarm_list(self):
        self.alarm_list_layout.clear_widgets()

        for alarm in self.app.alarm_manager.alarms:
            alarm_item = self.create_alarm_item(alarm)
            self.alarm_list_layout.add_widget(alarm_item)

    def create_alarm_item(self, alarm):
        item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(65))

        time_str = f"{alarm['hour']:02d}:{alarm['minute']:02d}"
        time_label = Label(
            text=time_str,
            size_hint_x=0.18,
            font_size=sp(18),
            bold=True,
            color=CUTE_COLORS['primary']
        )
        item_layout.add_widget(time_label)

        label_text = alarm['label']
        if alarm.get('content'):
            label_text += f"\n{alarm['content'][:12]}..."
        label = Label(
            text=label_text,
            size_hint_x=0.42,
            font_size=sp(13),
            halign='left',
            valign='middle',
            color=CUTE_COLORS['text']
        )
        label.bind(size=label.setter('text_size'))
        item_layout.add_widget(label)

        switch = Switch(active=alarm['enabled'], size_hint_x=0.15)
        switch.bind(active=lambda instance, value, a=alarm:
                   self.app.alarm_manager.toggle_alarm(a['id'], value))
        item_layout.add_widget(switch)

        edit_btn = Button(text='✏️', size_hint_x=0.12, font_size=sp(14), background_color=CUTE_COLORS['secondary'])
        edit_btn.bind(on_press=lambda instance, a=alarm: self.edit_alarm(a))
        item_layout.add_widget(edit_btn)

        del_btn = Button(text='🗑️', size_hint_x=0.1, font_size=sp(14), background_color=CUTE_COLORS['coral'])
        del_btn.bind(on_press=lambda instance, a=alarm: self.delete_alarm(a))
        item_layout.add_widget(del_btn)

        return item_layout

    def edit_alarm(self, alarm):
        self.dismiss()
        dialog = AlarmDialog(self.app.alarm_manager, self.app, alarm['id'])
        dialog.open()

    def delete_alarm(self, alarm):
        self.app.alarm_manager.remove_alarm(alarm['id'])
        self.update_alarm_list()

    def show_new_alarm_dialog(self, instance):
        self.dismiss()
        dialog = AlarmDialog(self.app.alarm_manager, self.app)
        dialog.open()

    def show_batch_add_dialog(self, instance):
        self.dismiss()
        dialog = BatchAddDialog(self.app.alarm_manager)
        dialog.open()

    def show_timer_dialog(self, instance):
        self.dismiss()
        self.app.show_timer_dialog()

    def show_settings(self, instance):
        self.dismiss()
        settings = SettingsDialog(self.app)
        settings.open()

    def export_alarms(self, instance):
        if self.app.alarm_manager.export_alarms('alarms_backup.json'):
            self.next_alarm_label.text = "✅ 闹钟已导出到 alarms_backup.json"
        else:
            self.next_alarm_label.text = "❌ 导出失败"


class SettingsDialog(CutePopup):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.title = '⚙️ 设置'
        self.size_hint = (0.9, 0.8)

        # 设置内容区域（使用ScrollView包装，确保小屏设备不溢出）
        settings_scroll = ScrollView(size_hint_y=0.88, do_scroll_x=False)
        settings_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12), size_hint_y=None)
        settings_content.bind(minimum_height=settings_content.setter('height'))

        size_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=dp(10))
        size_layout.add_widget(Label(text='🐾 宠物大小:', size_hint_x=0.4, font_size=sp(14), color=CUTE_COLORS['text']))
        self.size_slider = Slider(
            min=80,
            max=250,
            value=self.app.pet.pet_size,
            size_hint_x=0.6
        )
        self.size_slider.bind(value=self.on_size_change)
        size_layout.add_widget(self.size_slider)
        settings_content.add_widget(size_layout)

        opacity_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=dp(10))
        opacity_layout.add_widget(Label(text='👻 透明度:', size_hint_x=0.4, font_size=sp(14), color=CUTE_COLORS['text']))
        self.opacity_slider = Slider(
            min=0.3,
            max=1.0,
            value=self.app.pet.pet_opacity,
            size_hint_x=0.6
        )
        self.opacity_slider.bind(value=self.on_opacity_change)
        opacity_layout.add_widget(self.opacity_slider)
        settings_content.add_widget(opacity_layout)

        banner_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=dp(10))
        banner_layout.add_widget(Label(text='📢 横幅显示(秒):', size_hint_x=0.4, font_size=sp(14), color=CUTE_COLORS['text']))
        self.banner_slider = Slider(
            min=3,
            max=15,
            value=self.app.banner_display_time,
            size_hint_x=0.6
        )
        self.banner_slider.bind(value=self.on_banner_time_change)
        banner_layout.add_widget(self.banner_slider)
        settings_content.add_widget(banner_layout)

        snooze_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=dp(10))
        snooze_layout.add_widget(Label(text='😴 贪睡时间(分):', size_hint_x=0.4, font_size=sp(14), color=CUTE_COLORS['text']))
        self.snooze_slider = Slider(
            min=1,
            max=10,
            value=self.app.alarm_manager.settings.get('snooze_duration', 5),
            size_hint_x=0.6
        )
        self.snooze_slider.bind(value=self.on_snooze_change)
        snooze_layout.add_widget(self.snooze_slider)
        settings_content.add_widget(snooze_layout)

        max_snooze_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=dp(10))
        max_snooze_layout.add_widget(Label(text='🔢 最大贪睡:', size_hint_x=0.4, font_size=sp(14), color=CUTE_COLORS['text']))
        self.max_snooze_slider = Slider(
            min=1,
            max=5,
            value=self.app.alarm_manager.settings.get('max_snooze_count', 3),
            size_hint_x=0.6
        )
        self.max_snooze_slider.bind(value=self.on_max_snooze_change)
        max_snooze_layout.add_widget(self.max_snooze_slider)
        settings_content.add_widget(max_snooze_layout)

        vibrate_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=dp(10))
        vibrate_layout.add_widget(Label(text='📳 振动提醒:', size_hint_x=0.4, font_size=sp(14), color=CUTE_COLORS['text']))
        self.vibrate_switch = Switch(
            active=self.app.alarm_manager.settings.get('vibrate', True),
            size_hint_x=0.6
        )
        self.vibrate_switch.bind(active=self.on_vibrate_change)
        vibrate_layout.add_widget(self.vibrate_switch)
        settings_content.add_widget(vibrate_layout)

        sound_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=dp(10))
        sound_layout.add_widget(Label(text='🔔 声音提醒:', size_hint_x=0.4, font_size=sp(14), color=CUTE_COLORS['text']))
        self.sound_switch = Switch(
            active=self.app.alarm_manager.settings.get('sound_enabled', True),
            size_hint_x=0.6
        )
        self.sound_switch.bind(active=self.on_sound_change)
        sound_layout.add_widget(self.sound_switch)
        settings_content.add_widget(sound_layout)

        # 天气城市设置（带确认按钮和校验）
        city_layout = BoxLayout(orientation='horizontal', size_hint_y=0.10, spacing=dp(5))
        city_layout.add_widget(Label(text='🌤️ 城市:', size_hint_x=0.3, font_size=sp(14), color=CUTE_COLORS['text']))
        self.city_input = TextInput(
            text=self.app.weather_city,
            multiline=False,
            size_hint_x=0.4,
            font_size=sp(14),
            background_color=CUTE_COLORS['background']
        )
        self.city_input.bind(on_text_validate=self.on_city_change)
        city_layout.add_widget(self.city_input)
        city_confirm_btn = CuteButton(text='✅ 应用', size_hint_x=0.3, font_size=sp(13))
        city_confirm_btn.bind(on_press=self.on_city_change)
        city_layout.add_widget(city_confirm_btn)
        settings_content.add_widget(city_layout)

        # 天气API Key配置
        api_key_layout = BoxLayout(orientation='horizontal', size_hint_y=0.10, spacing=dp(5))
        api_key_layout.add_widget(Label(text='🔑 天气API Key:', size_hint_x=0.3, font_size=sp(14), color=CUTE_COLORS['text']))
        self.api_key_input = TextInput(
            text=self.app.weather_api_key,
            multiline=False,
            size_hint_x=0.4,
            font_size=sp(14),
            background_color=CUTE_COLORS['background'],
            password=True,  # 🔒 掩码显示，防止截图泄露 API Key
            hint_text='OpenWeatherMap API Key'
        )
        self.api_key_input.bind(on_text_validate=self.on_api_key_change)
        api_key_layout.add_widget(self.api_key_input)
        api_confirm_btn = CuteButton(text='✅ 应用', size_hint_x=0.3, font_size=sp(13))
        api_confirm_btn.bind(on_press=self.on_api_key_change)
        api_key_layout.add_widget(api_confirm_btn)
        settings_content.add_widget(api_key_layout)

        # 🔒 API Key 掩码提示标签
        self.api_key_masked_label = Label(
            text='',
            size_hint_y=0.035,
            font_size=sp(11),
            color=CUTE_COLORS['secondary'],
            halign='left'
        )
        self.api_key_masked_label.bind(size=self.api_key_masked_label.setter('text_size'))
        settings_content.add_widget(self.api_key_masked_label)

        # API Key 提示说明
        hint_label = Label(
            text='💡 免费API Key: openweathermap.org 免费注册获取',
            size_hint_y=0.035,
            font_size=sp(12),
            color=CUTE_COLORS['secondary'],
            halign='left'
        )
        hint_label.bind(size=hint_label.setter('text_size'))
        settings_content.add_widget(hint_label)

        # 🔥 新增:天气模式指示器(让用户清楚知道是否在使用模拟数据)
        self.weather_mode_label = Label(
            text=self._get_weather_mode_text(),
            size_hint_y=0.035,
            font_size=sp(12),
            color=CUTE_COLORS['warning'],
            halign='left'
        )
        self.weather_mode_label.bind(size=self.weather_mode_label.setter('text_size'))
        settings_content.add_widget(self.weather_mode_label)

        # 🔒 初始化 API Key 掩码提示（需要在 _update_api_key_masked_label 定义之后调用）
        # 但 SettingsDialog 使用 ScrollView，内容在 __init__ 末尾才渲染，所以下面单独在末尾调用
        # 这里先确保 api_key_masked_label 已创建，然后在 ScrollView 添加后再调用更新
        settings_scroll.add_widget(settings_content)
        layout.add_widget(settings_scroll)

        # 🔒 初始化 API Key 掩码提示
        self._update_api_key_masked_label()

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=dp(15))

        reset_btn = CuteButton(text='🔄 重置')
        reset_btn.bind(on_press=self.reset_settings)
        button_layout.add_widget(reset_btn)

        close_btn = CuteButton(text='✅ 关闭')
        close_btn.bind(on_press=self.dismiss)
        button_layout.add_widget(close_btn)

        layout.add_widget(button_layout)
        self.content = layout

    def on_size_change(self, instance, value):
        self.app.pet.pet_size = int(value)
        self.app.pet.size = (self.app.pet.pet_size, self.app.pet.pet_size)

    def on_opacity_change(self, instance, value):
        self.app.pet.pet_opacity = value
        self.app.pet.opacity = value

    def on_banner_time_change(self, instance, value):
        self.app.banner_display_time = value

    def on_snooze_change(self, instance, value):
        self.app.alarm_manager.settings['snooze_duration'] = int(value)
        self.app.alarm_manager.save_settings()

    def on_max_snooze_change(self, instance, value):
        self.app.alarm_manager.settings['max_snooze_count'] = int(value)
        self.app.alarm_manager.save_settings()

    def on_vibrate_change(self, instance, value):
        self.app.alarm_manager.settings['vibrate'] = value
        self.app.alarm_manager.save_settings()

    def on_sound_change(self, instance, value):
        self.app.alarm_manager.settings['sound_enabled'] = value
        self.app.alarm_manager.save_settings()

    def _get_weather_mode_text(self):
        """获取天气模式指示文本"""
        if self.app.weather_api_key and self.app.weather_api_key != 'demo_key':
            return '🌐 天气模式: 真实数据（已配置API Key）'
        else:
            return '🔮 天气模式: 模拟数据（可前往 openweathermap.org 注册免费API Key）'

    def _update_api_key_masked_label(self):
        """更新 API Key 掩码提示标签"""
        if hasattr(self, 'api_key_masked_label') and self.app:
            if self.app.weather_api_key and self.app.weather_api_key != 'demo_key':
                masked = self.app.weather_api_key[:4] + '****' + self.app.weather_api_key[-4:]
                self.api_key_masked_label.text = f'🔐 当前 Key: {masked}'
            else:
                self.api_key_masked_label.text = '🔐 当前: 未配置（使用模拟数据）'

    def _update_weather_mode_label(self):
        """更新天气模式指示器"""
        if hasattr(self, 'weather_mode_label'):
            self.weather_mode_label.text = self._get_weather_mode_text()

    def on_city_change(self, instance):
        """天气城市变更处理（支持按钮和Enter两种触发方式，带校验）"""
        new_city = self.city_input.text.strip()
        # 🔥 新增:城市名校验（至少2个字符，且不能是纯数字）
        if not new_city:
            self.city_input.text = self.app.weather_city  # 恢复原值
            print("城市名不能为空")
            return
        if len(new_city) < 2:
            self.city_input.text = self.app.weather_city  # 恢复原值
            print("城市名至少需要2个字符")
            return
        # 🚨 修复:移除 isdigit() 校验，支持中文城市名
        # 纯数字输入会被 len<2 拦截，无需额外校验

        self.app.weather_city = new_city
        self.app.save_settings()  # 立即保存
        # 同步到 Pet 对象的天气城市设置
        if hasattr(self.app, 'pet'):
            self.app.pet.weather_city = new_city
        # 立即更新天气显示
        self.app.update_weather_status(0)
        self._update_weather_mode_label()  # 🔥 新增:更新天气模式指示器
        print(f"天气城市已更新为: {new_city}")

    def on_api_key_change(self, instance):
        """天气API Key变更处理"""
        new_key = self.api_key_input.text.strip()
        # 🚨 修复:简化 API Key 校验逻辑
        # 空字符串时 WeatherAPI 会自动降级为 demo_key，无需提前校验
        self.app.weather_api_key = new_key
        self.app.save_settings()
        # 同步到 WeatherAPI 和 Pet 对象
        if hasattr(self.app, 'pet') and self.app.pet:
            self.app.pet.weather_api.api_key = new_key
            self.app.pet.weather_city = self.app.weather_city
        self._update_weather_mode_label()  # 🔥 更新天气模式指示器
        self._update_api_key_masked_label()  # 🔒 更新掩码提示
        print(f"天气API Key已更新: {'已设置' if new_key else '使用默认/demo'}")

    def reset_settings(self, instance):
        self.size_slider.value = 160
        self.opacity_slider.value = 1.0
        self.banner_slider.value = 5
        self.snooze_slider.value = 5
        self.max_snooze_slider.value = 3
        self.vibrate_switch.active = True
        self.sound_switch.active = True
        # 重置天气城市和API Key
        self.city_input.text = 'Beijing'
        self.api_key_input.text = 'demo_key'
        self.app.weather_city = 'Beijing'
        self.app.weather_api_key = 'demo_key'
        self.app.save_settings()
        self._update_weather_mode_label()  # 重置后更新天气模式指示器
        self._update_api_key_masked_label()  # 🔒 重置后更新掩码提示


class AlarmTriggerDialog(CutePopup):
    def __init__(self, app, alarm, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.alarm = alarm
        self.auto_dismiss = False

        self.title = f"⏰ {alarm['label']}"
        self.size_hint = (0.85, 0.5)

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        content_label = Label(
            text=alarm.get('content', '时间到了!'),
            font_size=sp(22),
            size_hint_y=0.4,
            color=CUTE_COLORS['text']
        )
        layout.add_widget(content_label)

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.35, spacing=dp(20))

        snooze_count = alarm.get('snooze_count', 0)
        max_snooze = alarm.get('max_snooze', 3)
        snooze_btn = CuteButton(
            text=f'😴 贪睡 ({snooze_count}/{max_snooze})'
        )
        # 贪睡次数已满时,按钮变红提醒用户
        if snooze_count >= max_snooze:
            snooze_btn.background_color = CUTE_COLORS['error']
        else:
            snooze_btn.background_color = CUTE_COLORS['accent']
        snooze_btn.bind(on_press=self.snooze_alarm)
        button_layout.add_widget(snooze_btn)

        close_btn = CuteButton(text='✅ 关闭闹钟')
        close_btn.bind(on_press=self.close_alarm)
        button_layout.add_widget(close_btn)

        layout.add_widget(button_layout)
        self.content = layout

    def snooze_alarm(self, instance):
        alarm_data = self.alarm  # 显式捕获，避免隐式闭包引用 self.alarm
        success, minutes = self.app.alarm_manager.snooze_alarm(alarm_data['id'])
        if success:
            self.app.stop_alarm_sound()  # 停止声音
            self.dismiss()
            self.app.show_notification(f"😴 贪睡 {minutes} 分钟后再次提醒")
        else:
            instance.text = '⚠️ 已达贪睡上限!'
            # 显式捕获 alarm_data，避免 late-binding 闭包陷阱
            Clock.schedule_once(
                lambda dt, a=alarm_data:
                    setattr(instance, 'text',
                            f'😴 贪睡 ({a.get("snooze_count", 0)}/{a.get("max_snooze", 3)})'), 2)

    def close_alarm(self, instance):
        self.app.stop_alarm_sound()  # 停止声音
        self.app.alarm_manager.stop_alarm(self.alarm['id'])
        self.dismiss()


# ==================== 主应用类 ====================
class DesktopPetAlarmApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pet = None
        self.banner = None
        self.alarm_manager = None
        self.timer_manager = None
        self.sleep_check_event = None
        self.alarm_sound = None
        self.banner_display_time = 5
        self.weather_api_key = 'demo_key'  # 天气API Key

    def build(self):
        from kivy.utils import platform
        from kivy.uix.widget import Widget
        from kivy.clock import Clock

        if platform == "android":
            try:
                from android.permissions import Permission, request_permission
                from android.permissions import check_permission

                has_permission = check_permission(Permission.SYSTEM_ALERT_WINDOW)

                if has_permission:
                    Clock.schedule_once(lambda dt: self.init_app_window(), 0.5)
                else:
                    def callback(permissions, results):
                        if all(results):
                            Clock.schedule_once(lambda dt: self.init_app_window(), 1)
                        else:
                            Clock.schedule_once(lambda dt: self.init_app_window(), 1)

                    request_permission(Permission.SYSTEM_ALERT_WINDOW, callback)

                return Widget()
            except ImportError:
                Clock.schedule_once(lambda dt: self.init_app_window(), 0.5)
                return Widget()
            except Exception:
                Clock.schedule_once(lambda dt: self.init_app_window(), 0.5)
                return Widget()
        else:
            return self.init_app_window()

    def init_app_window(self):
        """初始化应用窗口"""
        try:
            Window.borderless = True
            Window.always_on_top = True
            Window.resizable = False
            Window.size = (dp(350), dp(350))  # 🚨 修复:增大窗口(原200太小,标签全被挤出)
            Window.left = 100
            Window.top = 500

            from kivy.utils import platform
            if platform == "android":
                # 关键修复:Android悬浮窗透明度
                # Alpha=0.5 → 50%透明,可见但不太突兀
                Window.clearcolor = (0.95, 0.95, 0.95, 0.5)
                Window.top = 300
                Window.left = 50
                Window.size = (dp(350), dp(350))  # 🚨 修复:增大窗口以容纳所有标签
            else:
                pass
        except Exception as e:
            print(f"窗口初始化失败: {e}")
            # 不再返回Widget导致root=None崩溃,抛出异常让Kivy处理
            raise

        self.root = FloatLayout()

        self.alarm_manager = AlarmClock()
        self.timer_manager = TimerManager()

        self.pet = CutePet()
        self.root.add_widget(self.pet)

        self.banner = CuteBanner()
        self.root.add_widget(self.banner)

        self.load_alarm_sound()

        # 加载应用设置(必须在 add_mood_weather_calendar_labels 之前)
        self.load_settings()

        # TimerManager.__init__ 中已调用 start_checking(),不要重复调度!
        # 修复Bug:移除这里多余的 schedule_interval,否则计时器会快2倍
        # self.timer_manager.timer_check_event = Clock.schedule_interval(
        #     self.timer_manager.check_timers, 1
        # )
        # TimerManager.__init__ 中已调用 start_checking() 建立每秒轮询
        # 不需要也不应该在这里再次创建定时器
        # 保留这个检查只是为了将来防御性保护（如果 start_checking 被修改跳过）
        # 实际执行时条件永远为 False，避免重复调度
        # if self.timer_manager.timer_check_event is None:
        #     self.timer_manager.timer_check_event = Clock.schedule_interval(
        #         self.timer_manager.check_timers, 1
        #     )

        self.sleep_check_event = Clock.schedule_interval(self.check_pet_sleep_state, 60)

        # 修复Bug:启动时立即检查是否有需要触发的闹钟
        # 如果用户设置了在当前时间之后的闹钟但app刚被杀死重启,立即触发
        Clock.schedule_once(lambda dt: self.alarm_manager.check_alarms(), 1)

        # 添加心情、天气、日历显示标签
        self.add_mood_weather_calendar_labels()

        # 🔥 修复Bug:必须在 init_app_window 中创建定时器
        # 否则首次启动后，悬浮窗内的心情/天气/日历状态标签永远不会更新
        # on_resume 只在 Android 暂停恢复时触发，桌面模式不会触发
        if self.pet:
            # 取消旧的（防御性保护）
            if self.pet.mood_update_event:
                self.pet.mood_update_event.cancel()
            if self.pet.weather_update_event:
                self.pet.weather_update_event.cancel()
            if self.pet.calendar_update_event:
                self.pet.calendar_update_event.cancel()
            # 立即执行一次初始化更新（让标签立即显示有意义的内容）
            self.update_mood_status(0)
            self.update_weather_status(0)
            self.update_calendar_status(0)
            # 创建定时器：心情30秒、天气10分钟、日历10分钟
            self.pet.mood_update_event = Clock.schedule_interval(self.update_mood_status, 30)
            self.pet.weather_update_event = Clock.schedule_interval(self.update_weather_status, 600)
            self.pet.calendar_update_event = Clock.schedule_interval(self.update_calendar_status, 600)




    def load_settings(self):
        """加载应用设置(天气城市等)"""
        try:
            config_path = get_config_path('app_settings.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.weather_city = settings.get('weather_city', 'Beijing')
                    self.weather_api_key = settings.get('weather_api_key', 'demo_key')
            else:
                self.weather_city = 'Beijing'
                self.weather_api_key = 'demo_key'
        except Exception as e:
            print(f"加载设置失败: {e}")
            self.weather_city = 'Beijing'
            self.weather_api_key = 'demo_key'
        # 同步到 Pet 对象的天气城市设置，确保宠物系统使用一致的城市
        try:
            if self.pet:
                self.pet.weather_city = self.weather_city
                # 🔥 修复:同时同步 weather_api_key 到 WeatherAPI 对象
                # 否则重启后 weather_api 仍使用默认的 demo_key
                if hasattr(self.pet, 'weather_api') and self.weather_api_key:
                    self.pet.weather_api.api_key = self.weather_api_key
        except Exception:
            pass

    def save_settings(self):
        """保存应用设置"""
        try:
            config_path = get_config_path('app_settings.json')
            settings = {
                'weather_city': self.weather_city,
                'weather_api_key': getattr(self, 'weather_api_key', 'demo_key'),
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置失败: {e}")

    def load_alarm_sound(self):
        try:
            sound_files = ['alarm.wav', 'alarm.mp3', 'assets/alarm.wav']
            for sound_file in sound_files:
                path = resource_path(sound_file)
                if os.path.exists(path):
                    self.alarm_sound = SoundLoader.load(path)
                    break
        except Exception as e:
            print(f"加载声音失败: {e}")

    def show_main_menu(self):
        menu = MainMenu(self)
        menu.open()

    def show_quick_menu(self):
        # 🚨 修复:关闭已打开的菜单,避免多次长按打开多个菜单
        if hasattr(self, '_quick_menu') and self._quick_menu:
            try:
                self._quick_menu.dismiss()
            except Exception:
                pass
        self._quick_menu = QuickMenu(self)
        self._quick_menu.open()

    def show_timer_dialog(self):
        dialog = TimerDialog(self.timer_manager)
        dialog.open()

    def check_pet_sleep_state(self, dt):
        # 修复Bug:self.pet 可能为 None(极端时序/初始化异常)
        if self.pet is None:
            return
        now = datetime.now()
        hour = now.hour

        sleep_start = DEFAULT_PET_SETTINGS.get('sleep_start_hour', 22)
        sleep_end = DEFAULT_PET_SETTINGS.get('sleep_end_hour', 7)

        should_sleep = hour >= sleep_start or hour < sleep_end

        if should_sleep:
            if not self.pet.is_sleeping:
                self.pet.start_sleep_animation()
        else:
            if self.pet.is_sleeping:
                self.pet.wake_up_animation()

    def trigger_alarm(self, alarm):
        if self.pet.current_animation:
            self.pet.current_animation.cancel(self.pet)

        self.pet.excited_animation()
        self.show_alarm_banner(alarm)
        self.show_alarm_trigger_dialog(alarm)
        self.play_alarm_sound()
        self.vibrate()
        self.show_alarm_notification(alarm)

        Clock.schedule_once(lambda dt: self.alarm_manager.schedule_next_alarm(), 1)

    def trigger_timer_alarm(self, timer):
        self.banner.show(f"⏱️ {timer['label']}", "时间到了!")
        Clock.schedule_once(lambda dt: self.banner.hide(), self.banner_display_time)

        self.play_alarm_sound()
        self.vibrate()

        # 5秒后自动停止声音，避免计时器声音持续播放
        Clock.schedule_once(lambda dt: self.stop_alarm_sound(), 5)

        try:
            notification.notify(
                title=f"宠物闹钟 - {timer['label']}",
                message="倒计时结束!",
                app_name='宠物闹钟',
                timeout=10
            )
        except Exception as e:
            print(f"显示通知失败: {e}")

    def show_alarm_banner(self, alarm):
        title = alarm['label']
        content = alarm.get('content', '时间到了!')
        self.banner.show(title, content, self.banner_display_time)

    def show_alarm_trigger_dialog(self, alarm):
        dialog = AlarmTriggerDialog(self, alarm)
        dialog.open()

    def play_alarm_sound(self):
        try:
            if (self.alarm_manager.settings.get('sound_enabled', True) and
                self.alarm_sound):
                volume = self.alarm_manager.settings.get('volume', 0.8)
                self.alarm_sound.volume = volume
                self.alarm_sound.play()
        except Exception as e:
            print(f"播放声音失败: {e}")

    def stop_alarm_sound(self):
        """停止闹钟声音播放"""
        try:
            if self.alarm_sound:
                self.alarm_sound.stop()
        except Exception as e:
            print(f"停止声音失败: {e}")

    def vibrate(self):
        try:
            if self.alarm_manager.settings.get('vibrate', True):
                vibrator.vibrate(1)
        except Exception as e:
            print(f"振动失败: {e}")

    def show_alarm_notification(self, alarm):
        try:
            notification.notify(
                title=f"宠物闹钟 - {alarm['label']}",
                message=alarm.get('content', '时间到了!'),
                app_name='宠物闹钟',
                timeout=10
            )
        except Exception as e:
            print(f"显示通知失败: {e}")

    def show_notification(self, message):
        try:
            notification.notify(
                title="宠物闹钟",
                message=message,
                app_name='宠物闹钟',
                timeout=5
            )
        except Exception as e:
            print(f"显示通知失败: {e}")

    def add_mood_weather_calendar_labels(self):
        """添加心情、天气、日历显示标签到悬浮窗内"""
        # 🚨 修复:悬浮窗大小改为 350x350dp,标签布局需要适配
        label_width = 300
        label_height = 28

        # 心情显示标签 - 悬浮窗底部
        self.mood_label = Label(
            text="心情: 正常 😐",
            size_hint=(None, None),
            size=(label_width, label_height),
            pos_hint={'x': 0.07, 'y': 0.01},
            color=self.pet.mood_system.get_mood_color('normal'),
            font_size='12sp',
            halign='left'
        )
        self.root.add_widget(self.mood_label)

        # 天气显示标签 - 悬浮窗底部稍上
        self.weather_label = Label(
            text="天气: 加载中... ☁️",
            size_hint=(None, None),
            size=(label_width, label_height),
            pos_hint={'x': 0.07, 'y': 0.09},
            color=CUTE_COLORS['secondary'],
            font_size='12sp',
            halign='left'
        )
        self.root.add_widget(self.weather_label)

        # 日历显示标签 - 悬浮窗底部更上
        self.calendar_label = Label(
            text="日历: 加载中... 📅",
            size_hint=(None, None),
            size=(label_width, label_height),
            pos_hint={'x': 0.07, 'y': 0.17},
            color=CUTE_COLORS['text'],
            font_size='12sp',
            halign='left'
        )
        self.root.add_widget(self.calendar_label)

    def update_mood_status(self, dt):
        if self.pet:
            current_time = datetime.now()
            weather_data = self.pet.weather_api.get_current_weather(self.weather_city)
            weather_impact = weather_data.get('impact', 'normal') if weather_data else 'normal'
            next_event = self.pet.calendar.get_next_event()

            old_mood = self.pet.current_mood  # 保存旧心情用于比较
            new_mood = self.pet.mood_system.get_current_mood(current_time, weather_impact, next_event)
            self.pet.current_mood = new_mood

            # 🚨 修复:睡眠动画被心情系统覆盖bug
            # 只有在非手动睡眠模式下，才根据心情改变动画
            # 手动睡眠模式由用户点击快捷菜单的"睡眠模式"按钮触发
            # 自动睡眠（根据时间）不标记 _manual_sleep_mode，仍可被心情动画覆盖
            if not self.pet._manual_sleep_mode:
                # 根据心情改变动画
                if new_mood == 'happy':
                    self.pet.start_happy_animation()
                elif new_mood == 'sleepy':
                    self.pet.start_sleepy_animation()
                elif new_mood == 'excited':
                    self.pet.start_excited_animation()
                elif new_mood == 'angry':
                    self.pet.start_angry_animation()

            # 更新心情显示
            if self.mood_label:
                mood_emoji = self.pet.mood_system.generate_mood_emoji(new_mood)
                self.mood_label.text = f"心情: {new_mood} {mood_emoji}"
                self.mood_label.color = self.pet.mood_system.get_mood_color(new_mood)

            if new_mood != old_mood:
                self.pet.mood_system.save_state()

    def update_weather_status(self, dt):
        if self.pet:
            weather_data = self.pet.weather_api.get_current_weather(self.weather_city)
            self.pet.current_weather = weather_data

            # 更新天气显示
            if self.weather_label:
                weather_info = self.pet.weather_api.get_weather_for_pet(self.weather_city)
                self.weather_label.text = f"天气: {weather_info['description']} {weather_info['emoji']}"
                self.weather_label.color = CUTE_COLORS['secondary']

    def update_calendar_status(self, dt):
        if self.pet:
            next_event = self.pet.calendar.get_next_event()
            self.pet.next_calendar_event = next_event

            # 更新日历显示
            if self.calendar_label:
                if next_event:
                    event_emoji = self.pet.calendar.get_event_emoji(next_event['type'])
                    self.calendar_label.text = f"日历: {next_event['title']} {event_emoji}"
                    self.calendar_label.color = CUTE_COLORS['accent']
                else:
                    self.calendar_label.text = "日历: 无事件"
                    self.calendar_label.color = CUTE_COLORS['text']

    def on_pause(self):
        """Android 应用暂停时保存状态并暂停定时器"""
        try:
            # 暂停闹钟检查定时器
            if self.alarm_manager and self.alarm_manager.alarm_check_event:
                self.alarm_manager.alarm_check_event.cancel()
                self.alarm_manager.alarm_check_event = None

            # 暂停睡眠检查定时器
            if self.sleep_check_event:
                self.sleep_check_event.cancel()
                self.sleep_check_event = None

            # 暂停宠物定时器
            if self.pet:
                if self.pet.mood_update_event:
                    self.pet.mood_update_event.cancel()
                    self.pet.mood_update_event = None
                if self.pet.weather_update_event:
                    self.pet.weather_update_event.cancel()
                    self.pet.weather_update_event = None
                if self.pet.calendar_update_event:
                    self.pet.calendar_update_event.cancel()
                    self.pet.calendar_update_event = None
                # 暂停气泡动画定时器（节省后台资源）
                if self.pet.bubble_timer:
                    self.pet.bubble_timer.cancel()
                    self.pet.bubble_timer = None

            # 保存闹钟状态
            if self.alarm_manager:
                self.alarm_manager.save_alarms()

            # 保存窗口位置(使用 get_config_path 确保跨平台)
            try:
                window_pos = {
                    'left': Window.left,
                    'top': Window.top,
                    'pet_size': self.pet.pet_size if self.pet else 160,
                    'pet_opacity': self.pet.pet_opacity if self.pet else 1.0
                }
                config_path = get_config_path('window_pos.json')
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(window_pos, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"保存窗口位置失败: {e}")

            print("应用已暂停,状态已保存")
            return True
        except Exception as e:
            print(f"暂停时出错: {e}")
            return True

    def on_resume(self):
        """Android 应用恢复时重新启动定时器"""
        try:
            # 先取消旧的睡眠检查定时器(如果存在)
            if self.sleep_check_event:
                self.sleep_check_event.cancel()
            self.sleep_check_event = Clock.schedule_interval(self.check_pet_sleep_state, 60)

            if self.pet:
                # 先取消旧的心跳/天气/日历定时器(如果存在)
                if self.pet.mood_update_event:
                    self.pet.mood_update_event.cancel()
                if self.pet.weather_update_event:
                    self.pet.weather_update_event.cancel()
                if self.pet.calendar_update_event:
                    self.pet.calendar_update_event.cancel()

                # 重新创建定时器引用到 Pet 对象
                # 注意：天气恢复时用 600 秒（与 init_app_window 一致），避免切后台回来后刷新变慢
                self.pet.mood_update_event = Clock.schedule_interval(self.update_mood_status, 30)
                self.pet.weather_update_event = Clock.schedule_interval(self.update_weather_status, 600)  # 修复:恢复为10分钟，与init_app_window一致
                self.pet.calendar_update_event = Clock.schedule_interval(self.update_calendar_status, 600)
                # 恢复气泡动画定时器
                if self.pet.bubble_timer:
                    self.pet.bubble_timer.cancel()
                self.pet.bubble_timer = Clock.schedule_interval(self.pet.spawn_sleep_bubble, 3)

            if self.alarm_manager:
                self.alarm_manager.schedule_next_alarm()

            print("应用已恢复,定时器已重新启动")
        except Exception as e:
            print(f"恢复时出错: {e}")

    def on_stop(self):
        # 修复Bug：保存宠物心情状态，避免用户互动数据丢失
        if self.pet and hasattr(self.pet, 'mood_system'):
            self.pet.mood_system.save_state()

        if self.alarm_manager:
            self.alarm_manager.save_alarms()
            self.alarm_manager.save_settings()
            self.alarm_manager.cleanup()

        if self.timer_manager:
            self.timer_manager.cleanup()

        if self.pet:
            self.pet.cleanup()

        if self.banner:
            self.banner.cleanup()

        if self.sleep_check_event:
            self.sleep_check_event.cancel()

        try:
            window_pos = {
                'left': Window.left,
                'top': Window.top,
                'pet_size': self.pet.pet_size if self.pet else 160,
                'pet_opacity': self.pet.pet_opacity if self.pet else 1.0
            }
            config_path = get_config_path('window_pos.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(window_pos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存窗口位置失败: {e}")

        gc.collect()

    def on_start(self):
        """Android应用启动 - 恢复窗口位置、宠物状态和定时器"""
        try:
            from kivy.utils import platform
            if platform == "android":
                try:
                    from android import AndroidApplication
                    AndroidApplication.start_service()
                except Exception:
                    pass

                # 修复Bug:只在 root 尚未初始化时补初始化
                # 避免 build() 中 schedule_once 和 on_start 重复调用导致重复 pet 创建
                if self.root is None:
                    from kivy.clock import Clock
                    Clock.schedule_once(lambda dt: self.init_app_window(), 0.5)

                # 🚨 修复:on_start 也要初始化定时器（与 on_resume 对称）
                # init_app_window 通过 Clock.schedule_once 调用，有短暂窗口期没有定时器
                try:
                    if self.sleep_check_event:
                        self.sleep_check_event.cancel()
                    self.sleep_check_event = Clock.schedule_interval(self.check_pet_sleep_state, 60)

                    if self.pet:
                        for attr, method, interval in [
                            ('mood_update_event', self.update_mood_status, 30),
                            ('weather_update_event', self.update_weather_status, 600),
                            ('calendar_update_event', self.update_calendar_status, 600),
                        ]:
                            evt = getattr(self.pet, attr, None)
                            if evt:
                                evt.cancel()
                            setattr(self.pet, attr, Clock.schedule_interval(method, interval))

                    if self.alarm_manager:
                        self.alarm_manager.schedule_next_alarm()
                except AttributeError:
                    pass  # init_app_window 尚未运行，定时器尚未创建，等待 Clock.schedule_once
        except Exception:
            pass

        # 恢复窗口位置 - 修复Bug:添加 self.pet 空值保护避免崩溃
        # 修复Bug:日志输出让用户知道恢复是否成功
        try:
            config_path = get_config_path('window_pos.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    window_pos = json.load(f)
                Window.left = window_pos.get('left', 100)
                Window.top = window_pos.get('top', 500)
                # 修复Bug:self.pet 可能为 None(极端时序),增加保护
                if self.pet is not None:
                    self.pet.pet_size = window_pos.get('pet_size', 160)
                    self.pet.pet_opacity = window_pos.get('pet_opacity', 1.0)
                    self.pet.opacity = self.pet.pet_opacity
                print(f"窗口位置已恢复: ({Window.left}, {Window.top})")
            else:
                print("未找到窗口位置配置，使用默认值")
        except Exception as e:
            print(f"⚠️ 恢复窗口位置失败: {e}，使用默认值")


# 桌面模式默认背景色已在 init_app_window 中设置
if __name__ == '__main__':
    DesktopPetAlarmApp().run()
