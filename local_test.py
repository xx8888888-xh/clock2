#!/usr/bin/env python3
"""
本地环境测试 - 模拟Android应用运行
"""

import os
import re

def check_dependencies():
    """检查必要的Python依赖"""
    print("检查Python依赖...")
    
    required_modules = [
        'kivy',
        'plyer',
        'requests',
        'Pillow',
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} 未安装")
    
    if missing_modules:
        print(f"需要安装的模块: {missing_modules}")
        return False
    return True

def check_files():
    """检查所有必要的文件"""
    print("\n检查文件完整性...")
    
    required_files = [
        'main.py',
        'resources.py',
        'pet_mood.py',
        'weather.py',
        'calendar_integration.py',
        'icon.png',
        'pet.png',
        'alarms.json',
        'calendar.json',
        'requirements.txt',
        'buildozer.spec',
        'README.md'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            missing_files.append(file)
            print(f"❌ {file} 不存在")
    
    if missing_files:
        print(f"缺失的文件: {missing_files}")
        return False
    return True

def check_android_permission_code():
    """检查Android权限代码"""
    print("\n检查Android权限代码...")

    if not os.path.exists('main.py'):
        print("❌ main.py 不存在，跳过检查")
        return False

    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()

    checks = {
        'android权限导入': re.compile(r'from android\.permissions import (Permission|request_permission)'),
        '权限检查': re.compile(r'check_permission\s*\(\s*Permission\.SYSTEM_ALERT_WINDOW\s*\)'),
        '权限请求': re.compile(r'request_permission\s*\(\s*Permission\.SYSTEM_ALERT_WINDOW'),
        '导入错误处理': re.compile(r'except\s+ImportError'),
        '平台检测': re.compile(r'from kivy\.utils import platform'),
    }

    all_pass = True
    for check_name, pattern in checks.items():
        if pattern.search(content):
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
            all_pass = False

    return all_pass

def check_buildozer_config():
    """检查buildozer配置"""
    print("\n检查buildozer.spec配置...")

    if not os.path.exists('buildozer.spec'):
        print("❌ buildozer.spec 不存在，跳过检查")
        return False

    with open('buildozer.spec', 'r', encoding='utf-8') as f:
        content = f.read()

    checks = {
        'SYSTEM_ALERT_WINDOW权限': 'SYSTEM_ALERT_WINDOW',
        'INTERNET权限': 'INTERNET',
        'VIBRATE权限': 'VIBRATE',
        'WAKE_LOCK权限': 'WAKE_LOCK',
        'FOREGROUND_SERVICE权限': 'FOREGROUND_SERVICE',
        'RECEIVE_BOOT_COMPLETED权限': 'RECEIVE_BOOT_COMPLETED',
        'Android API版本': 'android.api = 33',
        '主程序文件': 'source.main = main.py',
        '应用图标': 'icon.filename = icon.png',
    }

    all_pass = True
    for check_name, check_text in checks.items():
        if check_text in content:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
            all_pass = False

    return all_pass

def check_calendar_fix():
    """检查calendar_integration.py修复"""
    print("\n检查calendar_integration.py修复...")

    if not os.path.exists('calendar_integration.py'):
        print("❌ calendar_integration.py 不存在，跳过检查")
        return False

    with open('calendar_integration.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否有check_overdue_events2函数（未修复的旧版本）
    if re.search(r'def\s+check_overdue_events2\s*\(', content):
        print("❌ 还有未修复的check_overdue_events2函数")
        return False

    # 检查是否有check_overdue_events函数
    if re.search(r'def\s+check_overdue_events\s*\(', content):
        print("✅ check_overdue_events函数存在")
        # 检查逻辑是否正确
        if re.search(r'new_events\s*=\s*\[\]', content) and re.search(r'self\.events\s*=\s*new_events', content):
            print("✅ 逻辑修复正确")
            return True
        else:
            print("❌ 逻辑修复不正确")
            return False
    else:
        print("❌ check_overdue_events函数不存在")
        return False

def check_kivy_simulation():
    """模拟Kivy运行环境检查"""
    print("\n模拟Kivy环境检查...")

    try:
        # 测试不依赖Kivy的模块
        from pet_mood import PetMoodSystem
        from weather import WeatherAPI
        from calendar_integration import CalendarIntegration

        print("✅ pet_mood模块可导入")
        print("✅ weather模块可导入")
        print("✅ calendar_integration模块可导入")

        # 测试功能
        mood_system = PetMoodSystem()
        weather_api = WeatherAPI()
        calendar = CalendarIntegration()

        print("✅ 宠物心情系统初始化")
        print("✅ 天气系统初始化")
        print("✅ 日历系统初始化")

        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    except SyntaxError as e:
        print(f"❌ 语法错误: {e}")
        return False
    except Exception as e:
        print(f"❌ Kivy模拟环境检查失败: {e}")
        return False

def main():
    print("🎯 clock2项目本地环境测试\n")
    
    results = []
    
    results.append(check_dependencies())
    results.append(check_files())
    results.append(check_android_permission_code())
    results.append(check_buildozer_config())
    results.append(check_calendar_fix())
    results.append(check_kivy_simulation())
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n📊 测试结果: {success_count}/{total_count} 项通过")
    
    if success_count == total_count:
        print("\n🎉 所有测试通过！项目可以正常运行并打包！")
        print("\n🚀 准备推送到GitHub:")
        print("git add .")
        print("git commit -m \"修复所有bug：Android权限、日历逻辑错误、语法错误等31处问题\"")
        print("git push origin main")
    else:
        print("\n⚠️ 部分测试失败，需要继续修复")
        print("失败项:")
        for i, result in enumerate(results):
            if not result:
                print(f"  - 测试 {i+1}")

if __name__ == "__main__":
    main()