# Android悬浮窗调试指南

## 当前问题
- Android应用闪退，显示loading图标后退出
- 窗口可能看不见（透明度设置问题）
- Android权限时序问题

## 调试步骤

### 1. 测试APK
首先测试已有的APK：

```bash
# 检查APK文件
ls -la *.apk

# 分析APK结构
python3 test_apk.py
```

### 2. 修改main.py
建议使用极简版本测试：

1. **备份原始main.py**：
```bash
cp main.py main_backup.py
```

2. **使用极简版本**：
```bash
cp ultimate_fix_main.py main.py
```

3. **检查配置**：
确保透明度不是完全透明：
```python
Window.clearcolor = (0, 0, 0, 0.01)  # 不是 (0, 0, 0, 0)
```

4. **延迟初始化**：
不要在build方法中立即初始化窗口，使用Clock.schedule_once延迟：
```python
def build(self):
    Clock.schedule_once(lambda dt: self.init_window_safe(), 0.5)
    return FloatLayout()  # 返回临时布局
```

### 3. 重新打包APK

1. **使用buildozer重新打包**：
```bash
buildozer android debug
```

2. **检查打包结果**：
- 确保APK文件生成
- APK大小应在10MB以上
- 包含所有Python文件

### 4. Android设备测试

1. **安装APK**：
```bash
adb install petalarm_v3.0.4.apk
```

2. **查看日志**：
```bash
adb logcat | grep "宠物闹钟"
adb logcat | grep "Window"
adb logcat | grep "Android"
```

3. **关键Android设置**：
- 允许悬浮窗权限
- 允许后台运行
- 关闭电池优化

### 5. 问题排查

#### 问题1：窗口看不见
- **原因**：透明度设置为(0, 0, 0, 0)是完全透明
- **解决方案**：改为(0, 0, 0, 0.01)

#### 问题2：闪退
- **原因**：Window初始化时序问题
- **解决方案**：延迟初始化窗口，先请求权限

#### 问题3：loading图标后退出
- **原因**：Android权限未获取或Service未启动
- **解决方案**：确保前台服务启动，延迟窗口创建

### 6. buildozer.spec关键配置

```python
# Android权限
android.permissions = INTERNET, VIBRATE, SYSTEM_ALERT_WINDOW, WAKE_LOCK, FOREGROUND_SERVICE, RECEIVE_BOOT_COMPLETED

# Android API版本
android.api = 33
android.minapi = 21
android.target_api = 33

# Service配置
android.manifest_placeholders = [foregroundServiceType: "dataSync"]
```

### 7. 代码架构选择

#### 方案A：极简架构（先测试）
```bash
cp ultimate_fix_main.py main.py
```

特点：
- 最简单的窗口
- 延迟初始化
- 固定窗口大小和位置
- 最少的功能

#### 方案B：Service架构（如果A失败）
```bash
cp android_fixed_main.py main.py
```

特点：
- Android Service支持
- 权限时序处理
- WindowManager架构
- 完整的闹钟功能

#### 方案C：混合架构（综合方案）
使用android_minimal_app.py

### 8. 测试流程

1. **方案A测试**：
```bash
buildozer android debug
adb install bin/petalarm-3.0.0-debug.apk
adb logcat | grep "宠物闹钟"
```

2. **如果失败** → **方案B测试**：
```bash
cp android_fixed_main.py main.py
buildozer android debug
adb install bin/petalarm-3.0.0-debug.apk
```

3. **如果失败** → **方案C测试**：
```bash
cp android_minimal_app.py main.py
buildozer android debug
adb install bin/petalarm-3.0.0-debug.apk
```

### 9. 成功标志

- 窗口出现，宠物可见
- 可以点击宠物
- 应用不闪退
- 日志显示正常

### 10. 常见错误日志

```
# 权限错误
Permission Denial: requires SYSTEM_ALERT_WINDOW permission

# Service错误
Service not started

# Window错误
Window initialization failed
```

### 11. 解决方案

1. **权限时序**：
```python
# 延迟3秒后创建窗口
Clock.schedule_once(lambda dt: self.create_window(), 3)
```

2. **Android Service**：
```python
# 先启动Service
if IS_ANDROID:
    android_api.startForegroundService()
```

3. **窗口位置**：
```python
# 使用固定值
Window.top = 200
Window.left = 100
```

## 总结

**核心问题**：Android悬浮窗需要特殊处理：
1. 权限时序：先获取权限，再创建窗口
2. Service架构：需要前台服务
3. 透明度：不能完全透明
4. 延迟初始化：在build方法中延迟初始化

**建议**：先从方案A开始测试，逐步添加功能。