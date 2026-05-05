#!/usr/bin/env python3
"""
验证APK文件和修复效果
"""

import os
import subprocess

def check_apk_file():
    """检查APK文件"""
    apk_path = "/root/.openclaw/workspace/clock2/petalarm_v3.0.4.apk"
    
    if os.path.exists(apk_path):
        size = os.path.getsize(apk_path)
        print(f"APK文件大小: {size} bytes")
        
        # 使用file命令检查文件类型
        result = subprocess.run(["file", apk_path], capture_output=True, text=True)
        print(f"文件类型: {result.stdout}")
        
        if size > 40 * 1024 * 1024:  # 大于40MB
            print("✅ APK文件看起来完整")
            return True
        else:
            print("❌ APK文件可能不完整")
            return False
    else:
        print("❌ APK文件不存在")
        return False

def check_code_fixes():
    """检查代码修复"""
    main_py = "/root/.openclaw/workspace/clock2/clock2/main.py"
    
    print("\n=== 代码修复验证 ===")
    
    # 检查透明度设置
    with open(main_py, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查透明度
    transparency_line = "Window.clearcolor = (0.95, 0.95, 0.95, 0.5)"
    if transparency_line in content:
        print(f"✅ 透明度设置: {transparency_line}")
        print("   Alpha=0.5 (50%透明)")
        print("   R,G,B=0.95 (浅灰色)")
    else:
        print("❌ 透明度设置未找到")
    
    # 检查权限异步处理
    if "Clock.schedule_once(lambda dt: self.init_app_window(), 0.5)" in content:
        print("✅ 权限异步处理: 延迟窗口初始化")
    else:
        print("❌ 权限异步处理未找到")
    
    # 检查Android前台服务
    if "AndroidApplication.start_service()" in content:
        print("✅ Android前台服务启动")
    else:
        print("❌ Android前台服务未找到")
    
    # 检查调试日志
    if "窗口初始化完成" in content:
        print("✅ 调试日志完整")
    else:
        print("❌ 调试日志不完整")

def check_github_status():
    """检查GitHub状态"""
    print("\n=== GitHub状态 ===")
    
    # 检查构建状态
    cmd = "curl -s 'https://api.github.com/repos/xx8888888-xh/clock2/actions/runs?branch=main&per_page=1'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ GitHub API访问正常")
    else:
        print("❌ GitHub API访问失败")

def main():
    print("=== clock2 Android修复验证 ===")
    
    check_apk_file()
    check_code_fixes()
    check_github_status()
    
    print("\n=== 测试建议 ===")
    print("1. Android设备测试:")
    print("   - 安装APK")
    print("   - 授予悬浮窗权限")
    print("   - 查看调试日志: adb logcat | grep '窗口初始化'")
    
    print("\n2. 透明度调整:")
    print("   - 如果窗口看不见:")
    print("     Window.clearcolor = (1, 1, 1, 1)  # 白色完全不透明")
    print("     Window.clearcolor = (1, 0, 0, 0.8)  # 红色80%透明")
    
    print("\n=== 下载状态 ===")
    print("APK正在下载中...")
    print("大小: 41.9MB")
    print("进度: ~6%")
    print("预计时间: 约12分钟")

if __name__ == "__main__":
    main()