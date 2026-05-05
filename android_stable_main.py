"""
宠物闹钟 - Android稳定架构版本
全新设计：Android Service + WindowManager + 渐进式初始化
"""

import os
import sys
import json
from datetime import datetime, timedelta

# ==================== Android环境检测 ====================
IS_ANDROID = False
ANDROID_SERVICE_SUPPORT = False

# 多种Android检测方式
try:
    # 方式1：尝试导入android
    import android
    IS_ANDROID = True
except ImportError:
    try:
        # 方式2：检查sys.modules
        if 'android' in sys.modules:
            IS_ANDROID = True
    except:
        pass

if IS_ANDROID:
    try:
        android_api = android.Android()
        ANDROID_SERVICE_SUPPORT = True
    except:
        ANDROID_SERVICE_SUPPORT = False

print(f"Android环境: {IS_ANDROID}, Service支持: {ANDROID_SERVICE_SUPPORT}")

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.properties import NumericProperty, ObjectProperty
from kivy.config import Config
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp

# ==================== Android Service架构 ====================
class AndroidWindowService:
    """Android窗口服务管理器"""
    def __init__(self):
        self.is_window_ready = False
        self.permission_granted = False
        self.init_step = 0
        self.init_states = []
        
        if IS_ANDROID:
            self.start_service_safe()
    
    def start_service_safe(self):
        """安全启动服务"""
        print("Android Service: 启动服务")
        
        # Android Service关键步骤
        self.init_states.append("Android Service初始化开始")
        
        # 延迟启动服务，避免Android时序问题
        Clock.schedule_once(lambda dt: self.init_android_window(), 1)
    
    def init_android_window(self):
        """Android窗口初始化"""
        print("Android Service: 初始化窗口")
        
        # 关键点1: 先设置窗口属性
        Window.clearcolor = (0, 0, 0, 0.01)  # 不是完全透明
        
        # 关键点2: 固定窗口大小
        Window.size = (280, 280)  # 比之前稍小
        
        # 关键点3: 固定窗口位置
        Window.top = 180
        Window.left = 60
        
        # 关键点4: Android特殊设置
        Window.dismiss_keyboard = False
        Window.allow_screensaver = True
        
        self.init_states.append("Android窗口基本设置完成")
        self.init_step += 1
        
        # 延迟检查窗口有效性
        Clock.schedule_once(lambda dt: self.verify_window_setup(), 2)
    
    def verify_window_setup(self):
        """验证窗口设置"""
        print(f"Android Service: 验证窗口 size={Window.size}, pos={Window.top},{Window.left}")
        
        # 如果窗口尺寸为0，重新设置
        if Window.width == 0 or Window.height == 0:
            print("Android Service: 窗口尺寸为0，重新设置")
            Window.size = (280, 280)
        
        # 确保窗口在可见范围内
        Window.top = max(50, min(Window.top, Window.height - 280))
        Window.left = max(50, min(Window.left, Window.width - 280))
        
        self.init_states.append("Android窗口验证完成")
        self.init_step += 1
        
        # 延迟完成初始化
        Clock.schedule_once(lambda dt: self.finalize_window(), 1)
    
    def finalize_window(self):
        """完成窗口初始化"""
        print(f"Android Service: 窗口初始化完成 size={Window.width}x{Window.height}")
        
        self.is_window_ready = True
        self.permission_granted = True
        self.init_states.append("Android窗口完全初始化")
        
        print(f"Android Service: 初始化步骤: {self.init_states}")
        
        # 通知主应用窗口已就绪
        app = App.get_running_app()
        if app and app.window_service == self:
            app.on_window_ready()

