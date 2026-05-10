import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_overlay_window/flutter_overlay_window.dart';
import 'package:intl/intl.dart';
import 'package:permission_handler/permission_handler.dart';

@pragma("vm:entry-point")
void overlayMain() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MaterialApp(
    debugShowCheckedModeBanner: false,
    home: FloatingPetWidget(),
  ));
}

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '宠物闹钟',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.indigo,
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}

/// 主界面：用于启动/停止悬浮窗
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _isOverlayActive = false;
  bool _hasPermission = false;

  @override
  void initState() {
    super.initState();
    _checkPermission();
    _checkOverlayStatus();
  }

  Future<void> _checkPermission() async {
    final status = await Permission.systemAlertWindow.status;
    setState(() {
      _hasPermission = status.isGranted;
    });
  }

  Future<void> _checkOverlayStatus() async {
    final isActive = await FlutterOverlayWindow.isActive();
    setState(() {
      _isOverlayActive = isActive ?? false;
    });
  }

  Future<void> _requestPermission() async {
    final status = await Permission.systemAlertWindow.request();
    setState(() {
      _hasPermission = status.isGranted;
    });
    if (!status.isGranted) {
      // 引导用户去设置开启
      await FlutterOverlayWindow.requestPermission();
    }
  }

  Future<void> _toggleOverlay() async {
    if (!_hasPermission) {
      await _requestPermission();
      return;
    }

    if (_isOverlayActive) {
      await FlutterOverlayWindow.closeOverlay();
      setState(() {
        _isOverlayActive = false;
      });
    } else {
      await FlutterOverlayWindow.showOverlay(
        enableDrag: true,
        overlayTitle: "宠物闹钟",
        overlayContent: '宠物闹钟正在运行',
        flag: OverlayFlag.defaultFlag,
        visibility: NotificationVisibility.visibilityPublic,
        positionGravity: PositionGravity.auto,
        height: 260,
        width: 220,
        startPosition: const OverlayPosition(100, 400),
      );
      setState(() {
        _isOverlayActive = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F4FF),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // 宠物图标
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  color: Colors.indigo.shade100,
                  shape: BoxShape.circle,
                ),
                child: const Center(
                  child: Text('🐱', style: TextStyle(fontSize: 60)),
                ),
              ),
              const SizedBox(height: 24),
              const Text(
                '宠物闹钟',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.indigo,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '开启悬浮窗，让宠物陪伴你',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey.shade600,
                ),
              ),
              const SizedBox(height: 48),

              // 权限状态
              if (!_hasPermission)
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.orange.shade50,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.orange.shade200),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.warning_amber, color: Colors.orange.shade700),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          '需要悬浮窗权限才能显示宠物',
                          style: TextStyle(color: Colors.orange.shade700),
                        ),
                      ),
                    ],
                  ),
                ),
              const SizedBox(height: 24),

              // 启动/停止按钮
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton.icon(
                  onPressed: _toggleOverlay,
                  icon: Icon(
                    _isOverlayActive ? Icons.stop : Icons.play_arrow,
                    size: 28,
                  ),
                  label: Text(
                    _isOverlayActive ? '停止悬浮窗' : '启动宠物悬浮窗',
                    style: const TextStyle(fontSize: 18),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _isOverlayActive ? Colors.red : Colors.indigo,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // 状态提示
              Text(
                _isOverlayActive ? '宠物正在桌面上陪伴你 ❤️' : '点击按钮启动宠物',
                style: TextStyle(
                  color: _isOverlayActive ? Colors.green : Colors.grey,
                  fontSize: 14,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// 悬浮窗内容：宠物时钟
class FloatingPetWidget extends StatefulWidget {
  const FloatingPetWidget({super.key});

  @override
  State<FloatingPetWidget> createState() => _FloatingPetWidgetState();
}

class _FloatingPetWidgetState extends State<FloatingPetWidget> {
  String _currentTime = '';
  String _currentDate = '';
  bool _isPetSleeping = false;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _updateTime();
    _timer = Timer.periodic(const Duration(seconds: 1), (_) => _updateTime());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _updateTime() {
    final now = DateTime.now();
    setState(() {
      _currentTime = DateFormat('HH:mm').format(now);
      _currentDate = DateFormat('MM-dd E', 'zh_CN').format(now);
      final hour = now.hour;
      _isPetSleeping = hour >= 22 || hour < 7;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: Container(
        width: 220,
        height: 260,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              const Color(0xFF8FB1FF),
              Colors.indigo.shade300,
            ],
          ),
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.25),
              blurRadius: 15,
              offset: const Offset(0, 8),
            ),
          ],
          border: Border.all(
            color: Colors.white.withOpacity(0.3),
            width: 1,
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // 关闭按钮
            Align(
              alignment: Alignment.topRight,
              child: Padding(
                padding: const EdgeInsets.only(top: 8, right: 8),
                child: GestureDetector(
                  onTap: () {
                    FlutterOverlayWindow.closeOverlay();
                  },
                  child: Container(
                    width: 24,
                    height: 24,
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.3),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.close,
                      size: 16,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
            ),

            // 宠物表情
            AnimatedSwitcher(
              duration: const Duration(milliseconds: 500),
              child: Text(
                _isPetSleeping ? '😴' : '🐱',
                key: ValueKey(_isPetSleeping),
                style: const TextStyle(fontSize: 56),
              ),
            ),
            const SizedBox(height: 4),

            // 时间
            Text(
              _currentTime,
              style: const TextStyle(
                fontSize: 36,
                color: Colors.white,
                fontWeight: FontWeight.bold,
                letterSpacing: 1,
              ),
            ),

            // 日期
            Text(
              _currentDate,
              style: TextStyle(
                fontSize: 12,
                color: Colors.white.withOpacity(0.8),
              ),
            ),
            const SizedBox(height: 8),

            // 状态文字
            Text(
              _isPetSleeping ? '睡觉中...' : '陪伴中',
              style: TextStyle(
                fontSize: 11,
                color: Colors.white.withOpacity(0.7),
              ),
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }
}
