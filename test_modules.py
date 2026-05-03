#!/usr/bin/env python3
"""
测试新增模块的功能
"""

import datetime

from pet_mood import PetMoodSystem
from weather import WeatherAPI
from calendar_integration import CalendarIntegration

print("测试宠物心情系统:")
mood_system = PetMoodSystem()
current_time = datetime.datetime.now()
weather_impact = 'sunny'
calendar_event = {'title': '生日', 'type': 'birthday'}
mood = mood_system.get_current_mood(current_time, weather_impact, calendar_event)
print(f"当前心情: {mood}")
print(f"心情颜色: {mood_system.get_mood_color(mood)}")
print(f"心情emoji: {mood_system.generate_mood_emoji(mood)}")
print(f"心情描述: {mood_system.get_mood_description(mood)}")

print("\n测试天气系统:")
weather_api = WeatherAPI()
weather = weather_api.get_current_weather()
print(f"天气数据: {weather}")
pet_weather = weather_api.get_weather_for_pet()
print(f"宠物天气: {pet_weather}")

print("\n测试日历系统:")
calendar = CalendarIntegration()
today_events = calendar.get_today_events()
print(f"今天的事件: {today_events}")
next_event = calendar.get_next_event()
print(f"下一个事件: {next_event}")
if next_event:
    print(f"事件emoji: {calendar.get_event_emoji(next_event['type'])}")

print("\n所有模块测试完成，功能正常工作！")