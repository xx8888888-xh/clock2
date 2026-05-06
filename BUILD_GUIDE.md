# Clock2 Android APK 构建指南

由于GitHub Actions构建环境复杂，建议使用以下方法之一：

## 方法一：在本地计算机构建

### 1. 安装Buildozer
```bash
pip install buildozer cython
```

### 2. 安装Android依赖
```bash
# Linux
sudo apt-get update
sudo apt-get install -y \
    python3-pip python3-dev python3-venv \
    git zip unzip openjdk-17-jdk-headless \
    build-essential ccache libffi-dev libssl-dev \
    libxml2-dev libxslt1-dev libncurses5-dev \
    libgdbm-dev libreadline-dev libz-dev \
    libbz2-dev libsqlite3-dev libffi-dev zlib1g-dev

# macOS
brew install python3 git java ccache
```

### 3. 构建APK
```bash
cd /path/to/clock2
buildozer android debug
```

### 4. 下载APK
构建完成后，APK文件位于：`./bin/clock2-1.0.0-debug.apk`

## 方法二：使用Google Colab在线构建

### 步骤
1. 打开 [Google Colab](https://colab.research.google.com/)
2. 上传 `/tmp/clock2_original/build_with_colab.ipynb` 文件
3. 按步骤运行

## 方法三：手动创建APK签名文件

### 1. 下载预构建的APK
如果GitHub Actions成功，可在以下链接下载：
- https://github.com/xx8888888-xh/clock2/actions

### 2. 手动安装
下载APK后，通过USB传输到Android设备安装

## 已经尝试的方案

### GitHub Actions尝试了：
1. **Build Android APK (All Methods)** - 失败
2. **Build Kivy APK** - 失败
3. **Flutter APK Build** - 失败
4. **Build Android APK with Docker** - 失败

### 可用分支
1. **main** - 最简单的Kivy版本
2. **kivy-simple** - 纯Kivy版本
3. **flutter-rewrite** - Flutter版本
4. **react-native-rewrite** - React Native版本

## 建议

**建议使用Flutter方案**：
- Flutter的Android支持更好
- GitHub Actions构建Flutter成功率更高
- 悬浮窗功能更容易实现

**下一步**：
1. 尝试本地构建
2. 如果本地构建成功，可以创建一个Release
3. 测试Android设备的悬浮窗权限