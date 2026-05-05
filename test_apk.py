"""
APK测试脚本 - 检查APK包中的问题
"""

import zipfile
import os

# 检查APK结构
def check_apk_structure():
    """检查APK结构"""
    apk_files = [
        "/root/.openclaw/workspace/clock2/petalarm_v3.0.4.apk"
    ]
    
    for apk_file in apk_files:
        if os.path.exists(apk_file):
            print(f"检查APK: {apk_file}")
            
            try:
                with zipfile.ZipFile(apk_file, 'r') as apk:
                    # 列出文件
                    print("APK中包含的文件:")
                    files = apk.namelist()
                    
                    # 查找Python相关文件
                    python_files = [f for f in files if f.endswith('.py')]
                    kivy_files = [f for f in files if 'kivy' in f]
                    android_files = [f for f in files if 'android' in f]
                    
                    print(f"Python文件数量: {len(python_files)}")
                    print(f"Kivy相关文件数量: {len(kivy_files)}")
                    print(f"Android相关文件数量: {len(android_files)}")
                    
                    # 检查重要文件
                    important_files = [
                        'main.py',
                        'android_fixed_main.py',
                        'android_service_main.py',
                        'simple_service_test.py',
                        'android_minimal_app.py',
                        'minimal_main.py'
                    ]
                    
                    for file in important_files:
                        if file in files:
                            print(f"✅ {file} 存在于APK中")
                        else:
                            print(f"❌ {file} 不在APK中")
                    
                    # 检查Android权限
                    android_permissions = []
                    for f in files:
                        if f.endswith('.py'):
                            try:
                                content = apk.read(f).decode('utf-8', errors='ignore')
                                if 'SYSTEM_ALERT_WINDOW' in content:
                                    android_permissions.append(f)
                            except:
                                pass
                    
                    print(f"包含权限的Python文件: {android_permissions}")
                    
                    return files
                    
            except Exception as e:
                print(f"无法打开APK: {e}")
    
    return []

# 检查APK的大小
def check_apk_size():
    """检查APK大小"""
    apk_files = [
        "/root/.openclaw/workspace/clock2/petalarm_v3.0.4.apk"
    ]
    
    for apk_file in apk_files:
        if os.path.exists(apk_file):
            size = os.path.getsize(apk_file)
            print(f"APK大小: {size} bytes ({size/1024/1024:.2f} MB)")
            
            # 典型Kivy APK大小
            if size < 10000000:
                print("⚠️ APK可能太小，缺少依赖")
            elif size > 20000000:
                print("⚠️ APK可能太大，包含过多资源")
            else:
                print("✅ APK大小适中")

# 检查buildozer.spec配置
def check_buildozer_spec():
    """检查buildozer.spec配置"""
    spec_file = "/root/.openclaw/workspace/clock2/buildozer.spec"
    
    if not os.path.exists(spec_file):
        print("❌ buildozer.spec文件不存在")
        return
    
    with open(spec_file, 'r') as f:
        content = f.read()
    
    print("检查buildozer.spec配置:")
    
    # Android权限
    if 'android.permissions' in content:
        print("✅ android.permissions配置存在")
        # 检查具体权限
        if 'SYSTEM_ALERT_WINDOW' in content:
            print("✅ SYSTEM_ALERT_WINDOW权限存在")
        else:
            print("❌ SYSTEM_ALERT_WINDOW权限缺失")
    else:
        print("❌ android.permissions配置缺失")
    
    # Android API版本
    if 'android.api' in content:
        print("✅ android.api配置存在")
        # API版本检查
        api_values = [line for line in content.split('\n') if 'android.api' in line]
        print(f"API配置: {api_values}")
    else:
        print("❌ android.api配置缺失")
    
    # 包名和版本
    if 'package.name' in content:
        print("✅ package.name配置存在")
    else:
        print("❌ package.name配置缺失")
    
    if 'package.domain' in content:
        print("✅ package.domain配置存在")
    else:
        print("❌ package.domain配置缺失")
    
    # 应用名称
    if 'title' in content:
        print("✅ title配置存在")
        title_lines = [line for line in content.split('\n') if 'title' in line]
        print(f"应用名称: {title_lines}")
    else:
        print("❌ title配置缺失")

# 生成修复建议
def generate_fixes():
    """生成修复建议"""
    print("\n=== Android悬浮窗修复建议 ===\n")
    
    print("1. APK打包问题:")
    print("   - 确保APK包含所有Python文件")
    print("   - 检查buildozer.spec配置")
    print("   - 确保android.permissions包含SYSTEM_ALERT_WINDOW")
    print("   - android.api至少设置为29")
    
    print("\n2. Android权限问题:")
    print("   - 确保应用在Android设备上获取SYSTEM_ALERT_WINDOW权限")
    print("   - 建议在代码中延迟窗口初始化")
    print("   - 先请求权限，再创建窗口")
    
    print("\n3. Window透明度问题:")
    print("   - Window.clearcolor必须不是完全透明 (0, 0, 0, 0)")
    print("   - 改为 (0, 0, 0, 0.01) 几乎透明")
    print("   - Window.top和Window.left必须是固定值")
    
    print("\n4. Kivy生命周期问题:")
    print("   - 不要在build方法中立即初始化窗口")
    print("   - 使用Clock.schedule_once延迟初始化")
    print("   - 先创建一个临时布局，然后替换")
    
    print("\n5. Service架构:")
    print("   - Android悬浮窗需要前台服务")
    print("   - 否则应用可能被系统杀死")
    print("   - 确保Android前台服务配置")
    
    print("\n6. 测试建议:")
    print("   - 先测试最简单版本 (minimal_main.py)")
    print("   - 逐步添加功能")
    print("   - 每次测试都要修改buildozer.spec")
    print("   - 确保APK打包正确")

# 主函数
def main():
    """主函数"""
    print("=== APK测试和分析 ===")
    
    # 检查APK结构
    files = check_apk_structure()
    
    # 检查APK大小
    check_apk_size()
    
    # 检查buildozer.spec
    check_buildozer_spec()
    
    # 生成修复建议
    generate_fixes()
    
    print("\n=== 关键步骤 ===\n")
    print("1. 修改main.py使用最简单的架构")
    print("2. 更新buildozer.spec增加权限")
    print("3. 重新打包APK")
    print("4. 在Android设备上安装测试")
    print("5. 如果还有问题，尝试android_fixed_main.py")

if __name__ == '__main__':
    main()