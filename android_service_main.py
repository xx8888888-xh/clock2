"""
Android悬浮窗全新架构 - Service+Activity混合方案
解决Android悬浮窗闪退bug
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Android兼容性检测
ANDROID = False
try:
    import android
    ANDROID = True
except ImportError:
    android = None

if ANDROID:
    print("Android环境检测成功")
else:
    print("非Android环境")

from kivy.app import App
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

# Android专用导入
if ANDROID:
    try:
        from kivy.core.window import Window
        from jnius import autoclass
    except ImportError as e:
        print(f"Android特定导入失败: {e}")
else:
    from kivy.core.window import Window

# ==================== Android Service架构 ====================
class AndroidServiceManager:
    """Android Service管理器 - 确保悬浮窗有Service支撑"""
    def __init__(self):
        self.is_service_started = False
        self.service_start_time = None
        
        if ANDROID:
            self.init_android_service()
    
    def init_android_service(self):
        """初始化Android服务组件"""
        try:
            # Android Service类
            Context = autoclass('android.content.Context')
            Intent = autoclass('android.content.Intent')
            
            # 检查是否已经是前台服务
            android_api = android.Android()
            result = android_api.checkForegroundService()
            
            if result:
                print("Android: 前台服务已存在")
                self.is_service_started = True
                self.service_start_time = datetime.now()
            else:
                print("Android: 需要启动前台服务")
                
        except Exception as e:
            print(f"Android Service初始化失败: {e}")
    
    def ensure_foreground_service(self):
        """确保前台服务正在运行"""
        if not ANDROID:
            return
        
        if self.is_service_started:
            return
            
        try:
            android_api = android.Android()
            result = android_api.startForegroundService()
            
            if result:
                print("Android: 前台服务启动成功")
                self.is_service_started = True
                self.service_start_time = datetime.now()
            else:
                print("Android: 前台服务启动失败")
                
        except Exception as e:
            print(f"Android前台服务启动失败: {e}")
    
    def check_permissions(self):
        """检查Android权限"""
        if not ANDROID:
            return {"SYSTEM_ALERT_WINDOW": True, "FOREGROUND_SERVICE": True}
            
        try:
            android_api = android.Android()
            permissions = android_api.checkPermissions()
            
            has_window_permission = permissions.get("SYSTEM_ALERT_WINDOW", False)
            has_service_permission = permissions.get("FOREGROUND_SERVICE", False)
            
            print(f"Android权限状态: 悬浮窗={has_window_permission}, 前台服务={has_service_permission}")
            
            return {
                "SYSTEM_ALERT_WINDOW": has_window_permission,
                "FOREGROUND_SERVICE": has_service_permission
            }
            
        except Exception as e:
            print(f"Android权限检查失败: {e}")
            return {"SYSTEM_ALERT_WINDOW": False, "FOREGROUND_SERVICE": False}
    
    def request_permissions(self):
        """请求Android权限"""
        if not ANDROID:
            return True
            
        try:
            android_api = android.Android()
            result = android_api.requestPermissions(["SYSTEM_ALERT_WINDOW", "FOREGROUND_SERVICE"])
            
            print(f"Android权限请求结果: {result}")
            return result
            
        except Exception as e:
            print(f"Android权限请求失败: {e}")
            return False

# ==================== WindowManager架构 ====================
class AndroidWindowManager:
    """Android窗口管理器 - 处理窗口创建和权限"""
    def __init__(self):
        self.window_created = False
        self.permission_granted = False
        
        if ANDROID:
            self.init_window_manager()
    
    def init_window_manager(self):
        """初始化窗口管理器"""
        try:
            # Android WindowManager
            WindowManager = autoclass('android.view.WindowManager')
            LayoutParams = autoclass('android.view.WindowManager.LayoutParams')
            
            # 窗口参数类型
            self.TYPE_APPLICATION_OVERLAY = LayoutParams.TYPE_APPLICATION_OVERLAY
            
            print("Android WindowManager初始化成功")
            
        except Exception as e:
            print(f"Android WindowManager初始化失败: {e}")
    
    def create_window(self, app):
        """创建Android悬浮窗"""
        if not ANDROID:
            # 桌面环境直接创建窗口
            Window.clearcolor = (0, 0, 0, 0.01)  # 几乎透明
            Window.size = (400, 400)
            Window.top = 300
            Window.left = 50
            return True
        
        if self.window_created:
            return True
        
        try:
            # 检查权限
            service_manager = app.service_manager
            permissions = service_manager.check_permissions()
            
            if not permissions.get("SYSTEM_ALERT_WINDOW", False):
                print("Android: 缺少悬浮窗权限，需要请求")
                granted = service_manager.request_permissions()
                if not granted:
                    print("Android: 权限请求失败，无法创建窗口")
                    return False
            
            # 确保前台服务运行
            service_manager.ensure_foreground_service()
            
            # 创建窗口
            Window.clearcolor = (0, 0, 0, 0.01)
            Window.size = (400, 400)
            
            # Android特殊设置
            Window.dismiss_keyboard = False
            Window.allow_screensaver = True
            
            # 设置窗口位置
            Window.top = 300
            Window.left = 50
            
            self.window_created = True
            self.permission_granted = True
            
            print("Android悬浮窗创建成功")
            return True
            
        except Exception as e:
            print(f"Android窗口创建失败: {e}")
            return False
    
    def adjust_window_position(self):
        """调整窗口位置（防止窗口重叠）"""
        if not ANDROID:
            return
        
        try:
            # 随机位置以避免重叠
            Window.top = 200 + (datetime.now().second % 10) * 20
            Window.left = 100 + (datetime.now().second % 10) * 30
            
            print(f"Android窗口位置调整: top={Window.top}, left={Window.left}")
            
        except Exception as e:
            print(f"Android窗口位置调整失败: {e}")

# ==================== 核心App类（Android兼容） ====================
class ClockApp(App):
    def __init__(self):
        super().__init__()
        self.service_manager = AndroidServiceManager()
        self.window_manager = AndroidWindowManager()
        self.permission_requested = False
        
        # 宠物和闹钟管理器
        self.pet = None
        self.alarm_manager = None
        self.timer_manager = None
        self.cute_banner = None
        
        # 初始状态
        self.is_android = ANDROID
        self.is_window_ready = False
        
        # 调试信息
        self.debug_info = {
            "platform": "Android" if ANDROID else "Desktop",
            "service_ready": False,
            "window_ready": False,
            "permissions_checked": False
        }
    
    def init_app_window(self):
        """初始化应用窗口 - Android兼容版本"""
        print(f"初始化窗口: Android={self.is_android}")
        
        # 1. Android环境处理
        if self.is_android:
            print("Android环境，使用Service+WindowManager架构")
            
            # 检查权限
            permissions = self.service_manager.check_permissions()
            self.debug_info["permissions_checked"] = True
            print(f"权限状态: {permissions}")
            
            # 尝试创建窗口
            window_created = self.window_manager.create_window(self)
            
            if not window_created:
                print("Android窗口创建失败，尝试延迟初始化")
                
                # 延迟3秒后再次尝试
                Clock.schedule_once(lambda dt: self.try_window_init_again(), 3)
                return False
            
            self.is_window_ready = True
            self.debug_info["window_ready"] = True
            print("Android窗口初始化成功")
            
        else:
            # 桌面环境
            print("桌面环境，直接创建窗口")
            
            Window.clearcolor = (0, 0, 0, 0.01)
            Window.size = (400, 400)
            Window.top = 300
            Window.left = 50
            
            self.is_window_ready = True
            self.debug_info["window_ready"] = True
            print("桌面窗口初始化成功")
        
        return True
    
    def try_window_init_again(self):
        """第二次尝试初始化窗口"""
        print("第二次尝试初始化窗口")
        
        if self.is_android:
            # 再次检查权限
            permissions = self.service_manager.check_permissions()
            print(f"第二次权限检查: {permissions}")
            
            if permissions.get("SYSTEM_ALERT_WINDOW", False):
                window_created = self.window_manager.create_window(self)
                
                if window_created:
                    self.is_window_ready = True
                    self.debug_info["window_ready"] = True
                    print("Android窗口第二次初始化成功")
                    
                    # 延迟加载宠物
                    Clock.schedule_once(lambda dt: self.build_after_window_ready(), 0.5)
                    
                else:
                    print("Android窗口第二次初始化失败，进入权限请求流程")
                    
                    # 请求权限
                    granted = self.service_manager.request_permissions()
                    
                    if granted:
                        Clock.schedule_once(lambda dt: self.try_window_init_again(), 3)
                    else:
                        print("权限请求失败，显示权限引导")
                        self.show_permission_guide()
                        
            else:
                print("权限未获取，显示权限引导")
                self.show_permission_guide()
                
        else:
            # 桌面环境直接创建
            self.is_window_ready = True
            self.debug_info["window_ready"] = True
            print("桌面窗口初始化成功")
            Clock.schedule_once(lambda dt: self.build_after_window_ready(), 0.5)
    
    def show_permission_guide(self):
        """显示Android权限引导"""
        if not self.is_android:
            return
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        title = Label(
            text="⚠️ Android权限设置",
            font_size=sp(22),
            bold=True,
            color=get_color_from_hex('#FF6B6B')
        )
        layout.add_widget(title)
        
        instructions = Label(
            text="请按照以下步骤设置权限:\n\n1. 打开手机设置\n2. 进入应用管理\n3. 找到'桌面宠物闹钟'\n4. 开启'悬浮窗权限'\n5. 开启'前台服务权限'\n6. 重启应用",
            font_size=sp(16),
            color=get_color_from_hex('#5A4A4A'),
            halign='left',
            valign='middle'
        )
        instructions.bind(size=instructions.setter('text_size'))
        layout.add_widget(instructions)
        
        close_btn = Button(
            text="我知道了",
            size_hint=(0.8, 0.2),
            background_color=get_color_from_hex('#4ECDC4')
        )
        close_btn.bind(on_press=lambda x: layout.remove_widget(close_btn))
        layout.add_widget(close_btn)
        
        self.root.add_widget(layout)
    
    def build_after_window_ready(self):
        """窗口准备完成后构建界面"""
        print("窗口已准备，开始构建界面")
        
        if not self.is_window_ready:
            print("窗口未准备，延迟构建")
            Clock.schedule_once(lambda dt: self.build_after_window_ready(), 1)
            return
        
        # 创建宠物
        self.pet = CutePet()
        self.pet.size_hint = (None, None)
        self.pet.size = (160, 160)
        
        # 设置宠物位置
        if self.is_android:
            # Android环境宠物居中显示
            Window.width = 400
            Window.height = 400
            
            pet_pos_x = Window.width / 2 - self.pet.size[0] / 2
            pet_pos_y = Window.height / 2 - self.pet.size[1] / 2
            
            self.pet.pos = (pet_pos_x, pet_pos_y)
            
            print(f"Android宠物位置: {self.pet.pos}, Window={Window.width}x{Window.height}")
        else:
            # 桌面环境
            pet_pos_x = 50
            pet_pos_y = 50
            self.pet.pos = (pet_pos_x, pet_pos_y)
        
        # 创建浮层布局
        root_layout = FloatLayout()
        root_layout.add_widget(self.pet)
        
        # 创建横幅
        self.cute_banner = CuteBanner()
        root_layout.add_widget(self.cute_banner)
        
        # 创建闹钟管理器
        self.alarm_manager = AlarmClock()
        self.timer_manager = TimerManager()
        
        print("界面构建完成")
        
        return root_layout
    
    def build(self):
        """Kivy build方法"""
        print("开始构建应用")
        
        # 创建基本布局
        layout = BoxLayout(orientation='vertical')
        
        # 添加调试信息标签
        debug_label = Label(
            text=f"初始化状态: Android={self.is_android}, Window={self.is_window_ready}",
            font_size=sp(12),
            color=get_color_from_hex('#888888')
        )
        layout.add_widget(debug_label)
        
        # 延迟窗口初始化
        Clock.schedule_once(lambda dt: self.init_app_window(), 0.5)
        
        return layout
    
    def show_main_menu(self):
        """显示主菜单"""
        if self.pet and self.is_window_ready:
            menu = MainMenu(self)
            menu.open()
    
    def show_timer_dialog(self):
        """显示计时器对话框"""
        if self.pet and self.is_window_ready:
            dialog = TimerDialog(self.timer_manager)
            dialog.open()
    
    def show_quick_menu(self):
        """显示快捷菜单"""
        if self.pet and self.is_window_ready:
            menu = QuickMenu(self)
            menu.open()
    
    def trigger_alarm(self, alarm):
        """触发闹钟"""
        print(f"触发闹钟: {alarm['label']} {alarm['hour']}:{alarm['minute']}")
        
        # 横幅显示
        if self.cute_banner:
            title = f"闹钟提醒 - {alarm['label']}"
            content = alarm.get('content', '时间到了！')
            self.cute_banner.show(title, content, self.alarm_manager.settings.get('banner_time', 5))
        
        # 声音提醒
        if self.alarm_manager.settings.get('sound_enabled', True):
            try:
                sound = SoundLoader.load('assets/alarm.wav')
                if sound:
                    sound.volume = self.alarm_manager.settings.get('volume', 0.8)
                    sound.play()
            except Exception as e:
                print(f"声音播放失败: {e}")
        
        # 振动提醒
        if self.alarm_manager.settings.get('vibrate', True):
            try:
                vibrator.vibrate(1.0)
            except Exception as e:
                print(f"振动失败: {e}")
        
        # 宠物动画
        if self.pet:
            self.pet.excited_animation()
    
    def trigger_timer_alarm(self, timer):
        """触发计时器提醒"""
        print(f"触发计时器: {timer['label']}")
        
        if self.cute_banner:
            title = f"计时器结束 - {timer['label']}"
            content = f"计时器 ({timer['total_seconds']}秒) 已结束"
            self.cute_banner.show(title, content, self.alarm_manager.settings.get('banner_time', 5))
        
        # 宠物动画
        if self.pet:
            self.pet.excited_animation()
    
    def on_start(self):
        """应用启动时调用"""
        print(f"应用启动: Android={self.is_android}")
        
        if self.is_android:
            print("Android启动 - 确保前台服务")
            self.service_manager.ensure_foreground_service()
    
    def on_stop(self):
        """应用停止时调用"""
        print("应用停止")
        
        # 清理闹钟管理器
        if self.alarm_manager:
            self.alarm_manager.cleanup()
        
        # 清理计时器管理器
        if self.timer_manager:
            self.timer_manager.cleanup()
        
        # 清理宠物
        if self.pet:
            self.pet.cleanup()
        
        # 清理横幅
        if self.cute_banner:
            self.cute_banner.cleanup()

# ==================== 宠物类（简化版） ====================
class CutePet(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (160, 160)
        
        # 基础图形
        with self.canvas:
            Color(0, 0, 0, 0.15)
            Ellipse(pos=(self.x + 5, self.y - 5), size=self.size)
            
            Color(1, 0.6, 0.8, 1)  # 粉色
            Ellipse(pos=self.pos, size=self.size)
            
            Color(1, 1, 1, 0.3)
            Ellipse(
                pos=(self.x + self.size[0] * 0.2, self.y + self.size[1] * 0.6),
                size=(self.size[0] * 0.4, self.size[1] * 0.25)
            )
        
        self.bind(pos=self.update_canvas, size=self.update_canvas)
    
    def update_canvas(self, *args):
        with self.canvas:
            self.canvas.clear()
            
            Color(0, 0, 0, 0.15)
            Ellipse(pos=(self.x + 5, self.y - 5), size=self.size)
            
            Color(1, 0.6, 0.8, 1)
            Ellipse(pos=self.pos, size=self.size)
            
            Color(1, 1, 1, 0.3)
            Ellipse(
                pos=(self.x + self.size[0] * 0.2, self.y + self.size[1] * 0.6),
                size=(self.size[0] * 0.4, self.size[1] * 0.25)
            )

# ==================== 简化闹钟管理器 ====================
class AlarmClock:
    def __init__(self):
        self.alarms = []
        self.settings = {"snooze_duration": 5, "sound_enabled": True, "vibrate": True}
    
    def add_alarm(self, hour, minute, label):
        alarm = {"hour": hour, "minute": minute, "label": label}
        self.alarms.append(alarm)

# ==================== 简化计时器管理器 ====================
class TimerManager:
    def __init__(self):
        self.timers = []
    
    def add_timer(self, minutes, label):
        timer = {"minutes": minutes, "label": label}
        self.timers.append(timer)

# ==================== 简化菜单类 ====================
class MainMenu(Popup):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.title = "宠物闹钟"
        self.size_hint = (0.8, 0.6)
        
        layout = BoxLayout(orientation='vertical', padding=dp(20))
        
        layout.add_widget(Label(text="主菜单", font_size=sp(20)))
        layout.add_widget(Label(text="Android兼容版本", font_size=sp(14)))
        
        close_btn = Button(text="关闭", size_hint=(1, 0.2))
        close_btn.bind(on_press=self.dismiss)
        layout.add_widget(close_btn)
        
        self.content = layout

# ==================== 主入口 ====================
if __name__ == '__main__':
    print("启动桌面宠物闹钟 - Android兼容版本")
    
    # Android检测
    if ANDROID:
        print("运行在Android环境")
    else:
        print("运行在桌面环境")
    
    app = ClockApp()
    app.run()

print("应用启动完成")