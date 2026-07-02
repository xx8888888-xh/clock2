import 'dart:async';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/pet_model.dart';

class PetProvider extends ChangeNotifier {
  PetState _state = PetState();
  Timer? _tickTimer;

  PetState get state => _state;
  PetMood get mood => _state.mood;
  int get hunger => _state.hunger;
  int get happiness => _state.happiness;

  Future<void> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    _state.hunger = prefs.getInt('pet_hunger') ?? 80;
    _state.happiness = prefs.getInt('pet_happiness') ?? 80;
    _state.updateMood();
    notifyListeners();
    startTick();
  }

  void startTick() {
    _tickTimer?.cancel();
    _tickTimer = Timer.periodic(const Duration(minutes: 5), (_) => tick());
  }

  @override
  void dispose() {
    _tickTimer?.cancel();
    super.dispose();
  }

  void tick() {
    _state.tick();
    _saveState();
    notifyListeners();
  }

  void feed() {
    _state.feed();
    _saveState();
    notifyListeners();
  }

  void pet() {
    _state.pet();
    _saveState();
    notifyListeners();
  }

  Future<void> _saveState() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('pet_hunger', _state.hunger);
    await prefs.setInt('pet_happiness', _state.happiness);
  }
}
