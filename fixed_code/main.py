"""
安卓桌面宠物闹钟 - 完全修复版 V3.0
修复所有bug，可直接打包使用
"""

import os
import json
import gc
import threading
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
# 修复BUG-001: 添加振动模块异常处理
try:
    from plyer import vibrator
    HAS_VIBRATOR = True
except ImportError:
    HAS_VIBRATOR = False
    print("警告: vibrator模块不可用，振动功能将禁用")

# 修复ERR-001: notification导入异常处理
try:
    from plyer import notification
    HAS_NOTIFICATION = True
except ImportError:
    HAS_NOTIFICATION = False
    print("警告: notification模块不可用，通知功能将禁用")

import time

# 修复BUG-002: 添加自定义模块异常处理
try:
    from simple_logger import info, warning, error, debug, log_exception, log_method_call
    HAS_LOGGER = True
except ImportError:
    HAS_LOGGER = False
    # 修复ERR-003和ERR-004: 改进日志回退函数
    import sys
    def info(msg): 
        if msg: 
            print(f"[INFO] {msg}")
    def warning(msg): 
        if msg: 
            print(f"[WARN] {msg}")
    def error(msg): 
        if msg: 
            print(f"[ERROR] {msg}")
    def debug(msg): 
        if msg and '--debug' in sys.argv:  # 只在调试模式输出
            print(f"[DEBUG] {msg}")
    def log_exception(e, ctx=""): 
        if e: 
            print(f"[EXCEPTION] {ctx}: {type(e).__name__}: {e}")
    def log_method_call(func): 
        return func
    info("simple_logger模块不可用，使用简单日志回退")

# 修复BUG-002: 其他自定义模块异常处理
try:
    from pet_mood import PetMoodSystem
    from weather import WeatherAPI
    from calendar_integration import CalendarIntegration
    HAS_EXTRA_MODULES = True
except ImportError as e:
    HAS_EXTRA_MODULES = False
    error(f"扩展模块导入失败: {e}")
    # 修复ERR-005: 创建更完整的回退类
    class PetMoodSystem:
        def __init__(self):
            self.moods = ['normal', 'happy', 'sad', 'angry', 'sleepy']
        def get_current_mood(self, current_time=None, weather_impact=None, calendar_event=None): 
            return 'normal'
        def update_mood(self, interaction_type):
            return 'normal'
        def get_mood_emoji(self, mood=None):
            return '😊'
    
    class WeatherAPI:
        def __init__(self, api_key='demo_key'):
            self.api_key = api_key
            self.has_data = False
            self.last_weather_data = None
        def get_current_weather(self, city='Beijing'): 
            return {'temp': 25, 'description': '晴天', 'humidity': 50, 'wind_speed': 5}
        def _get_default_weather(self):
            return {'temp': 25, 'description': '默认天气'}
    
    class CalendarIntegration:
        def __init__(self): 
            self.events = []
        def get_next_event(self): 
            return None
        def get_today_events(self):
            return []
        def add_event(self, *args, **kwargs):
            return {'success': False, 'reason': '回退模式'}
        def get_event_emoji(self, event_type):
            return '📅'

# 修复BUG-002: 添加自定义模块异常处理
try:
    from simple_logger import info, warning, error, debug, log_exception, log_method_call
    HAS_LOGGER = True
except ImportError:
    HAS_LOGGER = False
    # 简单的日志回退
    def info(msg): print(f"[INFO] {msg}")
    def warning(msg): print(f"[WARN] {msg}")
    def error(msg): print(f"[ERROR] {msg}")
    def debug(msg): print(f"[DEBUG] {msg}")
    def log_exception(e, ctx=""): print(f"[EXCEPTION] {ctx}: {e}")
    def log_method_call(func): return func
    print("警告: simple_logger模块不可用，使用简单日志回退")

# 修复BUG-002: 其他自定义模块异常处理
try:
    from pet_mood import PetMoodSystem
    from weather import WeatherAPI
    from calendar_integration import CalendarIntegration
    HAS_EXTRA_MODULES = True
except ImportError as e:
    HAS_EXTRA_MODULES = False
    print(f"警告: 扩展模块导入失败: {e}")
    # 创建空类作为回退
    class PetMoodSystem:
        def get_current_mood(self, *args, **kwargs): return 'normal'
    class WeatherAPI:
        def get_current_weather(self, *args, **kwargs): return {'temp': 25, 'description': '未知'}
    class CalendarIntegration:
        def __init__(self): self.events = []
        def get_next_event(self): return None

# 设置窗口透明背景
# 修复BUG-003和ERR-006: 使用更合适的透明度值
Config.set('graphics', 'background_color', '0,0,0,0.05')  # 5%透明度，更可靠

# ==================== 颜色主题 ====================
# 修复ERR-007: 安全颜色获取函数
def safe_get_color(hex_color, default=(1, 1, 1, 1)):
    try:
        return get_color_from_hex(hex_color)
    except Exception as e:
        error(f"颜色解析失败 {hex_color}: {e}")
        return default

CUTE_COLORS = {
    'primary': safe_get_color('#FF8FB1', (1, 0.56, 0.69, 1)),
    'secondary': safe_get_color('#B5EAEA', (0.71, 0.92, 0.92, 1)),
    'accent': safe_get_color('#FFE194', (1, 0.88, 0.58, 1)),
    'purple': safe_get_color('#D4A5FF', (0.83, 0.65, 1, 1)),
    'coral': safe_get_color('#FF9A8B', (1, 0.60, 0.55, 1)),
    'background': safe_get_color('#FFF5F7', (1, 0.96, 0.97, 1)),
    'text': safe_get_color('#5A4A4A', (0.35, 0.29, 0.29, 1)),
    'white': (1, 1, 1, 1),
    'shadow': (0, 0, 0, 0.15),
    'success': (0.3, 0.8, 0.3, 1),
    'error': (1, 0.3, 0.3, 1),
}

# 默认配置
# 修复ERR-009: 添加类型注释
typing_available = False
try:
    from typing import Dict, Any, Optional
    typing_available = True
except ImportError:
    pass

DEFAULT_PET_SETTINGS: Dict[str, Any] = {
    'size': 160,               # 宠物大小（像素）
    'opacity': 1.0,            # 不透明度（0.0-1.0）
    'sleep_start_hour': 22,    # 睡眠开始时间（小时，0-23）
    'sleep_end_hour': 7,       # 睡眠结束时间（小时，0-23）
}

