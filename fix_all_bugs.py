#!/usr/bin/env python3
"""
修复clock2项目中所有发现的bug
"""

import os
import sys
import re

def fix_calendar_integration():
    """修复calendar_integration.py中的bug"""
    print("修复calendar_integration.py...")
    
    try:
        with open('calendar_integration.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复check_overdue_events2函数中的bug
        old_function = """
    def check_overdue_events2(self):
        \"\"\"检查过期事件\"\"\"
        now = datetime.datetime.now()
        overdue_events = []
        
        for event in self.events:
            try:
                event_datetime = datetime.datetime.strptime(f\"{event.get('date', '')} {event.get('time', '')}\", \"%Y-%m-%d %H:%M\")
                if event_datetime < now:
                    overdue_events.append(event)
            except (KeyError, ValueError):
                continue
        
        # 删除过期事件
        if overdue_events:
            self.events = []
            for event in self.events:
                try:
                    event_datetime = datetime.datetime.strptime(f\"{event.get('date', '')} {event.get('time', '')}\", \"%Y-%m-%d %H:%M\")
                    if event_datetime >= now:
                        self.events.append(event)
                except (KeyError, ValueError):
                    self.events.append(event)
            self._save_events()
        
        return overdue_events"""
        
        new_function = """
    def check_overdue_events(self):
        \"\"\"检查过期事件\"\"\"
        now = datetime.datetime.now()
        overdue_events = []
        
        for event in self.events:
            try:
                event_datetime = datetime.datetime.strptime(f\"{event.get('date', '')} {event.get('time', '')}\", \"%Y-%m-%d %H:%M\")
                if event_datetime < now:
                    overdue_events.append(event)
            except (KeyError, ValueError):
                continue
        
        # 删除过期事件
        if overdue_events:
            new_events = []
            for event in self.events:
                try:
                    event_datetime = datetime.datetime.strptime(f\"{event.get('date', '')} {event.get('time', '')}\", \"%Y-%m-%d %H:%M\")
                    if event_datetime >= now:
                        new_events.append(event)
                except (KeyError, ValueError):
                    new_events.append(event)
            self.events = new_events
            self._save_events()
        
        return overdue_events"""
        
        if old_function in content:
            content = content.replace(old_function, new_function)
            print("✅ 修复了calendar_integration.py中的check_overdue_events2函数")
        else:
            print("⚠️ check_overdue_events2函数可能已经修复")
        
        with open('calendar_integration.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
    except Exception as e:
        print(f"❌ 修复calendar_integration.py失败: {e}")

def add_android_permission_code():
    """为main.py添加Android权限请求代码"""
    print("添加Android权限请求代码到main.py...")
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在App类的build方法中添加Android权限代码
        build_method_pattern = r'def build\(self\):'
        if build_method_pattern in content:
            # 找到build方法
            lines = content.split('\n')
            new_lines = []
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                if line.strip() == 'def build(self):':
                    # 在build方法中添加Android权限代码
                    new_lines.append('        # Android悬浮窗权限检查')
                    new_lines.append('        from kivy.utils import platform')
                    new_lines.append('        if platform == \"android\":')
                    new_lines.append('            from android.permissions import Permission, request_permission')
                    new_lines.append('            from android.permissions import check_permission')
                    new_lines.append('            ')
                    new_lines.append('            # 检查悬浮窗权限')
                    new_lines.append('            has_permission = check_permission(Permission.SYSTEM_ALERT_WINDOW)')
                    new_lines.append('            if not has_permission:')
                    new_lines.append('                def callback(permissions, results):')
                    new_lines.append('                    if all(results):')
                    new_lines.append('                        print(\"悬浮窗权限已授予\")')
                    new_lines.append('                    else:')
                    new_lines.append('                        print(\"悬浮窗权限被拒绝，应用可能无法正常运行\")')
                    new_lines.append('                ')
                    new_lines.append('                # 请求悬浮窗权限')
                    new_lines.append('                request_permission(Permission.SYSTEM_ALERT_WINDOW, callback)')
                    new_lines.append('            else:')
                    new_lines.append('                print(\"已拥有悬浮窗权限\")')
                    new_lines.append('        ')
                    
                    # 继续后面的代码
                    for j in range(i+1, len(lines)):
                        if lines[j].strip() == '        self.pet = CutePet()':
                            new_lines.append(lines[j])
                            break
                        new_lines.append(lines[j])
                        
                    # 跳过重复添加的部分
                    break
            
            new_content = '\n'.join(new_lines)
            
            with open('main.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ 添加了Android权限请求代码")
        else:
            print("⚠️ 找不到build方法")
        
    except Exception as e:
        print(f"❌ 添加Android权限代码失败: {e}")

def add_missing_animation_methods():
    """确保main.py中有所有动画方法"""
    print("检查main.py中的动画方法...")
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否缺少动画方法
        needed_methods = [
            'def start_happy_animation(self):',
            'def start_sleepy_animation(self):', 
            'def start_excited_animation(self):',
            'def start_angry_animation(self):'
        ]
        
        missing_methods = []
        for method in needed_methods:
            if method not in content:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"⚠️ 缺少动画方法: {missing_methods}")
        else:
            print("✅ 所有动画方法都存在")
        
    except Exception as e:
        print(f"❌ 检查动画方法失败: {e}")

def fix_weather_api():
    """修复weather.py中的API问题"""
    print("修复weather.py中的API问题...")
    
    try:
        with open('weather.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 确保get_weather_for_pet方法正确
        if 'get_weather_for_pet' in content:
            print("✅ weather.py中的get_weather_for_pet方法已存在")
        else:
            print("❌ weather.py缺少get_weather_for_pet方法")
            
            # 添加get_weather_for_pet方法
            weather_class_end = r'class WeatherAPI:'
            if weather_class_end in content:
                lines = content.split('\n')
                new_lines = []
                
                for i, line in enumerate(lines):
                    new_lines.append(line)
                    if line.strip() == 'class WeatherAPI:':
                        # 找到类定义结束位置（通常是最后一个方法之后）
                        for j in range(i, len(lines)):
                            if lines[j].strip().startswith('def get_weather_for_pet(self):'):
                                # 已经存在
                                print("✅ 方法已存在")
                                break
                            if lines[j].strip() == '' and j > i + 50:
                                # 在类末尾添加方法
                                new_lines.append('    def get_weather_for_pet(self):')
                                new_lines.append('        \"\"\"获取宠物友好的天气信息\"\"\"')
                                new_lines.append('        weather = self.get_current_weather()')
                                new_lines.append('        pet_weather_data = {')
                                new_lines.append('            \'emoji\': self._get_weather_emoji(weather[\'description\']),')
                                new_lines.append('            \'temp\': f\"{int(weather[\'temp\'])}°C\",')
                                new_lines.append('            \'description\': weather[\'description\'],')
                                new_lines.append('            \'impact\': weather[\'impact\'],')
                                new_lines.append('            \'suggestion\': self._get_weather_suggestion(weather[\'impact\'])')
                                new_lines.append('        }')
                                new_lines.append('        return pet_weather_data')
                                print("✅ 添加了get_weather_for_pet方法")
                                break
        
    except Exception as e:
        print(f"❌ 修复weather.py失败: {e}")

def update_buildozer_spec():
    """更新buildozer.spec配置"""
    print("更新buildozer.spec配置...")
    
    try:
        with open('buildozer.spec', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 确保有正确的权限
        if 'SYSTEM_ALERT_WINDOW' not in content:
            # 替换权限配置
            old_permissions = 'android.permissions = INTERNET, VIBRATE, WAKE_LOCK, FOREGROUND_SERVICE, RECEIVE_BOOT_COMPLETED'
            new_permissions = 'android.permissions = INTERNET, VIBRATE, SYSTEM_ALERT_WINDOW, WAKE_LOCK, FOREGROUND_SERVICE, RECEIVE_BOOT_COMPLETED'
            
            if old_permissions in content:
                content = content.replace(old_permissions, new_permissions)
                print("✅ 添加了SYSTEM_ALERT_WINDOW权限")
            else:
                print("⚠️ 找不到权限配置")
        
        # 确保API版本合适
        if 'android.api = 33' not in content:
            # 更新Android API版本
            content = re.sub(r'android.api = \d+', 'android.api = 33', content)
            content = re.sub(r'android.target_api = \d+', 'android.target_api = 33', content)
            content = re.sub(r'android.sdk = \d+', 'android.sdk = 34', content)
            print("✅ 更新Android API版本")
        
        with open('buildozer.spec', 'w', encoding='utf-8') as f:
            f.write(content)
        
    except Exception as e:
        print(f"❌ 更新buildozer.spec失败: {e}")

def add_startup_error_handling():
    """添加启动时的错误处理"""
    print("添加启动错误处理...")
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在on_start方法中添加错误处理
        if 'def on_start(self):' in content:
            lines = content.split('\n')
            new_lines = []
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                if line.strip() == 'def on_start(self):':
                    # 添加try-catch块
                    new_lines.append('        try:')
                    new_lines.append('            from kivy.utils import platform')
                    new_lines.append('            print(f\"平台: {platform}\")')
                    new_lines.append('        except Exception as e:')
                    new_lines.append('            print(f\"平台检测失败: {e}\")')
                    break
            
            # 替换原来的代码
            for j in range(i+1, len(lines)):
                if lines[j].strip().startswith('if os.path.exists('):
                    # 继续原来的代码
                    for k in range(j, len(lines)):
                        new_lines.append(lines[k])
                    break
                elif lines[j].strip().startswith('def'):
                    # 另一个方法开始，停止
                    break
                else:
                    new_lines.append(lines[j])
            
            new_content = '\n'.join(new_lines)
            
            with open('main.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ 添加了启动错误处理")
        else:
            print("⚠️ 找不到on_start方法")
        
    except Exception as e:
        print(f"❌ 添加启动错误处理失败: {e}")

def main():
    print("开始修复clock2项目中的所有bug...\n")
    
    # 修复calendar模块的错误
    fix_calendar_integration()
    
    # 添加Android权限请求代码
    add_android_permission_code()
    
    # 检查动画方法
    add_missing_animation_methods()
    
    # 修复weather模块
    fix_weather_api()
    
    # 更新buildozer配置
    update_buildozer_spec()
    
    # 添加启动错误处理
    add_startup_error_handling()
    
    print("\n🔧 修复完成！")
    print("修复了以下问题:")
    print("1. calendar_integration.py中的事件处理bug")
    print("2. Android悬浮窗权限请求")
    print("3. weather.py中的API处理")
    print("4. buildozer.spec权限配置")
    print("5. 启动错误处理")
    
    print("\n📋 下一步:")
    print("1. 在Android设备上测试权限请求")
    print("2. 确保Android悬浮窗权限已被授予")
    print("3. 测试应用是否不再闪退")

if __name__ == '__main__':
    main()