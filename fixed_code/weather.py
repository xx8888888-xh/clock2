"""
天气API集成模块
获取实时天气信息并影响宠物行为
"""

import requests
import json
import datetime

class WeatherAPI:
    """天气API类"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or 'demo_key'  # 默认使用免费API
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.last_weather_data = None
        self.has_data = False
        
    def get_current_weather(self, city="Beijing"):
        """
        获取当前天气信息
        Args:
            city: 城市名称
        Returns:
            dict: 天气信息
        """
        try:
            # 如果API密钥是demo_key，使用模拟数据
            if self.api_key == 'demo_key':
                return self._get_default_weather()
                
            # 使用OpenWeatherMap API
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'zh'
            }
            
            # 修复BUG-028和BUG-034: 添加超时和网络错误处理
            try:
                response = requests.get(self.base_url, params=params, timeout=10)  # 10秒超时
            except requests.exceptions.Timeout:
                print("天气API请求超时，使用默认天气数据")
                return self._get_default_weather()
            except requests.exceptions.RequestException as e:
                print(f"天气API网络错误: {e}，使用默认天气数据")
                return self._get_default_weather()
            
            if response.status_code == 200:
                try:
                    weather_data = response.json()
                    self.last_weather_data = weather_data
                    self.has_data = True
                    
                    # 解析天气数据
                    weather_info = {
                        'temp': weather_data['main']['temp'],
                    'description': weather_data['weather'][0]['description'],
                    'humidity': weather_data['main']['humidity'],
                    'pressure': weather_data['main']['pressure'],
                    'impact': self._calculate_weather_impact(weather_data)
                }
                
                    return weather_info
                except (KeyError, ValueError, TypeError) as e:
                    print(f"天气数据解析错误: {e}，使用默认天气数据")
                    return self._get_default_weather()
            else:
                # API调用失败，返回默认值
                print(f"天气API返回错误状态码: {response.status_code}")
                return self._get_default_weather()
                
        except Exception as e:
            print(f"天气API调用失败: {e}")
            return self._get_default_weather()
    
    def _calculate_weather_impact(self, weather_data):
        """
        计算天气对宠物行为的影响
        Returns:
            str: 影响级别 ('sunny', 'rainy', 'cloudy', etc.)
        """
        # 根据天气条件判断影响
        weather_main = weather_data['weather'][0]['main']
        temp = weather_data['main']['temp']
        
        if weather_main == 'Clear':
            return 'sunny'
        elif weather_main in ['Rain', 'Drizzle', 'Thunderstorm']:
            return 'rainy'
        elif weather_main in ['Clouds', 'Mist', 'Fog']:
            return 'cloudy'
        elif temp >= 30:
            return 'hot'
        elif temp <= 10:
            return 'cold'
        else:
            return 'normal'
    
    def _get_default_weather(self):
        """获取默认天气数据"""
        # 根据时间和季节返回不同的默认天气
        now = datetime.datetime.now()
        month = now.month
        hour = now.hour
        
        # 模拟季节性天气
        if month in [12, 1, 2]:  # 冬季
            if hour >= 6 and hour <= 18:
                return {
                    'temp': 5,
                    'description': '晴朗',
                    'humidity': 30,
                    'pressure': 1013,
                    'impact': 'cold'
                }
            else:
                return {
                    'temp': -2,
                    'description': '寒冷',
                    'humidity': 40,
                    'pressure': 1013,
                    'impact': 'cold'
                }
        elif month in [6, 7, 8]:  # 夏季
            if hour >= 6 and hour <= 18:
                return {
                    'temp': 32,
                    'description': '炎热',
                    'humidity': 60,
                    'pressure': 1013,
                    'impact': 'hot'
                }
            else:
                return {
                    'temp': 28,
                    'description': '晴朗',
                    'humidity': 50,
                    'pressure': 1013,
                    'impact': 'normal'
                }
        else:  # 春秋季
            return {
                'temp': 22,
                'description': '晴朗',
                'humidity': 50,
                'pressure': 1013,
                'impact': 'sunny'
            }
    
    def get_weather_for_pet(self):
        """获取适合宠物显示的天气信息"""
        weather = self.get_current_weather()
        
        pet_weather_data = {
            'emoji': self._get_weather_emoji(weather['description']),
            'temp': f"{int(weather['temp'])}°C",
            'description': weather['description'],
            'impact': weather['impact'],
            'suggestion': self._get_weather_suggestion(weather['impact'])
        }
        
        return pet_weather_data
    
    def _get_weather_emoji(self, description):
        """根据天气描述获取emoji"""
        emoji_map = {
            '晴天': '☀️',
            '多云': '☁️',
            '阴天': '🌥️',
            '下雨': '🌧️',
            '小雨': '🌦️',
            '大雨': '⛈️',
            '雷雨': '⚡',
            '雪': '❄️',
            '雾': '🌫️'
        }
        
        for key in emoji_map.keys():
            if key in description:
                return emoji_map[key]
        
        return '⛅'  # 默认emoji
    
    def _get_weather_suggestion(self, impact):
        """根据天气影响获取建议"""
        suggestion_map = {
            'sunny': '天气晴朗，宠物活力充沛',
            'rainy': '下雨天，宠物可能不太活跃',
            'cloudy': '多云天气，宠物心情平静',
            'hot': '天气炎热，注意让宠物保持凉爽',
            'cold': '天气寒冷，宠物需要保暖',
            'normal': '天气舒适，宠物状态良好'
        }
        
        return suggestion_map.get(impact, '天气正常')