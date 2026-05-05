"""
桌面宠物闹钟 - Android兼容版（最简化架构）
"""

import os
import sys
from datetime import datetime, timedelta
import json
import gc

# Android环境检测
IS_ANDROID = False
try:
    import android
    IS_ANDROID = True
except ImportError:
    pass

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, RoundedRectangle
from kivy.properties import NumericProperty
from kivy.config import Config
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp
from plyer import notification
from plyer import vibrator

# 窗口配置
Config.set('graphics', 'background_color', '0,0,0,0')

# ==================== 宠物类 ====================
class MinimalPet(Widget):
    """最小化的宠物类"""
    pet_size = NumericProperty(120)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (self.pet_size, self.pet_size)
        self.pos = (Window.width/2 - self.pet_size/2, Window.height/2 - self.pet_size/2)
        
        # 宠物颜色
        self.main_color = get_color_from_hex('#FF8FB1')
        self.shadow_color = (0, 0, 0, 0.15)
        
        # 画宠物
        self.draw_pet()
        
        # 绑定位置变化
        self.bind(pos=self.update_pet)
        
        # 简单的浮动动画
        Clock.schedule_interval(lambda dt: self.float_move(), 1)
        
    def draw_pet(self):
        """画宠物"""
        with self.canvas:
            # 阴影
            Color(*self.shadow_color)
            Ellipse(pos=(self.x + dp(2), self.y - dp(2)), size=self.size)
            
            # 主体
            Color(*self.main_color)
            Ellipse(pos=self.pos, size=self.size)
            
            # 眼睛
            Color(1, 1, 1, 1)
            eye_size = (self.pet_size * 0.15, self.pet_size * 0.15)
            Ellipse(
                pos=(self.x + self.pet_size * 0.25, self.y + self.pet_size * 0.6),
                size=eye_size
            )
            Ellipse(
                pos=(self.x + self.pet_size * 0.65, self.y + self.pet_size * 0.6),
                size=eye_size
            )
            
            # 嘴巴
            Color(1, 0.3, 0.5, 1)
            mouth_size = (self.pet_size * 0.3, self.pet_size * 0.1)
            Ellipse(
                pos=(self.x + self.pet_size * 0.35, self.y + self.pet_size * 0.3),
                size=mouth_size
            )
    
    def update_pet(self, *args):
        """更新宠物位置"""
        with self.canvas:
            self.canvas.clear()
            self.draw_pet()
    
    def float_move(self):
        """简单的浮动动画"""
        # 轻微浮动
        self.x += dp(1)
        self.y += dp(1)
        
        # 边界检查
        if self.x > Window.width - self.pet_size:
            self.x = Window.width - self.pet_size
        if self.y > Window.height - self.pet_size:
            self.y = Window.height - self.pet_size
    
    def on_touch_down(self, touch):
        """触摸事件"""
        if self.collide_point(*touch.pos):
            print(f"宠物被点击: {touch.pos}")
            self.show_menu()
            return True
        return False
    
    def show_menu(self):
        """显示菜单"""
        app = App.get_running_app()
        if app:
            app.show_simple_menu()

