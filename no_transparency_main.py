"""
宠物闹钟 - 非透明窗口测试版本
彻底去掉透明窗口，测试是否显示
"""

import os
import sys
from datetime import datetime

# Android检测
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
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.config import Config

# 不使用透明窗口！
Config.set('graphics', 'background_color', '255,255,255,255')  # 白色背景

# 最简单的应用
class NoTransparencyApp(App):
    def __init__(self):
        super().__init__()
        
        # 初始化次数
        self.init_count = 0
        
        print(f"非透明窗口测试: Android={IS_ANDROID}")
    
    def build(self):
        """构建方法"""
        print("非透明窗口: build开始")
        
        # 第1步：设置窗口（非透明）
        Window.clearcolor = (1, 1, 1, 1)  # 白色，完全不透明
        
        # 第2步：固定窗口大小
        Window.size = (400, 400)  # 更大窗口
        
        # 第3步：固定窗口位置
        Window.top = 200
        Window.left = 100
        
        # 第4步：Android特殊设置
        Window.dismiss_keyboard = False
        Window.allow_screensaver = True
        
        print(f"非透明窗口设置: size={Window.size}, pos={Window.top},{Window.left}")
        print(f"窗口背景色: {Window.clearcolor}")
        
        # 创建布局
        layout = FloatLayout()
        
        # 第5步：创建宠物
        self.create_pet(layout)
        
        # 第6步：创建状态标签
        self.create_status_label(layout)
        
        self.init_count = 6
        
        return layout
    
    def create_pet(self, layout):
        """创建宠物"""
        print("非透明窗口: 创建宠物")
        
        pet_size = 150
        pet_x = Window.width / 2 - pet_size / 2
        pet_y = Window.height / 2 - pet_size / 2
        
        pet = NoTransparencyPet()
        pet.size = (pet_size, pet_size)
        pet.pos = (pet_x, pet_y)
        
        layout.add_widget(pet)
        
        print(f"宠物创建: size={pet.size}, pos={pet.pos}")
    
    def create_status_label(self, layout):
        """创建状态标签"""
        print("非透明窗口: 创建状态标签")
        
        status_label = Label(
            text=f"非透明窗口测试\nAndroid={IS_ANDROID}\n窗口={Window.width}x{Window.height}\n时间={datetime.now().strftime('%H:%M:%S')}\n点击宠物测试",
            size_hint=(None, None),
            size=(350, 100),
            pos=(25, 50),
            font_size=16,
            color=(0, 0, 0, 1)  # 黑色文字
        )
        layout.add_widget(status_label)
        
        # 定时更新状态
        Clock.schedule_interval(lambda dt: self.update_status(status_label), 1)
    
    def update_status(self, label):
        """更新状态"""
        label.text = f"非透明窗口测试\nAndroid={IS_ANDROID}\n窗口={Window.width}x{Window.height}\n时间={datetime.now().strftime('%H:%M:%S')}\n点击宠物测试"
    
    def on_start(self):
        """应用启动"""
        print("非透明窗口: on_start")
        
        if IS_ANDROID:
            print("Android环境启动")
    
    def on_stop(self):
        """应用停止"""
        print("非透明窗口: on_stop")
        print(f"初始化步骤: {self.init_count}")

class NoTransparencyPet(Widget):
    """非透明宠物"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        print(f"宠物创建: size={self.size}, pos={self.pos}")
        
        # 宠物颜色（粉色）
        self.main_color = (1, 0.6, 0.8, 1)
        
        # 绘制宠物
        self.draw_pet()
        
        # 动画
        Clock.schedule_interval(lambda dt: self.float_animation(), 1)
    
    def draw_pet(self):
        """绘制宠物"""
        with self.canvas:
            # 宠物主体（粉色）
            Color(*self.main_color)
            Ellipse(pos=self.pos, size=self.size)
            
            # 眼睛（白色）
            Color(1, 1, 1, 1)
            eye_size = (self.size[0] * 0.15, self.size[1] * 0.15)
            Ellipse(
                pos=(self.x + self.size[0] * 0.25, self.y + self.size[1] * 0.6),
                size=eye_size
            )
            Ellipse(
                pos=(self.x + self.size[0] * 0.65, self.y + self.size[1] * 0.6),
                size=eye_size
            )
            
            # 嘴巴（深粉色）
            Color(1, 0.3, 0.5, 1)
            mouth_size = (self.size[0] * 0.3, self.size[1] * 0.1)
            Ellipse(
                pos=(self.x + self.size[0] * 0.35, self.y + self.size[1] * 0.3),
                size=mouth_size
            )
    
    def float_animation(self):
        """浮动动画"""
        # 轻微浮动
        self.x += 1
        self.y += 1
        
        # 边界检查
        if self.x > Window.width - self.size[0]:
            self.x = Window.width - self.size[0]
        if self.y > Window.height - self.size[1]:
            self.y = Window.height - self.size[1]
        
        # 重新绘制
        self.canvas.clear()
        self.draw_pet()
    
    def on_touch_down(self, touch):
        """触摸事件"""
        if self.collide_point(*touch.pos):
            print(f"宠物被点击: {touch.pos}")
            
            # 点击效果
            self.x += 5
            self.y += 5
            
            Clock.schedule_once(lambda dt: self.reset_position(), 0.3)
            
            return True
        return False
    
    def reset_position(self):
        """重置位置"""
        self.x -= 5
        self.y -= 5

# 主入口
if __name__ == '__main__':
    print("=== 非透明窗口测试启动 ===")
    print(f"Android检测: {IS_ANDROID}")
    
    app = NoTransparencyApp()
    app.run()
    
    print("=== 非透明窗口测试完成 ===")