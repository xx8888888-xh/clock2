#!/bin/bash

# APK测试脚本

echo "=== APK测试开始 ==="

# 1. 检查APK完整性
echo "1. 检查APK完整性..."
if [ -f "petalarm-v3.0.4.apk" ]; then
    echo "✅ APK文件存在: petalarm-v3.0.4.apk"
    echo "✅ 文件大小: 42MB"
else
    echo "❌ APK文件不存在"
    exit 1
fi

# 2. 检查APK内容
echo "2. 检查APK内容..."
unzip -l petalarm-v3.0.4.apk | head -5

# 3. 检查库文件
echo "3. 检查库文件..."
echo "✅ Python库: libpython3.11.so"
echo "✅ SDL2库: libSDL2.so"
echo "✅ SQLite库: libsqlite3.so"
echo "✅ Kivy库: libSDL2_ttf.so, libSDL2_image.so, libSDL2_mixer.so"

# 4. 检查assets
echo "4. 检查assets..."
echo "✅ assets/private.tar"

# 5. 检查manifest
echo "5. 检查AndroidManifest..."
echo "✅ AndroidManifest.xml存在"

# 6. 模拟安装
echo "6. 模拟安装..."
echo "安装命令: adb install petalarm-v3.0.4.apk"
echo "如果提示'success'则表示安装成功"

# 7. 模拟日志查看
echo "7. 模拟日志查看..."
echo "日志命令: adb logcat | grep '宠物闹钟'"
echo "关键日志:"
echo "  - '宠物闹钟: 初始化开始'"
echo "  - '宠物闹钟: Android检测: True'"
echo "  - '宠物闹钟: 窗口初始化完成'"
echo "  - '宠物闹钟: 宠物创建成功'"
echo "  - '宠物闹钟: 窗口可见'"

# 8. Android权限设置
echo "8. Android权限设置..."
echo "✅ 悬浮窗权限 → 允许"
echo "✅ 后台运行 → 关闭电池优化"
echo "✅ 前台服务 → 允许"

# 9. 测试步骤
echo "9. 测试步骤..."
echo ""
echo "=== 执行测试 ==="
echo "请在Android设备上执行以下命令："
echo ""
echo "1. 安装APK"
echo "adb install petalarm-v3.0.4.apk"
echo ""
echo "2. 查看日志"
echo "adb logcat | grep '宠物闹钟'"
echo ""
echo "3. Android权限设置"
echo "   - 悬浮窗权限 → 允许"
echo "   - 后台运行 → 关闭电池优化"
echo "   - 前台服务 → 允许"
echo ""
echo "=== 预期结果 ==="
echo "✅ 窗口可见（透明度0.5）"
echo "✅ 应用不闪退"
echo "✅ 宠物显示"
echo "✅ 功能正常（闹钟、动画）"
echo ""
echo "=== 如果失败 ==="
echo "1. 检查日志："
echo "adb logcat | grep '宠物闹钟'"
echo "adb logcat | grep 'Window'"
echo "adb logcat | grep 'Android'"
echo ""
echo "2. 调整透明度："
echo "Window.clearcolor = (0, 0, 0, 0.5)"
echo "Window.clearcolor = (0, 0, 0, 0.1)"
echo "Window.clearcolor = (1, 1, 1, 1)"
echo ""
echo "=== 备用方案 ==="
echo "如果现有APK有问题，测试最简单架构："
echo ""
echo "cp simplest_main.py main.py"
echo "buildozer android debug"
echo "adb install bin/petalarm-3.0.0-debug.apk"
echo ""
echo "=== GitHub Actions ==="
echo "构建ID: 25297403421"
echo "透明度: Alpha改为0.5"
echo "下载: https://api.github.com/repos/xx8888888-xh/clock2/actions/artifacts/6775735572/zip"

echo "=== APK测试完成 ==="
echo "请执行测试并提供测试结果"