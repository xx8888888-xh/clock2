"""
宠物闹钟 - 最终修复版本（极简架构）
专注于解决Android闪退问题
"""

import os
import sys
from datetime import datetime

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
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.config import Config

# ==================== 核心设置 ====================
class UltimateApp(App):
    """极简应用"""
    def __init__(self):
        super().__init__()
        
        # Window初始化标志
        self.window_initialized = False
        
        # 宠物
        self.pet = None
        
        # 日志
        print(f"应用初始化: Android={IS_ANDROID}")
    
    def safe_window_init(self):
        """安全的窗口初始化"""
        print("安全初始化窗口")
        
        # 关键设置1: 透明度（不是完全透明）
        Window.clearcolor = (0, 0, 0, 0.01)
        
        # 关键设置2: 固定窗口大小
        Window.size = (300, 300)
        
        # 关键设置3: 固定窗口位置
        Window.top = 150
        Window.left = 100
        
        # 关键设置4: Android特殊设置
        Window.dismiss_keyboard = False
        Window.allow_screensaver = True
        
        print(f"窗口设置完成: size={Window.size}, pos={Window.top},{Window.left}")
        print(f"透明度: {Window.clearcolor}")
        
        self.window_initialized = True
        
        return True
    
    def build(self):
        """构建方法 - 延迟初始化"""
        print("开始build方法")
        
        # 创建临时布局
        temp_layout = FloatLayout()
        
        # 初始化标签
        status_label = Label(
            text="正在初始化...",
            size_hint=(0.8, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            font_size=20
        )
        temp_layout.add_widget(status_label)
        
        # 延迟窗口初始化（0.5秒）
        Clock.schedule_once(lambda dt: self.init_window_and_create_pet(status_label), 0.5)
        
        return temp_layout
    
    def init_window_and_create_pet(self, status_label):
        """初始化窗口并创建宠物"""
        print("初始化窗口并创建宠物")
        
        # 1. 安全初始化窗口
        window_result = self.safe_window_init()
        
        if not window_result:
            print("窗口初始化失败")
            status_label.text = "窗口初始化失败"
            return
        
        # 2. 更新状态标签
        status_label.text = f"窗口已创建: {Window.size}"
        
        # 3. 延迟创建宠物（1秒）
        Clock.schedule_once(lambda dt: self.create_pet_and_replace_layout(status_label), 1)
    
    def create_pet_and_replace_layout(self, status_label):
        """创建宠物并替换布局"""
        print("创建宠物")
        
        # 创建宠物
        self.pet = UltimatePet()
        
        # 设置宠物位置
        pet_x = Window.width / 2 - self.pet.pet_size / 2
        pet_y = Window.height / 2 - self.pet.pet_size / 2
        self.pet.pos = (pet_x, pet_y)
        
        # 创建新布局
        main_layout = FloatLayout()
        main_layout.add_widget(self.pet)
        
        # 添加状态标签
        final_label = Label(
            text=f"Android: {IS_ANDROID}\nWindow: {Window.width}x{Window.height}\nTime: {datetime.now().strftime('%H:%M:%S')}",
            size_hint=(None, None),
            size=(200, 80),
            pos=(50, 50),
            font_size=14
        )
        main_layout.add_widget(final_label)
        
        # 替换root
        self.root.clear_widgets()
        self.root.add_widget(main_layout)
        
        # 定时更新状态
        Clock.schedule_interval(lambda dt: self.update_status(final_label), 1)
        
        print("宠物创建完成")
    
    def update_status(self, label):
        """更新状态标签"""
        label.text = f"Android: {IS_ANDROID}\nWindow: {Window.width}x{Window.height}\nTime: {datetime.now().strftime('%H:%M:%S')}"
    
    def on_start(self):
        """应用启动"""
        print("应用启动")
        
        if IS_ANDROID:
            print("Android环境启动")
        
        # 延迟进行最终检查
        Clock.schedule_once(lambda dt: self.final_check(), 2)
    
    def final_check(self):
        """最终检查"""
        print("最终检查")
        
        # 窗口状态检查
        if self.window_initialized:
            print(f"窗口状态良好: {Window.width}x{Window.height}")
        
        if self.pet:
            print(f"宠物状态良好: {self.pet.pos}, {self.pet.pet_size}")
    
    def on_stop(self):
        """应用停止"""
        print("应用停止")

class UltimatePet(Widget):
    """极简宠物"""
    pet_size = NumericProperty(120)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 宠物大小
        self.size_hint = (None, None)
        self.size = (self.pet_size, self.pet_size)
        
        # 宠物颜色
        self.main_color = (1, 0.6, 0.8, 1)  # 粉色
        
        # 绘制宠物
        self.draw_pet()
        
        # 绑定位置变化
        self.bind(pos=self.update_pet)
        
        # 简单动画
        Clock.schedule_interval(lambda dt: self.float_animation(), 2)
        
        print(f"宠物创建: size={self.size}, pos={self.pos}")
    
    def draw_pet(self):
        """绘制宠物"""
        with self.canvas:
            # 宠物主体
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
        """更新宠物"""
        with self.canvas:
            self.canvas.clear()
            self.draw_pet()
    
    def float_animation(self):
        """浮动动画"""
        # 轻微浮动
        self.x += 1
        self.y += 1
        
        # 边界检查
        if self.x > Window.width - self.pet_size:
            self.x = Window.width - self.pet_size
        if self.y > Window.height - self.pet_size:
            self.y = Window.height - self.pet_size
    
    def on_touch_down(self, touch):
        """触摸事件"""
        if self.collide_point(*touch.pos):
            print(f"宠物被点击: {touch.pos}")
            
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

# ==================== 主入口 ====================
if __name__ == '__main__':
    print("=== 宠物闹钟极简版启动 ===")
    
    # 基本配置
    Config.set('graphics', 'background_color', '0,0,0,0')
    
    # 启动应用
    app = UltimateApp()
    app.run()
    
    print("=== 应用运行完成 ===")