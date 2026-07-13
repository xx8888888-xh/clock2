import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/calendar_model.dart';

class CalendarProvider extends ChangeNotifier {
  List<CalendarEvent> _events = [];

  List<CalendarEvent> get events => _events;

  List<CalendarEvent> get upcomingEvents {
    final now = DateTime.now();
    return _events.where((e) => e.dateTime.isAfter(now)).toList()
      ..sort((a, b) => a.dateTime.compareTo(b.dateTime));
  }

  Future<void> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    final eventStr = prefs.getStringList('events') ?? [];
    _events = eventStr
        .map((s) => CalendarEvent.fromMap(
            Map<String, dynamic>.from(const JsonDecoder().convert(s))))
        .toList();
    notifyListeners();
  }

  Future<void> addEvent(CalendarEvent event) async {
    _events.add(event);
    await _saveEvents();
    notifyListeners();
  }

  Future<void> deleteEvent(int index) async {
    _events.removeAt(index);
    await _saveEvents();
    notifyListeners();
  }

  Future<void> _saveEvents() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(
      'events',
      _events.map((e) => const JsonEncoder().convert(e.toMap())).toList(),
    );
  }
}
