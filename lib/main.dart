import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  runApp(const PetClockApp());
}

// ==================== 宠物心情系统 ====================

enum PetMood {
  happy('😊', '开心', '心情很好！'),
  normal('😐', '普通', '还不错~'),
  sleepy('😴', '困倦', '好困...'),
  hungry('🥺', '饥饿', '想吃东西...'),
  sick('🤒', '生病', '不太舒服...');

  const PetMood(this.emoji, this.label, this.desc);
  final String emoji;
  final String label;
  final String desc;
}

class PetState {
  PetMood mood;
  int hunger; // 0-100, 100=full
  int happiness; // 0-100
  DateTime lastFed;
  DateTime lastInteraction;

  PetState({
    this.mood = PetMood.happy,
    this.hunger = 80,
    this.happiness = 80,
    DateTime? lastFed,
    DateTime? lastInteraction,
  })  : lastFed = lastFed ?? DateTime.now(),
        lastInteraction = lastInteraction ?? DateTime.now();

  void updateMood() {
    if (hunger < 20) {
      mood = PetMood.hungry;
    } else if (happiness < 20) {
      mood = PetMood.sick;
    } else {
      final hour = DateTime.now().hour;
      if (hour >= 23 || hour < 6) {
        mood = PetMood.sleepy;
      } else if (happiness > 60 && hunger > 50) {
        mood = PetMood.happy;
      } else {
        mood = PetMood.normal;
      }
    }
  }

  void feed() {
    hunger = (hunger + 30).clamp(0, 100);
    happiness = (happiness + 10).clamp(0, 100);
    lastFed = DateTime.now();
    lastInteraction = DateTime.now();
    updateMood();
  }

  void pet() {
    happiness = (happiness + 15).clamp(0, 100);
    lastInteraction = DateTime.now();
    updateMood();
  }

  void tick() {
    // 每5分钟降低一点饥饿和快乐
    hunger = (hunger - 1).clamp(0, 100);
    happiness = (happiness - 1).clamp(0, 100);
    updateMood();
  }
}

// ==================== 闹钟模型 ====================

class AlarmItem {
  final String id;
  final String time;
  final String label;
  bool enabled;
  bool triggeredToday;

  AlarmItem({
    required this.id,
    required this.time,
    required this.label,
    this.enabled = true,
    this.triggeredToday = false,
  });

  Map<String, dynamic> toMap() => {
        'id': id,
        'time': time,
        'label': label,
        'enabled': enabled,
      };

  factory AlarmItem.fromMap(Map<String, dynamic> m) => AlarmItem(
        id: m['id'] as String,
        time: m['time'] as String,
        label: m['label'] as String,
        enabled: m['enabled'] as bool? ?? true,
      );
}

// ==================== 日历事件模型 ====================

class CalendarEvent {
  final String id;
  final String title;
  final String date; // yyyy-MM-dd
  final String time; // HH:mm
  String notes;

  CalendarEvent({
    required this.id,
    required this.title,
    required this.date,
    required this.time,
    this.notes = '',
  });

  DateTime get dateTime =>
      DateTime.tryParse('$date $time') ?? DateTime.now();

  Map<String, dynamic> toMap() => {
        'id': id,
        'title': title,
        'date': date,
        'time': time,
        'notes': notes,
      };

  factory CalendarEvent.fromMap(Map<String, dynamic> m) => CalendarEvent(
        id: m['id'] as String,
        title: m['title'] as String,
        date: m['date'] as String,
        time: m['time'] as String,
        notes: m['notes'] as String? ?? '',
      );
}

// ==================== 主应用 ====================

class PetClockApp extends StatelessWidget {
  const PetClockApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '宠物闹钟',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.pink,
        scaffoldBackgroundColor: const Color(0xFFFFF0F5),
        useMaterial3: true,
        fontFamily: 'Roboto',
      ),
      home: const HomePage(),
    );
  }
}

// ==================== 主页 ====================

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => HomePageState();
}

