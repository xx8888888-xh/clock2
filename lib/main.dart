import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'dart:async';
import 'package:overlay_support/overlay_support.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return OverlaySupport(
      child: MaterialApp(
        title: '宠物闹钟 - Flutter完整版',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          visualDensity: VisualDensity.adaptivePlatformDensity,
        ),
        home: FloatingPetClock(),
      ),
    );
  }
}

class FloatingPetClock extends StatefulWidget {
  @override
  _FloatingPetClockState createState() => _FloatingPetClockState();
}

class _FloatingPetClockState extends State<FloatingPetClock> {
  Offset _position = Offset(100, 200);
  String _currentTime = '';
  String _currentDate = '';
  bool _isPetSleeping = false;
  List<Alarm> _alarms = [];
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _updateTime();
    _timer = Timer.periodic(Duration(seconds: 1), (_) => _updateTime());
    
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
      if (alarm.enabled && alarm.time == currentTimeStr && !alarm.triggeredToday) {
        _triggerAlarm(alarm);
        alarm.triggeredToday = true;
      }
    }
  }

  void _triggerAlarm(Alarm alarm) {
    showSimpleNotification(
      Text('⏰ ${alarm.label}时间到！'),
      background: Colors.blue,
      duration: Duration(seconds: 5),
    );
  }

  void _addAlarm() {
    // 添加闹钟逻辑
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('添加闹钟'),
        content: Text('闹钟功能（完整版实现）'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('确定'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Stack(
        children: [
          // 悬浮窗宠物闹钟
          Positioned(
            left: _position.dx,
            top: _position.dy,
            child: GestureDetector(
              onPanUpdate: (details) {
                setState(() {
                  _position = _position + details.delta;
                });
              },
              child: Container(
                width: 220,
                height: 260,
                decoration: BoxDecoration(
                  color: Color(0xFF8FB1FF).withOpacity(0.9),
                  borderRadius: BorderRadius.circular(25),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.3),
                      blurRadius: 12,
                      offset: Offset(0, 6),
                    ),
                  ],
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // 宠物表情（根据时间变化）
                    Text(
                      _isPetSleeping ? '😴' : '🐾',
                      style: TextStyle(fontSize: 60),
                    ),
                    
                    SizedBox(height: 10),
                    
                    // 时间显示
                    Text(
                      _currentTime,
                      style: TextStyle(
                        fontSize: 28,
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    
                    // 日期显示
                    Text(
                      _currentDate,
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.white70,
                      ),
                    ),
                    
                    SizedBox(height: 15),
                    
                    // 功能按钮
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        // 闹钟按钮
                        _buildFunctionButton('⏰', '闹钟', _addAlarm),
                        
                        // 设置按钮
                        _buildFunctionButton('⚙️', '设置', () {
                          // 设置功能
                        }),
                        
                        // 天气按钮
                        _buildFunctionButton('☀️', '天气', () {
                          // 天气功能
                        }),
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

  Widget _buildFunctionButton(String emoji, String label, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.2),
          borderRadius: BorderRadius.circular(15),
        ),
        child: Column(
          children: [
            Text(emoji, style: TextStyle(fontSize: 20)),
            Text(label, style: TextStyle(fontSize: 12, color: Colors.white)),
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
}
