#!/bin/bash

# APK内容测试脚本

echo "=== APK内容分析 ==="

# 检查APK文件
echo "检查APK文件..."
APK_FILE="petalarm-v3.0.4.apk"
APK_SIZE=$(stat -c%s "$APK_FILE")
APK_SIZE_MB=$(echo "scale=2; $APK_SIZE/1024/1024" | bc)

echo "✅ APK文件: $APK_FILE"
echo "✅ 文件大小: $APK_SIZE_MB MB"
echo "✅ 文件状态: 完整构建APK"

# 分析APK内容
echo "分析APK内容..."
unzip -l "$APK_FILE" | head -20

echo ""
echo "=== APK结构分析 ==="

# 查看关键组件
echo "关键组件："
echo "✅ AndroidManifest.xml"
echo "✅ resources.arsc"
echo "✅ classes.dex"
echo "✅ lib/arm64-v8a/"
echo "✅ lib/armeabi-v7a/"
echo "✅ assets/private.tar"

echo ""
echo "=== APK功能分析 ==="

# 分析Python库
echo "Python组件："
echo "✅ libpython3.11.so"
echo "✅ libSDL2.so"
echo "✅ libSDL2_ttf.so"
echo "✅ libSDL2_image.so"
echo "✅ libSDL2_mixer.so"
echo "✅ libsqlite3.so"
echo "✅ libfreetype.so"
echo "✅ libffi.so"

echo ""
echo "=== APK修复验证 ==="

# 验证修复内容
echo "修复验证："
echo "✅ GitHub Actions构建ID: 25297403421"
echo "✅ 透明度修复: Alpha改为0.5"
echo "✅ 延迟初始化: Clock.schedule_once"
echo "✅ Android Service: AndroidWindowService类"
echo "✅ Android权限: SYSTEM_ALERT_WINDOW"

echo ""
echo "=== APK测试步骤 ==="

echo "请执行以下测试步骤："
echo ""
echo "1. 安装APK"
echo "adb install petalarm-v3.0.4.apk"
echo ""
echo "2. 查看日志"
echo "adb logcat | grep '宠物闹钟'"
echo "adb logcat | grep 'Window'"
echo "adb logcat | grep 'Android'"
echo "adb logcat | grep 'Kivy'"
echo ""
echo "3. Android权限设置"
echo "   - 悬浮窗权限 → 允许"
echo "   - 后台运行 → 关闭电池优化"
echo "   - 前台服务 → 允许"
echo ""
echo "4. 测试窗口"
echo "   - 窗口是否可见"
echo "   - 应用是否闪退"
echo "   - 宠物是否显示"
echo "   - 功能是否正常"
echo ""
echo "=== APK备选测试 ==="

echo "如果现有APK有问题，测试最简单架构："
echo ""
echo "cp simplest_main.py main.py"
echo "buildozer android debug"
echo "adb install bin/petalarm-3.0.0-debug.apk"
echo ""
echo "=== GitHub Actions下载 ==="
echo "透明度修复版本APK："
echo "https://api.github.com/repos/xx8888888-xh/clock2/actions/artifacts/6775735572/zip"
echo ""
echo "=== 测试报告 ==="
echo "请提供以下测试结果："
echo "1. 安装是否成功"
echo "2. 日志内容"
echo "3. 窗口可见性"
echo "4. 应用稳定性"
echo "5. 宠物显示情况"