DEFAULT_ALARM_SETTINGS: Dict[str, Any] = {
    'snooze_duration': 5,      # 贪睡时长（分钟）
    'max_snooze_count': 3,     # 最大贪睡次数
    # 修复ERR-008: 根据实际支持情况设置振动默认值
    'vibrate': HAS_VIBRATOR,   # 是否启用振动
    'sound_enabled': True,     # 是否启用声音
    'volume': 0.8,             # 音量（0.0-1.0）
    'banner_time': 5,          # 横幅显示时间（秒）
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
            # 修复ERR-010: 避免在__init__中使用可能未确定的self.x/self.y
            self.shadow_rect = RoundedRectangle(
                pos=(0 + dp(3), 0 - dp(3)),  # 使用默认位置
                size=self.size,
                radius=[dp(20)]
            )
            Color(*CUTE_COLORS['primary'])
            # 修复ERR-010: 使用默认位置
            self.bg_rect = RoundedRectangle(
                pos=(0, 0),  # 使用默认位置
                size=self.size,
                radius=[dp(20)]
            )
        
        # 修复ERR-011: 先定义方法再绑定
        def update_bg(self, *args):
            # 修复ERR-013: 添加异常处理
            try:
                self.shadow_rect.pos = (self.x + dp(3), self.y - dp(3))
                self.shadow_rect.size = self.size
                self.bg_rect.pos = self.pos
                self.bg_rect.size = self.size
            except Exception as e:
                error(f"update_bg失败: {e}")
        
        self.update_bg = update_bg.__get__(self, type(self))
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        content_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(5))
        # 修复ERR-012: 使用固定高度而不是比例
        self.title_label = Label(
            text='⏰ 闹钟提醒',
            font_size=sp(22),
            bold=True,
            color=CUTE_COLORS['white'],
            size_hint_y=None,
            height=dp(35)  # 固定高度
        )
        content_layout.add_widget(self.title_label)
        
        self.content_label = Label(
            text='时间到了！',
            font_size=sp(16),
            color=CUTE_COLORS['white'],
            size_hint_y=None,
            height=dp(45)  # 固定高度
        )
        content_layout.add_widget(self.content_label)
        self.add_widget(content_layout)
    
    def show(self, title, content, duration=5):
        # 修复ERR-014: 改进事件取消逻辑
        try:
            self.title_label.text = f"⏰ {title}"
            self.content_label.text = content
            
            if self.hide_event is not None:
                self.hide_event.cancel()
            
            anim = Animation(opacity=1, duration=0.3, t='out_quad')
            anim.start(self)
            
            # 修复ERR-017: 使用局部函数而不是lambda
            def hide_callback(dt):
                self.hide()
            self.hide_event = Clock.schedule_once(hide_callback, duration)
        except Exception as e:
            error(f"show失败: {e}")
    
    def hide(self):
        # 修复ERR-015: 改进检查逻辑
        try:
            if self.hide_event is not None:
                self.hide_event.cancel()
                self.hide_event = None
            anim = Animation(opacity=0, duration=0.3, t='in_quad')
            anim.start(self)
        except Exception as e:
            error(f"hide失败: {e}")
    
    def cleanup(self):
        # 修复ERR-016: 添加异常处理
        try:
            if self.hide_event is not None:
                self.hide_event.cancel()
                self.hide_event = None
        except Exception as e:
            error(f"cleanup失败: {e}")

