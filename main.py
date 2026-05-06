from kivy.app import App
from kivy.uix.label import Label

class ClockApp(App):
    def build(self):
        return Label(text='Clock2\nAndroid APK Test')

if __name__ == '__main__':
    ClockApp().run()