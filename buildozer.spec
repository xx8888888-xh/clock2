[app]
title = 宠物闹钟
package.name = petalarm
package.domain = org.petalarm
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf,wav,mp3
source.main = simplest_main.py
version = 3.0.0
requirements = python3,kivy==2.3.0,plyer,pillow,cython
icon.filename = icon.png
orientation = portrait
fullscreen = 0
hide_status_bar = 0
hide_navigation_bar = 0
show_title_bar = 0
log_level = 2

# Android权限（悬浮窗最关键）
android.permissions = INTERNET, VIBRATE, SYSTEM_ALERT_WINDOW, WAKE_LOCK, FOREGROUND_SERVICE, RECEIVE_BOOT_COMPLETED

# Android API版本
android.api = 33
android.minapi = 21
android.target_api = 33
android.sdk = 34
android.ndk = 27
android.ndk_api = 21
android.archs = armeabi-v7a, arm64-v8a

# Android窗口配置
android.window_soft_input_mode = adjustResize
android.supports_any_density = True
android.allow_backup = True
android.use_androidx = True
android.enable_multidex = True

# 通知渠道
android.notification_channel = 宠物闹钟,宠物闹钟提醒

# Service配置（Android悬浮窗需要）
android.manifest_placeholders = [foregroundServiceType: "dataSync"]

# 打包配置
build.dir = ./.buildozer
bin.dir = ./bin

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin
