"""
日历集成模块
集成日历功能,显示事件并与闹钟关联
"""

import datetime
import json
import os
from datetime import datetime as dt


def get_calendar_path():
    """获取日历文件的跨平台路径"""
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app and hasattr(app, 'user_data_dir'):
            return os.path.join(app.user_data_dir, 'calendar.json')
    except Exception:
        pass
    return 'calendar.json'


class CalendarIntegration:
    """日历集成类"""

    def __init__(self):
        self.events = []
        self._load_events()

    def _load_events(self):
        """加载日历事件"""
        try:
            calendar_path = get_calendar_path()
            if os.path.exists(calendar_path):
                with open(calendar_path, 'r', encoding='utf-8') as f:
                    self.events = json.load(f)
            else:
                # 如果没有日历文件,创建一些示例事件
                self.events = self._create_sample_events()
                self._save_events()
        except Exception as e:
            print(f"加载日历事件失败: {e}")
            self.events = self._create_sample_events()
            self._save_events()

    def _save_events(self):
        """保存日历事件"""
        try:
            calendar_path = get_calendar_path()
            # 确保目录存在
            os.makedirs(os.path.dirname(calendar_path) if os.path.dirname(calendar_path) else '.', exist_ok=True)
            with open(calendar_path, 'w', encoding='utf-8') as f:
                json.dump(self.events, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存日历事件失败: {e}")

    def _create_sample_events(self):
        """创建示例日历事件 - 使用动态日期"""
        now = datetime.datetime.now()
        
        # 创建未来7天内的事件
        events = []
        
        # 今天的事件（如果还没过的话
        if now.hour < 23:
            events.append({
                'title': '每日提醒',
                'date': now.strftime('%Y-%m-%d'),
                'time': '21:00',
                'type': 'normal',
                'description': '今日待办提醒'
            })
        
        # 明天的事件
        tomorrow = now + datetime.timedelta(days=1)
        events.append({
            'title': '工作会议',
            'date': tomorrow.strftime('%Y-%m-%d'),
            'time': '09:00',
            'type': 'meeting',
            'description': '团队周会'
        })
        
        # 后天的事件
        day_after = now + datetime.timedelta(days=2)
        events.append({
            'title': '健身',
            'date': day_after.strftime('%Y-%m-%d'),
            'time': '19:00',
            'type': 'exercise',
            'description': '健身房锻炼'
        })
        
        # 下周的事件
        next_week = now + datetime.timedelta(days=5)
        events.append({
            'title': '周末活动',
            'date': next_week.strftime('%Y-%m-%d'),
            'time': '10:00',
            'type': 'normal',
            'description': '周末计划'
        })
        
        return events

    def get_next_event(self):
        """获取下一个即将到来的日历事件"""
        now = datetime.datetime.now()

        for event in self.events:
            try:
                event_datetime = datetime.datetime.strptime(
                    f"{event.get('date', '')} {event.get('time', '')}", 
                    "%Y-%m-%d %H:%M"
                )

                # 如果是今天的事件且在当前时间之后
                if event_datetime.date() == now.date() and event_datetime > now:
                    return event
                
                # 如果是未来事件
                if event_datetime > now:
                    return event
            except (KeyError, ValueError) as e:
                print(f"解析事件日期失败: {e}")
                continue

        return None

    def get_today_events(self):
        """获取今天的所有事件"""
        today = datetime.datetime.now().date()
        today_events = []

        for event in self.events:
            try:
                event_date = datetime.datetime.strptime(
                    event.get('date', ''), 
                    "%Y-%m-%d"
                ).date()
                if event_date == today:
                    today_events.append(event)
            except (KeyError, ValueError):
                continue

        return today_events

    def add_event(self, title, date, time, event_type='normal', description=''):
        """添加新的日历事件"""
        new_event = {
            'title': title,
            'date': date,
            'time': time,
            'type': event_type,
            'description': description,
            'created': datetime.datetime.now().isoformat()
        }

        self.events.append(new_event)
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
            if event.get('time', '') == alarm_time and event.get('type', '') == event_type:
                matching_events.append(event)

        return matching_events

    def get_event_by_type(self, event_type):
        """获取特定类型的日历事件"""
        return [event for event in self.events if event.get('type', '') == event_type]

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
        """检查并清理过期事件"""
        now = datetime.datetime.now()
        overdue_events = []
        
        new_events = []
        for event in self.events:
            try:
                event_datetime = datetime.datetime.strptime(
                    f"{event.get('date', '')} {event.get('time', '')}", 
                    "%Y-%m-%d %H:%M"
                )
                if event_datetime < now:
                    overdue_events.append(event)
                else:
                    new_events.append(event)
            except (KeyError, ValueError):
                # 保留无法解析的事件
                new_events.append(event)
        
        # 更新事件列表并保存
        if overdue_events:
            self.events = new_events
            self._save_events()
        
        return overdue_events
    
    def get_upcoming_events(self, days=7):
        """获取未来N天的事件"""
        now = datetime.datetime.now()
        end_date = now + datetime.timedelta(days=days)
        upcoming = []
        
        for event in self.events:
            try:
                event_datetime = datetime.datetime.strptime(
                    f"{event.get('date', '')} {event.get('time', '')}", 
                    "%Y-%m-%d %H:%M"
                )
                if now <= event_datetime <= end_date:
                    upcoming.append(event)
            except (KeyError, ValueError):
                continue
        
        # 按时间排序
        upcoming.sort(key=lambda x: datetime.datetime.strptime(
            f"{x.get('date', '')} {x.get('time', '')}", "%Y-%m-%d %H:%M"
        ))
        
        return upcoming
