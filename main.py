"""
宠物闹钟 - 最简单的架构（基准测试）
只测试最基本的窗口创建
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
from kivy.config import Config

# Android Service支持
class AndroidWindowService:
    def __init__(self):
        self.is_android = IS_ANDROID
        self.init_count = 0
        print(f"Android Service: Android={self.is_android}")

    def init_window_safe(self):
        """安全的Android窗口初始化"""
        if not self.is_android:
            return
        
        print("Android Service: 安全初始化窗口")
        
        # 步骤1: 透明度
        Window.clearcolor = (0, 0, 0, 0.01)
        self.init_count += 1
        
        # 步骤2: 固定窗口大小
        Window.size = (300, 300)
        self.init_count += 1
        
        # 步骤3: 固定窗口位置
        Window.top = 150
        Window.left = 100
        self.init_count += 1
        
        # 步骤4: Android特殊设置
        Window.dismiss_keyboard = False
        Window.allow_screensaver = True
        self.init_count += 1
        
        print(f"Android Service: 初始化完成，步骤={self.init_count}")

# 最简单的应用
class SimplestApp(App):
    def __init__(self):
        super().__init__()
        
        # 初始化次数
        self.init_count = 0
        print(f"最简单架构: Android={IS_ANDROID}")
    
    def build(self):
        """最简单的build方法"""
        print("最简单架构: build开始")
        
        # 延迟初始化窗口
        Clock.schedule_once(lambda dt: self.safe_init_window(), 1)
        
        # 临时布局
        layout = FloatLayout()
        
        # 状态标签
        self.status_label = Label(
            text=f"初始化步骤: {self.init_count}\nAndroid={IS_ANDROID}\n时间: {datetime.now().strftime('%H:%M:%S')}",
            size_hint=(0.8, 0.3),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            font_size=18
        )
        layout.add_widget(self.status_label)
        
        return layout
    
    def safe_init_window(self):
        """安全的窗口初始化"""
        print("最简单架构: 安全初始化窗口")
        
        # 使用Android Service
        if IS_ANDROID:
            android_service = AndroidWindowService()
            android_service.init_window_safe()
            self.init_count += android_service.init_count
        else:
            # 非Android环境
            # 步骤1: 设置透明度（必须不是完全透明）
            Window.clearcolor = (0, 0, 0, 0.01)
            self.init_count += 1
            self.update_status_label()
            
            # 步骤2: 固定窗口大小（非常重要）
            Window.size = (300, 300)
            self.init_count += 1
            self.update_status_label()
            
            # 步骤3: 固定窗口位置（避免计算错误）
            Window.top = 150
            Window.left = 100
            self.init_count += 1
            self.update_status_label()
            
            # 步骤4: Android特殊设置
            Window.dismiss_keyboard = False
            Window.allow_screensaver = True
            self.init_count += 1
            self.update_status_label()
            
            # 步骤5: 验证窗口
            Clock.schedule_once(lambda dt: self.verify_window(), 0.5)
    
    def verify_window(self):
        """验证窗口"""
        print(f"最简单架构: 验证窗口 size={Window.size}, pos={Window.top},{Window.left}")
        
        # 如果窗口尺寸为0，重新设置
        if Window.width == 0 or Window.height == 0:
            print("最简单架构: 窗口尺寸为0，重新设置")
            Window.size = (300, 300)
        
        self.init_count += 1
        self.update_status_label()
        
        # 步骤6: 创建宠物
        Clock.schedule_once(lambda dt: self.create_simplest_pet(), 0.5)
    
    def create_simplest_pet(self):
        """最简单的宠物"""
        print("最简单架构: 创建宠物")
        
        # 宠物大小
        pet_size = 100
        
        # 宠物位置
        pet_x = Window.width / 2 - pet_size / 2
        pet_y = Window.height / 2 - pet_size / 2
        
        # 最简单的宠物widget
        pet = SimplestPet()
        pet.size = (pet_size, pet_size)
        pet.pos = (pet_x, pet_y)
        
        self.root.add_widget(pet)
        
        self.init_count += 1
        self.update_status_label()
        
        # 步骤7: 完成初始化
        Clock.schedule_once(lambda dt: self.final_init(), 0.3)
    
    def final_init(self):
        """最终初始化"""
        print("最简单架构: 最终初始化")
        
        self.status_label.text = f"初始化完成\nAndroid={IS_ANDROID}\n窗口={Window.width}x{Window.height}\n宠物已创建\n时间: {datetime.now().strftime('%H:%M:%S')}"
        
        # 定时更新状态
        Clock.schedule_interval(lambda dt: self.update_time(), 1)
    
    def update_status_label(self):
        """更新状态标签"""
        self.status_label.text = f"初始化步骤: {self.init_count}\nAndroid={IS_ANDROID}\n窗口={Window.width}x{Window.height}\n时间: {datetime.now().strftime('%H:%M:%S')}"
    
    def update_time(self):
        """更新时间"""
        self.status_label.text = f"初始化完成\nAndroid={IS_ANDROID}\n窗口={Window.width}x{Window.height}\n宠物已创建\n时间: {datetime.now().strftime('%H:%M:%S')}"
    
    def on_start(self):
        """应用启动"""
        print("最简单架构: on_start")
        
        if IS_ANDROID:
            print("最简单架构: Android环境")
    
    def on_stop(self):
        """应用停止"""
        print("最简单架构: on_stop")

class SimplestPet(Widget):
    """最简单的宠物"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        print(f"最简单宠物: size={self.size}, pos={self.pos}")
        
        # 绘制宠物
        self.draw_simple_pet()
    
    def draw_simple_pet(self):
        """绘制最简单的宠物"""
        with self.canvas:
            # 宠物主体（粉色）
            Color(1, 0.6, 0.8, 1)
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
            
            # 嘴巴（深色）
            Color(1, 0.3, 0.5, 1)
            mouth_size = (self.size[0] * 0.3, self.size[1] * 0.1)
            Ellipse(
                pos=(self.x + self.size[0] * 0.35, self.y + self.size[1] * 0.3),
                size=mouth_size
            )
    
    def on_touch_down(self, touch):
        """触摸事件"""
        if self.collide_point(*touch.pos):
            print(f"最简单宠物被点击: {touch.pos}")
            
            # 点击动画
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
    print("=== 最简单架构启动 ===")
    print(f"Android检测: {IS_ANDROID}")
    
    # 配置
    Config.set('graphics', 'background_color', '0,0,0,0.5')
    
    app = SimplestApp()
    app.run()
    
    print("=== 最简单架构运行完成 ===")