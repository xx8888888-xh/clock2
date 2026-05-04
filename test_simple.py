#!/usr/bin/env python3
"""
简单测试所有模块
"""

import os

print("测试宠物心情系统...")

try:
    from pet_mood import PetMoodSystem
    mood_system = PetMoodSystem()
    print("✅ pet_mood模块导入成功")
except Exception as e:
    print(f"❌ pet_mood模块导入失败: {e}")

print("\n测试天气系统...")
try:
    from weather import WeatherAPI
    weather_api = WeatherAPI()
    print("✅ weather模块导入成功")
except Exception as e:
    print(f"❌ weather模块导入失败: {e}")

print("\n测试日历系统...")
try:
    from calendar_integration import CalendarIntegration
    calendar = CalendarIntegration()
    print("✅ calendar_integration模块导入成功")
except Exception as e:
    print(f"❌ calendar_integration模块导入失败: {e}")

print("\n测试main.py导入...")
try:
    from main import CutePet
    print("✅ main.py中的CutePet类导入成功")
except Exception as e:
    print(f"❌ main.py导入失败: {e}")

print("\n测试文件是否存在...")
files_to_check = ['alarms.json', 'calendar.json', 'icon.png', 'pet.png']
for file in files_to_check:
    if os.path.exists(file):
        print(f"✅ {file} 存在")
    else:
        print(f"❌ {file} 不存在")

print("\n✅ 所有基础测试完成")