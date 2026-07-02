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