# ==================== 渐进式宠物架构 ====================
class ProgressivePet:
    """渐进式宠物 - 逐步创建，避免一次性负载"""
    def __init__(self):
        self.app = None
        self.widget = None
        self.is_created = False
        self.steps = []
    
    def start_creation(self, app):
        """开始宠物创建"""
        self.app = app
        self.steps.append("宠物创建开始")
        
        # 步骤1: 创建基本结构
        Clock.schedule_once(lambda dt: self.create_basic_pet(), 0.5)
    
    def create_basic_pet(self):
        """创建基础宠物"""
        print("宠物: 创建基础结构")
        
        # 宠物大小
        pet_size = 140
        
        # 宠物位置（居中）
        pet_x = Window.width / 2 - pet_size / 2
        pet_y = Window.height / 2 - pet_size / 2
        
        # 创建宠物widget
        self.widget = SimplePetWidget()
        self.widget.size = (pet_size, pet_size)
        self.widget.pos = (pet_x, pet_y)
        
        self.steps.append("宠物基础创建完成")
        
        # 步骤2: 添加动画
        Clock.schedule_once(lambda dt: self.add_animation(), 1)
    
    def add_animation(self):
        """添加动画"""
        print("宠物: 添加动画")
        
        if self.widget:
            # 简单的浮动动画
            Clock.schedule_interval(lambda dt: self.widget.float_animation(), 1)
            
            self.steps.append("宠物动画添加完成")
        
        # 步骤3: 添加到布局
        Clock.schedule_once(lambda dt: self.add_to_layout(), 0.5)
    
    def add_to_layout(self):
        """添加到布局"""
        print("宠物: 添加到布局")
        
        if self.widget and self.app:
            self.app.root.add_widget(self.widget)
            self.is_created = True
            self.steps.append("宠物添加到布局")
    
    def get_status(self):
        """获取宠物状态"""
        return {
            "created": self.is_created,
            "steps": self.steps
        }

