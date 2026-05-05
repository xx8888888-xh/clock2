# Android模拟器安装指南

## 方案选择

### **方案1: Android SDK命令行工具**
```bash
# 安装Android SDK
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
unzip commandlinetools-linux-9477386_latest.zip
export ANDROID_HOME=~/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/bin

# 安装Android Emulator
sdkmanager "platforms;android-33" "system-images;android-33;google_apis;arm64-v8a" "emulator"

# 创建Android模拟器
avdmanager create avd -n android33 -k "system-images;android-33;google_apis;arm64-v8a"

# 启动模拟器
emulator -avd android33
```

### **方案2: Android Studio**
```bash
# 下载Android Studio
wget https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2023.3.1/android-studio-2023.3.1-linux.tar.gz
tar -xzf android-studio-2023.3.1-linux.tar.gz
cd android-studio/bin
./studio.sh
```

### **方案3: 使用现有APK测试**
```bash
# 如果无法安装Android模拟器，可以使用现有APK进行静态分析

# 检查APK中的Python代码
apktool d petalarm-v3.0.4.apk -o apk_analysis
```

## 实际测试APK

### **第1步: 安装Android模拟器**
```bash
# 下载Android SDK命令行工具
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
unzip commandlinetools-linux-9477386_latest.zip
export ANDROID_HOME=/home/user/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/bin

# 安装必要组件
sdkmanager --list
sdkmanager "platforms;android-33"
sdkmanager "system-images;android-33;google_apis;arm64-v8a"
sdkmanager "emulator"

# 创建模拟器
avdmanager create avd -n android33 -k "system-images;android-33;google_apis;arm64-v8a"

# 启动模拟器
emulator -avd android33
```

### **第2步: 连接模拟器**
```bash
# 等待模拟器启动
# 检查adb设备
adb devices

# 如果模拟器启动，会出现设备列表
# List of devices attached
# emulator-5554 device
```

### **第3步: 安装APK**
```bash
adb install petalarm-v3.0.4.apk
```

### **第4步: 启动应用**
```bash
adb shell am start -n org.petalarm/.DesktopPetAlarmApp
```

### **第5步: 查看日志**
```bash
adb logcat | grep "宠物闹钟"
adb logcat | grep "Window"
adb logcat | grep "Android"
adb logcat | grep "Kivy"
```

## 如果没有Android模拟器

### **静态分析APK**
```bash
# 反编译APK
apktool d petalarm-v3.0.4.apk -o apk_analysis

# 查看资源文件
ls -la apk_analysis/

# 查看smali代码
find apk_analysis/smali/ -name "*.smali" | head -20

# 查看Python代码
find apk_analysis/assets/ -name "*.py" | head -20
```

### **提取Python代码**
```bash
# 提取private.tar
unzip -p petalarm-v3.0.4.apk assets/private.tar > private.tar
tar -xf private.tar

# 查看Python文件
find . -name "*.py" | head -20
```

## APK中的关键修复验证

### **GitHub Actions构建**
```python
# GitHub Actions构建ID: 25297403421
# 透明度修复: Alpha改为0.5
# 下载URL: https://api.github.com/repos/xx8888888-xh/clock2/actions/artifacts/6775735572/zip
```

### **代码修复**
```python
# 透明度修复
Config.set('graphics', 'background_color', '0,0,0,0.5')
Window.clearcolor = (0, 0, 0, 0.01)

# 延迟初始化
Clock.schedule_once(lambda dt: self.safe_init_window(), 1)

# Android Service
class AndroidWindowService:
    def init_window_safe(self):
        Window.clearcolor = (0, 0, 0, 0.01)
        Window.size = (300, 300)
        Window.top = 150
        Window.left = 100
```

## 测试结果分析

### **成功情况**
```
宠物闹钟: Android检测: True
宠物闹钟: 窗口初始化完成
宠物闹钟: 透明度设置: (0, 0, 0, 0.5)
宠物闹钟: 窗口可见
宠物闹钟: Android Service: 初始化完成
```

### **失败情况**
```
宠物闹钟: 窗口初始化失败
宠物闹钟: Android权限未获取
宠物闹钟: 闪退原因: Window.clearcolor = (0, 0, 0, 0)
宠物闹钟: Android Service启动失败
```

## 调试策略

### **如果窗口看不见**
```python
# 调整透明度
Window.clearcolor = (0, 0, 0, 0.5)  # GitHub Actions构建
Window.clearcolor = (0, 0, 0, 0.1)  # 10%透明
Window.clearcolor = (1, 1, 1, 1)    # 完全不透明
```

### **如果闪退**
```python
# 增加延迟时间
Clock.schedule_once(lambda dt: self.safe_init_window(), 2)
Clock.schedule_once(lambda dt: self.safe_init_window(), 3)
```

### **如果Android Service无效**
```python
# 简化Android Service
Window.clearcolor = (0, 0, 0, 0.01)
Window.size = (300, 300)
Window.top = 150
Window.left = 100
```

## 安装Android SDK的可能问题

### **可能遇到的困难**
1. **网络问题**: Android SDK下载需要网络
2. **系统兼容性**: 需要Java环境
3. **空间需求**: Android SDK占用较大空间
4. **权限问题**: 需要安装权限

### **替代方案**
1. **使用现有APK**: 在真实Android设备上测试
2. **使用buildozer**: 重新构建APK测试
3. **静态分析**: 分析APK内容而不运行

## 当前代码状态

### **已完成修复**
✅ **透明度修复**: Config.set('graphics', 'background_color', '0,0,0,0.5')
✅ **延迟初始化**: Clock.schedule_once(lambda dt: self.safe_init_window(), 1)
✅ **Android Service**: AndroidWindowService类
✅ **Android权限**: SYSTEM_ALERT_WINDOW权限

### **需要测试**
❌ **窗口可见性**: 透明度0.5是否有效
❌ **应用稳定性**: 延迟初始化是否解决闪退
❌ **Android Service**: Android Service是否有效
❌ **整体功能**: 宠物是否显示，闹钟是否正常

## 下一步行动

### **立即行动**
```bash
# 尝试安装Android SDK模拟器
# 或使用真实Android设备测试

# 测试指令
adb install petalarm-v3.0.4.apk
adb shell am start -n org.petalarm/.DesktopPetAlarmApp
adb logcat | grep "宠物闹钟"
```

### **提供测试结果**
我需要以下信息：
1. ✅ 安装是否成功
2. ✅ 应用启动是否成功
3. ✅ 窗口是否可见
4. ✅ 宠物是否显示
5. ✅ 日志内容

### **根据测试结果调整**
我会根据测试结果调整代码并重新构建APK。