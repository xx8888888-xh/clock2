# Android APK测试指南

## APK文件信息

### 1. petalarm-v3.0.4.apk (42MB)
- **状态**: 完整构建APK
- **内容**: 包含SDL2库、Python3.11库、SQLite3库等
- **架构**: arm64-v8a和armeabi-v7a双架构
- **特点**: GitHub Actions构建的完整版本

### 2. petalarm_v3.0.4.apk (6.5MB)
- **状态**: 损坏或不完整APK
- **问题**: zip格式错误，无法解压
- **推测**: 可能是损坏的构建或下载不完整

## GitHub Actions构建状态

✅ **构建ID**: 25297403421
✅ **状态**: completed success
✅ **透明度修复**: Alpha改为0.5（50%透明）
✅ **下载**: https://api.github.com/repos/xx8888888-xh/clock2/actions/artifacts/6775735572/zip

## 修复内容验证

### ✅ 透明度修复
```python
# GitHub Actions构建已修复
Window.clearcolor = (0, 0, 0, 0.5)  # 50%透明
```

### ✅ 延迟初始化
```python
Clock.schedule_once(lambda dt: self.init_pet_and_banner(), 0.5)
```

### ✅ Android Service
```python
class AndroidWindowService:
    def init_window_safe(self):
        Clock.schedule_once(lambda dt: self.init_window_stage1(), 0.5)
        Clock.schedule_once(lambda dt: self.init_window_stage2(), 1.0)
        Clock.schedule_once(lambda dt: self.init_window_stage3(), 1.5)
```

### ✅ Android权限
```python
android.permissions = INTERNET, VIBRATE, SYSTEM_ALERT_WINDOW, WAKE_LOCK, FOREGROUND_SERVICE, RECEIVE_BOOT_COMPLETED
```

## 实际测试步骤

### 第1步: 安装APK
```bash
adb install petalarm-v3.0.4.apk
```

### 第2步: 查看日志
```bash
adb logcat | grep "宠物闹钟"
```

### 第3步: Android权限设置
1. **悬浮窗权限** → 允许
2. **后台运行** → 关闭电池优化
3. **前台服务** → 允许

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

## 备选测试方案

### 如果现有APK有问题
```bash
# 测试最简单架构
cp simplest_main.py main.py
cp buildozer_android.spec buildozer.spec
buildozer android debug
adb install bin/petalarm-3.0.0-debug.apk
```

### 最简单架构特点
```python
# 透明度
Window.clearcolor = (0, 0, 0, 0.01)

# 延迟初始化
Clock.schedule_once(lambda dt: self.safe_init_window(), 1)

# 窗口设置
Window.size = (300, 300)
Window.top = 150
Window.left = 100

# 宠物创建
Clock.schedule_once(lambda dt: self.create_pet(), 1)
```

## GitHub Actions透明度修复

GitHub Actions构建已将透明度修复为0.5：
```python
# buildozer.spec中的透明度设置
Config.set('graphics', 'background_color', '0,0,0,0.5')
```

## 测试期望结果

### ✅ 窗口可见性
- 透明度0.5 → 窗口可见
- 浅灰色背景 → 更容易看到窗口
- 窗口位置 → Window.top = 150, Window.left = 100

### ✅ 应用稳定性
- 不闪退 → 延迟初始化
- 不退出 → Android Service支持
- 稳定运行 → Android权限获取

### ✅ 功能正常
- 宠物显示 → 窗口内宠物可见
- 闹钟功能 → 定时提醒正常
- 宠物动画 → 浮动动画正常

## 立即测试

```bash
# 安装APK
adb install petalarm-v3.0.4.apk

# 查看日志
adb logcat | grep "宠物闹钟"

# Android权限设置
# 1. 悬浮窗权限 → 允许
# 2. 后台运行 → 关闭电池优化
# 3. 前台服务 → 允许
```

## 测试结果反馈

请提供：
1. ✅ 安装是否成功
2. ✅ 日志内容
3. ✅ 窗口可见性
4. ✅ 应用稳定性
5. ✅ 宠物显示情况

根据测试结果，我会进一步调整：
1. ✅ 透明度调整
2. ✅ 延迟时间调整
3. ✅ Android Service调整
4. ✅ 架构优化