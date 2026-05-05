# 快速测试指南

## 问题
Android悬浮窗应用闪退，显示loading图标后退出，窗口看不见。

## 解决方案选择

### 1. 最简单架构测试
**文件**: `simplest_main.py`
**目的**: 测试最基本的窗口创建是否成功
**步骤**:
```bash
# 1. 使用最简单架构
cp simplest_main.py main.py

# 2. 打包APK
cp buildozer_android.spec buildozer.spec
buildozer android debug

# 3. 安装测试
adb install bin/petalarm-3.0.0-debug.apk
```

### 2. 稳定架构测试
**文件**: `android_stable_main.py`
**目的**: 测试Android Service架构是否有效
**步骤**:
```bash
# 1. 使用稳定架构
cp android_stable_main.py main.py

# 2. 打包APK
buildozer android debug

# 3. 安装测试
adb install bin/petalarm-3.0.0-debug.apk
```

### 3. 完整架构测试
**文件**: `main.py`
**目的**: 测试完整功能是否正常
**步骤**:
```bash
# 1. 使用完整架构
# main.py保持不变

# 2. 打包APK
buildozer android debug

# 3. 安装测试
adb install bin/petalarm-3.0.0-debug.apk
```

## 一键测试脚本
```bash
# 使用一键测试脚本
chmod +x test_android.sh
./test_android.sh
```

## 成功标准

### 最简单架构测试成功
- ✅ 应用不闪退
- ✅ 窗口可见
- ✅ 宠物显示
- ✅ 可以点击宠物

### 稳定架构测试成功
- ✅ 应用不闪退
- ✅ 窗口可见
- ✅ Android Service启动
- ✅ 宠物动画正常

### 完整架构测试成功
- ✅ 应用不闪退
- ✅ 窗口可见
- ✅ 宠物动画正常
- ✅ 闹钟功能正常
- ✅ 菜单可打开

## Android权限设置
### 必须在Android设备上手动设置：
1. **悬浮窗权限** → 允许
2. **后台运行** → 关闭电池优化
3. **前台服务** → 允许

## 日志查看
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

## 常见错误

### 错误1: 窗口看不见
**原因**: Window.clearcolor = (0, 0, 0, 0) 完全透明
**解决方案**: 改为 Window.clearcolor = (0, 0, 0, 0.01)

### 错误2: 应用闪退
**原因**: Android权限时序问题
**解决方案**: 延迟初始化窗口

### 错误3: loading图标后退出
**原因**: Android Service未启动
**解决方案**: 使用Android Service架构

## GitHub Actions自动化测试
`.github/workflows/android-builds.yml` 会自动构建三个版本：
1. 最简单架构APK
2. 稳定架构APK
3. 完整架构APK

可以直接下载测试这三个版本。

## 架构分析
```bash
# 分析架构问题
python3 android_architecture_test.py
```

## APK测试
```bash
# 测试APK文件
python3 test_apk.py
```

## 调试指南
详细调试指南见：[android_debug_guide.md](./android_debug_guide.md)

## 最终选择
根据测试结果选择最稳定的架构：
1. 如果最简单架构成功 → 使用最简单架构
2. 如果稳定架构成功 → 使用稳定架构
3. 如果完整架构成功 → 使用完整架构