import 'package:flutter/services.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:flutter/material.dart';

class PermissionProvider extends ChangeNotifier {
  bool _hasOverlayPermission = false;
  bool _hasNotificationPermission = false;
  bool _isInitialized = false;

  bool get hasOverlayPermission => _hasOverlayPermission;
  bool get hasNotificationPermission => _hasNotificationPermission;
  bool get isInitialized => _isInitialized;

  Future<void> initialize() async {
    if (_isInitialized) return;
    final overlay = await Permission.systemAlertWindow.status;
    _hasOverlayPermission = overlay.isGranted;
    final notif = await Permission.notification.status;
    _hasNotificationPermission = notif.isGranted;
    _isInitialized = true;
    notifyListeners();
  }

  Future<bool> requestOverlayPermission() async {
    final result = await Permission.systemAlertWindow.request();
    _hasOverlayPermission = result.isGranted;
    notifyListeners();
    return result.isGranted;
  }

  Future<bool> requestNotificationPermission() async {
    final result = await Permission.notification.request();
    _hasNotificationPermission = result.isGranted;
    notifyListeners();
    return result.isGranted;
  }

  Future<void> openSettings() async {
    await openAppSettings();
  }

  void showPermissionSnackBar(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(_hasOverlayPermission
            ? '✅ 悬浮窗权限已开启'
            : '⚠️ 请在设置中开启悬浮窗权限'),
        backgroundColor: _hasOverlayPermission ? Colors.green : Colors.orange,
      ),
    );
  }
}
