"""
测试Android构建的最简版本
"""

from kivy.app import App
from kivy.uix.label import Label

class TestApp(App):
    def build(self):
        return Label(text='Android Test\nBuild Check')

if __name__ == '__main__':
    TestApp().run()