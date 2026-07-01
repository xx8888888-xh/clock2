"""
宠物心情系统
宠物会根据时间、互动、天气、日历事件等改变心情状态
"""

import datetime
import random

class PetMoodSystem:
    """宠物心情系统"""
    
    def __init__(self):
        # 心情状态定义
        self.moods = {
            'happy': {
                'color': (1, 0.9, 0.1, 1),  # 金色
                'animation': 'happy',
                'speed': 1.2
            },
            'normal': {
                'color': (1, 1, 1, 1),  # 白色
                'animation': 'idle',
                'speed': 1.0
            },
            'sleepy': {
                'color': (0.5, 0.5, 1, 1),  # 蓝色
                'animation': 'sleep',
                'speed': 0.6
            },
            'excited': {
                'color': (1, 0.5, 0, 1),  # 橙色
                'animation': 'excited',
                'speed': 1.5
            },
            'angry': {
                'color': (1, 0, 0, 1),  # 红色
                'animation': 'angry',
                'speed': 1.8
            }
        }
        
        self.current_mood = 'normal'
        self.last_interaction_time = datetime.datetime.now()
        self.interaction_count = 0
        
    def get_current_mood(self, current_time, weather_impact, calendar_event=None):
        """
        计算当前心情状态
        Args:
            current_time: 当前时间
            weather_impact: 天气影响 ('sunny', 'rainy', 'cloudy', etc.)
            calendar_event: 日历事件信息
        """
        # 基础心情计算
        mood_score = 0
        
        # 1. 时间影响
        hour = current_time.hour
        if hour >= 6 and hour <= 10:
            mood_score += 10  # 早晨活跃
        elif hour >= 22:
            mood_score -= 5   # 夜晚困倦
        
        # 2. 天气影响
        if weather_impact == 'sunny':
            mood_score += 15
        elif weather_impact == 'rainy':
            mood_score -= 10
        elif weather_impact == 'cloudy':
            mood_score -= 5
        
        # 3. 互动影响
        time_diff = current_time - self.last_interaction_time
        if time_diff.total_seconds() < 300:  # 5分钟内互动过
            mood_score += 10
        
        # 4. 日历事件影响
        if calendar_event:
            if calendar_event['type'] == 'birthday':
                mood_score += 20
            elif calendar_event['type'] == 'meeting':
                mood_score -= 10
        
        # 5. 随机因素
        mood_score += random.randint(-5, 5)
        
        # 确定最终心情
        if mood_score >= 20:
            return 'excited'
        elif mood_score >= 10:
            return 'happy'
        elif mood_score >= 0:
            return 'normal'
        elif mood_score >= -10:
            return 'sleepy'
        else:
            return 'angry'
    
    def update_interaction(self):
        """记录互动，提升心情"""
        self.last_interaction_time = datetime.datetime.now()
        self.interaction_count += 1
        
        if self.interaction_count >= 3:
            self.current_mood = 'happy'
    
    def get_mood_color(self, mood):
        """获取心情对应的颜色"""
        return self.moods[mood]['color']
    
    def get_mood_animation(self, mood):
        """获取心情对应的动画类型"""
        return self.moods[mood]['animation']
    
    def get_mood_speed(self, mood):
        """获取心情对应的动画速度"""
        return self.moods[mood]['speed']
    
    def generate_mood_emoji(self, mood):
        """生成心情表情"""
        emoji_map = {
            'happy': '😊',
            'normal': '😐',
            'sleepy': '😴',
            'excited': '😄',
            'angry': '😠'
        }
        return emoji_map.get(mood, '😐')
    
    def get_mood_description(self, mood):
        """获取心情描述"""
        description_map = {
            'happy': '心情愉快，活泼可爱',
            'normal': '心情平静，正常状态',
            'sleepy': '有点困倦，想要睡觉',
            'excited': '非常兴奋，活力满满',
            'angry': '有点生气，需要安抚'
        }
        return description_map.get(mood, '心情正常')