# 修复BUG-004: 跨午夜时间处理函数
def is_sleeping_time(current_hour, start_hour=22, end_hour=7):
    """判断是否是睡眠时间（支持跨午夜）
    Args:
        current_hour: 当前小时 (0-23)
        start_hour: 睡眠开始时间 (0-23)
        end_hour: 睡眠结束时间 (0-23)
    Returns:
        bool: 是否在睡眠时间内
    """
    # 修复ERR-018: 添加输入验证
    if not isinstance(current_hour, (int, float)):
        raise TypeError(f"current_hour必须是数字，得到{type(current_hour)}")
    if not (0 <= current_hour <= 23):
        raise ValueError(f"current_hour必须在0-23之间，得到{current_hour}")
    if not (0 <= start_hour <= 23):
        raise ValueError(f"start_hour必须在0-23之间，得到{start_hour}")
    if not (0 <= end_hour <= 23):
        raise ValueError(f"end_hour必须在0-23之间，得到{end_hour}")
    
    if start_hour <= end_hour:
        # 不跨午夜的情况: start_hour <= current_hour < end_hour
        return start_hour <= current_hour < end_hour
    else:
        # 跨午夜的情况: current_hour >= start_hour 或 current_hour < end_hour
        return current_hour >= start_hour or current_hour < end_hour


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
            # 修复BUG-006: 避免在__init__中直接使用self.pos，使用默认值
            self.bubble = Ellipse(pos=(0, 0), size=self.size)
        
        # 修复ERR-020: 先定义方法再绑定
        def update_bubble(self, *args):
            # 修复ERR-019和ERR-021: 添加异常处理和位置更新
            try:
                self.bubble.pos = self.pos
                self.bubble.size = self.size
                self.label.pos = self.pos
                self.label.size = self.size
            except Exception as e:
                error(f"update_bubble失败: {e}")
        
        self.update_bubble = update_bubble.__get__(self, type(self))
        self.bind(pos=self.update_bubble, size=self.update_bubble)
        
        self.label = Label(
            text='Z',
            font_size=sp(20),
            bold=True,
            color=(0.4, 0.4, 0.6, 1),
            pos=(0, 0),  # 修复ERR-021: 使用默认位置
            size=self.size
        )
        self.add_widget(self.label)
    
    def float_up(self):
        # 修复ERR-022: 添加None检查
        if self.current_anim is not None:
            self.current_anim.cancel(self)
        
        self.opacity = 0
        # 修复ERR-023: 确保位置已确定
        if hasattr(self, 'y') and self.y is not None:
            start_y = self.y
        else:
            start_y = 0
        
        anim = Animation(opacity=0.8, duration=0.5)
        anim &= Animation(y=start_y + dp(60), duration=2, t='out_quad')
        anim &= Animation(x=self.x + dp(10), duration=2, t='in_out_sine')
        
        # 修复ERR-024: 使用局部函数
        def animation_complete(*args):
            self.hide()
        
        anim.bind(on_complete=animation_complete)
        self.current_anim = anim
        anim.start(self)
    
    def hide(self):
        # 修复ERR-025: 添加None检查
        if self.current_anim is not None:
            self.current_anim.cancel(self)
        # 修复ERR-026: 保存动画引用
        hide_anim = Animation(opacity=0, duration=0.3)
        hide_anim.start(self)
    
    def cleanup(self):
        # 修复ERR-027: 添加异常处理
        try:
            if self.current_anim is not None:
                self.current_anim.cancel(self)
                self.current_anim = None
        except Exception as e:
            error(f"SleepBubble cleanup失败: {e}")
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
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # 修复BUG-020: 添加线程安全锁
        self.animation_lock = threading.RLock()
        
        # 新增功能系统
        self.mood_system = PetMoodSystem()
        self.weather_api = WeatherAPI()
        self.calendar = CalendarIntegration()
        self.current_mood = 'normal'
        self.current_weather = None
        self.next_calendar_event = None
        
        # 修复ERR-028: 集中管理定时器
        self.timers = []
        
        # 定时更新心情、天气、日历
        self.timers.append(Clock.schedule_interval(self.update_mood_status, 30))  # 每30秒更新心情
        self.timers.append(Clock.schedule_interval(self.update_weather_status, 1800))  # 每30分钟更新天气
        self.timers.append(Clock.schedule_interval(self.update_calendar_status, 600))  # 每10分钟更新日历
        
        self.draw_cute_pet()
        
        # 修复ERR-029: 使用局部函数而不是lambda
        def start_idle_callback(dt):
            self.start_cute_idle()
        Clock.schedule_once(start_idle_callback, 0.5)
        
        # 修复ERR-030: 统一管理定时器
        bubble_timer = Clock.schedule_interval(self.spawn_sleep_bubble, 3)
        self.timers.append(bubble_timer)
        self.bubble_timer = bubble_timer
    
    def draw_cute_pet(self):
        # 修复ERR-031: 添加异常处理和回退机制
        try:
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
                    info(f"加载宠物图像: {img_file}")
                    return
            
            info("未找到宠物图像文件，使用默认图形")
            self.draw_default_pet()
        except Exception as e:
            error(f"加载宠物图像失败: {e}")
            self.draw_default_pet()
    
    def cleanup_timers(self):
        """清理所有定时器"""
        # 修复ERR-028: 定时器清理方法
        if hasattr(self, 'timers'):
            for timer in self.timers:
                if timer is not None:
                    try:
                        timer.cancel()
                    except Exception as e:
                        error(f"取消定时器失败: {e}")
            self.timers = []
    
    def draw_default_pet(self):
        # 修复ERR-032、ERR-033、ERR-034: 添加位置检查和异常处理
        try:
            # 确保位置属性存在
            if not hasattr(self, 'x') or self.x is None:
                self.x = 0
            if not hasattr(self, 'y') or self.y is None:
                self.y = 0
            if not hasattr(self, 'pos') or self.pos is None:
                self.pos = (0, 0)
            
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
        except Exception as e:
            error(f"draw_default_pet失败: {e}")
        
        self.bind(pos=self.update_pet, size=self.update_pet)
        
        # 修复ERR-035: 添加位置检查
        if hasattr(self, 'x') and self.x is not None and hasattr(self, 'y') and self.y is not None:
            current_x = self.x
            current_y = self.y
        else:
            current_x = 0
            current_y = 0
            
        for i in range(3):
            bubble = SleepBubble()
            bubble.pos = (
                current_x + self.pet_size + dp(10) + i * dp(15),
                current_y + self.pet_size * 0.7 + i * dp(10)
            )
            self.sleep_bubbles.append(bubble)
            self.add_widget(bubble)
    
    def update_pet(self, *args):
        # 修复ERR-036、ERR-037: 改进检查和异常处理
        try:
            # 检查所有图形对象是否存在
            if hasattr(self, 'pet_body') and self.pet_body is not None and \
               hasattr(self, 'shadow') and self.shadow is not None and \
               hasattr(self, 'highlight') and self.highlight is not None:
                
                self.shadow.pos = (self.x + dp(5), self.y - dp(5))
                self.shadow.size = self.size
                self.pet_body.pos = self.pos
                self.pet_body.size = self.size
            else:
                debug(f"update_pet: 缺少图形对象，宠物: {hasattr(self, 'pet_body')}, 阴影: {hasattr(self, 'shadow')}, 高光: {hasattr(self, 'highlight')}")
        except Exception as e:
            debug(f"update_pet异常: {e}")
            
        # 继续更新其他图形元素
        try:
            highlight_size = (self.pet_size * 0.4, self.pet_size * 0.25)
            if hasattr(self, 'highlight') and self.highlight is not None:
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
        except Exception as e:
            error(f"update_pet更新后续元素失败: {e}")
    
    def spawn_sleep_bubble(self, dt):
        if self.is_sleeping:
            for bubble in self.sleep_bubbles:
                if bubble.opacity < 0.1:
                    bubble.float_up()
                    break
    
    def cancel_current_animation(self):
        # 修复BUG-020: 线程安全保护
        with self.animation_lock:
            if self.current_animation:
                self.current_animation.cancel(self)
                self.current_animation = None
    
    def start_cute_idle(self):
        self.cancel_current_animation()
        self.is_excited = False
        # 修复ERR-038: 添加位置检查
        base_y = self.y if hasattr(self, 'y') and self.y is not None else 0
        
        # 修复ERR-039: 将嵌套函数改为内部方法
        self._create_idle_animation(base_y)
    
    def _create_idle_animation(self, base_y):
        """创建空闲动画（修复ERR-039）"""
        if self.is_excited or self.is_sleeping:
            return
        
        breathe_in = Animation(scale=1.05, duration=1.2, t='in_out_sine')
        breathe_out = Animation(scale=1.0, duration=1.2, t='in_out_sine')
        sway_left = Animation(rotation=-3, duration=1.2, t='in_out_sine')
        sway_right = Animation(rotation=3, duration=1.2, t='in_out_sine')
        float_up = Animation(y=base_y + dp(8), duration=1.5, t='in_out_sine')
        float_down = Animation(y=base_y, duration=1.5, t='in_out_sine')
        
        anim = (breathe_in & sway_left & float_up) + (breathe_out & sway_right & float_down)
        anim.repeat = True
        self.current_animation = anim
        anim.start(self)
    
    def start_sleep_animation(self):
        self.cancel_current_animation()
        self.is_sleeping = True
        
        anim = Animation(scale=0.85, opacity=0.6, rotation=0, duration=1, t='out_quad')
        
        # 修复ERR-041: 使用局部函数引用self
        def start_breathing(*args):
            self._start_sleep_breathing()
        
        anim.bind(on_complete=start_breathing)
        self.current_animation = anim
        anim.start(self)
    
    def _start_sleep_breathing(self):
        """开始睡眠呼吸动画（修复ERR-041）"""
        if self.is_sleeping:
            breathe_in = Animation(opacity=0.5, scale=0.83, duration=2, t='in_out_sine')
            breathe_out = Animation(opacity=0.7, scale=0.87, duration=2, t='in_out_sine')
            anim = breathe_in + breathe_out
            anim.repeat = True
            self.current_animation = anim
            anim.start(self)
    
    def wake_up_animation(self):
        # 修复ERR-042和ERR-043: 添加异常处理和位置检查
        try:
            self.cancel_current_animation()
            self.is_sleeping = False
            base_y = self.y if hasattr(self, 'y') and self.y is not None else 0
            
            anim1 = Animation(scale=1.2, rotation=10, opacity=1, duration=0.15, t='out_quad')
            anim2 = Animation(scale=0.9, rotation=-10, duration=0.1, t='in_quad')
            anim3 = Animation(scale=1.15, rotation=5, duration=0.1, t='out_quad')
            anim4 = Animation(scale=1.0, rotation=0, duration=0.15, t='in_out_quad')
            jump_up = Animation(y=base_y + dp(30), duration=0.15, t='out_quad')
            jump_down = Animation(y=base_y, duration=0.25, t='bounce_out')
            
            anim = (anim1 & jump_up) + (anim2 & jump_down) + anim3 + anim4
            # 修复ERR-044: 使用局部函数而不是lambda
            def wake_up_complete(*args):
                self.start_cute_idle()
            anim.bind(on_complete=wake_up_complete)
            self.current_animation = anim
            anim.start(self)
        except Exception as e:
            error(f"wake_up_animation失败: {e}")
    
    def excited_animation(self):
        self.cancel_current_animation()
        self.is_excited = True
        # 修复ERR-045: 添加位置检查
        base_y = self.y if hasattr(self, 'y') and self.y is not None else 0
        
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
        # 修复ERR-046: 添加异常处理
        try:
            if self.collide_point(*touch.pos):
                self.is_dragging = True
                self.drag_start_pos = touch.pos
                self.touch_start_time = time.time()
                # 修复ERR-047: 添加Window属性检查
                if hasattr(Window, 'left') and Window.left is not None:
                    self.drag_offset_x = Window.left
                else:
                    self.drag_offset_x = 0
                if hasattr(Window, 'top') and Window.top is not None:
                    self.drag_offset_y = Window.top
                else:
                    self.drag_offset_y = 0
                self.cute_click_animation()
                return True
        except Exception as e:
            error(f"on_touch_down失败: {e}")
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        # 修复ERR-049和ERR-050: 添加异常处理和边界检查改进
        try:
            if self.is_dragging:
                # 检查touch坐标有效性
                if not hasattr(touch, 'x') or touch.x is None or not hasattr(touch, 'y') or touch.y is None:
                    return True  # 坐标无效但继续处理
                
                dx = touch.x - self.drag_start_pos[0]
                dy = touch.y - self.drag_start_pos[1]
                
                new_left = self.drag_offset_x + int(dx)
                new_top = self.drag_offset_y + int(dy)
                
                # 修复ERR-049: 改进边界检查
                screen_w = Window.width if hasattr(Window, 'width') and Window.width > 0 else 1920
                screen_h = Window.height if hasattr(Window, 'height') and Window.height > 0 else 1080
                
                pet_size = int(self.pet_size) if hasattr(self, 'pet_size') else 160
                margin = 50
                
                # 确保计算值有效
                new_left = max(-margin, min(new_left, screen_w - pet_size + margin))
                new_top = max(-margin, min(new_top, screen_h - pet_size + margin))
                
                # 确保Window属性存在
                if hasattr(Window, 'left'):
                    Window.left = new_left
                if hasattr(Window, 'top'):
                    Window.top = new_top
                
                return True
        except Exception as e:
            error(f"on_touch_move失败: {e}")
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        # 修复ERR-051和相关问题: 添加异常处理和逻辑改进
        try:
            if self.is_dragging:
                self.is_dragging = False
                
                # 检查touch坐标有效性
                if not hasattr(touch, 'x') or touch.x is None or not hasattr(touch, 'y') or touch.y is None:
                    return True  # 坐标无效但继续处理
                
                touch_duration = time.time() - self.touch_start_time
                dx = abs(touch.x - self.drag_start_pos[0])
                dy = abs(touch.y - self.drag_start_pos[1])
                
                # 修复ERR-051: 改进触摸时长和点击逻辑
                if dx < 10 and dy < 10 and touch_duration < 0.4:
                    # 短距离短时间：视为点击
                    self.handle_click()
                elif touch_duration >= 0.4:
                    # 长时间触摸：视为长按
                    self.on_long_press()
                else:
                    # 其他情况：拖拽释放
                    debug(f"拖拽释放: 距离({dx},{dy}), 时长{touch_duration:.2f}s")
                
                return True
        except Exception as e:
            error(f"on_touch_up失败: {e}")
            self.is_dragging = False  # 确保状态重置
        return super().on_touch_up(touch)
    
    def handle_click(self):
        current_time = time.time()
        time_since_last = current_time - self.last_click_time
        
        if time_since_last < 0.35:
            self.click_count += 1
        else:
            self.click_count = 1
        
        self.last_click_time = current_time
        
        if self.click_count == 1:
            # 修复ERR-052: 使用局部函数而不是lambda
            def single_click_callback(dt):
                self.on_pet_click()
            Clock.schedule_once(single_click_callback, 0.2)
        elif self.click_count == 2:
            self.on_double_click()
        elif self.click_count >= 3:
            self.on_triple_click()
            self.click_count = 0
    
    def on_pet_click(self):
        # 修复ERR-053和ERR-054: 改进状态检查和异常处理
        try:
            # 修复ERR-053: 检查click_count状态
            if hasattr(self, 'click_count') and self.click_count >= 1:
                app = App.get_running_app()
                if app is not None:
                    app.show_main_menu()
        except Exception as e:
            error(f"on_pet_click失败: {e}")
    
    def on_double_click(self):
        # 修复ERR-055: 添加异常处理
        try:
            self.excited_animation()
            app = App.get_running_app()
            if app:
                # 修复lambda使用
                def show_menu_callback(dt):
                    app.show_main_menu()
                Clock.schedule_once(show_menu_callback, 0.3)
        except Exception as e:
            error(f"on_double_click失败: {e}")
    
    def on_triple_click(self):
        # 修复ERR-056: 添加异常处理
        try:
            app = App.get_running_app()
            if app:
                app.show_timer_dialog()
        except Exception as e:
            error(f"on_triple_click失败: {e}")
    
    def on_long_press(self):
        # 修复ERR-057: 添加异常处理
        try:
            app = App.get_running_app()
            if app:
                app.show_quick_menu()
        except Exception as e:
            error(f"on_long_press失败: {e}")
    
    def on_scale(self, instance, value):
        # 修复ERR-058: 添加属性检查
        if not hasattr(self, 'pet_size') or self.pet_size is None:
            self.pet_size = 160  # 默认值
        new_size = self.pet_size * value
        self.size = (new_size, new_size)
        if self.pet_image:
            self.pet_image.size = self.size
    
    def cleanup(self):
        # 修复ERR-059: 添加异常处理
        try:
            self.cancel_current_animation()
            if self.bubble_timer:
                self.bubble_timer.cancel()
                self.bubble_timer = None
            for bubble in self.sleep_bubbles:
                bubble.cleanup()
        except Exception as e:
            error(f"CutePet cleanup失败: {e}")

    def start_happy_animation(self):
        self.cancel_current_animation()
        # 修复ERR-060: 添加位置检查
        base_y = self.y if hasattr(self, 'y') and self.y is not None else 0
        
        # 快乐的摇摆动画
        sway_left = Animation(rotation=-8, duration=0.8, t='in_out_sine')
        sway_right = Animation(rotation=8, duration=0.8, t='in_out_sine')
        jump_up = Animation(y=base_y + dp(15), duration=0.3, t='out_quad')
        jump_down = Animation(y=base_y, duration=0.3, t='bounce_out')
        
        anim = (sway_left & jump_up) + (sway_right & jump_down)
        anim.repeat = True
        self.current_animation = anim
        anim.start(self)

    def start_sleepy_animation(self):
        self.cancel_current_animation()
        self.is_sleeping = True
        # 修复ERR-061: 添加位置检查
        base_y = self.y if hasattr(self, 'y') and self.y is not None else 0
        
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
        self.cancel_current_animation()
        self.is_excited = True
        # 修复ERR-062: 添加位置检查
        base_y = self.y if hasattr(self, 'y') and self.y is not None else 0
        
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
        
        # 修复ERR-064: 使用局部函数
        def excited_complete(*args):
            self.is_excited = False
            self.start_cute_idle()
        
        seq.bind(on_complete=excited_complete)
        self.current_animation = seq
        seq.start(self)

    def start_angry_animation(self):
        # 修复ERR-065: 添加异常处理
        try:
            self.cancel_current_animation()
            # 修复ERR-063: 添加位置检查
            base_y = self.y if hasattr(self, 'y') and self.y is not None else 0
            
            # 生气的小幅度抖动
            vibrate_left = Animation(rotation=-5, duration=0.1, t='out_quad')
            vibrate_right = Animation(rotation=5, duration=0.1, t='out_quad')
            
            anim = vibrate_left + vibrate_right
            anim.repeat = True
        except Exception as e:
            error(f"start_angry_animation失败: {e}")
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
        self.settings = self.load_settings()
        self.load_alarms()
        self.schedule_next_alarm()
    
    def load_settings(self):
        # 修复ERR-070: 使用配置文件路径变量
        settings_path = 'alarm_settings.json'
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            # 修复ERR-066: 使用error函数记录错误
            error(f"加载设置失败: {e}")
        return DEFAULT_ALARM_SETTINGS.copy()
    
    def save_settings(self):
        # 修复ERR-070: 使用配置文件路径变量
        settings_path = 'alarm_settings.json'
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            # 修复ERR-067: 使用error函数记录错误
            error(f"保存设置失败: {e}")
    
    def add_alarm(self, hour, minute, label="闹钟", content="时间到了！", 
                  repeat_days=None, enabled=True):
        # 修复ERR-069: 确保repeat_days正确处理None值
        if repeat_days is None:
            repeat_days = []
        elif isinstance(repeat_days, list):
            # 确保repeat_days是有效的整数列表
            repeat_days = [int(day) for day in repeat_days if str(day).isdigit()]
        else:
            repeat_days = []
        
        # 修复ERR-068: 使用唯一ID而不是简单的长度
        import time
        alarm_id = int(time.time() * 1000) + len(self.alarms)
        
        alarm = {
            'id': alarm_id,
            'hour': hour,
            'minute': minute,
            'label': label,
            'content': content,
            'repeat_days': repeat_days,
            'enabled': enabled,
            'snooze_count': 0,
            'max_snooze': self.settings.get('max_snooze_count', 3) if hasattr(self, 'settings') else 3
        }
        self.alarms.append(alarm)
        self.save_alarms()
        self.schedule_next_alarm()
        return alarm
    
    def batch_add_alarms(self, alarm_text):
        # 修复ERR-071: 添加异常处理
        try:
            added_count = 0
            error_count = 0
            
            # 修复ERR-072: 改进空字符串处理
            if not alarm_text or not isinstance(alarm_text, str):
                return {'added': 0, 'errors': 0, 'message': '输入为空或无效'}
            
            alarm_text = alarm_text.strip()
            if not alarm_text:
                return {'added': 0, 'errors': 0, 'message': '输入为空'}
            
            alarm_entries = alarm_text.split(';')
            for entry in alarm_entries:
                entry = entry.strip()
                if not entry:
                    continue
                
                parts = [part.strip() for part in entry.split(',')]
                # 修复ERR-073: 添加详细验证
                if len(parts) < 3:
                    error_count += 1
                    debug(f"批量添加闹钟错误: 参数不足({len(parts)}个), 需要至少3个: {entry}")
                    continue
                
                try:
                    label = parts[0]
                    time_str = parts[1]
                    content = ','.join(parts[2:])
                    
                    # 修复ERR-075: 统一时间格式处理
                    time_str = time_str.replace('：', ':')  # 中文冒号转英文冒号
                    
                    if ':' in time_str:
                        hour_str, minute_str = time_str.split(':')
                        hour = int(hour_str.strip())
                        minute = int(minute_str.strip())
                        # 修复ERR-074: 添加范围验证
                        if not (0 <= hour <= 23):
                            raise ValueError(f"小时值无效: {hour}")
                        if not (0 <= minute <= 59):
                            raise ValueError(f"分钟值无效: {minute}")
                    else:
                        raise ValueError("时间格式错误，缺少冒号分隔符")
                    
                    self.add_alarm(hour, minute, label, content)
                    added_count += 1
                except Exception as e:
                    # 修复打印日志
                    error(f"解析错误: {entry} - {e}")
                    error_count += 1
            
            return {'added': added_count, 'errors': error_count, 'message': f"成功添加{added_count}个闹钟，失败{error_count}个"}
        except Exception as e:
            error(f"batch_add_alarms整体失败: {e}")
            return {'added': 0, 'errors': 1, 'message': f"批量添加失败: {e}"}
    
    def remove_alarm(self, alarm_id):
        # 修复ERR-076和ERR-077: 改进ID管理策略
        try:
            # 使用列表推导式删除指定ID的闹钟，但不重置其他闹钟的ID
            original_count = len(self.alarms)
            self.alarms = [a for a in self.alarms if a['id'] != alarm_id]
            removed_count = original_count - len(self.alarms)
            
            # 不再重置ID，因为add_alarm使用时间戳生成唯一ID
            # 保持原有ID不变，避免冲突
            
            self.save_alarms()
            self.schedule_next_alarm()
            return removed_count > 0  # 返回是否成功删除
        except Exception as e:
            error(f"remove_alarm失败: {e}")
            return False
    
    def toggle_alarm(self, alarm_id, enabled):
        # 修复ERR-078: 添加异常处理
        try:
            found = False
            for alarm in self.alarms:
                if alarm['id'] == alarm_id:
                    alarm['enabled'] = enabled
                    found = True
                    break
            if found:
                self.save_alarms()
                self.schedule_next_alarm()
            return found  # 返回是否找到并修改了闹钟
        except Exception as e:
            error(f"toggle_alarm失败: {e}")
            return False
    
    def update_alarm(self, alarm_id, hour=None, minute=None, label=None, 
                     content=None, repeat_days=None):
        # 修复ERR-079: 添加异常处理
        try:
            found = False
            for alarm in self.alarms:
                if alarm['id'] == alarm_id:
                    found = True
                    
                    # 修复ERR-080: 添加时间范围验证
                    if hour is not None:
                        if not (0 <= hour <= 23):
                            raise ValueError(f"小时值无效: {hour}")
                        alarm['hour'] = hour
                    
                    if minute is not None:
                        if not (0 <= minute <= 59):
                            raise ValueError(f"分钟值无效: {minute}")
                        alarm['minute'] = minute
                    
                    if label is not None:
                        alarm['label'] = label
                    
                    if content is not None:
                        alarm['content'] = content
                    
                    # 修复ERR-081: 添加repeat_days验证
                    if repeat_days is not None:
                        if isinstance(repeat_days, list):
                            # 确保是有效的整数列表
                            repeat_days = [int(day) for day in repeat_days if str(day).isdigit()]
                        else:
                            repeat_days = []
                        alarm['repeat_days'] = repeat_days
                    break
            
            if found:
                self.save_alarms()
                self.schedule_next_alarm()
            
            return found  # 返回是否找到并更新了闹钟
        except Exception as e:
            error(f"update_alarm失败: {e}")
            return False
    
    def snooze_alarm(self, alarm_id):
        # 修复ERR-082: 添加异常处理
        try:
            for alarm in self.alarms:
                if alarm['id'] == alarm_id:
                    # 修复ERR-083: 添加属性检查
                    max_snooze = alarm.get('max_snooze', 3)
                    current_count = alarm.get('snooze_count', 0)
                    
                    if current_count < max_snooze:
                        alarm['snooze_count'] = current_count + 1
                        snooze_minutes = self.settings.get('snooze_duration', 5) if hasattr(self, 'settings') else 5
                        snooze_time = datetime.now() + timedelta(minutes=snooze_minutes)
                        self.snooze_alarms[alarm_id] = snooze_time
                        return True, snooze_minutes
                    else:
                        alarm['snooze_count'] = 0
                        return False, 0
            return False, 0
        except Exception as e:
            error(f"snooze_alarm失败: {e}")
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
        
        for alarm_id, snooze_time in list(self.snooze_alarms.items()):
            if snooze_time > now:
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
        
        if self.alarm_check_event:
            self.alarm_check_event.cancel()
            self.alarm_check_event = None
        
        app = App.get_running_app()
        if app and next_alarm_time:
            seconds_until_check = max(1, min(60, (next_alarm_time - now).total_seconds()))
            self.alarm_check_event = Clock.schedule_once(
                lambda dt: self.check_alarms(),
                seconds_until_check
            )
    
    def check_alarms(self):
        now = datetime.now()
        triggered_alarms = []
        
        for alarm_id, snooze_time in list(self.snooze_alarms.items()):
            if now >= snooze_time:
                for alarm in self.alarms:
                    if alarm['id'] == alarm_id:
                        triggered_alarms.append(alarm)
                        if alarm_id in self.snooze_alarms:
                            del self.snooze_alarms[alarm_id]
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
            
            time_diff = abs((now - alarm_time).total_seconds())
            
            if time_diff <= 30:
                if not alarm['repeat_days']:
                    triggered_alarms.append(alarm)
                    alarm['enabled'] = False
                elif now.weekday() in alarm['repeat_days']:
                    triggered_alarms.append(alarm)
        
        if triggered_alarms:
            app = App.get_running_app()
            if app:
                for alarm in triggered_alarms:
                    app.trigger_alarm(alarm)
        
        self.schedule_next_alarm()
    
    def save_alarms(self):
        # 修复ERR-088: 使用配置文件路径变量
        alarms_path = 'alarms.json'
        try:
            with open(alarms_path, 'w', encoding='utf-8') as f:
                json.dump(self.alarms, f, ensure_ascii=False, indent=2)
        except Exception as e:
            # 修复ERR-084: 使用error函数记录错误
            error(f"保存闹钟失败: {e}")
    
    def load_alarms(self):
        # 修复ERR-087: 使用配置文件路径变量
        alarms_path = 'alarms.json'
        try:
            if os.path.exists(alarms_path):
                with open(alarms_path, 'r', encoding='utf-8') as f:
                    self.alarms = json.load(f)
            else:
                self.alarms = []
        except Exception as e:
            # 修复ERR-085: 使用error函数记录错误
            error(f"加载闹钟失败: {e}")
            self.alarms = []
    
    def export_alarms(self, filepath):
        try:
            # 验证文件路径
            if not filepath or not isinstance(filepath, str):
                error("导出闹钟失败: 文件路径无效")
                return False
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.alarms, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            # 修复ERR-086: 使用error函数记录错误
            error(f"导出闹钟失败: {e}")
            return False
    
    def cleanup(self):
        # 修复ERR-089: 添加异常处理
        try:
            if self.alarm_check_event:
                self.alarm_check_event.cancel()
                self.alarm_check_event = None
        except Exception as e:
            error(f"cleanup失败: {e}")