class HomePageState extends State<HomePage>
    with SingleTickerProviderStateMixin {
  // 宠物状态
  PetState petState = PetState();
  late AnimationController _bounceController;
  late Animation<double> _bounceAnimation;

  // 时钟
  String currentTime = '';
  String currentDate = '';

  // 闹钟
  List<AlarmItem> alarms = [];
  int _lastDay = 0;

  // 倒计时
  int countdownSeconds = 0;
  Timer? countdownTimer;
  bool countdownRunning = false;

  // 日历事件
  List<CalendarEvent> events = [];

  // 权限
  bool hasOverlayPermission = false;

  // 定时器
  Timer? _clockTimer;
  Timer? _petTimer;

  @override
  void initState() {
    super.initState();
    _bounceController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..repeat(reverse: true);
    _bounceAnimation =
        Tween<double>(begin: 0, end: -12).animate(_bounceController);

    _updateTime();
    _clockTimer =
        Timer.periodic(const Duration(seconds: 1), (_) => _updateTime());
    _petTimer =
        Timer.periodic(const Duration(minutes: 5), (_) => _petTick());

    _loadData();
    _requestPermissions();
  }

  @override
  void dispose() {
    _clockTimer?.cancel();
    _petTimer?.cancel();
    countdownTimer?.cancel();
    _bounceController.dispose();
    super.dispose();
  }

  // ==================== 权限 ====================

  Future<void> _requestPermissions() async {
    // 悬浮窗权限
    final overlayStatus =
        await Permission.systemAlertWindow.status;
    if (!overlayStatus.isGranted) {
      final result =
          await Permission.systemAlertWindow.request();
      setState(() {
        hasOverlayPermission = result.isGranted;
      });
    } else {
      setState(() {
        hasOverlayPermission = true;
      });
    }

    // 通知权限
    await Permission.notification.request();

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(hasOverlayPermission
              ? '✅ 悬浮窗权限已开启'
              : '⚠️ 请在设置中开启悬浮窗权限'),
          backgroundColor:
              hasOverlayPermission ? Colors.green : Colors.orange,
        ),
      );
    }
  }

  Future<void> _openOverlaySettings() async {
    await openAppSettings();
  }

  // ==================== 数据持久化 ====================

  Future<void> _loadData() async {
    final prefs = await SharedPreferences.getInstance();

    // 加载闹钟
    final alarmStr = prefs.getStringList('alarms') ?? [];
    setState(() {
      alarms = alarmStr
          .map((s) => AlarmItem.fromMap(
              Map<String, dynamic>.from(
                  const JsonDecoder().convert(s))))
          .toList();
    });

    // 加载日历事件
    final eventStr = prefs.getStringList('events') ?? [];
    setState(() {
      events = eventStr
          .map((s) => CalendarEvent.fromMap(
              Map<String, dynamic>.from(
                  const JsonDecoder().convert(s))))
          .toList();
    });

    // 加载宠物状态
    final hunger = prefs.getInt('pet_hunger') ?? 80;
    final happiness = prefs.getInt('pet_happiness') ?? 80;
    petState.hunger = hunger;
    petState.happiness = happiness;
    petState.updateMood();
  }

  Future<void> _saveAlarms() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(
        'alarms', alarms.map((a) => const JsonEncoder().convert(a.toMap())).toList());
  }

  Future<void> _saveEvents() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(
        'events', events.map((e) => const JsonEncoder().convert(e.toMap())).toList());
  }

  Future<void> _savePetState() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('pet_hunger', petState.hunger);
    await prefs.setInt('pet_happiness', petState.happiness);
  }

  // ==================== 时钟 ====================

  void _updateTime() {
    final now = DateTime.now();
    final currentDay = now.day;

    if (currentDay != _lastDay) {
      _lastDay = currentDay;
      for (final alarm in alarms) {
        alarm.triggeredToday = false;
      }
    }

    setState(() {
      currentTime = DateFormat('HH:mm:ss').format(now);
      currentDate = DateFormat('yyyy年MM月dd日 EEEE', 'zh_CN').format(now);
      _checkAlarms(now);
    });
  }

  void _checkAlarms(DateTime now) {
    final timeStr = DateFormat('HH:mm').format(now);
    for (final alarm in alarms) {
      if (alarm.enabled &&
          alarm.time == timeStr &&
          !alarm.triggeredToday) {
        _triggerAlarm(alarm);
        alarm.triggeredToday = true;
      }
    }
  }

  void _triggerAlarm(AlarmItem alarm) {
    HapticFeedback.heavyImpact();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('⏰ ${alarm.label} 时间到！'),
        backgroundColor: Colors.pink,
        duration: const Duration(seconds: 10),
        action: SnackBarAction(
          label: '确定',
          onPressed: () {},
          textColor: Colors.white,
        ),
      ),
    );
  }

  // ==================== 宠物 ====================

  void _petTick() {
    setState(() {
      petState.tick();
      _savePetState();
    });
  }

  void _onPetTap() {
    setState(() {
      petState.pet();
      _savePetState();
    });
  }

  void _onFeed() {
    setState(() {
      petState.feed();
      _savePetState();
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('🍖 喂食成功！宠物很开心~'),
        backgroundColor: Colors.pink,
        duration: Duration(seconds: 2),
      ),
    );
  }

  // ==================== 闹钟管理 ====================

  void _showAddAlarmDialog() {
    final timeCtrl = TextEditingController();
    final labelCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('添加闹钟'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: timeCtrl,
              decoration: const InputDecoration(
                labelText: '时间 (HH:mm)',
                hintText: '08:00',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.datetime,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: labelCtrl,
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
              onPressed: () => Navigator.pop(ctx),
              child: const Text('取消')),
          ElevatedButton(
            onPressed: () {
              final time = timeCtrl.text.trim();
              final label = labelCtrl.text.trim();
              if (RegExp(r'^\d{2}:\d{2}$').hasMatch(time)) {
                setState(() {
                  alarms.add(AlarmItem(
                    id: DateTime.now().millisecondsSinceEpoch.toString(),
                    time: time,
                    label: label.isNotEmpty ? label : '闹钟',
                  ));
                });
                _saveAlarms();
                Navigator.pop(ctx);
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.pink),
            child: const Text('添加'),
          ),
        ],
      ),
    );
  }

  void _toggleAlarm(int index) {
    setState(() => alarms[index].enabled = !alarms[index].enabled);
    _saveAlarms();
  }

  void _deleteAlarm(int index) {
    setState(() => alarms.removeAt(index));
    _saveAlarms();
  }

  // ==================== 倒计时 ====================

  void _startCountdown(int minutes) {
    setState(() {
      countdownSeconds = minutes * 60;
      countdownRunning = true;
    });
    countdownTimer?.cancel();
    countdownTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      setState(() {
        countdownSeconds--;
        if (countdownSeconds <= 0) {
          countdownRunning = false;
          countdownTimer?.cancel();
          HapticFeedback.heavyImpact();
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('⏰ 倒计时结束！'),
              backgroundColor: Colors.pink,
              duration: Duration(seconds: 10),
            ),
          );
        }
      });
    });
  }

  void _stopCountdown() {
    countdownTimer?.cancel();
    setState(() {
      countdownRunning = false;
      countdownSeconds = 0;
    });
  }

  String _formatCountdown(int seconds) {
    final m = seconds ~/ 60;
    final s = seconds % 60;
    return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
  }

  // ==================== 日历事件 ====================

  void _showAddEventDialog() {
    final titleCtrl = TextEditingController();
    final dateCtrl = TextEditingController(
        text: DateFormat('yyyy-MM-dd').format(DateTime.now()));
    final timeCtrl = TextEditingController(
        text: DateFormat('HH:mm').format(DateTime.now()));
    final notesCtrl = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('添加事件'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: titleCtrl,
                decoration: const InputDecoration(
                  labelText: '标题',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: dateCtrl,
                decoration: const InputDecoration(
                  labelText: '日期 (yyyy-MM-dd)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: timeCtrl,
                decoration: const InputDecoration(
                  labelText: '时间 (HH:mm)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: notesCtrl,
                decoration: const InputDecoration(
                  labelText: '备注',
                  border: OutlineInputBorder(),
                ),
                maxLines: 2,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('取消')),
          ElevatedButton(
            onPressed: () {
              final title = titleCtrl.text.trim();
              if (title.isNotEmpty) {
                setState(() {
                  events.add(CalendarEvent(
                    id: DateTime.now().millisecondsSinceEpoch.toString(),
                    title: title,
                    date: dateCtrl.text.trim(),
                    time: timeCtrl.text.trim(),
                    notes: notesCtrl.text.trim(),
                  ));
                });
                _saveEvents();
                Navigator.pop(ctx);
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.pink),
            child: const Text('添加'),
          ),
        ],
      ),
    );
  }

  void _deleteEvent(int index) {
    setState(() => events.removeAt(index));
    _saveEvents();
  }

  List<CalendarEvent> _getUpcomingEvents() {
    final now = DateTime.now();
    return events
        .where((e) => e.dateTime.isAfter(now))
        .toList()
      ..sort((a, b) => a.dateTime.compareTo(b.dateTime));
  }

  // ==================== UI 构建 ====================

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // 顶部：宠物 + 时钟
            _buildPetClockSection(),
            const SizedBox(height: 16),

            // 权限提示
            if (!hasOverlayPermission) _buildPermissionWarning(),
            if (!hasOverlayPermission) const SizedBox(height: 16),

            // 倒计时
            _buildCountdownSection(),
            const SizedBox(height: 16),

            // 闹钟列表
            _buildAlarmSection(),
            const SizedBox(height: 16),

            // 日历事件
            _buildCalendarSection(),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  // ---------- 宠物时钟区域 ----------

  Widget _buildPetClockSection() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.pink.shade300,
            Colors.pink.shade400,
            Colors.pinkAccent.shade200,
          ],
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.pink.withOpacity(0.3),
            blurRadius: 16,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        children: [
          // 宠物（可点击互动）
          GestureDetector(
            onTap: _onPetTap,
            child: _BouncingPetWidget(
              animation: _bounceAnimation,
              child: Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.3),
                  shape: BoxShape.circle,
                  border: Border.all(
                      color: Colors.white.withOpacity(0.5), width: 2),
                ),
                child: Center(
                  child: Text(
                    petState.mood.emoji,
                    style: const TextStyle(fontSize: 56),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: 8),

          // 心情文字
          Text(
            '${petState.mood.label} - ${petState.mood.desc}',
            style: const TextStyle(
                color: Colors.white, fontSize: 14, fontWeight: FontWeight.w500),
          ),
          const SizedBox(height: 4),

          // 饥饿/快乐进度条
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40),
            child: Row(
              children: [
                Expanded(
                  child: _buildSmallBar('🍖', petState.hunger),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildSmallBar('❤️', petState.happiness),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),

          // 喂食按钮
          SizedBox(
            height: 36,
            child: ElevatedButton.icon(
              onPressed: _onFeed,
              icon: const Icon(Icons.restaurant, size: 18),
              label: const Text('喂食'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white.withOpacity(0.9),
                foregroundColor: Colors.pink,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(18)),
              ),
            ),
          ),
          const SizedBox(height: 16),

          // 时钟
          Text(
            currentTime,
            style: const TextStyle(
              fontSize: 44,
              color: Colors.white,
              fontWeight: FontWeight.bold,
              letterSpacing: 2,
            ),
          ),
          Text(
            currentDate,
            style: TextStyle(
                color: Colors.white.withOpacity(0.8), fontSize: 13),
          ),
        ],
      ),
    );
  }

  Widget _buildSmallBar(String emoji, int value) {
    return Row(
      children: [
        Text(emoji, style: const TextStyle(fontSize: 14)),
        const SizedBox(width: 4),
        Expanded(
          child: ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: value / 100,
              backgroundColor: Colors.white.withOpacity(0.3),
              valueColor: AlwaysStoppedAnimation<Color>(
                value > 50 ? Colors.white : Colors.yellow.shade200,
              ),
              minHeight: 8,
            ),
          ),
        ),
        const SizedBox(width: 4),
        Text(
          '$value',
          style: const TextStyle(color: Colors.white, fontSize: 11),
        ),
      ],
    );
  }

  // ---------- 权限提示 ----------

  Widget _buildPermissionWarning() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.orange.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.orange.shade300),
      ),
      child: Row(
        children: [
          Icon(Icons.warning_amber, color: Colors.orange.shade700),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              '悬浮窗权限未开启，请点击开启',
              style: TextStyle(
                  color: Colors.orange.shade700, fontSize: 14),
            ),
          ),
          TextButton(
            onPressed: _openOverlaySettings,
            child: Text(
              '去设置',
              style: TextStyle(
                  color: Colors.orange.shade700,
                  fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }

  // ---------- 倒计时区域 ----------

  Widget _buildCountdownSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.pink.withOpacity(0.08),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '⏳ 倒计时',
            style: TextStyle(
                fontSize: 18, fontWeight: FontWeight.bold, color: Colors.pink),
          ),
          const SizedBox(height: 12),
          if (countdownRunning)
            Center(
              child: Text(
                _formatCountdown(countdownSeconds),
                style: const TextStyle(
                  fontSize: 48,
                  fontWeight: FontWeight.bold,
                  color: Colors.pink,
                ),
              ),
            )
          else
            Center(
              child: Text(
                countdownSeconds > 0
                    ? _formatCountdown(countdownSeconds)
                    : '00:00',
                style: TextStyle(
                  fontSize: 48,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey.shade300,
                ),
              ),
            ),
          const SizedBox(height: 12),
          if (!countdownRunning)
            Wrap(
              spacing: 8,
              runSpacing: 8,
              alignment: WrapAlignment.center,
              children: [
                _countdownBtn('1分钟', 1),
                _countdownBtn('5分钟', 5),
                _countdownBtn('10分钟', 10),
                _countdownBtn('25分钟', 25),
                _countdownBtn('60分钟', 60),
              ],
            )
          else
            Center(
              child: ElevatedButton(
                onPressed: _stopCountdown,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red.shade400,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20)),
                ),
                child: const Text('停止倒计时'),
              ),
            ),
        ],
      ),
    );
  }

  Widget _countdownBtn(String label, int minutes) {
    return ElevatedButton(
      onPressed: () => _startCountdown(minutes),
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.pink.shade50,
        foregroundColor: Colors.pink,
        shape:
            RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        side: BorderSide(color: Colors.pink.shade200),
      ),
      child: Text(label),
    );
  }

  // ---------- 闹钟区域 ----------

  Widget _buildAlarmSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.pink.withOpacity(0.08),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                '⏰ 我的闹钟',
                style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.pink),
              ),
              ElevatedButton.icon(
                onPressed: _showAddAlarmDialog,
                icon: const Icon(Icons.add, size: 16),
                label: const Text('添加'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.pink,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (alarms.isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Text(
                  '暂无闹钟，点击上方添加',
                  style: TextStyle(color: Colors.grey),
                ),
              ),
            )
          else
            ...alarms.asMap().entries.map((entry) => _buildAlarmCard(entry.value)),
        ],
      ),
    );
  }

  Widget _buildAlarmCard(AlarmItem alarm) {
    final index = alarms.indexOf(alarm);
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 1,
      child: Padding(
        padding:
            const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        child: Row(
          children: [
            Text(
              alarm.time,
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: alarm.enabled ? Colors.pink : Colors.grey,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    alarm.label,
                    style: TextStyle(
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
            Switch(
              value: alarm.enabled,
              onChanged: (_) => _toggleAlarm(index),
              activeColor: Colors.pink,
            ),
            IconButton(
              icon:
                  Icon(Icons.delete_outline, color: Colors.red.shade300),
              onPressed: () => _deleteAlarm(index),
            ),
          ],
        ),
      ),
    );
  }

  // ---------- 日历事件区域 ----------

  Widget _buildCalendarSection() {
    final upcoming = _getUpcomingEvents();
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.pink.withOpacity(0.08),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                '📅 日历事件',
                style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.pink),
              ),
              ElevatedButton.icon(
                onPressed: _showAddEventDialog,
                icon: const Icon(Icons.add, size: 16),
                label: const Text('添加'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.pink,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (upcoming.isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Text(
                  '暂无即将到来的事件',
                  style: TextStyle(color: Colors.grey),
                ),
              ),
            )
          else
            ...upcoming.asMap().entries.map((entry) =>
                _buildEventCard(entry.value)),
        ],
      ),
    );
  }

  Widget _buildEventCard(CalendarEvent event) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 1,
      child: Padding(
        padding:
            const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        child: Row(
          children: [
            Container(
              width: 4,
              height: 40,
              decoration: BoxDecoration(
                color: Colors.pink,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    event.title,
                    style: const TextStyle(
                        fontWeight: FontWeight.w600, fontSize: 15),
                  ),
                  Text(
                    '${event.date} ${event.time}',
                    style: TextStyle(
                        fontSize: 12, color: Colors.grey.shade600),
                  ),
                  if (event.notes.isNotEmpty)
                    Text(
                      event.notes,
                      style: TextStyle(
                          fontSize: 11, color: Colors.grey.shade400),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                ],
              ),
            ),
            IconButton(
              icon:
                  Icon(Icons.delete_outline, color: Colors.red.shade300),
              onPressed: () => _deleteEvent(events.indexOf(event)),
            ),
          ],
        ),
      ),
    );
  }
}

// ==================== 动画构建辅助 ====================

class _BouncingPetWidget extends AnimatedWidget {
  final Widget? child;

  const _BouncingPetWidget({
    required Animation<double> animation,
    this.child,
  }) : super(listenable: animation);

  Animation<double> get _animation => listenable as Animation<double>;

  @override
  Widget build(BuildContext context) {
    return Transform.translate(
      offset: Offset(0, _animation.value),
      child: child,
    );
  }
}
