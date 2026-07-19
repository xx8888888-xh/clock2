"""
桌面宠物闹钟 - Android修复版本（结合SimpleWindow和Service架构）
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Android环境检测
IS_ANDROID = False
ANDROID_SERVICE_AVAILABLE = False

try:
    # 尝试导入Android模块
    import android
    IS_ANDROID = True
    
    # 尝试检测Service支持
    try:
        android_api = android.Android()
        ANDROID_SERVICE_AVAILABLE = True
        print("✅ Android模块可用，Service支持可用")
    except Exception as e:
        print(f"⚠️ Android模块可用，但Service检测失败: {e}")
except ImportError:
    print("❌ Android模块不可用")

print(f"Android环境: {IS_ANDROID}, Service支持: {ANDROID_SERVICE_AVAILABLE}")

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch
from kivy.uix.image import Image
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

# ==================== Android Service架构 ====================
class AndroidServiceManager:
    """Android Service管理器"""
    def __init__(self):
        self.is_service_started = False
        self.permission_granted = False
        
    def ensure_foreground_service(self):
        """确保前台服务正在运行"""
        if not IS_ANDROID:
            return True
        
        if self.is_service_started:
            return True
        
        try:
            android_api = android.Android()
            
            # 检查是否已有权限
            permissions = android_api.checkPermissions()
            print(f"Android权限: {permissions}")
            
            if permissions.get("SYSTEM_ALERT_WINDOW", False):
                self.permission_granted = True
                print("✅ Android悬浮窗权限已获取")
            
            # 尝试启动前台服务
            result = android_api.startForegroundService()
            
            if result:
                self.is_service_started = True
                print("✅ Android前台服务启动成功")
                return True
            else:
                print("⚠️ Android前台服务启动失败")
                return False
                
        except Exception as e:
            print(f"❌ Android前台服务启动失败: {e}")
            return False
    
    def check_permissions(self):
        """检查权限"""
        if not IS_ANDROID:
            return {"SYSTEM_ALERT_WINDOW": True, "FOREGROUND_SERVICE": True}
            
        try:
            android_api = android.Android()
            permissions = android_api.checkPermissions()
            
            print(f"Android权限检查结果: {permissions}")
            
            has_window_permission = permissions.get("SYSTEM_ALERT_WINDOW", False)
            has_service_permission = permissions.get("FOREGROUND_SERVICE", False)
            
            return {
                "SYSTEM_ALERT_WINDOW": has_window_permission,
                "FOREGROUND_SERVICE": has_service_permission
            }
            
        except Exception as e:
            print(f"Android权限检查异常: {e}")
            return {"SYSTEM_ALERT_WINDOW": False, "FOREGROUND_SERVICE": False}
    
    def request_permissions(self):
        """请求权限"""
        if not IS_ANDROID:
            return True
            
        try:
            android_api = android.Android()
            result = android_api.requestPermissions(["SYSTEM_ALERT_WINDOW", "FOREGROUND_SERVICE"])
            
            print(f"Android权限请求结果: {result}")
            
            if result:
                self.permission_granted = True
            return result
            
        except Exception as e:
            print(f"Android权限请求异常: {e}")
            return False

# ==================== Window初始化策略 ====================
class WindowManager:
    """Window管理器"""
    def __init__(self):
        self.window_initialized = False
        self.window_creation_attempts = 0
    
    def init_window(self):
        """初始化窗口"""
        print("初始化Window")
        
        # 第1次尝试：基本设置
        Window.clearcolor = (0, 0, 0, 0.01)  # 几乎透明
        
        # 第2次尝试：固定大小和位置
        Window.size = (300, 300)  # 中等大小
        Window.top = 200  # 固定位置
        Window.left = 50  # 固定位置
        
        # 第3次尝试：Android特定设置
        Window.dismiss_keyboard = False  # 禁止键盘弹出
        Window.allow_screensaver = True  # 允许屏保
        Window.borderless = True  # 无边框
        
        # 第4次尝试：延迟验证
        Clock.schedule_once(lambda dt: self.verify_window(), 1)
        
        self.window_initialized = True
        self.window_creation_attempts += 1
        
        print(f"Window初始化完成: size={Window.size}, pos={Window.top},{Window.left}")
        print(f"透明度: {Window.clearcolor}")
        
        return True
    
    def verify_window(self):
        """验证窗口是否有效"""
        print(f"验证Window: width={Window.width}, height={Window.height}")
        
        # 如果窗口尺寸为0，重新设置
        if Window.width == 0 or Window.height == 0:
            print("⚠️ Window尺寸为0，重新设置")
            Window.size = (300, 300)
        
        print(f"Window验证完成: width={Window.width}, height={Window.height}")
    
    def adjust_window_position(self):
        """调整窗口位置"""
        if Window.width > 0 and Window.height > 0:
            # 确保窗口在屏幕范围内
            Window.top = max(50, min(Window.top, Window.height - 300))
            Window.left = max(50, min(Window.left, Window.width - 300))
            print(f"Window位置调整: top={Window.top}, left={Window.left}")
    
    def get_window_status(self):
        """获取Window状态"""
        return {
            "initialized": self.window_initialized,
            "attempts": self.window_creation_attempts,
            "size": (Window.width, Window.height),
            "position": (Window.top, Window.left),
            "clearcolor": Window.clearcolor
        }

# ==================== 宠物类 ====================
class CutePet(Widget):
    """简化宠物类"""
    pet_size = NumericProperty(160)
    pet_opacity = NumericProperty(1.0)
    is_dragging = BooleanProperty(False)
    drag_start_pos = ListProperty([0, 0])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (self.pet_size, self.pet_size)
        
        # 宠物图像
        self.pet_image = None
        
        # 设置宠物位置
        self.pos = (Window.width/2 - self.pet_size/2, Window.height/2 - self.pet_size/2)
        
        # 绘制宠物
        self.draw_cute_pet()
        
        # 动画
        Clock.schedule_once(lambda dt: self.start_idle_animation(), 0.5)
        
        print(f"宠物创建: size={self.size}, pos={self.pos}")
    
    def draw_cute_pet(self):
        """绘制宠物"""
        # 先尝试使用图像
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
                return
        
        # 如果没有图像，使用默认图形
        with self.canvas:
            # 阴影
            Color(0, 0, 0, 0.15)
            Ellipse(pos=(self.x + dp(5), self.y - dp(5)), size=self.size)
            
            # 主体（粉色）
            Color(1, 0.6, 0.8, 1)
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
    
    def start_idle_animation(self):
        """开始空闲动画"""
        # 简单的呼吸动画
        breathe_in = Animation(pet_opacity=0.8, duration=2, t='in_out_sine')
        breathe_out = Animation(pet_opacity=1.0, duration=2, t='in_out_sine')
        
        anim = breathe_in + breathe_out
        anim.repeat = True
        anim.start(self)
    
    def on_touch_down(self, touch):
        """触摸事件"""
        if self.collide_point(*touch.pos):
            self.is_dragging = True
            self.drag_start_pos = touch.pos
            self.handle_click()
            return True
        return False
    
    def handle_click(self):
        """处理点击"""
        print("宠物被点击")
        
        # 点击动画
        anim1 = Animation(pet_opacity=0.7, duration=0.1, t='out_quad')
        anim2 = Animation(pet_opacity=1.0, duration=0.1, t='in_quad')
        (anim1 + anim2).start(self)
        
        # 显示菜单
        app = App.get_running_app()
        if app:
            Clock.schedule_once(lambda dt: app.show_main_menu(), 0.1)

# ==================== 闹钟管理器 ====================
class AlarmClock:
    """闹钟管理器"""
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
        
        print(f"闹钟加载: {len(self.alarms)} 个闹钟")
    
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
        
        print(f"闹钟添加: {hour}:{minute} {label}")
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
                
                if time_diff <= 60:
                    triggered_alarms.append(alarm)
                    alarm['enabled'] = False
        
        return triggered_alarms

# ==================== 应用类 ====================
class ClockApp(App):
    """主应用类"""
    def __init__(self):
        super().__init__()
        
        # Android Service管理器
        self.service_manager = AndroidServiceManager()
        
        # Window管理器
        self.window_manager = WindowManager()
        
        # 宠物
        self.pet = None
        
        # 闹钟管理器
        self.alarm_manager = AlarmClock()
        
        # 日志
        print(f"ClockApp初始化: Android={IS_ANDROID}")
    
    def build(self):
        """构建应用"""
        print("开始build方法")
        
        # 延迟初始化窗口
        Clock.schedule_once(lambda dt: self.init_window_and_pet(), 0.1)
        
        # 临时布局
        temp_layout = FloatLayout()
        temp_label = Label(
            text=f"正在初始化...\nAndroid={IS_ANDROID}",
            size_hint=(0.8, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            font_size=sp(16)
        )
        temp_layout.add_widget(temp_label)
        
        return temp_layout
    
    def init_window_and_pet(self):
        """初始化窗口和宠物"""
        print("初始化窗口和宠物")
        
        # 1. 初始化窗口
        window_result = self.window_manager.init_window()
        
        if not window_result:
            print("窗口初始化失败")
            self.show_error_message("窗口初始化失败")
            return
        
        # 2. Android Service检查
        if IS_ANDROID:
            print("Android环境，检查Service")
            service_result = self.service_manager.ensure_foreground_service()
            
            if not service_result:
                print("Android Service初始化失败")
                self.show_error_message("Android Service启动失败")
                return
        
        # 3. 构建宠物
        self.build_pet_interface()
        
        # 4. 开始闹钟检查
        Clock.schedule_interval(lambda dt: self.check_and_trigger_alarms(), 60)
        
        print("窗口和宠物初始化完成")
    
    def build_pet_interface(self):
        """构建宠物界面"""
        print("构建宠物界面")
        
        # 创建宠物
        self.pet = CutePet()
        
        # 创建布局
        layout = FloatLayout()
        layout.add_widget(self.pet)
        
        # 状态标签
        status_label = Label(
            text=f"状态:\nAndroid={IS_ANDROID}\n窗口={Window.width}x{Window.height}\n位置={Window.top},{Window.left}",
            size_hint=(None, None),
            size=(dp(250), dp(80)),
            pos=(dp(25), dp(25)),
            font_size=sp(12),
            color=get_color_from_hex('#333333')
        )
        layout.add_widget(status_label)
        
        # 更新状态
        Clock.schedule_interval(lambda dt: self.update_status(status_label), 1)
        
        # 替换root
        self.root.clear_widgets()
        self.root.add_widget(layout)
        
        print("宠物界面构建完成")
    
    def update_status(self, label):
        """更新状态标签"""
        label.text = f"状态:\nAndroid={IS_ANDROID}\n窗口={Window.width}x{Window.height}\n位置={Window.top},{Window.left}\n时间={datetime.now().strftime('%H:%M:%S')}"
    
    def check_and_trigger_alarms(self):
        """检查并触发闹钟"""
        triggered_alarms = self.alarm_manager.check_alarms()
        
        if triggered_alarms:
            print(f"触发 {len(triggered_alarms)} 个闹钟")
            
            for alarm in triggered_alarms:
                print(f"闹钟触发: {alarm['hour']}:{alarm['minute']} - {alarm['label']}")
                
                # 宠物动画
                if self.pet:
                    self.pet.handle_click()
                
                # 振动提醒（如果可用）
                try:
                    vibrator.vibrate(1.0)
                except Exception as e:
                    print(f"振动失败: {e}")
    
    def show_main_menu(self):
        """显示主菜单"""
        print("显示主菜单")
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # 标题
        layout.add_widget(Label(
            text="宠物闹钟",
            font_size=sp(22),
            bold=True,
            color=get_color_from_hex('#FF8FB1')
        ))
        
        # 状态
        layout.add_widget(Label(
            text=f"Android: {IS_ANDROID}\n窗口: {Window.width}x{Window.height}",
            font_size=sp(14),
            color=get_color_from_hex('#666666')
        ))
        
        # 闹钟列表
        if self.alarm_manager.alarms:
            layout.add_widget(Label(
                text="📋 闹钟列表:",
                font_size=sp(16),
                color=get_color_from_hex('#FF8FB1')
            ))
            
            scroll = ScrollView()
            alarm_list = BoxLayout(orientation='vertical', size_hint_y=None)
            alarm_list.bind(minimum_height=alarm_list.setter('height'))
            
            for alarm in self.alarm_manager.alarms:
                alarm_item = Label(
                    text=f"{alarm['hour']:02d}:{alarm['minute']:02d} - {alarm['label']}",
                    font_size=sp(14),
                    color=get_color_from_hex('#333333'),
                    size_hint_y=None,
                    height=dp(30)
                )
                alarm_list.add_widget(alarm_item)
            
            scroll.add_widget(alarm_list)
            layout.add_widget(scroll)
        else:
            layout.add_widget(Label(
                text="📭 没有闹钟",
                font_size=sp(16),
                color=get_color_from_hex('#666666')
            ))
        
        # 按钮
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10))
        
        add_button = Button(text="➕ 添加闹钟", size_hint_x=0.5)
        add_button.bind(on_press=lambda x: self.show_add_alarm_dialog())
        button_layout.add_widget(add_button)
        
        close_button = Button(text="❌ 关闭", size_hint_x=0.5)
        close_button.bind(on_press=lambda x: self.dismiss_menu())
        button_layout.add_widget(close_button)
        
        layout.add_widget(button_layout)
        
        popup = Popup(title='菜单', content=layout, size_hint=(0.8, 0.8))
        popup.open()
    
    def show_add_alarm_dialog(self):
        """显示添加闹钟对话框"""
        dialog_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        dialog_layout.add_widget(Label(text="添加闹钟", font_size=sp(20)))
        
        hour_input = TextInput(text="08", font_size=sp(16))
        minute_input = TextInput(text="00", font_size=sp(16))
        label_input = TextInput(text="闹钟", font_size=sp(16))
        
        dialog_layout.add_widget(hour_input)
        dialog_layout.add_widget(minute_input)
        dialog_layout.add_widget(label_input)
        
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10))
        
        cancel_button = Button(text="❌ 取消")
        cancel_button.bind(on_press=lambda x: self.dismiss_menu())
        button_layout.add_widget(cancel_button)
        
        save_button = Button(text="✅ 保存")
        save_button.bind(on_press=lambda x: self.add_alarm(
            hour_input.text, minute_input.text, label_input.text
        ))
        button_layout.add_widget(save_button)
        
        dialog_layout.add_widget(button_layout)
        
        dialog = Popup(title='添加闹钟', content=dialog_layout, size_hint=(0.7, 0.7))
        dialog.open()
    
    def add_alarm(self, hour_str, minute_str, label):
        """添加闹钟"""
        try:
            hour = int(hour_str)
            minute = int(minute_str)
            
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                self.alarm_manager.add_alarm(hour, minute, label)
                print(f"闹钟添加成功: {hour}:{minute} {label}")
            else:
                print(f"闹钟添加失败: {hour}:{minute} {label}")
                
        except ValueError:
            print(f"闹钟添加失败（格式错误）: {hour_str}:{minute_str} {label}")
    
    def show_error_message(self, message):
        """显示错误消息"""
        print(f"错误: {message}")
        
        layout = BoxLayout(orientation='vertical', padding=dp(20))
        layout.add_widget(Label(text=message, font_size=sp(18)))
        
        close_button = Button(text="关闭", size_hint=(1, 0.3))
        close_button.bind(on_press=lambda x: self.dismiss_menu())
        layout.add_widget(close_button)
        
        popup = Popup(title='错误', content=layout, size_hint=(0.7, 0.5))
        popup.open()
    
    def dismiss_menu(self):
        """关闭菜单"""
        App.get_running_app().popup.dismiss()
    
    def on_start(self):
        """应用启动"""
        print("应用启动")
        
        if IS_ANDROID:
            print("Android环境启动")
        
        # 延迟进行更多初始化
        Clock.schedule_once(lambda dt: self.final_init(), 3)
    
    def final_init(self):
        """最终初始化"""
        print("最终初始化")
        
        # 调整窗口位置
        self.window_manager.adjust_window_position()
        
        # 保存闹钟
        self.alarm_manager.save_alarms()
    
    def on_stop(self):
        """应用停止"""
        print("应用停止")
        
        # 保存数据
        self.alarm_manager.save_alarms()

# ==================== 主入口 ====================
if __name__ == '__main__':
    print("=== 宠物闹钟启动 ===")
    print(f"Android环境: {IS_ANDROID}")
    print(f"Service支持: {ANDROID_SERVICE_AVAILABLE}")
    
    app = ClockApp()
    app.run()
    
    print("=== 应用运行完成 ===")