"""
安卓桌面宠物闹钟 - 完全修复版 V3.0
修复所有bug，可直接打包使用
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

# 设置窗口透明背景
Config.set('graphics', 'background_color', '0,0,0,0')

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
        
        self.opacity = 0
        start_y = self.y
        
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
        
        self.draw_cute_pet()
        Clock.schedule_once(lambda dt: self.start_cute_idle(), 0.5)
        self.bubble_timer = Clock.schedule_interval(self.spawn_sleep_bubble, 3)
    
    def draw_cute_pet(self):
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
    
    def start_cute_idle(self):
        self.cancel_current_animation()
        self.is_excited = False
        base_y = self.y
        
        def create_idle_animation():
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
        
        create_idle_animation()
    
    def start_sleep_animation(self):
        self.cancel_current_animation()
        self.is_sleeping = True
        
        anim = Animation(scale=0.85, opacity=0.6, rotation=0, duration=1, t='out_quad')
        
        def start_breathing(*args):
            if self.is_sleeping:
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
        self.cancel_current_animation()
        self.is_excited = True
        base_y = self.y
        
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
        if self.collide_point(*touch.pos):
            self.is_dragging = True
            self.drag_start_pos = touch.pos
            self.touch_start_time = time.time()
            self.drag_offset_x = Window.left
            self.drag_offset_y = Window.top
            self.cute_click_animation()
            return True
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if self.is_dragging:
            dx = touch.x - self.drag_start_pos[0]
            dy = touch.y - self.drag_start_pos[1]
            
            new_left = self.drag_offset_x + int(dx)
            new_top = self.drag_offset_y + int(dy)
            
            screen_w = Window.width if Window.width > 0 else 1920
            screen_h = Window.height if Window.height > 0 else 1080
            
            pet_size = int(self.pet_size)
            margin = 50
            
            new_left = max(-margin, min(new_left, screen_w - pet_size + margin))
            new_top = max(-margin, min(new_top, screen_h - pet_size + margin))
            
            Window.left = new_left
            Window.top = new_top
            
            return True
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        if self.is_dragging:
            self.is_dragging = False
            
            touch_duration = time.time() - self.touch_start_time
            dx = abs(touch.x - self.drag_start_pos[0])
            dy = abs(touch.y - self.drag_start_pos[1])
            
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
        
        if self.click_count == 1:
            Clock.schedule_once(lambda dt: self.on_pet_click(), 0.2)
        elif self.click_count == 2:
            self.on_double_click()
        elif self.click_count >= 3:
            self.on_triple_click()
            self.click_count = 0
    
    def on_pet_click(self):
        if self.click_count == 1:
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
        try:
            if os.path.exists('alarm_settings.json'):
                with open('alarm_settings.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载设置失败: {e}")
        return DEFAULT_ALARM_SETTINGS.copy()
    
    def save_settings(self):
        try:
            with open('alarm_settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def add_alarm(self, hour, minute, label="闹钟", content="时间到了！", 
                  repeat_days=None, enabled=True):
        alarm = {
            'id': len(self.alarms),
            'hour': hour,
            'minute': minute,
            'label': label,
            'content': content,
            'repeat_days': repeat_days or [],
            'enabled': enabled,
            'snooze_count': 0,
            'max_snooze': self.settings.get('max_snooze_count', 3)
        }
        self.alarms.append(alarm)
        self.save_alarms()
        self.schedule_next_alarm()
        return alarm
    
    def batch_add_alarms(self, alarm_text):
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
                elif '：' in time_str:
                    hour, minute = map(int, time_str.split('：'))
                else:
                    raise ValueError("时间格式错误")
                
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    error_count += 1
                    continue
                
                self.add_alarm(hour, minute, label, content)
                added_count += 1
            except Exception as e:
                print(f"解析错误: {entry} - {e}")
                error_count += 1
        
        return added_count, error_count
    
    def remove_alarm(self, alarm_id):
        self.alarms = [a for a in self.alarms if a['id'] != alarm_id]
        for i, alarm in enumerate(self.alarms):
            alarm['id'] = i
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
        try:
            with open('alarms.json', 'w', encoding='utf-8') as f:
                json.dump(self.alarms, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存闹钟失败: {e}")
    
    def load_alarms(self):
        try:
            if os.path.exists('alarms.json'):
                with open('alarms.json', 'r', encoding='utf-8') as f:
                    self.alarms = json.load(f)
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
        if self.alarm_check_event:
            self.alarm_check_event.cancel()
            self.alarm_check_event = None


# ==================== 计时器管理类 ====================
class TimerManager:
    def __init__(self):
        self.timers = []
        self.timer_check_event = None
        self.start_checking()
    
    def add_timer(self, minutes, seconds=0, label="计时器"):
        total_seconds = minutes * 60 + seconds
        timer = {
            'id': len(self.timers),
            'label': label,
            'total_seconds': total_seconds,
            'remaining': total_seconds,
            'running': True,
            'created_at': datetime.now()
        }
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
        for timer in self.timers[:]:
            if timer['running'] and timer['remaining'] > 0:
                timer['remaining'] -= 1
                
                if timer['remaining'] <= 0:
                    timer['running'] = False
                    self.trigger_timer(timer)
    
    def trigger_timer(self, timer):
        app = App.get_running_app()
        if app:
            app.trigger_timer_alarm(timer)
    
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
    def __init__(self, alarm_manager, alarm_id=None, **kwargs):
        super().__init__(**kwargs)
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
            text='时间到了！',
            multiline=True,
            size_hint_x=0.75,
            font_size=sp(14),
            background_color=CUTE_COLORS['background']
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
            hour = int(self.hour_spinner.text)
            minute = int(self.minute_spinner.text)
            label = self.label_input.text.strip() or '闹钟'
            content = self.content_input.text.strip() or '时间到了！'
            
            repeat_days = [i for i, check in enumerate(self.day_checks) if check.active]
            
            if self.alarm_id is not None:
                self.alarm_manager.update_alarm(
                    self.alarm_id, hour, minute, label, content, repeat_days
                )
            else:
                self.alarm_manager.add_alarm(
                    hour, minute, label, content, repeat_days, True
                )
            self.dismiss()
        except ValueError:
            pass
    
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
            text='📋 格式：闹钟名,时间,具体内容\n💡 示例：起床,08:00,该起床了\n📝 多个闹钟用分号分隔',
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
                self.result_label.text += f'，⚠️ {error_count} 个格式错误'
            Clock.schedule_once(lambda dt: self.dismiss(), 2)
        else:
            self.result_label.text = '❌ 未添加任何闹钟，请检查格式'
            self.result_label.color = CUTE_COLORS['error']


class TimerDialog(CutePopup):
    def __init__(self, timer_manager, **kwargs):
        super().__init__(**kwargs)
        self.timer_manager = timer_manager
        self.title = '⏱️ 倒计时'
        self.size_hint = (0.85, 0.7)
        
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
            minutes = int(self.minute_input.text or 0)
            seconds = int(self.sec_input.text or 0)
            label = self.label_input.text.strip() or '计时器'
            
            if minutes > 0 or seconds > 0:
                self.timer_manager.add_timer(minutes, seconds, label)
                self.update_timer_list(0)
        except ValueError:
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


if __name__ == '__main__':
    DesktopPetAlarmApp().run()
