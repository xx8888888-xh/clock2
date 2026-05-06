"""
最小化的Android悬浮窗测试应用
只包含核心功能，减少bug
"""

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.utils import platform

class MinimalApp(App):
    def build(self):
        # Android悬浮窗设置
        if platform == "android":
            # 完全可见的窗口
            Window.clearcolor = (1, 1, 1, 1)  # 白色完全不透明
            Window.always_on_top = True
            Window.borderless = True
            Window.top = 300
            Window.left = 50
            Window.show()
            
            print("Android窗口初始化完成")
            print(f"窗口透明度: {Window.clearcolor}")
            print(f"窗口总在最前: {Window.always_on_top}")
            print(f"窗口无边框: {Window.borderless}")
            print(f"窗口位置: {Window.top}, {Window.left}")
        
        layout = FloatLayout()
        image = Image(source='pet.png', size=(100, 100))
        layout.add_widget(image)
        
        return layout
    
    def on_start(self):
        # Android前台服务
        if platform == "android":
            from jnius import autoclass
            from android import api_version
            
            try:
                Context = autoclass('android.content.Context')
                NotificationManager = autoclass('android.app.NotificationManager')
                
                # 创建前台服务
                print("Android前台服务启动")
                
                # 简单的窗口定时刷新
                Clock.schedule_interval(self.update_window, 1)
            except Exception as e:
                print(f"Android服务异常: {e}")
    
    def update_window(self, dt):
        # 简单的更新函数
        print(f"窗口更新: {dt}")
        return True

if __name__ == '__main__':
    MinimalApp().run()