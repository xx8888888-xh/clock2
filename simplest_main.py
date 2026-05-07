import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.label import Label

class SimpleClockApp(App):
    def build(self):
        return Label(text='Simple Clock2', font_size=50)

if __name__ == '__main__':
    SimpleClockApp().run()