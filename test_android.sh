#!/bin/bash

# Android悬浮窗一键测试脚本

echo "=== Android悬浮窗架构测试 ==="

# 检查当前main.py
if [ -f "main.py" ]; then
    echo "当前main.py存在"
else
    echo "❌ main.py不存在"
    exit 1
fi

# 备份原来的main.py
echo "备份原来的main.py..."
cp main.py main_backup.py

echo ""
echo "选择架构版本："
echo "1. 最简单架构（窗口创建测试）"
echo "2. 稳定架构（Android Service测试）"
echo "3. 完整架构（功能完整测试）"
echo ""

read -p "请输入选项 (1/2/3): " ARCHITECTURE

case $ARCHITECTURE in
    1)
        echo "使用最简单架构..."
        cp simplest_main.py main.py
        echo "✅ 已切换到最简单架构"
        ;;
    2)
        echo "使用稳定架构..."
        cp android_stable_main.py main.py
        echo "✅ 已切换到稳定架构"
        ;;
    3)
        echo "使用完整架构..."
        # 保持原来的main.py
        echo "✅ 使用完整架构"
        ;;
    *)
        echo "❌ 无效选项，使用默认架构"
        ;;
esac

echo ""
echo "使用Android专用buildozer配置..."
cp buildozer_android.spec buildozer.spec

echo ""
echo "开始构建APK..."
echo "注意：需要buildozer环境"

echo ""
echo "构建命令："
echo "buildozer android debug"

echo ""
echo "测试建议："
echo "1. 构建完成后安装APK到Android设备"
echo "2. 开启悬浮窗权限"
echo "3. 关闭电池优化"
echo "4. 查看日志：adb logcat | grep '宠物闹钟'"

echo ""
echo "架构文件说明："
echo "- simplest_main.py: 最简单架构，验证窗口创建"
echo "- android_stable_main.py: 稳定架构，Android Service支持"
echo "- android_fixed_main.py: 修复版本架构"
echo "- android_minimal_app.py: 最小化架构"
echo "- minimal_main.py: 最小化版本"
echo "- android_service_main.py: Android Service架构"
echo "- ultimate_fix_main.py: 最终修复版本"

echo ""
echo "当前选择的架构：$ARCHITECTURE"
echo "main.py已更新"
echo "buildozer.spec已更新"
echo ""

echo "=== 测试准备完成 ==="
echo "运行 buildozer android debug 开始构建"