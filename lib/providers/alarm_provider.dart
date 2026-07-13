import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/alarm_model.dart';

class AlarmProvider extends ChangeNotifier {
  List<AlarmItem> _alarms = [];
  int _lastDay = 0;

  List<AlarmItem> get alarms => _alarms;

  Future<void> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    final alarmStr = prefs.getStringList('alarms') ?? [];
    _alarms = alarmStr
        .map((s) => AlarmItem.fromMap(
            Map<String, dynamic>.from(const JsonDecoder().convert(s))))
        .toList();
    notifyListeners();
  }

  void startAlarmCheck(void Function(AlarmItem) onAlarmTriggered) {
    Timer.periodic(const Duration(seconds: 1), (_) => _check(onAlarmTriggered));
  }

  void _check(void Function(AlarmItem) onAlarmTriggered) {
    final now = DateTime.now();
    if (now.day != _lastDay) {
      _lastDay = now.day;
      for (final a in _alarms) a.triggeredToday = false;
    }
    final timeStr = DateFormat('HH:mm').format(now);
    for (final alarm in _alarms) {
      if (alarm.enabled && alarm.time == timeStr && !alarm.triggeredToday) {
        HapticFeedback.heavyImpact();
        onAlarmTriggered(alarm);
        alarm.triggeredToday = true;
        _saveAlarms();
        notifyListeners();
      }
    }
  }

  Future<void> addAlarm(String time, String label) async {
    _alarms.add(AlarmItem(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      time: time,
      label: label,
    ));
    await _saveAlarms();
    notifyListeners();
  }

  Future<void> toggleAlarm(int index) async {
    _alarms[index].enabled = !_alarms[index].enabled;
    await _saveAlarms();
    notifyListeners();
  }

  Future<void> deleteAlarm(int index) async {
    _alarms.removeAt(index);
    await _saveAlarms();
    notifyListeners();
  }

  Future<void> _saveAlarms() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(
      'alarms',
      _alarms.map((a) => const JsonEncoder().convert(a.toMap())).toList(),
    );
  }
}
