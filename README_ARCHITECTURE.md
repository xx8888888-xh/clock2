# Android悬浮窗架构测试指南

## 问题描述
- Android悬浮窗应用闪退
- 显示loading图标后退出
- 窗口看不见（完全透明）

## 解决方案

### 架构选择

#### 1. 最简单架构 (`simplest_main.py`)
**特点**：
- 最简化的窗口创建
- 透明度固定为0.01（不是完全透明）
- 延迟初始化
- 没有复杂功能

**适用场景**：
- 测试窗口创建是否成功
- 验证Android悬浮窗权限
- 检查窗口可见性

#### 2. 稳定架构 (`android_stable_main.py`)
**特点**：
- Android Service支持
- 渐进式初始化
- 窗口验证机制
- 宠物可见性保证

**适用场景**：
- 需要Android Service支持
- 窗口创建稳定性
- 渐进式界面构建

#### 3. 完整架构 (`main.py`)
**特点**：
- 原功能完整版本
- 完整的闹钟功能
- 宠物动画
- 菜单交互

**适用场景**：
- 功能完整的应用
- 用户体验优先
- 需要完整功能

## 测试步骤

### 步骤1：选择架构
```bash
# 使用最简单架构测试
cp simplest_main.py main.py

# 使用稳定架构测试
cp android_stable_main.py main.py

# 使用完整架构测试
# main.py保持不变
```

### 步骤2：配置buildozer.spec
```bash
# 使用专门针对Android悬浮窗的配置
cp buildozer_android.spec buildozer.spec
```

### 步骤3：打包APK
```bash
buildozer android debug
```

### 步骤4：安装测试
```bash
adb install bin/petalarm-3.0.0-debug.apk
```

### 步骤5：查看日志
```bash
adb logcat | grep "宠物闹钟"
adb logcat | grep "Window"
adb logcat | grep "Android"
```

## 关键配置点

### 1. 透明度
```python
# ❌ 错误：完全透明，窗口看不见
Window.clearcolor = (0, 0, 0, 0)

# ✅ 正确：几乎透明，窗口可见
Window.clearcolor = (0, 0, 0, 0.01)
```

### 2. Android权限
```python
# buildozer.spec配置
android.permissions = INTERNET, VIBRATE, SYSTEM_ALERT_WINDOW, WAKE_LOCK, FOREGROUND_SERVICE, RECEIVE_BOOT_COMPLETED
```

### 3. Android API版本
```python
# Android API至少33
android.api = 33
android.target_api = 33
```

### 4. Android Service配置
```python
# 前台服务类型
android.manifest_placeholders = [foregroundServiceType: "dataSync"]
```

### 5. 窗口初始化时机
```python
# ❌ 错误：在build中立即初始化
def build(self):
    Window.clearcolor = (0, 0, 0, 0)  # 错误时机

# ✅ 正确：延迟初始化
def build(self):
    Clock.schedule_once(lambda dt: self.init_window_safe(), 0.5)  # 延迟
```

### 6. 窗口大小和位置
```python
# ✅ 正确：固定值
Window.size = (300, 300)
Window.top = 200
Window.left = 100
```

## 架构分析

### 最简单架构优缺点
**优点**：
1. 代码最简单
2. 最容易调试
3. 窗口创建成功率最高
4. 适合验证基本功能

**缺点**：
1. 功能有限
2. 没有Android Service支持
3. 窗口稳定性较差

### 稳定架构优缺点
**优点**：
1. Android Service支持
2. 渐进式初始化
3. 窗口验证机制
4. 稳定性较高

**缺点**：
1. 代码复杂度增加
2. 需要理解Android Service

### 完整架构优缺点
**优点**：
1. 功能完整
2. 用户体验好
3. 宠物动画完整

**缺点**：
1. 代码复杂度最高
2. Android兼容性问题可能最多
3. 调试困难

## 推荐测试顺序

1. **最简单架构** → 验证窗口创建
2. **稳定架构** → 验证Android Service
3. **完整架构** → 验证完整功能

## 调试技巧

### 查看Android日志
```bash
# 筛选宠物闹钟日志
adb logcat | grep "宠物闹钟"

# 查看Window相关日志
adb logcat | grep "Window"

# 查看Android Service日志
adb logcat | grep "Service"
```

### Android设备权限设置
1. **悬浮窗权限**：必须在Android设置中手动开启
2. **后台运行**：关闭电池优化
3. **前台服务**：允许应用前台运行

### 窗口可见性检查
1. **透明度**：必须是0.01而不是0
2. **窗口大小**：必须有具体大小
3. **窗口位置**：必须在屏幕范围内

## 常见错误

### 错误1：窗口看不见
**原因**：透明度设置为0
**解决方案**：改为0.01

### 错误2：应用闪退
**原因**：Android权限未获取或窗口初始化过早
**解决方案**：延迟初始化，先请求权限

### 错误3：loading图标后退出
**原因**：Android Service未启动或窗口创建失败
**解决方案**：使用Android Service架构

## 架构选择决策树

```
开始 → 窗口是否可见？
├── 是 → 功能是否完整？
│   ├── 是 → 使用完整架构
│   ├── 否 → 使用稳定架构
└── 否 → Android权限是否开启？
    ├── 是 → 使用最简单架构测试
    ├── 否 → 开启权限后再测试
```

## 提交到GitHub

```bash
git add .
git commit -m "新增Android悬浮窗架构测试版本"
git push origin main
```

## GitHub Actions自动化测试
会自动构建三个架构版本：
1. 简单架构
2. 稳定架构  
3. 完整架构