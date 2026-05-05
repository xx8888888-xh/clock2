"""
安卓桌面宠物闹钟 - Android兼容修复版
修复Android悬浮窗闪退和窗口看不见的问题
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

# Android环境检测
IS_ANDROID = False
try:
    import android
    IS_ANDROID = True
except ImportError:
    pass

# Android权限处理
if IS_ANDROID:
    try:
        from android.permissions import Permission, request_permissions
        HAS_PERMISSION_MODULE = True
    except ImportError:
        HAS_PERMISSION_MODULE = False

# 设置窗口透明背景 - 修复：不使用完全透明
Config.set('graphics', 'background_color', '0,0,0,0.01')  # 改为几乎透明，保证窗口可见

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

# ==================== Android窗口服务 ====================
class AndroidWindowService:
    """Android悬浮窗服务，解决窗口初始化时序问题"""
    def __init__(self, app):
        self.app = app
        self.window_init_done = False
        self.permissions_requested = False
        print("AndroidWindowService初始化")
    
    def init_window_safe(self):
        """安全的窗口初始化，分阶段初始化"""
        if not IS_ANDROID:
            self.init_window_direct()
            return
        
        # Android平台：分阶段初始化
        Clock.schedule_once(lambda dt: self.init_window_stage1(), 0.5)
        Clock.schedule_once(lambda dt: self.init_window_stage2(), 1.0)
        Clock.schedule_once(lambda dt: self.init_window_stage3(), 1.5)
    
    def init_window_direct(self):
        """非Android平台直接初始化"""
        print("非Android平台：直接初始化窗口")
        Window.borderless = True
        Window.always_on_top = True
        Window.resizable = False
        Window.size = (dp(200), dp(200))
        Window.left = 100
        Window.top = 500
        Window.clearcolor = (0, 0, 0, 0.01)  # 保证窗口可见
        self.window_init_done = True
    
    def init_window_stage1(self):
        """第一阶段：窗口设置"""
        print("Android窗口初始化：阶段1")
        
        # 窗口基本设置
        Window.borderless = True
        Window.always_on_top = True
        Window.resizable = False
        
        # 透明度设置为0.01（几乎透明），确保窗口可见
        Window.clearcolor = (0, 0, 0, 0.01)
        
        # 固定窗口大小，避免窗口大小变化导致的闪退
        Window.size = (280, 280)
    
    def init_window_stage2(self):
        """第二阶段：窗口位置"""
        print("Android窗口初始化：阶段2")
        
        # 固定窗口位置
        Window.top = 180
        Window.left = 60
        
        # 检查窗口是否可见
        if Window.width == 0 or Window.height == 0:
            print("窗口大小异常，重新设置")
            Window.size = (300, 300)
            Window.top = 200
            Window.left = 100
    
    def init_window_stage3(self):
        """第三阶段：宠物和组件初始化"""
        print("Android窗口初始化：阶段3")
        
        # 初始化宠物
        if self.app.pet:
            self.app.root.add_widget(self.app.pet)
        
        # 初始化横幅
        if self.app.banner:
            self.app.root.add_widget(self.app.banner)
        
        # 请求Android权限（如果需要）
        if IS_ANDROID and HAS_PERMISSION_MODULE:
            try:
                from android.permissions import Permission, request_permissions
                request_permissions([Permission.SYSTEM_ALERT_WINDOW])
                print("Android权限请求成功")
            except Exception as e:
                print(f"Android权限请求失败: {e}")
        
        self.window_init_done = True
        print("窗口初始化完成")

# ==================== 宠物部件修复版 ====================
class CutePetFixed(Widget):
    """修复版宠物部件，解决Android兼容性问题"""
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
        
        # 延迟初始化绘制
        Clock.schedule_once(lambda dt: self.draw_cute_pet_fixed(), 0.3)
    
    def draw_cute_pet_fixed(self):
        """延迟绘制宠物，避免Android初始化问题"""
        image_files = ['pet.png', 'pet_default.png', 'assets/pet.png']
        for img_file in image_files:
            if os.path.exists(img_file):
                self.pet_image = Image(
                    source=img_file,
                    size=self.size,
                    pos=self.pos,
                    allow_stretch=True,
                    keep_ratio=True
                )
                self.add_widget(self.pet_image)
                return
        
        # 默认宠物绘制
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
        
        self.bind(pos=self.update_pet_fixed, size=self.update_pet_fixed)
    
    def update_pet_fixed(self, *args):
        """更新宠物位置"""
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
    
    def on_touch_down(self, touch):
        """触摸事件"""
        if self.collide_point(*touch.pos):
            self.is_dragging = True
            self.drag_start_pos = touch.pos
            self.touch_start_time = time.time()
            
            # 保存窗口当前位置
            self.drag_offset_x = Window.left
            self.drag_offset_y = Window.top
            
            # 点击动画
            self.cute_click_animation()
            return True
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        """拖拽事件"""
        if self.is_dragging:
            dx = touch.x - self.drag_start_pos[0]
            dy = touch.y - self.drag_start_pos[1]
            
            # 计算新位置
            new_left = self.drag_offset_x + int(dx)
            new_top = self.drag_offset_y + int(dy)
            
            # Android屏幕边界检查
            screen_w = Window.width if Window.width > 0 else 1920
            screen_h = Window.height if Window.height > 0 else 1080
            
            pet_size = int(self.pet_size)
            margin = 50
            
            # 边界限制
            new_left = max(-margin, min(new_left, screen_w - pet_size + margin))
            new_top = max(-margin, min(new_top, screen_h - pet_size + margin))
            
            # 更新窗口位置
            Window.left = new_left
            Window.top = new_top
            
            return True
        return super().on_touch_move(touch)
    
    def cute_click_animation(self):
        """点击动画"""
        anim1 = Animation(scale_x=1.15, scale_y=0.85, duration=0.08, t='out_quad')
        anim2 = Animation(scale_x=0.95, scale_y=1.05, duration=0.1, t='out_quad')
        anim3 = Animation(scale_x=1.02, scale_y=0.98, duration=0.08, t='in_out_quad')
        anim4 = Animation(scale_x=1.0, scale_y=1.0, duration=0.08, t='in_out_quad')
        (anim1 + anim2 + anim3 + anim4).start(self)

# ==================== 主应用修复版 ====================
class DesktopPetAlarmAppFixed(App):
    """修复版主应用，解决Android闪退问题"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pet = None
        self.banner = None
        self.alarm_manager = None
        self.timer_manager = None
        self.sleep_check_event = None
        self.alarm_sound = None
        self.banner_display_time = 5
        
        # Android窗口服务
        self.android_service = None
    
    def build(self):
        """构建方法 - 修复Android初始化时序"""
        print("应用构建开始")
        
        # Android窗口服务
        if IS_ANDROID:
            self.android_service = AndroidWindowService(self)
        
        # 创建布局
        self.root = FloatLayout()
        
        # 延迟初始化窗口（Android需要延迟）
        Clock.schedule_once(lambda dt: self.init_window_and_pet(), 0.5)
        
        return self.root
    
    def init_window_and_pet(self):
        """延迟初始化窗口和宠物"""
        print("延迟初始化窗口和宠物")
        
        # 窗口透明度修复：改为0.01确保可见
        Window.clearcolor = (0, 0, 0, 0.01)
        
        # 窗口设置
        Window.borderless = True
        Window.always_on_top = True
        Window.resizable = False
        Window.size = (dp(200), dp(200))
        
        # Android特殊窗口位置
        if IS_ANDROID:
            Window.left = 60  # Android需要较小的偏移
            Window.top = 180
        else:
            Window.left = 100
            Window.top = 500
        
        # 初始化宠物
        self.pet = CutePetFixed()
        self.root.add_widget(self.pet)
        
        # 初始化横幅
        self.banner = CuteBanner()
        self.root.add_widget(self.banner)
        
        # 初始化闹钟管理器
        self.alarm_manager = AlarmClock()
        self.timer_manager = TimerManager()
        
        # 加载声音
        self.load_alarm_sound()
        
        # 定时检查睡眠状态
        self.sleep_check_event = Clock.schedule_interval(self.check_pet_sleep_state, 60)
        
        # Android Service初始化
        if IS_ANDROID and self.android_service:
            self.android_service.init_window_safe()
        
        print("窗口初始化完成")
    
    def load_alarm_sound(self):
        """加载闹钟声音"""
        try:
            sound_files = ['alarm.wav', 'alarm.mp3', 'assets/alarm.wav']
            for sound_file in sound_files:
                if os.path.exists(sound_file):
                    self.alarm_sound = SoundLoader.load(sound_file)
                    print(f"加载声音文件: {sound_file}")
                    break
        except Exception as e:
            print(f"加载声音失败: {e}")
    
    def check_pet_sleep_state(self, dt):
        """检查宠物睡眠状态"""
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
        """触发闹钟"""
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
        """触发计时器"""
        self.banner.show(f"⏱️ {timer['label']}", "时间到了！")
        Clock.schedule_once(lambda dt: self.banner.hide(), self.banner_display_time)
        
        self.play_alarm_sound()
        self.vibrate()
        
        try:
            notification.notify(
                title=f"宠物闹钟 - {timer['label']}",
                message="倒计时结束！",
                app_name='宠物闹钟',
                timeout=10
            )
        except Exception as e:
            print(f"显示通知失败: {e}")
    
    def show_alarm_banner(self, alarm):
        """显示闹钟横幅"""
        title = alarm['label']
        content = alarm.get('content', '时间到了！')
        self.banner.show(title, content, self.banner_display_time)
    
    def play_alarm_sound(self):
        """播放闹钟声音"""
        try:
            if (self.alarm_manager.settings.get('sound_enabled', True) and 
                self.alarm_sound):
                volume = self.alarm_manager.settings.get('volume', 0.8)
                self.alarm_sound.volume = volume
                self.alarm_sound.play()
        except Exception as e:
            print(f"播放声音失败: {e}")
    
    def vibrate(self):
        """振动"""
        try:
            if self.alarm_manager.settings.get('vibrate', True):
                vibrator.vibrate(1)
        except Exception as e:
            print(f"振动失败: {e}")
    
    def show_alarm_notification(self, alarm):
        """显示闹钟通知"""
        try:
            notification.notify(
                title=f"宠物闹钟 - {alarm['label']}",
                message=alarm.get('content', '时间到了！'),
                app_name='宠物闹钟',
                timeout=10
            )
        except Exception as e:
            print(f"显示通知失败: {e}")
    
    def show_notification(self, message):
        """显示通知"""
        try:
            notification.notify(
                title="宠物闹钟",
                message=message,
                app_name='宠物闹钟',
                timeout=5
            )
        except Exception as e:
            print(f"显示通知失败: {e}")
    
    def on_stop(self):
        """应用停止"""
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
            with open('window_pos.json', 'w', encoding='utf-8') as f:
                json.dump(window_pos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存窗口位置失败: {e}")
        
        gc.collect()
    
    def on_start(self):
        """应用启动"""
        try:
            if os.path.exists('window_pos.json'):
                with open('window_pos.json', 'r', encoding='utf-8') as f:
                    window_pos = json.load(f)
                Window.left = window_pos.get('left', 100)
                Window.top = window_pos.get('top', 500)
                if self.pet:
                    self.pet.pet_size = window_pos.get('pet_size', 160)
                    self.pet.pet_opacity = window_pos.get('pet_opacity', 1.0)
                    self.pet.opacity = self.pet.pet_opacity
        except Exception as e:
            print(f"恢复窗口位置失败: {e}")
            
        if IS_ANDROID:
            print("Android环境启动")
            if self.android_service:
                self.android_service.init_window_safe()

# ==================== 运行应用 ====================
if __name__ == '__main__':
    print("=== 宠物闹钟Android修复版启动 ===")
    print(f"Android检测: {IS_ANDROID}")
    app = DesktopPetAlarmAppFixed()
    app.run()
    print("=== 宠物闹钟Android修复版完成 ===")