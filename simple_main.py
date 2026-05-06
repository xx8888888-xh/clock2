"""
最简单的Kivy Android应用
保证一定能构建成功
"""

from kivy.app import App
from kivy.uix.label import Label

class SimpleApp(App):
    def build(self):
        return Label(text='宠物闹钟\n测试版本')

if __name__ == '__main__':
    SimpleApp().run()