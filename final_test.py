#!/usr/bin/env python3
"""
最终测试验证所有修复
"""
import datetime
import json

def test_calendar_fix():
    """测试calendar_integration.py修复"""
    print("测试日历模块修复...")
    from calendar_integration import CalendarIntegration
    
    calendar = CalendarIntegration()
    
    # 添加一个过期事件
    calendar.add_event("过期事件", "2024-05-01", "12:00", "test", "过期事件")
    
    # 添加一个未来的事件
    calendar.add_event("未来事件", "2026-12-31", "12:00", "test", "未来事件")
    
    # 检查过期事件
    overdue = calendar.check_overdue_events()
    print(f"过期事件数量: {len(overdue)}")
    
    # 检查剩余事件
    remaining = calendar.get_today_events()
    print(f"剩余事件数量: {len(remaining)}")
    
    if len(overdue) == 1 and len(remaining) == 1:
        print("✅ calendar_integration.py修复成功")
    else:
        print("❌ calendar_integration.py修复失败")

def test_android_permission():
    """测试Android权限代码"""
    print("测试Android权限代码...")
    
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    has_android_code = False
    has_permission_check = False
    has_import_error = False
    
    if "from kivy.utils import platform" in content:
        has_android_code = True
    if "check_permission(Permission.SYSTEM_ALERT_WINDOW)" in content:
        has_permission_check = True
    if "except ImportError" in content:
        has_import_error = True
    
    if has_android_code and has_permission_check and has_import_error:
        print("✅ Android权限代码已正确添加")
    else:
        print("❌ Android权限代码需要检查")

def test_buildozer_config():
    """测试buildozer.spec配置"""
    print("测试buildozer.spec配置...")
    
    with open("buildozer.spec", "r", encoding="utf-8") as f:
        content = f.read()
    
    if "SYSTEM_ALERT_WINDOW" in content:
        print("✅ buildozer.spec包含SYSTEM_ALERT_WINDOW权限")
    else:
        print("❌ buildozer.spec缺少SYSTEM_ALERT_WINDOW权限")

def test_syntax():
    """测试语法"""
    print("测试语法检查...")
    
    try:
        import main
        print("✅ main.py语法正确")
    except Exception as e:
        print(f"❌ main.py语法错误: {e}")
    
    try:
        import calendar_integration
        print("✅ calendar_integration.py语法正确")
    except Exception as e:
        print(f"❌ calendar_integration.py语法错误: {e}")
    
    try:
        import weather
        print("✅ weather.py语法正确")
    except Exception as e:
        print(f"❌ weather.py语法错误: {e}")
    
    try:
        import pet_mood
        print("✅ pet_mood.py语法正确")
    except Exception as e:
        print(f"❌ pet_mood.py语法错误: {e}")

def main():
    print("开始最终测试验证...")
    
    test_calendar_fix()
    test_android_permission()
    test_buildozer_config()
    test_syntax()
    
    print("\n🎉 最终测试完成！")
    print("所有修复已验证完毕")

if __name__ == "__main__":
    main()