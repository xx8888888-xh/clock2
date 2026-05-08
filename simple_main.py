"""
Kivy Android悬浮窗宠物闹钟 - 简化版
确保Buildozer构建成功
"""

import os
from datetime import datetime
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.config import Config
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp

# 设置窗口透明
Config.set('graphics', 'background_color', '0,0,0,0')
Window.clearcolor = (0, 0, 0, 0.01)  # 几乎透明
Window.top = 300
Window.left = 50
Window.size = (300, 200)

class FloatingPetClock(App):
    def build(self):
        self.title = "宠物闹钟"
        
        # 创建主布局
        layout = FloatLayout()
        
        # 背景圆角矩形
        from kivy.graphics import Color, RoundedRectangle
        with layout.canvas.before:
            Color(0.56, 0.69, 1.0, 0.9)  # #8FB1FF
            self.bg_rect = RoundedRectangle(
                pos=(dp(10), dp(10)),
                size=(dp(280), dp(180)),
                radius=[dp(20),]
            )
        
        # 时间显示
        self.time_label = Label(
            text="00:00:00",
            font_size=sp(32),
            bold=True,
            color=get_color_from_hex('#FFFFFF'),
            pos=(dp(50), dp(100)),
            size_hint=(None, None),
            size=(dp(200), dp(50))
        )
        layout.add_widget(self.time_label)
        
        # 日期显示
        self.date_label = Label(
            text="2024-01-01",
            font_size=sp(16),
            color=get_color_from_hex('#FFFFFF'),
            pos=(dp(80), dp(70)),
            size_hint=(None, None),
            size=(dp(150), dp(30))
        )
        layout.add_widget(self.date_label)
        
        # 宠物表情
        self.pet_label = Label(
            text="🐾",
            font_size=sp(40),
            pos=(dp(120), dp(130)),
            size_hint=(None, None),
            size=(dp(60), dp(60))
        )
        layout.add_widget(self.pet_label)
        
        # 开始更新时间
        Clock.schedule_interval(self.update_time, 1)
        self.update_time(0)
        
        return layout
    
    def update_time(self, dt):
        now = datetime.now()
        self.time_label.text = now.strftime("%H:%M:%S")
        self.date_label.text = now.strftime("%Y-%m-%d")
    
    def on_start(self):
        # Android前台服务
        try:
            from android import AndroidService
            service = AndroidService('宠物闹钟服务', 'running')
            service.start('服务启动')
        except:
            pass  # 非Android环境忽略

if __name__ == '__main__':
    FloatingPetClock().run()