import 'package:flutter/material.dart';
import 'package:overlay_support/overlay_support.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return OverlaySupport(
      child: MaterialApp(
        title: '宠物闹钟',
        theme: ThemeData(
          primarySwatch: Colors.blue,
        ),
        home: FloatingPetWindow(),
      ),
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

  @override
  void initState() {
    super.initState();
    // 初始化悬浮窗
    showOverlay();
  }

  void showOverlay() {
    Overlay.of(context).insert(
      OverlayEntry(
        builder: (context) => Positioned(
          left: position.dx,
          top: position.dy,
          child: GestureDetector(
            onPanUpdate: (details) {
              setState(() {
                position = position + details.delta;
              });
            },
            child: Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                color: Color(0xFF8FB1),
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.3),
                    blurRadius: 4,
                    offset: Offset(0, 2),
                  ),
                ],
              ),
              child: Center(
                child: Text(
                  '🐾',
                  style: TextStyle(fontSize: 40),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Container(),
    );
  }
}