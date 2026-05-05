#!/bin/bash

# 完整架构测试脚本
echo "=== 完整架构测试 ==="

# 备份原来的main.py
if [ -f "main.py" ]; then
    cp main.py main_backup.py
    echo "✅ 备份原来的main.py"
fi

# 选择测试架构
echo ""
echo "选择架构版本："
echo "1. 修复版架构 (main_fixed.py)"
echo "2. 最简单架构 (simplest_main.py)"
echo "3. 稳定架构 (android_stable_main.py)"
echo "4. 完整架构 (main.py)"
echo ""

read -p "请输入选项 (1/2/3/4): " CHOICE

case $CHOICE in
    1)
        echo "使用修复版架构..."
        cp main_fixed.py main.py
        echo "✅ 已切换到修复版架构"
        ;;
    2)
        echo "使用最简单架构..."
        cp simplest_main.py main.py
        echo "✅ 已切换到最简单架构"
        ;;
    3)
        echo "使用稳定架构..."
        cp android_stable_main.py main.py
        echo "✅ 已切换到稳定架构"
        ;;
    4)
        echo "使用完整架构..."
        # 保持原来的main.py
        echo "✅ 使用完整架构"
        ;;
    *)
        echo "❌ 无效选项，使用修复版架构"
        cp main_fixed.py main.py
        ;;
esac

# 测试Android配置
echo ""
echo "=== 测试Android配置 ==="

# 检查main.py
echo "检查main.py中的Window.clearcolor设置:"
grep "Window.clearcolor" main.py | head -5

# 检查buildozer.spec
echo ""
echo "检查buildozer.spec配置:"
cp buildozer_android.spec buildozer.spec
echo "android.permissions:"
grep "android.permissions" buildozer.spec
echo "android.api:"
grep "android.api" buildozer.spec
echo "android.manifest_placeholders:"
grep "android.manifest_placeholders" buildozer.spec

# 检查Android兼容性
echo ""
echo "=== Android兼容性检查 ==="

# 检查Android权限请求
echo "检查Android权限请求代码:"
grep -n "request_permissions\|Permission\|android" main.py | head -10

# 检查延迟初始化
echo "检查延迟初始化代码:"
grep -n "Clock.schedule_once\|init_window" main.py | head -10

# 检查透明度设置
echo "检查透明度设置:"
grep -n "clearcolor\|opacity" main.py | head -10

# 构建测试
echo ""
echo "=== 构建测试 ==="
echo "可以运行以下命令测试构建:"
echo ""
echo "1. 构建APK:"
echo "   buildozer android debug"
echo ""
echo "2. 安装APK:"
echo "   adb install bin/petalarm-3.0.0-debug.apk"
echo ""
echo "3. 查看日志:"
echo "   adb logcat | grep '宠物闹钟'"
echo "   adb logcat | grep 'Window'"
echo "   adb logcat | grep 'Android'"

# 架构分析
echo ""
echo "=== 架构分析 ==="
echo "运行架构分析:"
echo "python3 android_architecture_test.py"

# 创建测试报告
echo ""
echo "=== 创建测试报告 ==="
echo "架构: $CHOICE"
echo "main.py: $(basename $(ls -l main.py))"
echo ""
echo "修复点:"
echo "1. Window.clearcolor = (0, 0, 0, 0.01)  # 几乎透明"
echo "2. Clock.schedule_once(lambda dt: self.init_window(), 0.5)  # 延迟初始化"
echo "3. Android权限请求"
echo "4. Android Service支持"
echo ""
echo "测试建议:"
echo "1. 先测试修复版架构 (main_fixed.py)"
echo "2. 如果修复版成功，测试完整架构 (main.py)"
echo "3. 如果修复版失败，测试最简单架构 (simplest_main.py)"
echo ""
echo "=== 测试完成 ==="

# 保存测试配置
echo ""
echo "当前配置已保存到: main.py"
echo "可以使用以下命令构建:"
echo "buildozer android debug"