# clock2 - 桌面宠物闹钟

基于 Kivy 构建的 Android 桌面宠物闹钟应用。

## 功能特性

- 🐾 可爱宠物悬浮窗（可拖拽）
- ⏰ 多闹钟管理（支持重复、批量添加）
- ⏱️ 倒计时器
- 😴 睡眠模式
- 🌤️ 天气信息显示
- 📅 日历事件集成
- 💡 快捷操作菜单

## 技术栈

- **框架**: Kivy 2.3.0
- **语言**: Python 3.12+
- **平台**: Android
- **打包**: buildozer + python-for-android

## 项目结构

```
clock2/
├── main.py              # 主程序入口
├── buildozer.spec       # buildozer 配置文件
├── alarms.json          # 闹钟数据存储
├── calendar.json        # 日历数据
├── pet.png              # 宠物图标
├── icon.png             # 应用图标
├── pet_mood.py          # 宠物心情系统
├── weather.py           # 天气 API 模块
└── calendar_integration.py  # 日历集成模块
```

## 构建方法

### 本地构建（需要 Android SDK / Buildozer）

```bash
# 安装依赖
pip install buildozer kivy

# 构建 APK
buildozer -v android debug
```

### GitHub Actions 自动构建

本项目配置了 GitHub Actions 自动化构建：
- `.github/workflows/` 目录下的工作流文件
- 每次推送自动构建 APK

## 运行要求

- Python 3.11+
- Android API 21+ (Android 5.0+)
- Android 权限: INTERNET, VIBRATE, SYSTEM_ALERT_WINDOW, WAKE_LOCK
