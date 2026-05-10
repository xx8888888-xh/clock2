import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'dart:async';
import 'package:overlay_support/overlay_support.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return OverlaySupport(
      child: MaterialApp(
        title: '宠物闹钟 - Flutter完整版',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
        ),
        home: const FloatingPetClock(),
      ),
    );
  }
}

class FloatingPetClock extends StatefulWidget {
  const FloatingPetClock({super.key});

  @override
  State<FloatingPetClock> createState() => _FloatingPetClockState();
}

class _FloatingPetClockState extends State<FloatingPetClock> {
  Offset _position = const Offset(100, 200);
  String _currentTime = '';
  String _currentDate = '';
  bool _isPetSleeping = false;
  List<Alarm> _alarms = [];
  Timer? _timer;
  int _lastDay = 0;

  @override
  void initState() {
    super.initState();
    _lastDay = DateTime.now().day;
    _updateTime();
    _timer = Timer.periodic(const Duration(seconds: 1), (_) => _updateTime());

    // 初始化示例闹钟
    _alarms = [
      Alarm(time: '08:00', enabled: true, label: '起床'),
      Alarm(time: '12:30', enabled: true, label: '午餐'),
      Alarm(time: '23:00', enabled: false, label: '睡觉'),
    ];
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _updateTime() {
    final now = DateTime.now();
    final currentDay = now.day;

    // 跨天重置所有闹钟的 triggeredToday 状态
    if (currentDay != _lastDay) {
      _lastDay = currentDay;
      for (final alarm in _alarms) {
        alarm.triggeredToday = false;
      }
    }

    setState(() {
      _currentTime = DateFormat('HH:mm:ss').format(now);
      _currentDate = DateFormat('yyyy-MM-dd EEEE', 'zh_CN').format(now);

      // 检查宠物睡眠时间（22:00-07:00）
      final hour = now.hour;
      _isPetSleeping = hour >= 22 || hour < 7;

      // 检查闹钟
      _checkAlarms(now);
    });
  }

  void _checkAlarms(DateTime now) {
    final currentTimeStr = DateFormat('HH:mm').format(now);
    for (final alarm in _alarms) {
      if (alarm.enabled &&
          alarm.time == currentTimeStr &&
          !alarm.triggeredToday) {
        _triggerAlarm(alarm);
        alarm.triggeredToday = true;
      }
    }
  }

  void _triggerAlarm(Alarm alarm) {
    showSimpleNotification(
      Text('⏰ ${alarm.label}时间到！'),
      background: Colors.blue,
      duration: const Duration(seconds: 5),
    );
  }

  void _addAlarm() {
    final timeController = TextEditingController();
    final labelController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('添加闹钟'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: timeController,
              decoration: const InputDecoration(
                labelText: '时间 (HH:mm)',
                hintText: '08:00',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.datetime,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: labelController,
              decoration: const InputDecoration(
                labelText: '标签',
                hintText: '起床',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              final time = timeController.text.trim();
              final label = labelController.text.trim();
              if (time.isNotEmpty &&
                  RegExp(r'^\d{2}:\d{2}$').hasMatch(time)) {
                setState(() {
                  _alarms.add(Alarm(
                    time: time,
                    label: label.isNotEmpty ? label : '闹钟',
                  ));
                });
                Navigator.pop(context);
                showSimpleNotification(
                  const Text('✅ 闹钟已添加'),
                  background: Colors.green,
                  duration: const Duration(seconds: 2),
                );
              } else {
                showSimpleNotification(
                  const Text('❌ 请输入正确的时间格式 (HH:mm)'),
                  background: Colors.red,
                  duration: const Duration(seconds: 2),
                );
              }
            },
            child: const Text('添加'),
          ),
        ],
      ),
    );
  }

  void _showSettings() {
    showSimpleNotification(
      const Text('⚙️ 设置功能开发中...'),
      background: Colors.orange,
      duration: const Duration(seconds: 2),
    );
  }

  void _showWeather() {
    showSimpleNotification(
      const Text('☀️ 天气功能开发中...'),
      background: Colors.orange,
      duration: const Duration(seconds: 2),
    );
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;

    return Scaffold(
      backgroundColor: const Color(0xFF1A1A2E),
      body: Stack(
        children: [
          // 背景装饰
          Positioned.fill(
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color(0xFF1A1A2E),
                    Color(0xFF16213E),
                    Color(0xFF0F3460),
                  ],
                ),
              ),
            ),
          ),
          // 悬浮窗宠物闹钟
          Positioned(
            left: _position.dx,
            top: _position.dy,
            child: GestureDetector(
              onPanUpdate: (details) {
                setState(() {
                  // 添加屏幕边界限制
                  double newX = _position.dx + details.delta.dx;
                  double newY = _position.dy + details.delta.dy;
                  newX = newX.clamp(0.0, screenSize.width - 220);
                  newY = newY.clamp(0.0, screenSize.height - 260);
                  _position = Offset(newX, newY);
                });
              },
              child: Container(
                width: 220,
                height: 260,
                decoration: BoxDecoration(
                  color: const Color(0xFF8FB1FF).withOpacity(0.9),
                  borderRadius: BorderRadius.circular(25),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.3),
                      blurRadius: 12,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // 宠物表情（根据时间变化）
                    Text(
                      _isPetSleeping ? '😴' : '🐾',
                      style: const TextStyle(fontSize: 60),
                    ),

                    const SizedBox(height: 10),

                    // 时间显示
                    Text(
                      _currentTime,
                      style: const TextStyle(
                        fontSize: 28,
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),

                    // 日期显示
                    Text(
                      _currentDate,
                      style: const TextStyle(
                        fontSize: 14,
                        color: Colors.white70,
                      ),
                    ),

                    const SizedBox(height: 15),

                    // 功能按钮
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        _buildFunctionButton('⏰', '闹钟', _addAlarm),
                        _buildFunctionButton('⚙️', '设置', _showSettings),
                        _buildFunctionButton('☀️', '天气', _showWeather),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFunctionButton(
      String emoji, String label, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.2),
          borderRadius: BorderRadius.circular(15),
        ),
        child: Column(
          children: [
            Text(emoji, style: const TextStyle(fontSize: 20)),
            Text(label,
                style: const TextStyle(fontSize: 12, color: Colors.white)),
          ],
        ),
      ),
    );
  }
}

class Alarm {
  final String time;
  final String label;
  bool enabled;
  bool triggeredToday;

  Alarm({
    required this.time,
    required this.label,
    this.enabled = true,
    this.triggeredToday = false,
  });

  @override
  String toString() => 'Alarm(time: $time, label: $label, enabled: $enabled)';
}
