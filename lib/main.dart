import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import 'dart:async';
import 'package:overlay_support/overlay_support.dart';
import 'package:permission_handler/permission_handler.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
  ]);
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return OverlaySupport(
      child: MaterialApp(
        title: '宠物闹钟',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          primarySwatch: Colors.indigo,
          useMaterial3: true,
          scaffoldBackgroundColor: const Color(0xFFF0F4FF),
        ),
        home: const PetClockHome(),
      ),
    );
  }
}

class PetClockHome extends StatefulWidget {
  const PetClockHome({super.key});

  @override
  State<PetClockHome> createState() => _PetClockHomeState();
}

class _PetClockHomeState extends State<PetClockHome> {
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
    _alarms = [
      Alarm(time: '08:00', enabled: true, label: '起床'),
      Alarm(time: '12:30', enabled: true, label: '午餐'),
      Alarm(time: '23:00', enabled: false, label: '睡觉'),
    ];
    // 延迟申请权限，等 UI 渲染完
    Future.delayed(const Duration(milliseconds: 500), _requestPermissions);
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  /// 申请运行时权限
  void _requestPermissions() async {
    // 申请通知权限（Android 13+）
    final notificationStatus = await Permission.notification.request();
    // 申请闹钟权限（Android 12+）
    await Permission.scheduleExactAlarm.request();

    if (mounted) {
      if (notificationStatus.isGranted) {
        showSimpleNotification(
          const Text('🔔 宠物闹钟已启动，通知权限已开启'),
          background: Colors.green,
          duration: const Duration(seconds: 3),
        );
      } else {
        showSimpleNotification(
          const Text('⚠️ 请在设置中开启通知权限，否则闹钟无法提醒'),
          background: Colors.orange,
          duration: const Duration(seconds: 5),
        );
      }
    }
  }

  void _updateTime() {
    final now = DateTime.now();
    final currentDay = now.day;

    if (currentDay != _lastDay) {
      _lastDay = currentDay;
      for (final alarm in _alarms) {
        alarm.triggeredToday = false;
      }
    }

    setState(() {
      _currentTime = DateFormat('HH:mm:ss').format(now);
      _currentDate = DateFormat('yyyy年MM月dd日 EEEE', 'zh_CN').format(now);
      final hour = now.hour;
      _isPetSleeping = hour >= 22 || hour < 7;
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
    // 触发振动
    HapticFeedback.heavyImpact();
    showSimpleNotification(
      Text('⏰ ${alarm.label}时间到！'),
      background: Colors.deepOrange,
      duration: const Duration(seconds: 10),
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
          ElevatedButton(
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

  void _toggleAlarm(int index) {
    setState(() {
      _alarms[index].enabled = !_alarms[index].enabled;
    });
    final alarm = _alarms[index];
    showSimpleNotification(
      Text(alarm.enabled ? '✅ ${alarm.label} 已开启' : '🔕 ${alarm.label} 已关闭'),
      background: alarm.enabled ? Colors.green : Colors.grey,
      duration: const Duration(seconds: 2),
    );
  }

  void _deleteAlarm(int index) {
    final alarm = _alarms[index];
    setState(() {
      _alarms.removeAt(index);
    });
    showSimpleNotification(
      Text('🗑️ 已删除 ${alarm.label}'),
      background: Colors.red,
      duration: const Duration(seconds: 2),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // 顶部：宠物 + 时间
            Expanded(
              flex: 3,
              child: Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Colors.indigo.shade400,
                      Colors.indigo.shade700,
                    ],
                  ),
                  borderRadius: const BorderRadius.only(
                    bottomLeft: Radius.circular(32),
                    bottomRight: Radius.circular(32),
                  ),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // 宠物表情
                    AnimatedSwitcher(
                      duration: const Duration(milliseconds: 500),
                      child: Text(
                        _isPetSleeping ? '😴' : '🐱',
                        key: ValueKey(_isPetSleeping),
                        style: const TextStyle(fontSize: 80),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _isPetSleeping ? '嘘...我在睡觉' : '你好！我是你的宠物闹钟',
                      style: const TextStyle(
                        fontSize: 16,
                        color: Colors.white70,
                      ),
                    ),
                    const SizedBox(height: 16),
                    // 时间
                    Text(
                      _currentTime,
                      style: const TextStyle(
                        fontSize: 48,
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 2,
                      ),
                    ),
                    const SizedBox(height: 4),
                    // 日期
                    Text(
                      _currentDate,
                      style: const TextStyle(
                        fontSize: 14,
                        color: Colors.white60,
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // 底部：闹钟列表
            Expanded(
              flex: 2,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 标题栏
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          '我的闹钟',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Colors.indigo,
                          ),
                        ),
                        ElevatedButton.icon(
                          onPressed: _addAlarm,
                          icon: const Icon(Icons.add, size: 18),
                          label: const Text('添加'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.indigo,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(20),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),

                    // 闹钟列表
                    Expanded(
                      child: _alarms.isEmpty
                          ? const Center(
                              child: Text(
                                '暂无闹钟，点击上方添加',
                                style: TextStyle(
                                  color: Colors.grey,
                                  fontSize: 16,
                                ),
                              ),
                            )
                          : ListView.builder(
                              itemCount: _alarms.length,
                              itemBuilder: (context, index) {
                                final alarm = _alarms[index];
                                return _buildAlarmCard(alarm, index);
                              },
                            ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAlarmCard(Alarm alarm, int index) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          children: [
            // 时间
            Text(
              alarm.time,
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: alarm.enabled ? Colors.indigo : Colors.grey,
              ),
            ),
            const SizedBox(width: 12),
            // 标签
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    alarm.label,
                    style: TextStyle(
                      fontSize: 16,
                      color: alarm.enabled ? Colors.black87 : Colors.grey,
                    ),
                  ),
                  Text(
                    alarm.enabled ? '已开启' : '已关闭',
                    style: TextStyle(
                      fontSize: 12,
                      color: alarm.enabled ? Colors.green : Colors.grey,
                    ),
                  ),
                ],
              ),
            ),
            // 开关
            Switch(
              value: alarm.enabled,
              onChanged: (_) => _toggleAlarm(index),
              activeColor: Colors.indigo,
            ),
            // 删除
            IconButton(
              icon: const Icon(Icons.delete_outline, color: Colors.redAccent),
              onPressed: () => _deleteAlarm(index),
            ),
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
  String toString() =>
      'Alarm(time: $time, label: $label, enabled: $enabled)';
}
