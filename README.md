# clock2 - 桌面宠物闹钟

基于 Kivy 构建的 Android 桌面宠物闹钟应用。

## 功能特性

### 🐾 宠物系统
- 可爱宠物悬浮窗（可拖拽、点击交互）
- 多状态动画（idle/happy/sleep/excited/angry）
- 心情随时间、天气、互动变化

### ⏰ 闹钟功能
- 多闹钟管理（支持重复、批量添加）
- 贪睡功能（可配置时长和次数）
- 声音+振动提醒

### ⏱️ 计时器
- 倒计时功能
- 实时显示剩余时间
- 到时通知提醒

### 😴 睡眠模式
- 自动检测睡眠时间
- 夜间宠物休眠动画
- 气泡特效

### 🌤️ 天气系统
- 实时天气显示（需要 OpenWeatherMap API Key）
- 天气影响宠物心情
- 默认模拟数据（无需配置）
- **应用内城市设置**（设置中可直接修改天气城市）

### 🐾 宠物状态持久化
- 宠物心情、互动数据自动保存
- 重启后恢复宠物状态
- 互动次数记录

### 📅 日历集成
- 日历事件管理
- 下一个事件提醒
- 与闹钟关联

### 💡 快捷操作
- 长按弹出快捷菜单
- 快速新建闹钟/计时器
- 一键睡眠模式

## 技术栈

- **框架**: Kivy 2.3.0
- **语言**: Python 3.12+
- **平台**: Android
- **打包**: buildozer + python-for-android

## 项目结构

```
clock2/
├── main.py              # 主程序入口（所有UI和业务逻辑）
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
- 每次推送 main 分支自动构建 APK

## 配置说明

### 天气 API（可选）
默认使用模拟天气数据，无需配置。如需真实天气：
```python
# 在 weather.py 中设置您的 API Key
weather_api = WeatherAPI(api_key='your_openweathermap_key')
```

## 运行要求

- Python 3.11+
- Android API 21+ (Android 5.0+)
- Android 权限: INTERNET, VIBRATE, SYSTEM_ALERT_WINDOW, WAKE_LOCK

## 版本历史

- **V3.4**: 宠物状态持久化、应用内城市设置、on_resume回调修复
- V3.3: 修复on_resume天气定时器、window_pos路径、添加on_exit
- V3.2: 修复悬浮窗初始化时序问题
- V3.1: 完善心情/天气/日历系统，增加定时器清理
- V3.0: 完整重构，Kivy 2.3.0
- V2.0: 多闹钟和批量添加
- V1.0: 基础版本
