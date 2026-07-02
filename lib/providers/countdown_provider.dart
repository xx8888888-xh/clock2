import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class CountdownProvider extends ChangeNotifier {
  int _seconds = 0;
  bool _running = false;
  Timer? _timer;

  int get seconds => _seconds;
  bool get running => _running;
  String get formatted =>
      '${(_seconds ~/ 60).toString().padLeft(2, '0')}:${(_seconds % 60).toString().padLeft(2, '0')}';

  void start(int minutes, VoidCallback onComplete) {
    _timer?.cancel();
    _seconds = minutes * 60;
    _running = true;
    notifyListeners();

    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (_seconds > 0) {
        _seconds--;
        notifyListeners();
      } else {
        stop();
        HapticFeedback.heavyImpact();
        onComplete();
      }
    });
  }

  void stop() {
    _timer?.cancel();
    _running = false;
    _seconds = 0;
    notifyListeners();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
}
