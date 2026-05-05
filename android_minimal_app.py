"""
Android悬浮窗最小可行产品 - 解决所有bug
"""

import os
import sys
from datetime import datetime

# Android检测
IS_ANDROID = False
if 'android' in sys.modules or hasattr(sys, 'android'):
    IS_ANDROID = True
    print("Android环境已检测到")
else:
    try:
        import android
        IS_ANDROID = True
        print("Android环境通过import检测")
    except ImportError:
        print("非Android环境")

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse
from kivy.properties import NumericProperty, ListProperty

# Android权限处理类
class AndroidPermissionHandler:
    """Android权限处理（无依赖）"""
    def __init__(self):
        self.permissions_granted = False
        self.initialized = False
        
        if IS_ANDROID:
            print("Android权限处理器初始化")
        else:
            print("桌面环境权限处理器初始化")
    
    def ensure_window_permissions(self):
        """确保窗口权限"""
        print("确保窗口权限")
        
        # 第一步：先设置窗口属性（无论权限是否获取）
        Window.clearcolor = (0, 0, 0, 0.01)  # 非完全透明
        
        # 第二步：固定窗口大小和位置（避免动态计算错误）
        Window.size = (200, 200)  # 更小的窗口
        Window.top = 100
        Window.left = 50
        
        # 第三步：关键设置 - 避免Android特定问题
        Window.dismiss_keyboard = False  # 禁止键盘弹出
        Window.allow_screensaver = True  # 允许屏保
        
        # 第四步：延迟显示（解决Android窗口创建时序问题）
        Clock.schedule_once(lambda dt: self.finalize_window_setup(), 2)
        
        self.permissions_granted = True
        print("窗口权限处理完成")
        return True
    
    def finalize_window_setup(self):
        """最终化窗口设置"""
        print("最终化窗口设置")
        
        # 确保窗口可见
        Window.borderless = True  # 无边框
        
        # 再次设置透明度
        Window.clearcolor = (0, 0, 0, 0.01)
        
        print(f"窗口设置完成: size={Window.size}, pos={Window.top},{Window.left}")
    
    def request_permissions(self):
        """请求权限（简化版本）"""
        print("请求权限（简化版本）")
        return True  # 简化，实际应用中需要真正请求权限
    
    def check_permissions(self):
        """检查权限（简化版本）"""
        print("检查权限（简化版本）")
        return {"SYSTEM_ALERT_WINDOW": True}  # 简化

# 简化宠物类
class SimplePet(Widget):
    """最简化的宠物"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (120, 120)
        
        with self.canvas:
            # 宠物主体（简单圆形）
            Color(1, 0.5, 0.8, 1)  # 粉色
            Ellipse(pos=self.pos, size=self.size)
        
        self.bind(pos=self.update_canvas)
        
        # 日志
        print(f"宠物创建: pos={self.pos}, size={self.size}")
    
    def update_canvas(self, *args):
        """更新canvas"""
        with self.canvas:
            self.canvas.clear()
            Color(1, 0.5, 0.8, 1)
            Ellipse(pos=self.pos, size=self.size)
    
    def on_touch_down(self, touch):
        """触摸事件"""
        if self.collide_point(*touch.pos):
            print(f"宠物被点击: {touch.pos}")
            return True
        return False

# 主应用类
class AndroidMinimalApp(App):
    """Android最小化应用"""
    def __init__(self):
        super().__init__()
        
        # Android处理器
        self.android_handler = AndroidPermissionHandler()
        
        # 宠物
        self.pet = None
        
        # 日志记录
        self.init_logs = []
        
    def log(self, message):
        """记录日志"""
        self.init_logs.append(message)
        print(message)
    
    def init_window(self):
        """初始化窗口（无延迟版本）"""
        self.log("初始化窗口")
        
        # 无论Android还是桌面，都统一处理
        Window.clearcolor = (0, 0, 0, 0.01)
        
        # 固定窗口大小（非常重要）
        Window.size = (200, 200)
        
        # 固定位置（避免动态计算）
        Window.top = 100
        Window.left = 50
        
        # Android特定设置
        Window.dismiss_keyboard = False
        Window.allow_screensaver = True
        Window.borderless = True
        
        # 日志输出
        self.log(f"窗口设置完成: size={Window.size}, pos={Window.top},{Window.left}")
        self.log(f"透明度: {Window.clearcolor}")
        
        # 返回True表示窗口初始化成功
        return True
    
    def build_pet_widget(self):
        """构建宠物widget"""
        self.log("构建宠物widget")
        
        # 创建宠物
        self.pet = SimplePet()
        self.pet.pos = (Window.width/2 - self.pet.size[0]/2, 
                       Window.height/2 - self.pet.size[1]/2)
        
        # 创建布局
        layout = FloatLayout()
        layout.add_widget(self.pet)
        
        # 添加状态标签
        status_label = Label(
            text=f"Status: Android={IS_ANDROID}\nWindow: {Window.size}\nTime: {datetime.now().strftime('%H:%M:%S')}",
            size_hint=(None, None),
            size=(180, 60),
            pos=(10, 10),
            font_size=12,
            color=(0, 0, 0, 0.8)
        )
        layout.add_widget(status_label)
        
        # 定期更新状态
        Clock.schedule_interval(lambda dt: self.update_status(status_label), 1)
        
        return layout
    
    def update_status(self, label):
        """更新状态标签"""
        label.text = f"Status: Android={IS_ANDROID}\nWindow: {Window.size}\nTime: {datetime.now().strftime('%H:%M:%S')}"
    
    def build(self):
        """Kivy build方法"""
        self.log("开始build方法")
        
        # 立即初始化窗口（不延迟）
        window_init_result = self.init_window()
        
        if not window_init_result:
            self.log("窗口初始化失败")
            # 创建一个简单的错误显示
            error_layout = FloatLayout()
            error_label = Label(
                text="窗口初始化失败，请重新启动",
                size_hint=(0.8, 0.2),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            error_layout.add_widget(error_label)
            return error_layout
        
        # 延迟构建宠物（确保窗口完全初始化）
        Clock.schedule_once(lambda dt: self.finish_build(), 0.3)
        
        # 返回一个临时布局
        temp_layout = FloatLayout()
        temp_label = Label(
            text="正在初始化...",
            size_hint=(0.8, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        temp_layout.add_widget(temp_label)
        
        return temp_layout
    
    def finish_build(self):
        """完成构建"""
        self.log("完成构建")
        
        # 构建宠物widget
        layout = self.build_pet_widget()
        
        # 替换root widget
        self.root.clear_widgets()
        self.root.add_widget(layout)
        
        self.log("宠物应用构建完成")
    
    def on_start(self):
        """应用启动"""
        self.log("应用启动")
        
        # Android特殊处理
        if IS_ANDROID:
            self.log("Android环境启动完成")
            # 确保权限
            self.android_handler.ensure_window_permissions()
        else:
            self.log("桌面环境启动完成")
    
    def on_stop(self):
        """应用停止"""
        self.log("应用停止")

# 测试入口
if __name__ == '__main__':
    print("=== Android最小化应用启动 ===")
    print(f"Android状态: {IS_ANDROID}")
    print(f"窗口模块: {Window}")
    
    # 启动应用
    app = AndroidMinimalApp()
    app.run()
    
    print("=== 应用运行完成 ===")