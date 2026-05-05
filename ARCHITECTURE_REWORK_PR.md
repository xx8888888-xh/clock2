# Android悬浮窗架构大改 - Pull Request说明

## 问题
之前的Android悬浮窗应用有bug：
1. 闪退，显示loading图标后退出
2. 窗口看不见（完全透明）
3. 权限时序问题

## 解决方案
创建了多个架构版本，逐步解决Android悬浮窗问题：

### 架构1: 最简单架构 (`simplest_main.py`)
- 最简化的窗口创建
- 透明度固定为0.01（不是完全透明）
- 延迟初始化窗口
- 没有复杂功能，仅验证窗口创建

### 架构2: 稳定架构 (`android_stable_main.py`)
- Android Service支持
- 渐进式初始化（分阶段）
- 窗口验证机制
- 宠物可见性保证

### 架构3: 完整架构 (`main.py`)
- 原功能完整版本
- 保持所有闹钟功能
- 宠物动画完整

## 关键修复点

### 1. 透明度修复
```python
# ❌ 原来的代码
Window.clearcolor = (0, 0, 0, 0)  # 完全透明，看不见窗口

# ✅ 修复后的代码
Window.clearcolor = (0, 0, 0, 0.01)  # 几乎透明，窗口可见
```

### 2. 初始化时序修复
```python
# ❌ 原来的代码
def build(self):
    Window.clearcolor = (0, 0, 0, 0)  # 立即初始化

# ✅ 修复后的代码
def build(self):
    Clock.schedule_once(lambda dt: self.init_window_safe(), 0.5)  # 延迟初始化
```

### 3. Android Service架构
```python
# Android Service管理器
class AndroidWindowService:
    def init_android_window(self):
        # 分阶段初始化
        Window.clearcolor = (0, 0, 0, 0.01)
        Window.size = (280, 280)
        Window.top = 180
        Window.left = 60
```

### 4. 渐进式初始化
```python
# 渐进式创建宠物
class ProgressivePet:
    def start_creation(self):
        Clock.schedule_once(lambda dt: self.create_basic_pet(), 0.5)
        Clock.schedule_once(lambda dt: self.add_animation(), 1)
        Clock.schedule_once(lambda dt: self.add_to_layout(), 0.5)
```

## 测试指南

### 一键测试脚本
```bash
chmod +x test_android.sh
./test_android.sh
```

### 测试顺序建议
1. **最简单架构** → 验证窗口创建是否成功
2. **稳定架构** → 验证Android Service是否有效
3. **完整架构** → 验证完整功能是否正常

### 打包配置
```bash
# 使用Android专用配置
cp buildozer_android.spec buildozer.spec
```

### GitHub Actions自动化构建
`.github/workflows/android-builds.yml` 会自动构建三个版本：
1. 简单架构APK
2. 稳定架构APK
3. 完整架构APK

## 文件说明

### 核心文件
- `simplest_main.py`: 最简单架构
- `android_stable_main.py`: 稳定架构
- `android_fixed_main.py`: 完整修复版本
- `android_minimal_app.py`: 最小化架构
- `minimal_main.py`: 最小化版本
- `android_service_main.py`: Android Service架构
- `ultimate_fix_main.py`: 最终修复版本

### 辅助文件
- `android_debug_guide.md`: 调试指南
- `android_architecture_test.py`: 架构分析
- `test_apk.py`: APK测试
- `test_android.sh`: 一键测试脚本

### GitHub Actions
- `.github/workflows/android-builds.yml`: 多架构自动化构建

## Android权限配置
```python
# buildozer.spec
android.permissions = INTERNET, VIBRATE, SYSTEM_ALERT_WINDOW, WAKE_LOCK, FOREGROUND_SERVICE, RECEIVE_BOOT_COMPLETED
android.manifest_placeholders = [foregroundServiceType: "dataSync"]
android.api = 33
android.target_api = 33
```

## 提交内容
- ✅ 多个架构版本
- ✅ Android Service支持
- ✅ 渐进式初始化
- ✅ 透明度修复
- ✅ 延迟初始化时序
- ✅ 一键测试脚本
- ✅ GitHub Actions自动化构建
- ✅ 详细调试指南

## 预期效果
1. **修复闪退**：窗口创建时序修复
2. **修复窗口看不见**：透明度从0改为0.01
3. **修复权限时序**：延迟初始化窗口
4. **Android Service支持**：前台服务架构

## 分支
分支名称：`architecture-rework`

## 下一步
1. 测试最简单架构
2. 测试稳定架构
3. 测试完整架构
4. 根据测试结果选择最终方案