# Android悬浮窗APK测试指南

## APK测试焦点

GitHub认证问题不影响测试。专注测试APK。

### **现有APK**
```bash
adb install petalarm-v3.0.4.apk
adb shell am start -n org.petalarm/.DesktopPetAlarmApp
adb logcat | grep "宠物闹钟"
```

### **Android权限**
1. 悬浮窗权限 → 允许
2. 后台运行 → 关闭电池优化
3. 前台服务 → 允许

## 透明度调试

### **APK透明度**
```python
Window.clearcolor = (0, 0, 0, 0.8)  # 80%透明
```

### **GitHub Actions透明度**
```python
Window.clearcolor = (0, 0, 0, 0.5)  # 50%透明
```

### **本地修复透明度**
```python
Config.set('graphics', 'background_color', '0,0,0,0.5')
Window.clearcolor = (0, 0, 0, 0.01)  # 几乎透明
```

## 调试策略

### **窗口看不见**
```python
Window.clearcolor = (0, 0, 0, 0.5)  # GitHub Actions
Window.clearcolor = (0, 0, 0, 0.1)  # 10%透明
Window.clearcolor = (0, 0, 0, 0.01)  # 几乎透明
Window.clearcolor = (1, 1, 1, 1)    # 完全不透明
```

### **闪退**
```python
Clock.schedule_once(lambda dt: self.safe_init_window(), 2)
Clock.schedule_once(lambda dt: self.safe_init_window(), 3)
```

### **Android Service无效**
```python
# 简化Android Service
Window.clearcolor = (0, 0, 0, 0.5)
Window.size = (300, 300)
Window.top = 150
Window.left = 100
```

## GitHub状态

GitHub认证失败不影响测试。

GitHub Actions构建ID: 25297403421
透明度修复: Alpha改为0.5
下载URL: https://api.github.com/repos/xx8888888-xh/clock2/actions/artifacts/6775735572/zip

## 测试结果记录

### **日志分析**
```
adb logcat | grep "宠物闹钟"
adb logcat | grep "Window"
adb logcat | grep "透明度"
adb logcat | grep "Android"
```

### **成功日志**
```
宠物闹钟: 初始化开始
宠物闹钟: Android检测: True
宠物闹钟: 窗口初始化完成
宠物闹钟: 透明度设置: (0, 0, 0, 0.8)
宠物闹钟: 窗口可见
宠物闹钟: Android Service: 初始化完成
```

### **失败日志**
```
宠物闹钟: 窗口初始化失败
宠物闹钟: Android权限未获取
宠物闹钟: 闪退原因: Window.clearcolor = (0, 0, 0, 0)
宠物闹钟: Android Service启动失败
```

## 立即测试

### **测试现有APK**
```bash
adb install petalarm-v3.0.4.apk
adb shell am start -n org.petalarm/.DesktopPetAlarmApp
adb logcat | grep "宠物闹钟"
```

### **提供测试结果**
1. ✅ 安装是否成功
2. ✅ 应用启动是否成功
3. ✅ 窗口是否可见
4. ✅ 宠物是否显示
5. ✅ 日志内容

GitHub认证问题不影响APK测试。专注测试现有APK。