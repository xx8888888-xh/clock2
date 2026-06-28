#!/usr/bin/env python3
"""
测试新增模块的功能
"""

import datetime
import os

# 切换到脚本所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 延迟导入模块
try:
    from pet_mood import PetMoodSystem
    from weather import WeatherAPI
    from calendar_integration import CalendarIntegration
except ModuleNotFoundError as e:
    print(f"缺少模块: {e}")
    exit(1)

print("测试宠物心情系统:")
try:
    mood_system = PetMoodSystem()
    current_time = datetime.datetime.now()
    weather_impact = 'sunny'
    calendar_event = {'title': '生日', 'type': 'birthday'}
    mood = mood_system.get_current_mood(current_time, weather_impact, calendar_event)
    print(f"当前心情: {mood}")
    
    # 添加断言验证功能
    assert mood is not None, "心情数据不能为None"
    assert mood in ['happy', 'sad', 'excited', 'calm', 'anxious', 'tired'], f"无效的心情值: {mood}"
    print(f"心情颜色: {mood_system.get_mood_color(mood)}")
    
    emoji = mood_system.generate_mood_emoji(mood)
    assert emoji is not None, "emoji不能为None"
    print(f"心情emoji: {emoji}")
    
    desc = mood_system.get_mood_description(mood)
    assert desc is not None and len(desc) > 0, "心情描述不能为空"
    print(f"心情描述: {desc}")
except Exception as e:
    print(f"宠物心情系统测试失败: {e}")
    exit(1)

print("\n测试天气系统:")
try:
    weather_api = WeatherAPI()
    weather = weather_api.get_current_weather()
    print(f"天气数据: {weather}")
    
    # 添加断言验证功能
    assert weather is not None, "天气数据不能为None"
    assert 'temp' in weather, "天气数据缺少temp字段"
    assert 'condition' in weather, "天气数据缺少condition字段"
    
    pet_weather = weather_api.get_weather_for_pet()
    assert pet_weather is not None, "宠物天气数据不能为None"
    print(f"宠物天气: {pet_weather}")
except Exception as e:
    print(f"天气系统测试失败: {e}")
    exit(1)

print("\n测试日历系统:")
try:
    calendar = CalendarIntegration()
    today_events = calendar.get_today_events()
    print(f"今天的事件: {today_events}")
    
    # 添加断言验证功能
    assert today_events is not None, "事件列表不能为None"
    assert isinstance(today_events, list), "事件列表必须是list类型"
    
    next_event = calendar.get_next_event()
    print(f"下一个事件: {next_event}")
    if next_event:
        assert 'type' in next_event, "事件缺少type字段"
        emoji = calendar.get_event_emoji(next_event['type'])
        assert emoji is not None, "事件emoji不能为None"
        print(f"事件emoji: {emoji}")
except Exception as e:
    print(f"日历系统测试失败: {e}")
    exit(1)

print("\n所有模块测试完成，功能正常工作！")
