"""
日历集成模块
集成日历功能，显示事件并与闹钟关联
"""

import datetime
import json
from datetime import datetime as dt

class CalendarIntegration:
    """日历集成类"""
    
    def __init__(self):
        self.events = []
        self._load_events()
    
    def _load_events(self):
        """加载日历事件"""
        try:
            # 修复BUG-029和BUG-037: 添加编码参数和错误处理
            with open('calendar.json', 'r', encoding='utf-8') as f:
                self.events = json.load(f)
            print("日历事件加载成功")
        except FileNotFoundError:
            # 如果没有日历文件，创建一些示例事件
            print("日历文件不存在，创建示例事件")
            self.events = self._create_sample_events()
            self._save_events()
        except json.JSONDecodeError as e:
            print(f"日历JSON解析错误: {e}，使用示例事件")
            self.events = self._create_sample_events()
            self._save_events()
        except PermissionError:
            print("没有日历文件读取权限，使用示例事件")
            self.events = self._create_sample_events()
        except Exception as e:
            print(f"日历加载未知错误: {e}，使用示例事件")
            self.events = self._create_sample_events()
    
    def _save_events(self):
        """保存日历事件"""
        try:
            with open('calendar.json', 'w', encoding='utf-8') as f:
                json.dump(self.events, f, ensure_ascii=False, indent=2)
            print("日历事件保存成功")
        except Exception as e:
            print(f"日历保存失败: {e}")
    
    def _create_sample_events(self):
        """创建示例日历事件"""
        return [
            {
                'title': '生日',
                'date': '2024-05-01',
                'time': '12:00',
                'type': 'birthday',
                'description': '朋友生日派对'
            },
            {
                'title': '工作会议',
                'date': '2024-05-02',
                'time': '09:00',
                'type': 'meeting',
                'description': '每周团队会议'
            },
            {
                'title': '健身房',
                'date': '2024-05-03',
                'time': '19:00',
                'type': 'exercise',
                'description': '健身锻炼'
            }
        ]
    
    def get_next_event(self):
        """获取下一个即将到来的日历事件"""
        now = datetime.datetime.now()
        
        for event in self.events:
            try:
                # 修复BUG-038: 添加日期解析错误处理
                event_datetime = datetime.datetime.strptime(f"{event.get('date', '')} {event.get('time', '')}", "%Y-%m-%d %H:%M")
                
                # 如果是今天的事件
                if event_datetime.date() == now.date():
                    if event_datetime > now:
                        return event
            except (ValueError, KeyError) as e:
                print(f"事件日期解析错误: {e}, 事件: {event.get('title', '未知')}")
                continue
        
        return None
    
    def get_today_events(self):
        """获取今天的所有事件"""
        today = datetime.datetime.now().date()
        today_events = []
        
        for event in self.events:
            try:
                event_date = datetime.datetime.strptime(event.get('date', ''), "%Y-%m-%d").date()
                if event_date == today:
                    today_events.append(event)
            except (ValueError, KeyError) as e:
                print(f"今天事件日期解析错误: {e}, 事件: {event.get('title', '未知')}")
                continue
        
        return today_events
    
    def add_event(self, title, date, time, type='normal', description=''):
        """添加新的日历事件"""
        new_event = {
            'title': title,
            'date': date,
            'time': time,
            'type': type,
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
    
    def check_overdue_events2(self):
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
            self.events = []
            for event in self.events:
                try:
                    event_datetime = datetime.datetime.strptime(f"{event.get('date', '')} {event.get('time', '')}", "%Y-%m-%d %H:%M")
                    if event_datetime >= now:
                        self.events.append(event)
                except (KeyError, ValueError):
                    self.events.append(event)
            self._save_events()
        
        return overdue_events