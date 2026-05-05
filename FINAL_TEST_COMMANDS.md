# 最终测试指令

## 测试顺序（建议）

### 第1步：非透明窗口测试
```bash
# 使用非透明窗口测试
cp no_transparency_main.py main.py
cp buildozer_no_transparency.spec buildozer.spec
buildozer android debug
```

**检查**：
- 窗口是否可见
- 宠物是否显示
- 应用是否闪退

### 第2步：最简单架构测试
```bash
# 使用最简单架构
cp simplest_main.py main1分钟.py
cp buildozer_android.spec buildozer.spec
buildozer android debug
```

**检查**：
- 窗口是否可见（透明度0.01）
- 宠物是否显示
- 应用是否闪退

### 第3步：稳定架构测试
```bash
# 使用稳定架构
cp android_stable_main.py main.py
cp buildozer_android.spec buildozer.spec
buildozer android debug
```

**检查**：
- Android Service是否启动
- 渐进式初始化是否成功
- 窗口验证是否有效

### 第4步：完整架构测试
```bash
# 使用完整架构
# main.py保持不变
cp buildozer_android.spec buildozer.spec
buildozer android debug
```

**检查**：
- 所有功能是否正常
- 闹钟是否工作
- 宠物动画是否正常

## 一键测试脚本
```bash
# 运行一键测试脚本
./test_android.sh

# 或者手动测试
# 1. 非透明窗口测试
cp no_transparency_main.py main.py
cp buildozer_no_transparency.spec buildozer.spec
buildozer android debug

# 2. 最简单架构测试
cp simplest_main.py main.py
cp buildozer_android.spec buildozer.spec
buildozer android debug

# 3. 稳定架构测试
cp android_stable_main.py main.py
cp buildozer_android.spec buildozer.spec
buildozer android debug

# 4. 完整架构测试
# main.py保持不变
cp buildozer_android.spec buildozer.spec
buildozer android debug
```

## Android设备安装
```bash
adb install bin/petalarm-3.0.0-debug.apk
```

## 查看日志
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

## Android权限设置
1. **悬浮窗权限** → 允许
2. **后台运行** → 关闭电池优化
3. **前台服务** → 允许

## 架构分析
```bash
# 分析架构问题
python3 android_architecture_test.py

# 输出结果：
# 1. Android环境检测
# 2. Kivy窗口常见问题分析
# 3. Android悬浮窗解决方案
# 4. 现有代码问题
# 5. 改进代码架构
# 6. 最终建议
```

## 核心问题总结

### 问题1: 窗口看不见
**根本原因**: Window.clearcolor = (0, 0, 0, 0) 是完全透明
**解决方案**: 
1. Window.clearcolor = (0, 0, 0, 0.01)  # 几乎透明
2. Window.clearcolor = (1, 1, 1, 1)  # 完全不透明（测试）

### 问题2: 应用闪退
**根本原因**: Android权限时序问题
**解决方案**: 
1. 延迟初始化窗口
2. 渐进式初始化

### 问题3: loading图标后退出
**根本原因**: Android Service未启动
**解决方案**: 
1. Android Service架构
2. 前台服务配置

## 测试成功标志

### 非透明窗口测试
- ✅ 窗口可见（白色背景）
- ✅ 宠物显示
- ✅ 应用不闪退

### 最简单架构测试
- ✅ 窗口可见（透明度0.01）
- ✅ 宠物显示
- ✅ 应用不闪退

### 稳定架构测试
- ✅ Android Service启动
- ✅ 渐进式初始化成功
- ✅ 窗口验证有效

### 完整架构测试
- ✅ 所有功能正常
- ✅ 闹钟工作
- ✅ 宠物动画正常

## 下一步操作

### 如果非透明窗口测试失败
```bash
# 尝试完全不透明版本
Window.clearcolor = (1, 1, 1, 1)

# 尝试半透明版本
Window.clearcolor = (1, 1, 1, 0.5)
```

### 如果最简单架构失败
```bash
# 尝试固定窗口位置
Window.top = 200
Window.left = 100

# 尝试更大窗口
Window.size = (400, 400)
```

### 如果稳定架构失败
```bash
# 尝试更多延迟
Clock.schedule_once(lambda dt: self.init_window(), 2)

# 尝试更简单的Service架构
```

### 如果完整架构失败
```bash
# 回到稳定架构或最简单架构
```

## GitHub Actions测试
一旦GitHub连接恢复，会自动构建三个版本：
1. 最简单架构APK
2. 稳定架构APK
3. 完整架构APK

## 最终决策
根据测试结果选择最稳定的架构：

| 架构 | 窗口可见 | 不闪退 | 功能正常 | 最终选择 |
|------|----------|--------|----------|----------|
| 非透明窗口 | ✅/❌ | ✅/❌ | ✅/❌ | |
| 最简单架构 | ✅/❌ | ✅/❌ | ✅/❌ | |
| 稳定架构 | ✅/❌ | ✅/❌ | ✅/❌ | |
| 完整架构 | ✅/❌ | ✅/❌ | ✅/❌ | |

**推荐顺序**: 从非透明窗口测试开始，逐步测试到完整架构。