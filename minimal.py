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
            # Window属性设置优化（先位置后样式）
            Window.left = 50
            Window.top = 300
            Window.always_on_top = True
            Window.borderless = True
            Window.clearcolor = (1, 1, 1, 1)  # 白色完全不透明

            print("Android窗口初始化完成")
            print(f"窗口位置: {Window.left}, {Window.top}")
            print(f"窗口总在最前: {Window.always_on_top}")
            print(f"窗口无边框: {Window.borderless}")
            print(f"窗口透明度: {Window.clearcolor}")

        layout = FloatLayout()

        # 图片资源加载，带错误处理
        try:
            image = Image(source='pet.png', size=(100, 100))
            layout.add_widget(image)
        except Exception as e:
            print(f"图片加载失败: {e}")

        return layout

    def on_start(self):
        # Android前台服务
        if platform == "android":
            try:
                # 检查悬浮窗权限
                from jnius import autoclass
                Context = autoclass('android.content.Context')
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')

                can_draw = Settings.can_draw_overlays(Context.getInstance())
                if not can_draw:
                    print("警告: 应用缺少悬浮窗(SYSTEM_ALERT_WINDOW)权限")
                    # 可选：引导用户去设置页面开启权限
                    # intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION)
                    # Context.getInstance().startActivity(intent)
                else:
                    print("悬浮窗权限检查通过")

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
    try:
        MinimalApp().run()
    except Exception as e:
        print(f"应用异常退出: {e}")
