# Android悬浮窗APK真实测试流程

## 测试环境准备

### **前提条件**
1. Android设备连接
2. adb工具可用
3. Android设备已开启开发者模式
4. Android设备已开启USB调试

### **APK文件状态**
✅ **APK文件**: petalarm-v3.0.4.apk (42MB)
✅ **APK格式**: 已验证正确
✅ **APK内容**: Python库、SDL库等

## 真实测试步骤

### **第1步：安装APK**
```bash
adb install petalarm-v3.0.4.apk
```

### **第2步：启动应用**
```bash
adb shell am start -n org.petalarm/.DesktopPetAlarmApp
```

### **第3步：查看日志**
```bash
adb logcat | grep "宠物闹钟"
adb logcat | grep "Window"
adb logcat | grep "Android"
adb logcat | grep "Kivy"
adb logcat | grep "init"
adb logcat | grep "build"
```

### **第4步：Android权限设置**
1. **悬浮窗权限**: 允许应用显示悬浮窗
2. **后台运行**: 关闭电池优化
3. **前台服务**: 允许前台服务

## 预期测试结果

### **成功情况**
✅ 安装成功
✅ 应用启动成功
✅ 窗口可见
✅ 宠物显示
✅ 应用不闪退
✅ 功能正常

### **失败情况**
❌ 安装失败
❌ 应用闪退
❌ 窗口看不见
❌ 宠物不显示

## 测试指令详细说明

### **安装APK**
```bash
# 安装APK
adb install petalarm-v3.0.4.apk

# 安装成功后查看应用包名
adb shell pm list packages | grep petalarm
```

### **启动应用**
```bash
# 启动应用
adb shell am start -n org.petalarm/.DesktopPetAlarmApp

# 或者使用启动器
adb shell am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n org.petalarm/.DesktopPetAlarmApp
```

### **查看应用进程**
```bash
# 查看应用进程
adb shell ps | grep petalarm

# 查看应用活动
adb shell dumpsys activity | grep org.petalarm
```

## 关键日志信息

### **成功日志**
```
宠物闹钟: 初始化开始
宠物闹钟: Android检测: True
宠物闹钟: 窗口初始化完成
宠物闹钟: 宠物创建成功
宠物闹钟: 窗口可见
宠物闹钟: 透明度设置: (0, 0, 0, 0.5)
宠物闹钟: 延迟初始化完成
```

### **失败日志**
```
宠物闹钟: 窗口初始化失败
宠物闹钟: Android权限未获取
宠物闹钟: 闪退原因: Window.clearcolor = (0, 0, 0, 0)
宠物闹钟: 应用退出
宠物闹钟: 权限错误: SYSTEM_ALERT_WINDOW
宠物闹钟: Android Service启动失败
```

## 调试策略

### **如果窗口看不见**
```python
# 调整透明度
Window.clearcolor = (0, 0, 0, 0.1)  # 10%透明
Window.clearcolor = (0, 0, 0, 0.2)  # 20%透明
Window.clearcolor = (0, 0, 0, 0.3)  # 30%透明
Window.clearcolor = (1, 1, 1, 1)    # 完全不透明
```

### **如果闪退**
```python
# 增加延迟时间
Clock.schedule_once(lambda dt: self.init_pet_and_banner(), 1)  # 1秒延迟
Clock.schedule_once(lambda dt: self.init_pet_and_banner(), 2)  # 2秒延迟
Clock.schedule_once(lambda dt: self.init_pet_and_banner(), 3)  # 3秒延迟
```

### **如果Android Service无效**
```python
# 简化Android Service
def init_window_simple():
    Window.clearcolor = (0, 0, 0, 0.5)
    Window.size = (280, 280)
    Window.top = 180
    Window.left = 60
```

## 备选方案

### **测试最简单架构**
```bash
# 使用最简单架构
cp simplest_main.py main.py
cp buildozer_android.spec buildozer.spec

# 重新构建
buildozer android debug

# 测试
adb install bin/petalarm-3.0.0-debug.apk
```

### **测试修复版架构**
```bash
# 使用修复版架构
cp main_fixed.py main.py
cp buildozer_android.spec buildozer.spec

# 重新构建
buildozer android debug

# 测试
adb install bin/petalarm-3.0.0-debug.apk
```

### **GitHub Actions APK**
```bash
# 下载GitHub Actions APK
# 透明度已修复为0.5
# 下载URL: https://api.github.com/repos/xx8888888-xh/clock2/actions/artifacts/6775735572/zip
```

## 测试结果记录

### **测试结果模板**
```bash
# 测试结果
✅ 安装成功
✅ 应用启动成功
✅ 窗口可见（透明度: 0.5）
✅ 宠物显示
✅ 应用稳定运行
✅ 功能正常
```

### **日志记录**
```bash
# 保存日志
adb logcat | grep "宠物闹钟" > petalarm_log.txt
adb logcat | grep "Window" > window_log.txt
adb logcat | grep "Android" > android_log.txt
```

## 立即执行

### **执行测试**
```bash
# 第1步
adb install petalarm-v3.0.4.apk

# 第2步
adb shell am start -n org.petalarm/.DesktopPetAlarmApp

# 第3步
adb logcat | grep "宠物闹钟"
```

### **提供测试结果**
1. ✅ 安装是否成功
2. ✅ 应用启动是否成功
3. ✅ 窗口是否可见
4. ✅ 宠物是否显示
5. ✅ 日志内容

根据测试结果，我会调整架构、透明度、延迟时间等参数。