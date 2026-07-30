"""
日历集成模块
集成日历功能,显示事件并与闹钟关联
"""

import datetime
import json
import os



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
        self._update_timer = None
        self._load_events()
        # 修复Bug：删除重复的 cleanup_old_events() 调用
        # _load_events 中已包含清理过期事件（现在会保存），无需再次调用

    def _load_events(self):
        """加载日历事件"""
        try:
            calendar_path = get_calendar_path()
            if os.path.exists(calendar_path):
                with open(calendar_path, 'r', encoding='utf-8') as f:
                    self.events = json.load(f)
                # 自动清理过期事件
                self.cleanup_old_events()
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
            calendar_dir = os.path.dirname(calendar_path)
            if calendar_dir:
                os.makedirs(calendar_dir, exist_ok=True)
            with open(calendar_path, 'w', encoding='utf-8') as f:
                json.dump(self.events, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存日历事件失败: {e}")

    def cleanup_old_events(self):
        """清理过期事件并保存到文件（供外部调用）"""
        now = datetime.datetime.now()
        new_events = []
        for event in list(self.events):  # 复制列表避免迭代中修改导致RuntimeError
            try:
                event_datetime = datetime.datetime.strptime(
                    f"{event.get('date', '')} {event.get('time', '')}",
                    "%Y-%m-%d %H:%M"
                )
                if event_datetime >= now:
                    new_events.append(event)
            except (KeyError, ValueError):
                # 🔒 安全：不再打印 event.get('title')，避免泄露用户隐私
                # 解析失败的事件直接丢弃，不保留不显示
                pass
        self.events = new_events
        # 保存到文件，否则重启app过期事件仍会出现
        self._save_events()
        return len(new_events)

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
        """获取下一个即将到来的日历事件（返回最近的一个）"""
        now = datetime.datetime.now()
        next_event = None
        next_datetime = None

        for event in self.events:
            try:
                event_datetime = datetime.datetime.strptime(
                    f"{event.get('date', '')} {event.get('time', '')}", 
                    "%Y-%m-%d %H:%M"
                )
                # 只考虑未来事件
                if event_datetime > now:
                    if next_datetime is None or event_datetime < next_datetime:
                        next_datetime = event_datetime
                        next_event = event
            except (KeyError, ValueError):
                # 🔒 安全：不再打印事件标题，避免泄露用户隐私
                continue

        return next_event

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
    
    def cleanup(self):
        """清理资源，防止内存泄漏"""
        # 取消定时器
        if self._update_timer:
            self._update_timer.cancel()
            self._update_timer = None
        
        # 清空事件列表
        self.events = []