# ==================== 闹钟管理器 ====================
class SimpleAlarmManager:
    """简化的闹钟管理器"""
    def __init__(self):
        self.alarms = []
        self.load_alarms()
    
    def load_alarms(self):
        """加载闹钟"""
        try:
            if os.path.exists('alarms.json'):
                with open('alarms.json', 'r', encoding='utf-8') as f:
                    self.alarms = json.load(f)
        except Exception as e:
            print(f"加载闹钟失败: {e}")
            self.alarms = []
    
    def add_alarm(self, hour, minute, label):
        """添加闹钟"""
        alarm = {
            'hour': hour,
            'minute': minute,
            'label': label,
            'enabled': True
        }
        self.alarms.append(alarm)
        self.save_alarms()
        return alarm
    
    def save_alarms(self):
        """保存闹钟"""
        try:
            with open('alarms.json', 'w', encoding='utf-8') as f:
                json.dump(self.alarms, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存闹钟失败: {e}")
    
    def check_alarms(self):
        """检查闹钟"""
        now = datetime.now()
        triggered_alarms = []
        
        for alarm in self.alarms:
            if alarm['enabled']:
                alarm_time = now.replace(hour=alarm['hour'], minute=alarm['minute'], second=0, microsecond=0)
                time_diff = abs((now - alarm_time).total_seconds())
                
                if time_diff <= 30:
                    triggered_alarms.append(alarm)
                    alarm['enabled'] = False
        
        return triggered_alarms

# ==================== 简单菜单 ====================
class SimpleMenu(Popup):
    """最简单的菜单"""
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.title = "宠物闹钟"
        self.size_hint = (0.8, 0.6)
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # 状态
        layout.add_widget(Label(
            text=f"Android: {IS_ANDROID}\n窗口: {Window.width}x{Window.height}\n时间: {datetime.now().strftime('%H:%M')}",
            font_size=sp(16),
            color=get_color_from_hex('#5A4A4A')
        ))
        
        # 闹钟列表
        alarm_label = Label(text="📋 闹钟列表:", font_size=sp(16), color=get_color_from_hex('#FF8FB1'))
        layout.add_widget(alarm_label)
        
        if self.app.alarm_manager.alarms:
            for alarm in self.app.alarm_manager.alarms:
                time_str = f"{alarm['hour']:02d}:{alarm['minute']:02d}"
                status = "✅" if alarm['enabled'] else "⏸️"
                layout.add_widget(Label(
                    text=f"{time_str} {status} {alarm['label']}",
                    font_size=sp(14)
                ))
        else:
            layout.add_widget(Label(text="没有闹钟", font_size=sp(14)))
        
        # 按钮
        add_btn = Button(text="➕ 添加闹钟", size_hint=(1, 0.3))
        add_btn.background_color = get_color_from_hex('#FF8FB1')
        add_btn.bind(on_press=lambda x: self.app.show_add_alarm())
        layout.add_widget(add_btn)
        
        close_btn = Button(text="❌ 关闭", size_hint=(1, 0.3))
        close_btn.background_color = get_color_from_hex('#FF6B6B')
        close_btn.bind(on_press=self.dismiss)
        layout.add_widget(close_btn)
        
        self.content = layout

# ==================== 添加闹钟对话框 ====================
class AddAlarmPopup(Popup):
    """添加闹钟对话框"""
    def __init__(self, alarm_manager, **kwargs):
        super().__init__(**kwargs)
        self.alarm_manager = alarm_manager
        self.title = "添加闹钟"
        self.size_hint = (0.8, 0.7)
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # 时间
        layout.add_widget(Label(text="时间:", font_size=sp(18)))
        time_layout = BoxLayout(orientation='horizontal', spacing=dp(10))
        
        hour_label = Label(text="小时:", size_hint_x=0.3)
        hour_input = TextInput(text="08", size_hint_x=0.7, font_size=sp(16))
        
        minute_label = Label(text="分钟:", size_hint_x=0.3)
        minute_input = TextInput(text="00", size_hint_x=0.7, font_size=sp(16))
        
        time_layout.add_widget(hour_label)
        time_layout.add_widget(hour_input)
        time_layout.add_widget(minute_label)
        time_layout.add_widget(minute_input)
        layout.add_widget(time_layout)
        
        # 标签
        layout.add_widget(Label(text="标签:", font_size=sp(18)))
        label_input = TextInput(text="闹钟", size_hint=(1, 0.3), font_size=sp(16))
        layout.add_widget(label_input)
        
        # 按钮
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10))
        
        cancel_btn = Button(text="❌ 取消", size_hint_x=0.5)
        cancel_btn.bind(on_press=self.dismiss)
        button_layout.add_widget(cancel_btn)
        
        save_btn = Button(text="✅ 保存", size_hint_x=0.5)
        save_btn.bind(on_press=lambda x: self.save_alarm(hour_input.text, minute_input.text, label_input.text))
        button_layout.add_widget(save_btn)
        
        layout.add_widget(button_layout)
        self.content = layout
    
    def save_alarm(self, hour_str, minute_str, label):
        """保存闹钟"""
        try:
            hour = int(hour_str)
            minute = int(minute_str)
            
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                self.alarm_manager.add_alarm(hour, minute, label)
                self.dismiss()
        except ValueError:
            pass

