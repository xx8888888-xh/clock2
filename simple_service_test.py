"""
Android悬浮窗最小化测试 - Service核心架构
只实现最基本功能，解决闪退问题
"""

import os
import time
from datetime import datetime

# Android兼容性检测
ANDROID = False
try:
    import android
    ANDROID = True
except ImportError:
    android = None

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty

# 最小化窗口设置
class SimpleApp(App):
    def __init__(self):
        super().__init__()
        self.is_android = ANDROID
        self.permission_checked = False
        
        # 宠物数据
        self.pet_x = 100
        self.pet_y = 200
        self.pet_size = 120
        
        # 日志记录
        self.log_history = []
        
    def init_window_safe(self):
        """安全初始化窗口"""
        print("开始安全初始化窗口")
        
        # Android环境处理
        if self.is_android:
            print("Android环境检测到")
            
            # 检查权限（简化版本）
            try:
                if android:
                    android_api = android.Android()
                    print("Android API可用")
                    
                    # 延迟权限检查（Android需要时间）
                    Clock.schedule_once(lambda dt: self.check_android_permissions(), 1)
                else:
                    print("Android API不可用，直接尝试窗口")
                    
                    self.create_window_directly()
                    
            except Exception as e:
                print(f"Android权限检查失败: {e}")
                self.create_window_directly()
                
        else:
            # 桌面环境直接创建
            self.create_window_directly()
    
    def check_android_permissions(self):
        """检查Android权限"""
        print("检查Android权限")
        
        # 设置窗口（即使权限未获取）
        Window.clearcolor = (0, 0, 0, 0.01)  # 几乎透明
        
        # 固定窗口大小
        Window.size = (300, 300)
        
        # 固定窗口位置（避免因位置计算错误导致闪退）
        Window.top = 200
        Window.left = 100
        
        # 禁止键盘弹出（防止键盘干扰）
        Window.dismiss_keyboard = False
        
        print(f"Android窗口设置: size={Window.size}, pos={Window.top},{Window.left}")
        
        # 标记权限已检查
        self.permission_checked = True
        
        # 延迟构建界面
        Clock.schedule_once(lambda dt: self.build_pet(), 0.5)
    
    def create_window_directly(self):
        """直接创建窗口（非Android环境）"""
        print("创建桌面窗口")
        
        Window.clearcolor = (0, 0, 0, 0.01)
        Window.size = (300, 300)
        Window.top = 200
        Window.left = 100
        
        print(f"桌面窗口设置: size={Window.size}, pos={Window.top},{Window.left}")
        
        # 延迟构建界面
        Clock.schedule_once(lambda dt: self.build_pet(), 0.3)
    
    def build_pet(self):
        """构建宠物界面"""
        print("构建宠物界面")
        
        layout = FloatLayout()
        
        # 简单宠物（圆形）
        pet = SimplePet()
        pet.pos = (self.pet_x, self.pet_y)
        pet.size = (self.pet_size, self.pet_size)
        layout.add_widget(pet)
        
        # 状态标签
        status_label = Label(
            text=f"Android: {self.is_android}\nSize: {Window.size}\nPos: {Window.top},{Window.left}\nTime: {datetime.now().strftime('%H:%M:%S')}",
            size_hint=(None, None),
            size=(200, 80),
            pos=(50, 350),
            font_size=12,
            color=(0.3, 0.3, 0.3, 1)
        )
        layout.add_widget(status_label)
        
        # 定时更新状态
        Clock.schedule_interval(lambda dt: self.update_status(status_label), 1)
        
        self.root = layout
        print("宠物界面构建完成")
    
    def update_status(self, label):
        """更新状态标签"""
        label.text = f"Android: {self.is_android}\nSize: {Window.size}\nPos: {Window.top},{Window.left}\nTime: {datetime.now().strftime('%H:%M:%S')}"
    
    def build(self):
        """Kivy build方法"""
        print("开始build方法")
        
        # 延迟初始化窗口
        Clock.schedule_once(lambda dt: self.init_window_safe(), 0.1)
        
        # 创建一个最小布局
        layout = FloatLayout()
        return layout
    
    def on_start(self):
        """应用启动"""
        print("应用启动")
        
        # Android特定日志
        if self.is_android:
            self.log_history.append("Android环境启动")
        else:
            self.log_history.append("桌面环境启动")
    
    def on_stop(self):
        """应用停止"""
        print("应用停止")
        self.log_history.append("应用停止")

class SimplePet(Widget):
    """简单宠物 - 只有一个圆形"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        with self.canvas:
            # 阴影
            Color(0, 0, 0, 0.15)
            Ellipse(pos=(self.x + 2, self.y - 2), size=self.size)
            
            # 主体
            Color(1, 0.5, 0.8, 1)  # 粉色
            Ellipse(pos=self.pos, size=self.size)
            
            # 眼睛
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
            
            # 嘴巴
            Color(1, 0.3, 0.5, 1)
            mouth_size = (self.size[0] * 0.3, self.size[1] * 0.1)
            Ellipse(
                pos=(self.x + self.size[0] * 0.35, self.y + self.size[1] * 0.3),
                size=mouth_size
            )
        
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
        # 简单动画
        Clock.schedule_interval(lambda dt: self.float_animation(), 1)
    
    def update_canvas(self, *args):
        """更新canvas（简化版本）"""
        with self.canvas:
            self.canvas.clear()
            
            # 阴影
            Color(0, 0, 0, 0.15)
            Ellipse(pos=(self.x + 2, self.y - 2), size=self.size)
            
            # 主体
            Color(1, 0.5, 0.8, 1)
            Ellipse(pos=self.pos, size=self.size)
            
            # 眼睛
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
            
            # 嘴巴
            Color(1, 0.3, 0.5, 1)
            mouth_size = (self.size[0] * 0.3, self.size[1] * 0.1)
            Ellipse(
                pos=(self.x + self.size[0] * 0.35, self.y + self.size[1] * 0.3),
                size=mouth_size
            )
    
    def float_animation(self):
        """浮动动画"""
        pass  # 简化版本，不做动画

if __name__ == '__main__':
    print("启动最小化测试应用")
    
    # 平台检测
    if ANDROID:
        print("Android环境")
        print(f"android模块: {android}")
    else:
        print("桌面环境")
    
    app = SimpleApp()
    app.run()

print("应用启动完成")