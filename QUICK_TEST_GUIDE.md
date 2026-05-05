# 快速测试指南

## 核心问题修复

### ✅ 已修复的问题
1. **透明度**: Window.clearcolor = (0, 0, 0, 0.01) 改为 (0, 0, 0, 0.5)
2. **延迟初始化**: Clock.schedule_once(lambda dt: self.init_pet_and_banner(), 0.5)
3. **Android Service**: AndroidWindowService类
4. **Android权限**: SYSTEM_ALERT_WINDOW权限

### ✅ GitHub Actions构建
- **构建ID**: 25297403421
- **透明度**: Alpha改为0.5（50%透明）
- **下载**: https://api.github.com/repos/xx8888888-xh/clock2/actions/artifacts/6775735572/zip

## 测试方案

### 方案1: 测试现有APK (快速)
```bash
# 安装现有APK
adb install petalarm-v3.0.4.apk

# 查看日志
adb logcat | grep "宠物闹钟"
adb logcat | grep "Window"
adb logcat | grep "Android"

# Android权限设置
# 1. 悬浮窗权限 → 允许
# 2. 后台运行 → 关闭电池优化
# 3. 前台服务 → 允许
```

### 方案2: 本地构建最简单架构
```bash
# 选择最简单架构
cp simplest_main.py main.py
cp buildozer_android.spec buildozer.spec

# 如果本地有buildozer环境，可以构建
buildozer android debug

# 安装测试
adb install bin/petalarm-3.0.0-debug.apk
```

### 方案3: 手动下载GitHub Actions APK
1. 访问 https://github.com/xx8888888-xh/clock2/actions/runs/25297403421
2. 下载clock2-apk artifact
3. 安装测试

## 架构版本选择

### 最简单架构 (simplest_main.py)
```bash
cp simplest_main.py main.py
```

**特点**:
- 最简化的窗口创建
- 透明度: Window.clearcolor = (0, 0, 0, 0.01)
- 延迟初始化: Clock.schedule_once(lambda dt: self.safe_init_window(), 1)
- 目的: 验证窗口是否可见

### 完整架构修复版 (main.py)
```bash
# main.py已修复完毕
```

**特点**:
- 透明度修复: Window.clearcolor = (0, 0, 0, 0.01)
- 延迟初始化: Clock.schedule_once(lambda dt: self.init_pet_and_banner(), 0.5)
- Android Service: AndroidWindowService类
- Android权限请求: SYSTEM_ALERT_WINDOW

## 关键日志信息

### 成功日志
```
宠物闹钟: 初始化开始
宠物闹钟: Android检测: True
宠物闹钟: 窗口初始化完成
宠物闹钟: 宠物创建成功
宠物闹钟: 窗口可见
```

### 失败日志
```
宠物闹钟: 窗口初始化失败
宠物闹钟: Android权限未获取
宠物闹钟: 闪退原因: Window.clearcolor = (0, 0, 0, 0)
宠物闹钟: 应用退出
```

## Android权限设置

**必须在Android设备上手动设置**:
1. **悬浮窗权限** → 允许
2. **后台运行** → 关闭电池优化
3. **前台服务** → 允许

## 测试结果分析

### 如果窗口看不见
```python
# 调整透明度
Window.clearcolor = (0, 0, 0, 0.5)  # 改为50%透明
Window.clearcolor = (0, 0, 0, 0.1)  # 改为10%透明
Window.clearcolor = (1, 1, 1, 1)    # 改为完全不透明
```

### 如果闪退
```python
# 增加延迟时间
Clock.schedule_once(lambda dt: self.init_window_safe(), 2)  # 改为2秒延迟
```

### 如果Android Service无效
```python
# 简化Android Service
def init_window_safe():
    Window.clearcolor = (0, 0, 0, 0.01)
    Window.size = (280, 280)
    Window.top = 180
    Window.left = 60
```

## GitHub Actions下载指南

### 手动下载
1. 访问 https://github.com/xx8888888-xh/clock2
2. Actions页面
3. 找到构建25297403421
4. 下载clock2-apk artifact

### APK内容
- **透明度**: Alpha改为0.5（50%透明）
- **浅灰色背景**: 更容易看到窗口
- **窗口位置调整**: 更好的Android兼容性

## 下一步行动

### 立即测试
```bash
# 测试现有APK
adb install petalarm-v3.0.4.apk
```

### 根据结果调整
1. **窗口看不见** → 调整透明度
2. **闪退** → 增加延迟时间
3. **Android Service无效** → 简化Service

### 反馈测试结果
请告诉我：
1. **窗口是否可见**
2. **应用是否闪退**
3. **宠物是否显示**
4. **日志内容**

我会根据测试结果进一步调整架构。