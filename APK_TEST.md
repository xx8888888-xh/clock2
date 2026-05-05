# APK测试指南

## 可用APK文件

### 1. petalarm-v3.0.4.apk (42MB)
- **状态**: 完整构建APK
- **内容**: 包含SDL2库、Python3.11库、SQLite3库等
- **架构**: arm64-v8a和armeabi-v7a双架构
- **包含**: 多个classes.dex文件（说明有多个模块）

### 2. petalarm_v3.0.4.apk (6.5MB)
- **状态**: 损坏或不完整APK
- **问题**: zip格式错误，无法解压
- **推测**: 可能是损坏的构建或下载不完整

## GitHub Actions构建
- **构建ID**: 25297403421
- **状态**: completed success
- **透明度修复**: Alpha改为0.5（50%透明）
- **下载**: https://api.github.com/repos/xx8888888-xh/clock2/actions/artifacts/6775735572/zip
- **需要认证**: GitHub API需要认证才能下载

## 修复内容

### ✅ 已修复的问题
1. **透明度**: Window.clearcolor = (0, 0, 0, 0.01)
2. **延迟初始化**: Clock.schedule_once(lambda dt: self.init_pet_and_banner(), 0.5)
3. **Android Service**: AndroidWindowService类
4. **Android权限**: SYSTEM_ALERT_WINDOW权限

## 测试建议

### 步骤1: 安装现有APK
```bash
adb install petalarm-v3.0.4.apk
```

### 步骤2: 查看日志
```bash
adb logcat | grep "宠物闹钟"
adb logcat | grep "Window"
adb logcat | grep "Android"
adb logcat | grep "Kivy"
```

### 步骤3: 权限设置
**Android设备上需要手动设置**:
1. **悬浮窗权限**: 允许
2. **后台运行**: 关闭电池优化
3. **前台服务**: 允许

### 步骤4: 观察效果
1. **窗口可见性**: 窗口是否可见
2. **闪退**: 应用是否闪退
3. **宠物显示**: 宠物是否显示
4. **功能正常**: 闹钟、动画等功能

## 如果现有APK有问题

### 重新构建
```bash
# 选择架构
./test_complete_architecture.sh

# 构建APK
cp buildozer_android.spec buildozer.spec
buildozer android debug

# 安装测试
adb install bin/petalarm-3.0.0-debug.apk
```

### 架构选择
1. **最简单架构**: simplest_main.py → 验证窗口创建
2. **稳定架构**: android_stable_main.py → 验证Android Service
3. **修复版架构**: main_fixed.py → 验证完整功能修复
4. **完整架构**: main.py → 验证最终修复效果

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

## GitHub Actions下载方法

如果需要下载GitHub Actions构建的APK：

### 方法1: 直接访问
1. 访问 https://github.com/xx8888888-xh/clock2
2. Actions页面
3. 找到构建25297403421
4. 下载clock2-apk artifact

### 方法2: API下载
需要GitHub认证，无法自动下载。

## 总结

### 建议测试顺序
1. **测试现有APK**: petalarm-v3.0.4.apk（42MB）
2. **观察日志**: adb logcat查看问题
3. **根据问题选择架构**: 对应修复
4. **重新构建**: 如果有问题

### 预期修复效果
1. ✅ 窗口可见（透明度0.01或0.5）
2. ✅ 应用不闪退（延迟初始化）
3. ✅ 宠物显示（Android Service支持）
4. ✅ 功能正常（闹钟、动画等）