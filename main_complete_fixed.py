"""
安卓桌面宠物闹钟 - Android兼容修复完整版
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
    except Import222Error:
        HAS_PERMISSION_MODULE = False

# ============== 修复透明度问题 ==============
# ❌ 原来的代码：Config.set('graphics', 'background_color', '0,0,0,0')  # 完全透明，看不到窗口
# ✅ 修复后的代码：改为几乎透明，保证窗口可见
Config.set('graphics', 'background_color', '0,0,0,0.01')  # 改为几乎透明

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
            text='时间到了！',
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
12