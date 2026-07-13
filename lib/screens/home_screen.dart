import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';

import '../providers/pet_provider.dart';
import '../providers/alarm_provider.dart';
import '../providers/countdown_provider.dart';
import '../providers/calendar_provider.dart';
import '../providers/permission_provider.dart';
import '../models/alarm_model.dart';
import '../models/calendar_model.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => HomeScreenState();
}

class HomeScreenState extends State<HomeScreen>
    with SingleTickerProviderStateMixin {
  String _currentTime = '';
  String _currentDate = '';
  Timer? _clockTimer;

  late AnimationController _bounceController;
  late Animation<double> _bounceAnimation;

  @override
  void initState() {
    super.initState();

    _bounceController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..repeat(reverse: true);
    _bounceAnimation = Tween<double>(begin: 0, end: -12).animate(_bounceController);

    _updateTime();
    _clockTimer = Timer.periodic(const Duration(seconds: 1), (_) => _updateTime());

    _initProviders();
  }

  Future<void> _initProviders() async {
    final permProvider = context.read<PermissionProvider>();
    final petProvider = context.read<PetProvider>();
    final alarmProvider = context.read<AlarmProvider>();
    final calendarProvider = context.read<CalendarProvider>();

    await permProvider.initialize();
    await petProvider.initialize();
    await alarmProvider.initialize();
    await calendarProvider.initialize();

    alarmProvider.startAlarmCheck(_onAlarmTriggered);
    petProvider.startTick();

    if (mounted) {
      permProvider.showPermissionSnackBar(context);
    }
  }

  void _updateTime() {
    final now = DateTime.now();
    setState(() {
      _currentTime = DateFormat('HH:mm:ss').format(now);
      _currentDate = DateFormat('yyyy年MM月dd日 EEEE', 'zh_CN').format(now);
    });
  }

  void _onAlarmTriggered(AlarmItem alarm) {
    if (!mounted) return;
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

  @override
  void dispose() {
    _clockTimer?.cancel();
    _bounceController.dispose();
    super.dispose();
  }

  // ==================== 宠物 ====================

  void _onPetTap() => context.read<PetProvider>().pet();

  void _onFeed() {
    context.read<PetProvider>().feed();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('🍖 喂食成功！宠物很开心~'),
        backgroundColor: Colors.pink,
        duration: Duration(seconds: 2),
      ),
    );
  }

  // ==================== 闹钟 ====================

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
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('取消')),
          ElevatedButton(
            onPressed: () {
              final time = timeCtrl.text.trim();
              final label = labelCtrl.text.trim();
              if (RegExp(r'^\d{2}:\d{2}$').hasMatch(time)) {
                context.read<AlarmProvider>().addAlarm(
                  time,
                  label.isNotEmpty ? label : '闹钟',
                );
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

  // ==================== 倒计时 ====================

  void _startCountdown(int minutes) {
    context.read<CountdownProvider>().start(minutes, () {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('⏰ 倒计时结束！'),
          backgroundColor: Colors.pink,
          duration: Duration(seconds: 10),
        ),
      );
    });
  }

  // ==================== 日历 ====================

  void _showAddEventDialog() {
    final titleCtrl = TextEditingController();
    final dateCtrl = TextEditingController(
      text: DateFormat('yyyy-MM-dd').format(DateTime.now()),
    );
    final timeCtrl = TextEditingController(
      text: DateFormat('HH:mm').format(DateTime.now()),
    );
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
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('取消')),
          ElevatedButton(
            onPressed: () {
              final title = titleCtrl.text.trim();
              if (title.isNotEmpty) {
                context.read<CalendarProvider>().addEvent(CalendarEvent(
                  id: DateTime.now().millisecondsSinceEpoch.toString(),
                  title: title,
                  date: dateCtrl.text.trim(),
                  time: timeCtrl.text.trim(),
                  notes: notesCtrl.text.trim(),
                ));
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

  // ==================== UI ====================

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _buildPetClockSection(),
            const SizedBox(height: 16),
            _buildPermissionWarning(),
            const SizedBox(height: 16),
            _buildCountdownSection(),
            const SizedBox(height: 16),
            _buildAlarmSection(),
            const SizedBox(height: 16),
            _buildCalendarSection(),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildPetClockSection() {
    return Consumer<PetProvider>(
      builder: (context, pet, _) {
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
              // 宠物
              GestureDetector(
                onTap: _onPetTap,
                child: AnimatedBuilder(
                  animation: _bounceAnimation,
                  builder: (_, __) => Transform.translate(
                    offset: Offset(0, _bounceAnimation.value),
                    child: Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.3),
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white.withOpacity(0.5), width: 2),
                      ),
                      child: Center(
                        child: Text(pet.mood.emoji, style: const TextStyle(fontSize: 56)),
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '${pet.mood.label} - ${pet.mood.desc}',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 4),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 40),
                child: Row(
                  children: [
                    Expanded(child: _buildSmallBar('🍖', pet.hunger)),
                    const SizedBox(width: 16),
                    Expanded(child: _buildSmallBar('❤️', pet.happiness)),
                  ],
                ),
              ),
              const SizedBox(height: 12),
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
                      borderRadius: BorderRadius.circular(18),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Text(
                _currentTime,
                style: const TextStyle(
                  fontSize: 44,
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 2,
                ),
              ),
              Text(
                _currentDate,
                style: TextStyle(color: Colors.white.withOpacity(0.8), fontSize: 13),
              ),
            ],
          ),
        );
      },
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
        Text('$value', style: const TextStyle(color: Colors.white, fontSize: 11)),
      ],
    );
  }

  Widget _buildPermissionWarning() {
    return Consumer<PermissionProvider>(
      builder: (context, perm, _) {
        if (perm.hasOverlayPermission) return const SizedBox.shrink();
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
                  style: TextStyle(color: Colors.orange.shade700, fontSize: 14),
                ),
              ),
              TextButton(
                onPressed: () async {
                  final granted = await perm.requestOverlayPermission();
                  if (!granted && context.mounted) {
                    perm.openSettings();
                  }
                },
                child: Text(
                  '去设置',
                  style: TextStyle(
                    color: Colors.orange.shade700,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildCountdownSection() {
    return Consumer<CountdownProvider>(
      builder: (context, cd, _) {
        return Container(
          padding: const EdgeInsets.all(16),
          decoration: _cardDecoration(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '⏳ 倒计时',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.pink,
                ),
              ),
              const SizedBox(height: 12),
              Center(
                child: Text(
                  cd.formatted,
                  style: TextStyle(
                    fontSize: 48,
                    fontWeight: FontWeight.bold,
                    color: cd.running ? Colors.pink : Colors.grey.shade300,
                  ),
                ),
              ),
              const SizedBox(height: 12),
              if (!cd.running)
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
                    onPressed: cd.stop,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red.shade400,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(20),
                      ),
                    ),
                    child: const Text('停止倒计时'),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }

  Widget _countdownBtn(String label, int minutes) {
    return ElevatedButton(
      onPressed: () => _startCountdown(minutes),
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.pink.shade50,
        foregroundColor: Colors.pink,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        side: BorderSide(color: Colors.pink.shade200),
      ),
      child: Text(label),
    );
  }

  Widget _buildAlarmSection() {
    return Consumer<AlarmProvider>(
      builder: (context, alarmProv, _) {
        return Container(
          padding: const EdgeInsets.all(16),
          decoration: _cardDecoration(),
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
                      color: Colors.pink,
                    ),
                  ),
                  ElevatedButton.icon(
                    onPressed: _showAddAlarmDialog,
                    icon: const Icon(Icons.add, size: 16),
                    label: const Text('添加'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.pink,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              if (alarmProv.alarms.isEmpty)
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(16),
                    child: Text('暂无闹钟，点击上方添加', style: TextStyle(color: Colors.grey)),
                  ),
                )
              else
                ...alarmProv.alarms.asMap().entries.map(
                  (entry) => _buildAlarmCard(entry.value, entry.key),
                ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildAlarmCard(AlarmItem alarm, int index) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 1,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
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
              onChanged: (_) => context.read<AlarmProvider>().toggleAlarm(index),
              activeColor: Colors.pink,
            ),
            IconButton(
              icon: Icon(Icons.delete_outline, color: Colors.red.shade300),
              onPressed: () => context.read<AlarmProvider>().deleteAlarm(index),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCalendarSection() {
    return Consumer<CalendarProvider>(
      builder: (context, calProv, _) {
        return Container(
          padding: const EdgeInsets.all(16),
          decoration: _cardDecoration(),
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
                      color: Colors.pink,
                    ),
                  ),
                  ElevatedButton.icon(
                    onPressed: _showAddEventDialog,
                    icon: const Icon(Icons.add, size: 16),
                    label: const Text('添加'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.pink,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              if (calProv.upcomingEvents.isEmpty)
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(16),
                    child: Text('暂无即将到来的事件', style: TextStyle(color: Colors.grey)),
                  ),
                )
              else
                ...calProv.upcomingEvents.asMap().entries.map(
                  (entry) => _buildEventCard(entry.value, entry.key),
                ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildEventCard(CalendarEvent event, int index) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 1,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
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
                    style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15),
                  ),
                  Text(
                    '${event.date} ${event.time}',
                    style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                  ),
                  if (event.notes.isNotEmpty)
                    Text(
                      event.notes,
                      style: TextStyle(fontSize: 11, color: Colors.grey.shade400),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                ],
              ),
            ),
            IconButton(
              icon: Icon(Icons.delete_outline, color: Colors.red.shade300),
              onPressed: () => context.read<CalendarProvider>().deleteEvent(index),
            ),
          ],
        ),
      ),
    );
  }

  BoxDecoration _cardDecoration() {
    return BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(20),
      boxShadow: [
        BoxShadow(
          color: Colors.pink.withOpacity(0.08),
          blurRadius: 8,
          offset: const Offset(0, 4),
        ),
      ],
    );
  }
}