# ==================== 主应用 ====================
class ClockApp(App):
    """主应用类"""
    def __init__(self):
        super().__init__()
        
        # 宠物和闹钟管理器
        self.pet = None
        self.alarm_manager = SimpleAlarmManager()
        
        # Android兼容设置
        self.is_android = IS_ANDROID
        
        # 日志
        print(f"应用初始化: Android={self.is_android}")
    
    def setup_window(self):
        """设置窗口"""
        print("设置窗口")
        
        # 核心窗口设置（Android兼容）
        Window.clearcolor = (0, 0, 0, 0.01)  # 几乎透明
        
        # 固定窗口大小和位置
        Window.size = (300, 300)
        Window.top = 200
        Window.left = 100
        
        # Android特定设置
        Window.dismiss_keyboard = False
        Window.allow_screensaver = True
        
        print(f"窗口设置完成: size={Window.size}, pos={Window.top},{Window.left}")
    
    def build(self):
        """构建应用"""
        print("开始build")
        
        # 设置窗口
        self.setup_window()
        
        # 延迟构建宠物
        Clock.schedule_once(lambda dt: self.build_pet(), 0.3)
        
        # 返回临时布局
        layout = FloatLayout()
        init_label = Label(
            text="宠物闹钟正在启动...",
            size_hint=(0.8, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        layout.add_widget(init_label)
        
        return layout
    
    def build_phg(self):
        """构建宠物"""
        print("构建宠物")
        
        # 宠物位置
        pet_x = Window.width/2 - 60
        pet_y = Window.height/2 - 60
        
        self.pet = MinimalPet()
        self.pet.pos = (pet_x, pet_y)
        
        # 创建布局
        layout = FloatLayout()
        layout.add_widget(self.pet)
        
        # 闹钟检查
        Clock.schedule_interval(lambda dt: self.check_alarms(), 30)
        
        return layout
    
    def check_alarms(self):
        """检查闹钟"""
        alarms = self.alarm_manager.check_alarms()
        
        if alarms:
            for alarm in alarms:
                print(f"闹钟触发: {alarm['hour']}:{alarm['minute']} {alarm['label']}")
                
                # 声音提醒
                try:
                    from plyer import vibrator
                    vibrator.vibrate(0.5)
                except Exception as e:
                    print(f"振动失败: {e}")
    
    def show_simple_menu(self):
        """显示简单菜单"""
        menu = SimpleMenu(self)
        menu.open()
    
    def show_add_alarm(self):
        """显示添加闹钟对话框"""
        dialog = AddAlarmPopup(self.alarm_manager)
        dialog.open()
    
    def on_start(self):
        """应用启动"""
        print("应用启动")
        
        if self.is_android:
            print("Android环境启动")
        else:
            print("桌面环境启动")
    
    def on_stop(self):
        """应用停止"""
        print("应用停止")
        
        # 保存闹钟
        self.alarm_manager.save_alarms()

# ==================== 启动应用 ====================
if __name__ == '__main__':
    print("=== 宠物闹钟启动 ===")
    print(f"Android环境: {IS_ANDROID}")
    print(f"窗口模块: {Window}")
    
    # 启动应用
    app = ClockApp()
    app.run()
    
    print("=== 应用运行完成 ===")