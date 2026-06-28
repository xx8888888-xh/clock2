"""
日历集成模块
集成日历功能,显示事件并与闹钟关联
"""

import datetime
import json
import os
from datetime import datetime as dt

class CalendarIntegration:
    """日历集成类"""

    def __init__(self):
        self.events = []
        self._load_events()

    def _load_events(self):
        """加载日历事件"""
        try:
            with open('calendar.json', 'r') as f:
                self.events = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # 如果没有日历文件或文件损坏,创建一些示例事件
            self.events = self._create_sample_events()
            self._save_events()

    def _save_events(self):
        """保存日历事件（原子写入：先写临时文件再rename）"""
        tmp_path = 'calendar.json.tmp'
        try:
            with open(tmp_path, 'w') as f:
                json.dump(self.events, f)
            os.replace(tmp_path, 'calendar.json')
        except OSError as e:
            # 如果写入失败，清理临时文件
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise IOError(f"保存日历失败: {e}") from e

    def _create_sample_events(self):
        """创建示例日历事件"""
        return [
            {
                'title': '生日',
                'date': '2026-05-01',
                'time': '12:00',
                'event_type': 'birthday',
                'description': '朋友生日派对'
            },
            {
                'title': '工作会议',
                'date': '2026-05-02',
                'time': '09:00',
                'event_type': 'meeting',
                'description': '每周团队会议'
            },
            {
                'title': '健身房',
                'date': '2026-05-03',
                'time': '19:00',
                'event_type': 'exercise',
                'description': '健身锻炼'
            }
        ]

    def _sort_events(self):
        """按日期和时间排序事件"""
        self.events.sort(key=lambda e: (e.get('date', ''), e.get('time', '')))

    def get_next_event(self):
        """获取下一个即将到来的日历事件"""
        now = datetime.datetime.now()

        for event in self.events:
            event_datetime = datetime.datetime.strptime(f"{event['date']} {event['time']}", "%Y-%m-%d %H:%M")

            # 如果是今天的事件
            if event_datetime.date() == now.date():
                if event_datetime > now:
                    return event

        return None

    def get_today_events(self):
        """获取今天的所有事件"""
        today = datetime.datetime.now().date()
        today_events = []

        for event in self.events:
            event_date = datetime.datetime.strptime(event['date'], "%Y-%m-%d").date()
            if event_date == today:
                today_events.append(event)

        return today_events

    def add_event(self, title, date, time, event_type='normal', description=''):
        """添加新的日历事件"""
        new_event = {
            'title': title,
            'date': date,
            'time': time,
            'event_type': event_type,
            'description': description,
            'created': datetime.datetime.now().isoformat()
        }

        self.events.append(new_event)
        self._sort_events()
        self._save_events()

        return new_event

    def delete_event(self, event_title):
        """删除日历事件"""
        self.events = [event for event in self.events if event.get('title', '') != event_title]
        self._save_events()

    def link_to_alarm(self, alarm_time, event_type):
        """将闹钟与日历事件关联"""
        # 查找匹配的事件
        matching_events = []
        for event in self.events:
            if event.get('time', '') == alarm_time and event.get('event_type', '') == event_type:
                matching_events.append(event)

        return matching_events

    def get_event_by_type(self, event_type):
        """获取特定类型的日历事件"""
        return [event for event in self.events if event.get('event_type', '') == event_type]

    def get_event_emoji(self, event_type):
        """根据事件类型获取emoji"""
        emoji_map = {
            'birthday': '🎂',
            'meeting': '📅',
            'exercise': '🏋️',
            'work': '💼',
            'study': '📚',
            'travel': '✈️',
            'normal': '📝'
        }

        return emoji_map.get(event_type, '📝')

    def check_overdue_events(self):
        """检查过期事件"""
        now = datetime.datetime.now()
        overdue_events = []
        
        for event in self.events:
            try:
                event_datetime = datetime.datetime.strptime(f"{event.get('date', '')} {event.get('time', '')}", "%Y-%m-%d %H:%M")
                if event_datetime < now:
                    overdue_events.append(event)
            except (KeyError, ValueError):
                continue
        
        # 删除过期事件
        if overdue_events:
            new_events = []
            for event in self.events:
                try:
                    event_datetime = datetime.datetime.strptime(f"{event.get('date', '')} {event.get('time', '')}", "%Y-%m-%d %H:%M")
                    if event_datetime >= now:
                        new_events.append(event)
                except (KeyError, ValueError):
                    new_events.append(event)
            self.events = new_events
            self._save_events()
        
        return overdue_events
