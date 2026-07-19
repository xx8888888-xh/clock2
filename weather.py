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
        self.api_key = api_key or 'demo_key'  # 默认使用模拟数据
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.last_weather_data = None
        self.has_data = False
        self._last_update = None
        
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
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                weather_data = response.json()
                self.last_weather_data = weather_data
                self.has_data = True
                self._last_update = datetime.datetime.now()
                
                # 解析天气数据
                weather_info = {
                    'temp': weather_data['main']['temp'],
                    'description': weather_data['weather'][0]['description'],
                    'humidity': weather_data['main']['humidity'],
                    'pressure': weather_data['main']['pressure'],
                    'wind_speed': weather_data['wind'].get('speed', 0),
                    'impact': self._calculate_weather_impact(weather_data)
                }
                
                return weather_info
            else:
                # API调用失败，返回默认值
                return self._get_default_weather()
                
        except requests.exceptions.Timeout:
            print("天气API请求超时，使用默认数据")
            return self._get_default_weather()
        except requests.exceptions.RequestException as e:
            print(f"天气API请求失败: {e}")
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
        elif weather_main in ['Clouds', 'Mist', 'Fog', 'Haze']:
            return 'cloudy'
        elif temp >= 35:
            return 'hot'
        elif temp <= 5:
            return 'cold'
        else:
            return 'normal'
    
    def _get_default_weather(self):
        """获取默认天气数据 - 基于当前时间和季节"""
        now = datetime.datetime.now()
        month = now.month
        hour = now.hour
        
        # 根据季节和时段返回不同的默认天气
        if month in [12, 1, 2]:  # 冬季
            if 6 <= hour <= 18:
                return {
                    'temp': 8,
                    'description': '晴朗',
                    'humidity': 35,
                    'pressure': 1020,
                    'wind_speed': 3,
                    'impact': 'cold'
                }
            else:
                return {
                    'temp': 2,
                    'description': '寒冷',
                    'humidity': 45,
                    'pressure': 1022,
                    'wind_speed': 4,
                    'impact': 'cold'
                }
        elif month in [6, 7, 8]:  # 夏季
            if 10 <= hour <= 16:
                return {
                    'temp': 34,
                    'description': '炎热',
                    'humidity': 65,
                    'pressure': 1005,
                    'wind_speed': 2,
                    'impact': 'hot'
                }
            elif 6 <= hour <= 9 or 19 <= hour <= 21:
                return {
                    'temp': 28,
                    'description': '晴朗',
                    'humidity': 55,
                    'pressure': 1010,
                    'wind_speed': 3,
                    'impact': 'normal'
                }
            else:
                return {
                    'temp': 26,
                    'description': '夜晚凉爽',
                    'humidity': 60,
                    'pressure': 1012,
                    'wind_speed': 2,
                    'impact': 'normal'
                }
        elif month in [3, 4, 5]:  # 春季
            if 8 <= hour <= 17:
                return {
                    'temp': 22,
                    'description': '晴朗',
                    'humidity': 50,
                    'pressure': 1015,
                    'wind_speed': 4,
                    'impact': 'sunny'
                }
            else:
                return {
                    'temp': 16,
                    'description': '多云',
                    'humidity': 55,
                    'pressure': 1016,
                    'wind_speed': 3,
                    'impact': 'cloudy'
                }
        else:  # 秋季 (9, 10, 11)
            if 8 <= hour <= 17:
                return {
                    'temp': 20,
                    'description': '秋高气爽',
                    'humidity': 45,
                    'pressure': 1018,
                    'wind_speed': 3,
                    'impact': 'sunny'
                }
            else:
                return {
                    'temp': 14,
                    'description': '凉爽',
                    'humidity': 50,
                    'pressure': 1019,
                    'wind_speed': 3,
                    'impact': 'normal'
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
            '晴': '☀️',
            '多云': '☁️',
            '阴': '🌥️',
            '雨': '🌧️',
            '雷': '⛈️',
            '雪': '❄️',
            '雾': '🌫️',
            '热': '🔥',
            '凉爽': '🍃',
            '寒': '🥶',
            '夜晚': '🌙',
            '秋': '🍂'
        }
        
        for key, emoji in emoji_map.items():
            if key in description:
                return emoji
        
        return '⛅'  # 默认emoji
    
    def _get_weather_suggestion(self, impact):
        """根据天气影响获取建议"""
        suggestion_map = {
            'sunny': '☀️ 天气晴朗，宠物活力充沛',
            'rainy': '🌧️ 下雨天，宠物可能不太活跃',
            'cloudy': '☁️ 多云天气，宠物心情平静',
            'hot': '🔥 天气炎热，注意让宠物保持凉爽',
            'cold': '🥶 天气寒冷，宠物需要保暖',
            'normal': '🌤️ 天气舒适，宠物状态良好'
        }
        
        return suggestion_map.get(impact, '🌤️ 天气正常')
    
    def get_forecast(self, city="Beijing", days=3):
        """获取天气预报（需要有效的API密钥）"""
        if self.api_key == 'demo_key':
            return self._get_default_forecast()
        
        try:
            forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'zh'
            }
            
            response = requests.get(forecast_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                forecasts = []
                
                # 每3小时一个预报，取每天12:00的预报
                for item in data.get('list', []):
                    dt_txt = item.get('dt_txt', '')
                    if '12:00' in dt_txt:
                        forecasts.append({
                            'date': dt_txt.split(' ')[0],
                            'temp': item['main']['temp'],
                            'description': item['weather'][0]['description']
                        })
                
                return forecasts[:days]
            
        except Exception as e:
            print(f"获取预报失败: {e}")
        
        return self._get_default_forecast()
    
    def _get_default_forecast(self):
        """获取默认预报"""
        now = datetime.datetime.now()
        forecasts = []
        
        for i in range(1, 4):
            day = now + datetime.timedelta(days=i)
            forecasts.append({
                'date': day.strftime('%Y-%m-%d'),
                'temp': 22,
                'description': '晴'
            })
        
        return forecasts
