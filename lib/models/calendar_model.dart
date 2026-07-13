class CalendarEvent {
  final String id;
  final String title;
  final String date;
  final String time;
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
