# 本地测试指南

由于GitHub连接问题，我们先进行本地测试。以下是本地测试步骤：

## 1. 选择架构

### 方案A: 最简单架构
```bash
cp simplest_main.py main.py
```

**特点**：
- 最简化的窗口创建
- 透明度固定为0.01
- 延迟初始化
- 适合验证窗口可见性

### 方案B: 稳定架构
```bash
cp android_stable_main.py main.py
```

**特点**：
- Android Service支持
- 渐进式初始化
- 窗口验证机制
- 适合Android兼容性测试

### 方案C: 完整架构
```bash
# 保持原来的main.py
```

**特点**：
- 原功能完整版本
- 保持所有闹钟功能
- 宠物动画完整

## 2. 配置buildozer
```bash
cp buildozer_android.spec buildozer.spec
```

**关键配置**：
```python
android.permissions = INTERNET, VIBRATE, SYSTEM_ALERT_WINDOW, WAKE_LOCK, FOREGROUND_SERVICE, RECEIVE_BOOT_COMPLETED
android.api = 33
android.manifest_placeholders = [foregroundServiceType: "dataSync"]
```

## 3. 一键测试
```bash
# 运行一键测试脚本
./test_android.sh

# 手动选择架构
chmod +x test_android.sh
./test_android.sh

# 然后选择架构：
# 1. 最简单架构
# 2. 稳定架构
# 3. 完整架构
```

## 4. 本地构建
```bash
# 安装buildozer（如果需要）
pip install buildozer

# 构建APK
buildozer android debug

# 构建完成后APK位置
ls bin/*.apk
```

## 5. Android设备测试

### 安装APK
```bash
adb install bin/petalarm-3.0.0-debug.apk
```

### 查看日志
```bash
# 查看应用日志
adb logcat | grep "宠物闹钟"

# 查看窗口日志
adb logcat | grep "Window"

# 查看Android日志
adb logcat | grep "Android"

# 查看Kivy日志
adb logcat | grep "Kivy"
```

### Android权限设置
1. **悬浮窗权限** → 允许
2. **后台运行** → 关闭电池优化
3. **前台服务** → 允许

## 6. 架构分析
```bash
# 分析架构问题
python3 android_architecture_test.py

# 输出分析结果
# 1. Android环境检测
# 2. Kivy窗口常见问题分析
# 3. Android悬浮窗解决方案
# 4. 现有代码问题
# 5. 改进代码架构
# 6. 最终建议
```

## 7. APK测试
```bash
# 测试APK文件
python3 test_apk.py

# 检查：
# 1. APK结构
# 2. APK大小
# 3. buildozer.spec配置
```

## 8. 调试指南

### 问题1: 窗口看不见
**解决方案**：
```python
# 透明度改为0.01
Window.clearcolor = (0, 0, 0, 0.01)

# 固定窗口大小和位置
Window.size = (300, 300)
Window.top = 150
Window.left = 100
```

### 问题2: 应用闪退
**解决方案**：
```python
# 延迟初始化
Clock.schedule_once(lambda dt: self.init_window_safe(), 0.5)

# 渐进式初始化
Clock.schedule_once(lambda dt: self.create_basic_pet(), 0.5)
Clock.schedule_once(lambda dt: self.add_animation(), 1)
Clock.schedule_once(lambda dt: self.add_to_layout(), 0.5)
```

### 问题3: loading图标后退出
**解决方案**：
```python
# Android Service支持
android.permissions = INTERNET, VIBRATE, SYSTEM_ALERT_WINDOW, WAKE_LOCK, FOREGROUND_SERVICE, RECEIVE_BOOT_COMPLETED
android.manifest_placeholders = [foregroundServiceType: "dataSync"]
```

## 9. 测试顺序建议

### 顺序1: 最简单架构
```bash
cp simplest_main.py main.py
buildozer android debug
adb install bin/petalarm-3.0.0-debug.apk
```

**检查**：
- ✅ 窗口是否可见
- ✅ 宠物是否显示
- ✅ 是否可以点击宠物

### 顺序2: 稳定架构
```bash
cp android_stable_main.py main1分钟.py
buildozer android debug
adb install bin/petalarm-3.0.0-debug.apk
```

**检查**：
- ✅ Android Service是否启动
- ✅ 渐进式初始化是否成功
- ✅ 窗口验证是否有效

### 顺序3: 完整架构
```bash
# 使用原来的main.py
buildozer android debug
adb install bin/petalarm-3.0.0-debug.apk
```

**检查**：
- ✅ 所有功能是否正常
- ✅ 闹钟是否工作
- ✅ 宠物动画是否正常

## 10. 本地GitHub模拟

### 提交到本地仓库
```bash
git add .
git commit -m "Android悬浮窗架构大改"
```

### 查看提交记录
```bash
git log --oneline
```

### 创建分支
```bash
git branch android-fixes
git checkout android-fixes
```

## 11. 文件说明

### 架构文件
- `simplest_main.py`: 最简单架构
- `android_stable_main.py`: 稳定架构
- `android_fixed_main.py`: 完整修复版本
- `android_minimal_app.py`: 最小化架构
- `minimal_main.py`: 最小化版本
- `android_service_main.py`: Android Service架构
- `ultimate_fix_main.py`: 最终修复版本

### 辅助文件
- `test_android.sh`: 一键测试脚本
- `android_debug_guide.md`: 调试指南
- `android_architecture_test.py`: 架构分析
- `test_apk.py`: APK测试
- `README_ARCHITECTURE.md`: 架构选择指南
- `QUICK_TEST.md`: 快速测试指南

## 12. 测试结果记录

| 架构 | 窗口可见 | 不闪退 | 功能正常 | 结论 |
|------|----------|--------|----------|------|
| 最简单架构 | ✅/❌ | ✅/❌ | ✅/❌ | |
| 稳定架构 | ✅/❌ | ✅/❌ | ✅/❌ | |
| 完整架构 | ✅/❌ | ✅/❌ | ✅/❌ | |

## 13. 最终选择
根据测试结果选择最稳定的架构：
1. 如果最简单架构成功 → 使用最简单架构
2. 如果稳定架构成功 → 使用稳定架构
3. 如果完整架构成功 → 使用完整架构

## 14. 后续工作
一旦GitHub连接恢复，可以推送：
```bash
git push origin architecture-rework
```

## 15. 紧急问题解决

### 如果所有架构都失败
尝试以下紧急修复：
1. **透明度设置为0.5**
```python
Window.clearcolor = (0, 0, 0, 0.5)  # 半透明
```

2. **完全放弃透明窗口**
```python
Window.clearcolor = (1, 1, 1, 1)  # 白色背景
```

3. **使用Activity模式**
```python
# 不使用悬浮窗，使用常规Activity
orientation = portrait
fullscreen = 0
show_title_bar = 1  # 显示标题栏
```

**关键**：先测试最简单架构，这是最基础的验证。