# 宠物闹钟 - Android悬浮窗架构大改

## 问题描述
Android悬浮窗应用闪退，显示loading图标后退出，窗口看不见。

## 解决方案
针对Android悬浮窗bug，我们创建了多个架构版本进行测试：

### 1. 最简单架构 (`simplest_main.py`)
- **特点**：最简化的窗口创建
- **适用场景**：验证窗口创建是否成功
- **代码复杂度**：⭐☆☆☆☆

### 2. 稳定架构 (`android_stable_main.py`)
- **特点**：Android Service + 渐进式初始化
- **适用场景**：Android兼容性测试
- **代码复杂度**：⭐⭐⭐☆☆

### 3. 完整架构 (`main.py`)
- **特点**：原功能完整版本
- **适用场景**：功能完整应用
- **代码复杂度**：⭐⭐⭐⭐⭐

## 架构选择指南

### 测试顺序建议：
1. **最简单架构** → 验证窗口创建
2. **稳定架构** → 验证Android Service
3. **完整架构** → 验证完整功能

### 一键测试脚本：
```bash
chmod +x test_android.sh
./test_android.sh
```

## 核心修复点

### 1. 透明度问题
```python
# ❌ 错误：完全透明，窗口看不见
Window.clearcolor = (0, 0, 0, 0)

# ✅ 正确：几乎透明，窗口可见
Window.clearcolor = (0, 0, 0, 0.01)
```

### 2. Android权限时序
```python
# ❌ 错误：build方法中立即初始化窗口
def build(self):
    Window.clearcolor = (0, 0, 0, 0)  # 错误

# ✅ 正确：延迟初始化
def build(self):
    Clock.schedule_once(lambda dt: self.init_window_safe(), 0.5)  # 延迟
```

### 3. Service架构支持
Android悬浮窗需要前台服务支持：
```python
android.permissions = INTERNET, VIBRATE, SYSTEM_ALERT_WINDOW, WAKE_LOCK, FOREGROUND_SERVICE, RECEIVE_BOOT_COMPLETED
android.manifest_placeholders = [foregroundServiceType: "dataSync"]
```

## GitHub Actions自动化构建
`.github/workflows/android-builds.yml` 会自动构建三个架构版本：
1. 简单架构
2. 稳定架构
3. 完整架构

## 调试指南
查看详细调试指南：[android_debug_guide.md](./android_debug_guide.md)

## 架构分析
查看架构分析：[android_architecture_test.py](./android_architecture_test.py)

## APK测试
查看APK测试：[test_apk.py](./test_apk.py)

## 使用步骤

### 1. 选择架构
```bash
# 使用最简单架构
cp simplest_main.py main.py

# 使用稳定架构
cp android_stable_main.py main.py

# 使用完整架构
# 保持main.py原样
```

### 2. 配置Android
```bash
cp buildozer_android.spec buildozer.spec
```

### 3. 构建APK
```bash
buildozer android debug
```

### 4. 安装测试
```bash
adb install bin/petalarm-3.0.0-debug.apk
```

## Android权限设置
1. **悬浮窗权限**：必须在Android设置中手动开启
2. **后台运行**：关闭电池优化
3. **前台服务**：允许应用前台运行

## 日志查看
```bash
adb logcat | grep "宠物闹钟"
adb logcat | grep "Window"
adb logcat | grep "Android"
```

## 许可证
MIT License