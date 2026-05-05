#!/bin/bash
# 下载clock2仓库的所有文件

cd clock2

files=(
    "README.md"
    "buildozer.spec"
    "icon.png"
    "main.py"
    "pet.png"
    "requirements.txt"
    "resources.py"
)

echo "开始下载clock2仓库的所有文件..."

for file in "${files[@]}"
do
    echo "正在下载 $file..."
    curl -L "https://raw.githubusercontent.com/xx8888888-xh/clock2/main/$file" -o "$file"
done

echo "下载完成！"