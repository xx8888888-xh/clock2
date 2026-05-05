#!/bin/bash

# APK分析脚本

echo "=== APK分析 ==="

# 安装apktool
echo "安装apktool..."
apt-get update && apt-get install -y apktool || echo "无法安装apktool"

# 检查APK文件
echo "APK文件大小："
ls -lh *.apk

# 提取AndroidManifest.xml
echo "尝试提取AndroidManifest.xml..."
unzip -l petalarm-v3.0.4.apk | grep AndroidManifest.xml
unzip -l petalarm_v3.0.4.apk | grep AndroidManifest.xml

# 检查APK内容
echo "检查APK内容..."

# 大APK
echo "petalarm-v3.0.4.apk (42MB) 内容："
unzip -l petalarm-v3.0.4.apk | grep -E "\.so$|classes\.dex|resources\.arsc" | head -20

echo ""
echo "petalarm_v3.0.4.apk (6.5MB) 内容："
unzip -l petalarm_v3.0.4.apk | grep -E "\.so$|classes\.dex|resources\.arsc" | head -20

# 猜测：大APK可能是完整构建，小APK可能是debug版本
echo ""
echo "推测："
echo "- petalarm-v3.0.4.apk (42MB) → 完整构建，包含所有依赖"
echo "- petalarm_v3.0.4.apk (6.5MB) → debug版本，精简"

echo ""
echo "=== 测试建议 ==="
echo "1. 先测试小APK (6.5MB) → 精简版本"
echo "2. 如果小APK可用，再测试大APK (42MB) → 完整功能"
echo ""
echo "=== 构建分析 ==="
echo "GitHub Actions构建ID: 25297403421"
echo "构建状态: completed success"
echo "透明度修复: Alpha=0.5"
echo "APK下载: https://api.github.com/repos/xx8888888-xh/clock2/actions/artifacts/6775735572/zip"
echo ""
echo "=== 本地测试 ==="
echo "可以测试现有APK或使用buildozer重新构建："