class SimplePetWidget(Widget):
    """最简单宠物widget"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 宠物颜色
        self.color_pink = get_color_from_hex('#FF8FB1')
        self.color_white = (1, 1, 1, 1)
        self.color_dark = (1, 0.3, 0.5, 1)
        
        # 绘制宠物
        self.draw_pet()
        
        print(f"宠物widget创建: size={self.size}, pos={self.pos}")
    
    def draw_pet(self):
        """绘制宠物"""
        with self.canvas:
            # 宠物主体
            Color(*self.color_pink)
            Ellipse(pos=self.pos, size=self.size)
            
            # 眼睛
            Color(*self.color_white)
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
            Color(*self.color_dark)
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
1分钟
            self.y = Window.height - self.size[1]
        
        # 刷新
        self.canvas.clear()
        self.draw_pet()
    
    def on_touch_down(self, touch):
        """触摸事件"""
        if self.collide_point(*touch.pos):
            print(f"宠物点击: {touch.pos}")
            
            # 点击反馈
            self.x += 5
            self.y += 5
            
            Clock.schedule_once(lambda dt: self.reset_position(), 0.3)
            
            return True
        return False
    
    def reset_position(self):
        """重置位置"""
        self.x -= 5
        self.y -= 5

# ==================== 应用主类 ====================
class StableClockApp(App):
    """稳定架构的宠物闹钟应用"""
    def __init__(self):
        super().__init__()
        
        # Android服务
        self.window_service = AndroidWindowService()
        
        # 渐进式宠物
        self.progressive_pet = ProgressivePet()
        
        # 状态跟踪
        self.init_stages = []
        self.window_ready = False
        
        print(f"稳定架构应用初始化: Android={IS_ANDROID}")
    
    def build(self):
        """构建应用 - 渐进式"""
        print("稳定架构: build方法开始")
        
        self.init_stages.append("build开始")
        
        # 创建临时布局
        temp_layout = FloatLayout()
        
        # 状态标签
        self.status_label = Label(
            text=f"应用启动...\nAndroid={IS_ANDROID}\nStage: 0",
            size_hint=(0.8, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            font_size=sp(16),
            color=get_color_from_hex('#333333')
        )
        temp_layout.add_widget(self.status_label)
        
        self.init_stages.append("状态标签创建")
        
        # 开始渐进式初始化
        Clock.schedule_once(lambda dt: self.start_progressive_init(), 0.3)
        
        return temp_layout
    
    def start_progressive_init(self):
        """开始渐进式初始化"""
        print("稳定架构: 开始渐进式初始化")
        
        self.init_stages.append("渐进式初始化开始")
        
        # 阶段1: 更新状态
        self.status_label.text = f"阶段1: 窗口初始化\nAndroid={IS_ANDROID}"
        
        # 阶段2: 延迟Android服务初始化
        Clock.schedule_once(lambda dt: self.start_window_service(), 0.5)
    
    def start_window_service(self):
        """启动窗口服务"""
        print("稳定架构: 启动窗口服务")
        
        self.init_stages.append("窗口服务启动")
        self.status_label.text = f"阶段2: 启动窗口服务"
        
        # Android服务自动启动（在构造函数中已启动）
        
        # 阶段3: 监控窗口准备
        Clock.schedule_once(lambda dt: self.monitor_window_ready(), 1)
    
    def monitor_window_ready(self):
        """监控窗口准备"""
        print("稳定架构: 监控窗口准备")
        
        if self.window_service.is_window_ready:
            print("稳定架构: 窗口已就绪")
            self.window_ready = True
            self.status_label.text = f"阶段3: 窗口就绪\nsize={Window.width}x{Window.height}"
            Clock.schedule_once(lambda dt: self.create_pet(), 0.3)
        else:
            print("稳定架构: 窗口未就绪，继续等待")
            self.status_label.text = f"阶段3: 等待窗口\nsize={Window.width}x{Window.height}"
            Clock.schedule_once(lambda dt: self.monitor_window_ready(), 1)
    
    def create_pet(self):
        """创建宠物"""
        print("稳定架构: 创建宠物")
        
        self.init_stages.append("宠物创建开始")
        self.status_label.text = f"阶段4: 创建宠物"
        
        # 开始渐进式宠物创建
        self.progressive_pet.start_creation(self)
        
        # 监控宠物创建状态
        Clock.schedule_once(lambda dt: self.monitor_pet_creation(), 1)
    
    def monitor_pet_creation(self):
        """监控宠物创建"""
        pet_status = self.progressive_pet.get_status()
        
        if pet_status["created"]:
            print("稳定架构: 宠物创建完成")
            self.status_label.text = f"阶段5: 宠物已创建\nsize={self.progressive_pet.widget.size}"
            self.init_stages.append("宠物创建完成")
            Clock.schedule_once(lambda dt: self.finalize_application(), 0.5)
        else:
            print(f"稳定架构: 宠物创建步骤: {pet_status['steps']}")
            self.status_label.text = f"阶段5: 宠物创建中\nsteps={len(pet_status['steps'])}"
            Clock.schedule_once(lambda dt: self.monitor_pet_creation(), 1)
    
    def finalize_application(self):
        """最终化应用"""
        print("稳定架构: 最终化应用")
        
        self.init_stages.append("应用最终化")
        self.status_label.text = f"宠物闹钟已启动\nAndroid={IS_ANDROID}\n窗口={Window.width}x{Window.height}"
        
        # 添加最终界面元素
        Clock.schedule_once(lambda dt: self.add_final_elements(), 0.5)
    
    def add_final_elements(self):
        """添加最终界面元素"""
        print("稳定架构: 添加最终界面元素")
        
        # 宠物状态标签
        pet_status_label = Label(
            text=f"宠物位置: {self.progressive_pet.widget.pos}\n宠物大小: {self.progressive_pet.widget.size}",
            size_hint=(None, None),
            size=(dp(200), dp(60)),
            pos=(dp(40), dp(Window.height - 80)),
            font_size=sp(12),
            color=get_color_from_hex('#666666')
        )
        self.root.add_widget(pet_status_label)
        
        # 定时更新
        Clock.schedule_interval(lambda dt: self.update_pet_status(pet_status_label), 1)
        
        print(f"稳定架构: 初始化完成，共{len(self.init_stages)}个阶段")
    
    def update_pet_status(self, label):
        """更新宠物状态"""
        label.text = f"宠物位置: {self.progressive_pet.widget.pos}\n宠物大小: {self.progressive_pet.widget.size}\n时间: {datetime.now().strftime('%H:%M:%S')}"
    
    def on_window_ready(self):
        """窗口已就绪的回调"""
        print("稳定架构: on_window_ready回调")
        
        self.window_ready = True
        self.init_stages.append("窗口ready回调")
        
        # 确保宠物创建开始
        if not self.progressive_pet.is_created:
            Clock.schedule_once(lambda dt: self.create_pet(), 0.3)
    
    def on_start(self):
        """应用启动"""
        print("稳定架构: on_start")
        self.init_stages.append("on_start")
    
    def on_stop(self):
        """应用停止"""
        print("稳定架构: on_stop")
        print(f"初始化阶段记录: {self.init_stages}")

# ==================== 启动 ====================
if __name__ == '__main__':
    print("=== Android稳定架构启动 ===")
    print(f"Android环境: {IS_ANDROID}")
    
    # 基本配置
    Config.set('graphics', 'background_color', '0,0,0,0')
    
    app = StableClockApp()
    app.run()
    
    print("=== Android稳定架构运行完成 ===")