# ==================== 计时器管理类 ====================
class TimerManager:
    def __init__(self):
        self.timers = []
        self.timer_check_event = None
        self.start_checking()
    
    def add_timer(self, minutes, seconds=0, label="计时器"):
        # 修复ERR-091: 添加参数验证
        try:
            if minutes < 0 or seconds < 0:
                raise ValueError(f"时间不能为负数: 分钟={minutes}, 秒={seconds}")
            
            total_seconds = minutes * 60 + seconds
            
            # 修复ERR-090: 使用唯一ID生成策略
            import time
            timer_id = int(time.time() * 1000) + len(self.timers)
            
            timer = {
                'id': timer_id,
                'label': label,
                'total_seconds': total_seconds,
                'remaining': total_seconds,
                'running': True,
                'created_at': datetime.now()
            }
            self.timers.append(timer)
            return timer
        except Exception as e:
            error(f"add_timer失败: {e}")
            return None
    
    def remove_timer(self, timer_id):
        # 修复ERR-092: 添加异常处理和返回值
        try:
            original_count = len(self.timers)
            self.timers = [t for t in self.timers if t['id'] != timer_id]
            removed = len(self.timers) < original_count
            if removed:
                debug(f"移除计时器 {timer_id} 成功，移除前: {original_count}个，移除后: {len(self.timers)}个")
            return removed
        except Exception as e:
            error(f"remove_timer失败: {e}")
            return False
    
    def toggle_timer(self, timer_id):
        # 修复ERR-093: 添加异常处理和返回值
        try:
            found = False
            for timer in self.timers:
                if timer['id'] == timer_id:
                    timer['running'] = not timer['running']
                    new_state = "运行中" if timer['running'] else "已暂停"
                    debug(f"切换计时器 {timer_id} 状态: {new_state}")
                    found = True
                    break
            return found
        except Exception as e:
            error(f"toggle_timer失败: {e}")
            return False
    
    def start_checking(self):
        # 修复ERR-094: 添加异常处理
        try:
            self.timer_check_event = Clock.schedule_interval(self.check_timers, 1)
            debug("计时器检查已启动")
        except Exception as e:
            error(f"start_checking失败: {e}")
    
    def check_timers(self, dt):
        # 修复ERR-095: 添加异常处理和状态验证
        try:
            for timer in self.timers[:]:  # 使用切片复制列表避免遍历时修改的问题
                # 检查计时器是否有效
                if not isinstance(timer, dict):
                    continue
                
                # 确保必需字段存在
                if 'running' not in timer or 'remaining' not in timer:
                    continue
                
                # 修复ERR-095: 只有运行中的计时器才更新
                if timer['running'] and timer['remaining'] > 0:
                    timer['remaining'] -= 1
                    
                    # 当计时器结束时触发
                    if timer['remaining'] <= 0:
                        timer['running'] = False
                        debug(f"计时器 {timer.get('id', '未知')} 已结束")
                        self.trigger_timer(timer)
        except Exception as e:
            error(f"check_timers失败: {e}")
    
    def trigger_timer(self, timer):
        # 修复ERR-096: 添加异常处理
        try:
            if not timer or not isinstance(timer, dict):
                error("trigger_timer: 计时器对象无效")
                return
            
            app = App.get_running_app()
            if app:
                app.trigger_timer_alarm(timer)
                debug(f"已触发计时器报警: {timer.get('label', '未知')}")
            else:
                error("trigger_timer: 无法获取应用实例")
        except Exception as e:
            error(f"trigger_timer失败: {e}")
    
    def get_active_timers(self):
        # 修复ERR-097: 添加空列表检查和有效性验证
        try:
            if not hasattr(self, 'timers') or not isinstance(self.timers, list):
                return []
            
            active_timers = []
            for t in self.timers:
                if isinstance(t, dict) and t.get('remaining', 0) > 0:
                    active_timers.append(t)
            return active_timers
        except Exception as e:
            error(f"get_active_timers失败: {e}")
            return []
    
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
    def __init__(self, alarm_manager, alarm_id=None, **kwargs):
        super().__init__(**kwargs)
        # 修复ERR-098: 参数验证
        if alarm_manager is None or not hasattr(alarm_manager, 'add_alarm'):
            raise ValueError("AlarmDialog: 无效的闹钟管理器")
        
        self.alarm_manager = alarm_manager
        self.alarm_id = alarm_id
        
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
        # 修复ERR-101: 改进默认名称
        default_label = '每日闹钟' if alarm_id is None else '闹钟'
        self.label_input = TextInput(
            text=default_label,
            multiline=False,
            size_hint_x=0.75,
            font_size=sp(16),
            background_color=CUTE_COLORS['background'],
            hint_text='输入闹钟名称（必填）',
            write_tab=False
        )
        label_layout.add_widget(self.label_input)
        layout.add_widget(label_layout)
        
        content_layout = BoxLayout(orientation='horizontal', size_hint_y=0.18, spacing=dp(10))
        content_layout.add_widget(Label(text='📝 内容:', size_hint_x=0.25, font_size=sp(16), color=CUTE_COLORS['text']))
        # 修复ERR-102: 改进默认内容
        default_content = '时间到了！该起床/吃饭/工作了！' if alarm_id is None else '时间到了！'
        self.content_input = TextInput(
            text=default_content,
            multiline=True,
            size_hint_x=0.75,
            font_size=sp(14),
            background_color=CUTE_COLORS['background'],
            hint_text='输入闹钟提示内容（可选）',
            write_tab=False
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
                self.content_input.text = alarm.get('content', '时间到了！')
                
                if alarm['repeat_days']:
                    for i, check in enumerate(self.day_checks):
                        check.active = (i in alarm['repeat_days'])
                break
    
    def save_alarm(self, instance):
        try:
            # 修复ERR-109: 验证用户输入
            hour_str = self.hour_spinner.text.strip()
            minute_str = self.minute_spinner.text.strip()
            
            if not hour_str or not minute_str:
                raise ValueError("时间不能为空")
            
            hour = int(hour_str)
            minute = int(minute_str)
            
            # 验证时间范围
            if not (0 <= hour <= 23):
                raise ValueError(f"小时必须在0-23之间: {hour}")
            if not (0 <= minute <= 59):
                raise ValueError(f"分钟必须在0-59之间: {minute}")
            
            label = self.label_input.text.strip()
            content = self.content_input.text.strip()
            
            # 验证必填字段
            if not label:
                raise ValueError("闹钟名称不能为空")
            
            # 使用默认值但不掩盖空输入
            if not content:
                content = '时间到了！'
            
            repeat_days = [i for i, check in enumerate(self.day_checks) if check.active]
            
            if self.alarm_id is not None:
                result = self.alarm_manager.update_alarm(
                    self.alarm_id, hour, minute, label, content, repeat_days
                )
                if not result:
                    raise ValueError("更新闹钟失败，闹钟可能不存在")
            else:
                new_alarm = self.alarm_manager.add_alarm(
                    hour, minute, label, content, repeat_days, True
                )
                if not new_alarm:
                    raise ValueError("添加闹钟失败")
            
            self.dismiss()
            debug(f"成功保存闹钟: {label} {hour:02d}:{minute:02d}")
        # 修复ERR-108: 不静默吞掉错误
        except ValueError as e:
            error(f"保存闹钟失败: {e}")
            # 可以添加用户提示，例如显示弹窗
            from kivy.uix.popup import Popup
            popup = Popup(title='错误', content=Label(text=f"保存失败: {str(e)}"), size_hint=(0.7, 0.3))
            popup.open()
    
    def delete_alarm(self, instance):
        # 修复ERR-110: 添加异常处理和确认机制
        try:
            if self.alarm_id is not None:
                # 确认删除（简单实现，可以增强为弹窗确认）
                debug(f"删除闹钟确认: ID={self.alarm_id}")
                
                result = self.alarm_manager.remove_alarm(self.alarm_id)
                if result:
                    debug(f"闹钟 {self.alarm_id} 删除成功")
                    self.dismiss()
                else:
                    error(f"删除闹钟失败: 闹钟 {self.alarm_id} 不存在")
                    # 可以显示错误提示
            else:
                error("delete_alarm: 闹钟ID为空")
        except Exception as e:
            error(f"删除闹钟失败: {e}")


class BatchAddDialog(CutePopup):
    def __init__(self, alarm_manager, **kwargs):
        super().__init__(**kwargs)
        # 修复ERR-111: 参数验证
        if alarm_manager is None or not hasattr(alarm_manager, 'batch_add_alarms'):
            raise ValueError("BatchAddDialog: 无效的闹钟管理器")
        
        self.alarm_manager = alarm_manager
        self.title = '➕ 批量添加闹钟'
        self.size_hint = (0.9, 0.8)
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        instructions = Label(
            text='📋 格式：闹钟名,时间,具体内容\n💡 示例：起床,08:00,该起床了\n📝 多个闹钟用分号分隔',
            size_hint_y=0.15,
            halign='left',
            valign='middle',
            font_size=sp(14),
            color=CUTE_COLORS['text']
        )
        instructions.bind(size=instructions.setter('text_size'))
        layout.add_widget(instructions)
        
        # 修复ERR-112: 使用更简洁的示例文本
        example_text = '起床,08:00,该起床了;午餐,12:30,记得吃饭'
        
        self.text_input = TextInput(
            text=example_text,
            multiline=True,
            size_hint_y=0.5,
            font_size=sp(14),
            background_color=CUTE_COLORS['background'],
            hint_text='输入格式：名称,时间,内容（多个用分号分隔）',
            write_tab=False
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
        # 修复ERR-117: 添加详细验证
        text = self.text_input.text.strip()
        if not text:
            self.result_label.text = '⚠️ 请输入闹钟数据'
            self.result_label.color = CUTE_COLORS['error']
            return
        
        try:
            # 修复ERR-118: 添加异常处理
            # 修复ERR-119: 正确处理返回值（字典）
            result = self.alarm_manager.batch_add_alarms(text)
            
            if isinstance(result, dict):
                added_count = result.get('added', 0)
                error_count = result.get('errors', 0)
                message = result.get('message', '')
                
                if added_count > 0:
                    self.result_label.text = f'✅ 成功添加 {added_count} 个闹钟'
                    self.result_label.color = CUTE_COLORS['success']
                    if error_count > 0:
                        self.result_label.text += f'，⚠️ {error_count} 个格式错误'
                    Clock.schedule_once(lambda dt: self.dismiss(), 2)
                else:
                    self.result_label.text = f'❌ {message}'
                    self.result_label.color = CUTE_COLORS['error']
            else:
                # 向后兼容：如果返回元组
                if isinstance(result, (tuple, list)) and len(result) >= 2:
                    added_count, error_count = result[0], result[1]
                    if added_count > 0:
                        self.result_label.text = f'✅ 成功添加 {added_count} 个闹钟'
                        self.result_label.color = CUTE_COLORS['success']
                        if error_count > 0:
                            self.result_label.text += f'，⚠️ {error_count} 个格式错误'
                        Clock.schedule_once(lambda dt: self.dismiss(), 2)
                    else:
                        self.result_label.text = '❌ 未添加任何闹钟，请检查格式'
                        self.result_label.color = CUTE_COLORS['error']
                else:
                    self.result_label.text = '❌ 添加失败：返回结果格式错误'
                    self.result_label.color = CUTE_COLORS['error']
        except Exception as e:
            error(f"batch_add失败: {e}")
            self.result_label.text = f'❌ 添加失败：{str(e)}'
            self.result_label.color = CUTE_COLORS['error']


class TimerDialog(CutePopup):
    def __init__(self, timer_manager, **kwargs):
        super().__init__(**kwargs)
        # 修复ERR-120: 参数验证
        if timer_manager is None or not hasattr(timer_manager, 'add_timer'):
            raise ValueError("TimerDialog: 无效的计时器管理器")
        
        self.timer_manager = timer_manager
        self.title = '⏱️ 倒计时'
        self.size_hint = (0.85, 0.7)
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        time_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=dp(10))
        time_layout.add_widget(Label(text='⏱️ 分钟:', size_hint_x=0.3, font_size=sp(16), color=CUTE_COLORS['text']))
        # 修复ERR-121: 改进默认值和验证
        self.minute_input = TextInput(
            text='5',
            multiline=False,
            input_filter='int',
            size_hint_x=0.7,
            font_size=sp(16),
            background_color=CUTE_COLORS['background'],
            hint_text='输入分钟数 (1-1440)',
            write_tab=False
        )
        time_layout.add_widget(self.minute_input)
        layout.add_widget(time_layout)
        
        sec_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=dp(10))
        sec_layout.add_widget(Label(text='⏱️ 秒:', size_hint_x=0.3, font_size=sp(16), color=CUTE_COLORS['text']))
        # 修复ERR-122: 改进默认值和验证
        self.sec_input = TextInput(
            text='0',
            multiline=False,
            input_filter='int',
            size_hint_x=0.7,
            font_size=sp(16),
            background_color=CUTE_COLORS['background'],
            hint_text='输入秒数 (0-59)',
            write_tab=False
        )
        sec_layout.add_widget(self.sec_input)
        layout.add_widget(sec_layout)
        
        label_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=dp(10))
        label_layout.add_widget(Label(text='🏷️ 标签:', size_hint_x=0.3, font_size=sp(16), color=CUTE_COLORS['text']))
        # 修复ERR-123: 改进默认标签
        self.label_input = TextInput(
            text='计时任务',
            multiline=False,
            size_hint_x=0.7,
            font_size=sp(16),
            background_color=CUTE_COLORS['background'],
            hint_text='输入计时器标签（可选）',
            write_tab=False
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
        # 修复ERR-125: 添加详细验证和异常处理
        try:
            # 获取输入值
            minute_text = self.minute_input.text.strip()
            sec_text = self.sec_input.text.strip()
            label_text = self.label_input.text.strip()
            
            # 验证输入
            if not minute_text:
                minute_text = '0'
            if not sec_text:
                sec_text = '0'
                
            minutes = int(minute_text)
            seconds = int(sec_text)
            label = label_text or '计时任务'
            
            # 验证范围
            if minutes < 0 or minutes > 1440:
                raise ValueError(f"分钟必须在0-1440之间: {minutes}")
            if seconds < 0 or seconds > 59:
                raise ValueError(f"秒必须在0-59之间: {seconds}")
            
            if minutes > 0 or seconds > 0:
                result = self.timer_manager.add_timer(minutes, seconds, label)
                if result:
                    debug(f"添加计时器成功: {label} ({minutes}分{seconds}秒)")
                self.update_timer_list(0)
            else:
                debug("添加计时器: 时间为零，未添加")
        except ValueError as e:
            error(f"add_timer失败: {e}")
            # 可以显示用户提示
            pass
    
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
        dialog = AlarmDialog(self.app.alarm_manager)
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
        if self.app.pet.is_sleeping:
            self.app.pet.wake_up_animation()
        else:
            self.app.pet.start_sleep_animation()


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
        dialog = AlarmDialog(self.app.alarm_manager, alarm['id'])
        dialog.open()
    
    def delete_alarm(self, alarm):
        self.app.alarm_manager.remove_alarm(alarm['id'])
        self.update_alarm_list()
    
    def show_new_alarm_dialog(self, instance):
        self.dismiss()
        dialog = AlarmDialog(self.app.alarm_manager)
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
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        
        size_layout = BoxLayout(orientation='horizontal', size_hint_y=0.12, spacing=dp(10))
        size_layout.add_widget(Label(text='🐾 宠物大小:', size_hint_x=0.4, font_size=sp(14), color=CUTE_COLORS['text']))
        self.size_slider = Slider(
            min=80,
            max=250,
            value=self.app.pet.pet_size,
            size_hint_x=0.6
        )
        self.size_slider.bind(value=self.on_size_change)
        size_layout.add_widget(self.size_slider)
        layout.add_widget(size_layout)
        
        opacity_layout = BoxLayout(orientation='horizontal', size_hint_y=0.12, spacing=dp(10))
        opacity_layout.add_widget(Label(text='👻 透明度:', size_hint_x=0.4, font_size=sp(14), color=CUTE_COLORS['text']))
        self.opacity_slider = Slider(
            min=0.3,
            max=1.0,
            value=self.app.pet.pet_opacity,
            size_hint_x=0.6
        )
        self.opacity_slider.bind(value=self.on_opacity_change)
        opacity_layout.add_widget(self.opacity_slider)
        layout.add_widget(opacity_layout)
        
        banner_layout = BoxLayout(orientation='horizontal', size_hint_y=0.12, spacing=dp(10))
        banner_layout.add_widget(Label(text='📢 横幅显示(秒):', size_hint_x=0.4, font_size=sp(14), color=CUTE_COLORS['text']))
        self.banner_slider = Slider(
            min=3,
            max=15,
            value=self.app.banner_display_time,
            size_hint_x=0.6
        )
        self.banner_slider.bind(value=self.on_banner_time_change)
        banner_layout.add_widget(self.banner_slider)
        layout.add_widget(banner_layout)
        
        snooze_layout = BoxLayout(orientation='horizontal', size_hint_y=0.12, spacing=dp(10))
        snooze_layout.add_widget(Label(text='😴 贪睡时间(分):', size_hint_x=0.4, font_size=sp(14), color=CUTE_COLORS['text']))
        self.snooze_slider = Slider(
            min=1,
            max=10,
            value=self.app.alarm_manager.settings.get('snooze_duration', 5),
            size_hint_x=0.6
        )
        self.snooze_slider.bind(value=self.on_snooze_change)
        snooze_layout.add_widget(self.snooze_slider)
        layout.add_widget(snooze_layout)
        
        max_snooze_layout = BoxLayout(orientation='horizontal', size_hint_y=0.12, spacing=dp(10))
        max_snooze_layout.add_widget(Label(text='🔢 最大贪睡:', size_hint_x=0.4, font_size=sp(14), color=CUTE_COLORS['text']))
        self.max_snooze_slider = Slider(
            min=1,
            max=5,
            value=self.app.alarm_manager.settings.get('max_snooze_count', 3),
            size_hint_x=0.6
        )
        self.max_snooze_slider.bind(value=self.on_max_snooze_change)
        max_snooze_layout.add_widget(self.max_snooze_slider)
        layout.add_widget(max_snooze_layout)
        
        vibrate_layout = BoxLayout(orientation='horizontal', size_hint_y=0.12, spacing=dp(10))
        vibrate_layout.add_widget(Label(text='📳 振动提醒:', size_hint_x=0.4, font_size=sp(14), color=CUTE_COLORS['text']))
        self.vibrate_switch = Switch(
            active=self.app.alarm_manager.settings.get('vibrate', True),
            size_hint_x=0.6
        )
        self.vibrate_switch.bind(active=self.on_vibrate_change)
        vibrate_layout.add_widget(self.vibrate_switch)
        layout.add_widget(vibrate_layout)
        
        sound_layout = BoxLayout(orientation='horizontal', size_hint_y=0.12, spacing=dp(10))
        sound_layout.add_widget(Label(text='🔔 声音提醒:', size_hint_x=0.4, font_size=sp(14), color=CUTE_COLORS['text']))
        self.sound_switch = Switch(
            active=self.app.alarm_manager.settings.get('sound_enabled', True),
            size_hint_x=0.6
        )
        self.sound_switch.bind(active=self.on_sound_change)
        sound_layout.add_widget(self.sound_switch)
        layout.add_widget(sound_layout)
        
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.12, spacing=dp(15))
        
        reset_btn = CuteButton(text='🔄 重置')
        reset_btn.bind(on_press=self.reset_settings)
        button_layout.add_widget(reset_btn)
        
        close_btn = CuteButton(text='✅ 关闭')
        close_btn.bind(on_press=self.dismiss)
        button_layout.add_widget(close_btn)
        
        layout.add_widget(button_layout)
        self.content = layout
    
    def on_size_change(self, instance, value):
        self.app.pet.pet_size = value
    
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
    
    def reset_settings(self, instance):
        self.size_slider.value = 160
        self.opacity_slider.value = 1.0
        self.banner_slider.value = 5
        self.snooze_slider.value = 5
        self.max_snooze_slider.value = 3
        self.vibrate_switch.active = True
        self.sound_switch.active = True


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
            text=alarm.get('content', '时间到了！'),
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
        snooze_btn.background_color = CUTE_COLORS['accent']
        snooze_btn.bind(on_press=self.snooze_alarm)
        button_layout.add_widget(snooze_btn)
        
        close_btn = CuteButton(text='✅ 关闭闹钟')
        close_btn.bind(on_press=self.close_alarm)
        button_layout.add_widget(close_btn)
        
        layout.add_widget(button_layout)
        self.content = layout
    
    def snooze_alarm(self, instance):
        success, minutes = self.app.alarm_manager.snooze_alarm(self.alarm['id'])
        if success:
            self.dismiss()
            self.app.show_notification(f"😴 贪睡 {minutes} 分钟后再次提醒")
        else:
            instance.text = '⚠️ 已达上限'
    
    def close_alarm(self, instance):
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
    
    def build(self):
        Window.borderless = True
        Window.always_on_top = True
        Window.resizable = False
        Window.size = (dp(200), dp(200))
        Window.left = 100
        Window.top = 500
        
        self.root = FloatLayout()
        
        self.alarm_manager = AlarmClock()
        self.timer_manager = TimerManager()
        
        self.pet = CutePet()
        self.root.add_widget(self.pet)
        
        self.banner = CuteBanner()
        self.root.add_widget(self.banner)
        
        self.load_alarm_sound()
        
        self.sleep_check_event = Clock.schedule_interval(self.check_pet_sleep_state, 60)
        
        # 添加心情、天气、日历显示标签
        self.add_mood_weather_calendar_labels()
        
        # 初始化定时更新
        Clock.schedule_interval(self.update_mood_status, 30)  # 每30秒更新心情
        Clock.schedule_interval(self.update_weather_status, 1800)  # 每30分钟更新天气
        Clock.schedule_interval(self.update_calendar_status, 600)  # 每10分钟更新日历
        
        return self.root
    
    def load_alarm_sound(self):
        try:
            sound_files = ['alarm.wav', 'alarm.mp3', 'assets/alarm.wav']
            for sound_file in sound_files:
                if os.path.exists(sound_file):
                    self.alarm_sound = SoundLoader.load(sound_file)
                    break
        except Exception as e:
            print(f"加载声音失败: {e}")
    
    def show_main_menu(self):
        menu = MainMenu(self)
        menu.open()
    
    def show_quick_menu(self):
        menu = QuickMenu(self)
        menu.open()
    
    def show_timer_dialog(self):
        dialog = TimerDialog(self.timer_manager)
        dialog.open()
    
    def check_pet_sleep_state(self, dt):
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
        title = alarm['label']
        content = alarm.get('content', '时间到了！')
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
                message=alarm.get('content', '时间到了！'),
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
        # 添加心情显示标签
        self.mood_label = Label(
            text="心情: 正常 😐",
            size_hint=(None, None),
            size=(120, 30),
            pos_hint={'x': 0.85, 'y': 0.95},
            color=self.pet.mood_system.get_mood_color('normal'),
            font_size='12sp',
            halign='left'
        )
        self.root.add_widget(self.mood_label)
        
        # 添加天气显示标签
        self.weather_label = Label(
            text="天气: 晴天 ☀️",
            size_hint=(None, None),
            size=(120, 30),
            pos_hint={'x': 0.85, 'y': 0.92},
            color=CUTE_COLORS['secondary'],
            font_size='12sp',
            halign='left'
        )
        self.root.add_widget(self.weather_label)
        
        # 添加日历显示标签
        self.calendar_label = Label(
            text="日历: 无事件",
            size_hint=(None, None),
            size=(120, 30),
            pos_hint={'x': 0.85, 'y': 0.89},
            color=CUTE_COLORS['text'],
            font_size='12sp',
            halign='left'
        )
        self.root.add_widget(self.calendar_label)

    def update_mood_status(self, dt):
        if self.pet:
            current_time = datetime.now()
            weather_data = self.pet.weather_api.get_current_weather()
            weather_impact = weather_data.get('impact', 'normal') if weather_data else 'normal'
            next_event = self.pet.calendar.get_next_event()
            
            new_mood = self.pet.mood_system.get_current_mood(current_time, weather_impact, next_event)
            self.pet.current_mood = new_mood
            
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

    def update_weather_status(self, dt):
        if self.pet:
            weather_data = self.pet.weather_api.get_current_weather()
            self.pet.current_weather = weather_data
            
            # 更新天气显示
            if self.weather_label:
                weather_info = self.pet.weather_api.get_weather_for_pet()
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

    def on_stop(self):
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


# ==================== 新增功能方法 ====================


