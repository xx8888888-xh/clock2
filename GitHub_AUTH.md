# GitHub认证与测试指南

## 认证问题

GitHub推送失败原因：
```bash
# HTTPS认证失败
fatal: could not read Username for 'https://github.com': No such device or address

# SSH认证失败
git@github.com: Permission denied (publickey)
```

## 解决方案

### **方案1: GitHub令牌认证**
1. 在GitHub生成令牌
2. 使用令牌推送：
```bash
git remote set-url origin https://github.com/xx8888888-xh/clock2.git
git push origin architecture-rework
```

### **方案2: SSH密钥认证**
```bash
# 生成SSH密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 将公钥添加到GitHub SSH密钥设置

# 设置SSH远程URL
git remote set-url origin git@github.com:xx8888888-xh/clock2.git

# 推送
git push origin architecture-rework
```

### **方案3: 手动上传**
1. 在GitHub网站上：
   - 访问 https://github.com/xx8888888-xh/clock2
   - 切换到architecture-rework分支
   - 手动上传修复文件

## 修复摘要

### **透明度修复**
```python
Config.set('graphics', 'background_color', '0,0,0,0.5')
Window.clearcolor = (0, 0, 0, 0.01)
```

### **延迟初始化**
```python
Clock.schedule_once(lambda dt: self.safe_init_window(), 1)
```

### **Android Service**
```python
class AndroidWindowService:
    def init_window_safe(self):
        Window.clearcolor = (0, 0, 0, 0.01)
        Window.size = (300, 300)
        Window.top = 150
        Window.left = 100
```

### **Android权限**
```python
android.permissions = INTERNET, VIBRATE, SYSTEM_ALERT_WINDOW, WAKE_LOCK, FOREGROUND_SERVICE, RECEIVE_BOOT_COMPLETED
```

## GitHub Actions构建

GitHub Actions构建ID: 25297403421
透明度修复: Alpha改为0.5
下载URL: https://api.github.com/repos/xx8888888-xh/clock2/actions/artifacts/6775735572/zip

## APK测试计划

### **现有APK**
透明度: Window.clearcolor = (0, 0, 0, 0.8) → 80%透明

### **GitHub Actions APK**
透明度: Window.clearcolor = (0, 0, 0, 0.5) → 50%透明

### **本地修复**
透明度: Config.set('graphics', 'background_color', '0,0,0,0.5')
透明度: Window.clearcolor = (0, 0, 0, 0.01) → 几乎透明

## 测试指令

```bash
# 测试现有APK
adb install petalarm-v3.0.4.apk
adb shell am start -n org.petalarm/.DesktopPetAlarmApp
adb logcat | grep "宠物闹钟"

# 测试GitHub Actions APK
# 下载：https://api.github.com/repos/xx8888888-xh/clock2/actions/artifacts/6775735572/zip
adb install github_actions.apk
adb shell am start -n org.petalarm/.DesktopPetAlarmApp
adb logcat | grep "宠物闹钟"
```

## 网络状态

✅ ping github.com: 成功
✅ curl https://github.com: 成功
❌ git push origin architecture-rework: 需要认证

GitHub认证失败不影响测试APK。先测试现有APK，根据结果调整。