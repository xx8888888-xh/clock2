import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'dart:async';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '宠物闹钟',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: FloatingPetWindow(),
    );
  }
}

class FloatingPetWindow extends StatefulWidget {
  @override
  _FloatingPetWindowState createState() => _FloatingPetWindowState();
}

class _FloatingPetWindowState extends State<FloatingPetWindow> {
  Offset position = Offset(100, 100);
  bool isVisible = true;
  String currentTime = '';

  @override
  void initState() {
    super.initState();
    _updateTime();
    // 每秒更新一次时间
    Timer.periodic(Duration(seconds: 1), (timer) {
      _updateTime();
    });
  }

  void _updateTime() {
    setState(() {
      currentTime = DateFormat('HH:mm:ss').format(DateTime.now());
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Stack(
        children: [
          Positioned(
            left: position.dx,
            top: position.dy,
            child: GestureDetector(
              onPanUpdate: (details) {
                setState(() {
                  position = position + details.delta;
                });
              },
              child: Container(
                width: 150,
                height: 180,
                decoration: BoxDecoration(
                  color: Color(0xFF8FB1FF).withOpacity(0.9),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.3),
                      blurRadius: 8,
                      offset: Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      '🐾',
                      style: TextStyle(fontSize: 50),
                    ),
                    SizedBox(height: 10),
                    Text(
                      currentTime,
                      style: TextStyle(
                        fontSize: 20,
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      '宠物闹钟',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.white70,
                      ),
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
}