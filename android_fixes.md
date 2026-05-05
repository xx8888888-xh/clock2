# Android悬浮窗应用闪退解决方案

## 主要问题分析

1. **Android权限问题**：
   - Android 8.0+ 需要动态请求 `SYSTEM_ALERT_WINDOW` 权限
   - 应用必须在manifest中声明权限并在运行时请求

2. **buildozer.spec配置问题**：
   - Android API级别可能需要调整
   - 可能需要添加更多权限

3. **代码逻辑问题**：
   - 缺少Android兼容性代码
   - 初始化顺序问题

## 修复方案

### 1. 添加Android权限请求代码

需要在 `main.py` 中添加以下代码：

```python
# 在App类中添加权限请求
class PetAlarmApp(App):
    def build(self):
        # Android悬浮窗权限检查
        if platform == 'android':
            from android.permissions import Permission, request_permission
            
            def callback(permissions, results):
                if all(results):
                    print("权限授予成功")
                else:
                    print("权限授予失败")
            
            # 请求悬浮窗权限
            request_permission(Permission.SYSTEM_ALERT_WINDOW, callback)
```

### 2. 更新buildozer.spec

需要添加以下权限：

```spec
android.permissions = INTERNET, VIBRATE, SYSTEM_ALERT_WINDOW, WAKE_LOCK, FOREGROUND_SERVICE, RECEIVE_BOOT_COMPLETED
```

另外可能需要设置：

```spec
android.api = 33
android.minapi = 21
android.target_api = 33
android.sdk = 34
android.ndk = 25b
android.ndk_api = 21
```

### 3. 添加Android兼容性代码

```python
# 在main.py开头添加
import platform
from kivy.utils import platform

if platform == 'android':
    # Android特定设置
    from android import AndroidApplication
```

### 4. 修复代码中的bug

之前发现的bug：
1. calendar_integration.py中的`check_overdue_events2`函数 - 已修复
2. 缺少Android权限请求 - 需要添加
3. 可能的资源文件缺失 - 确保pet.png、icon.png存在
4. 缺少Android运行时检查

### 5. 添加异常处理

```python
# 在主循环中添加异常处理
def on_start(self):
    try:
        # Android悬浮窗权限检查
        if platform == 'android':
            # Android权限处理代码
        # 其他初始化代码
    except Exception as e:
        print(f"应用启动失败: {e}")
```

## 具体修复步骤

1. 修改main.py，添加Android权限请求
2. 确保buildozer.spec配置正确
3. 添加适当的异常处理
4. 测试在Android模拟器上的运行

## Android悬浮窗权限要求

- Android 6.0: 需要手动开启悬浮窗权限
- Android 8.0+: 需要动态请求权限
- 小米/华为等厂商ROM: 需要额外的设置（可能在安全中心）

## 用户指导

1. **首次启动**：
   - 应用会请求悬浮窗权限
   - 用户必须在设置中允许"在其他应用上显示"权限

2. **常见问题**：
   - 闪退：通常是权限问题
   - 无法显示：可能是电池优化阻止了后台运行
   - 悬浮窗位置错误：Window位置设置问题

## 测试建议

1. 在Android模拟器上测试权限请求
2. 测试多厂商ROM兼容性
3. 测试电池优化设置的影响