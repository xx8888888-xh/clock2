"""
资源文件：包含测试数据和配置文件
安卓桌面宠物闹钟 - 资源模块
"""

import os
from datetime import datetime, timedelta

# 默认宠物图片路径
PET_IMAGE_PATH = 'pet_default.png'
ALTERNATIVE_PET_IMAGES = [
    'pet.png',
    'pet_default.png',
    'assets/pet.png',
    'images/pet.png'
]

# 默认闹钟声音文件
ALARM_SOUND_PATHS = [
    'alarm.wav',
    'alarm.mp3',
    'assets/alarm.wav',
    'assets/alarm.mp3',
    'sounds/alarm.wav'
]

# 应用配置
APP_CONFIG = {
    'app_name': '宠物闹钟',
    'version': '1.0.0',
    'author': 'Pet Alarm Team',
    'description': '一个可爱的桌面宠物闹钟应用',
    'website': 'https://github.com/petalarm',
    'support_email': 'support@petalarm.com'
}

# 颜色配置
COLORS = {
    'primary': [0.2, 0.6, 0.8, 1],      # 主要颜色 - 蓝色
    'secondary': [0.3, 0.7, 0.9, 1],    # 次要颜色 - 浅蓝
    'accent': [1, 0.6, 0.2, 1],         # 强调色 - 橙色
    'background': [0.95, 0.95, 0.95, 1], # 背景色
    'text': [0.1, 0.1, 0.1, 1],         # 文字颜色
    'success': [0.3, 0.8, 0.3, 1],      # 成功颜色 - 绿色
    'warning': [1, 0.8, 0.2, 1],        # 警告颜色 - 黄色
    'error': [1, 0.3, 0.3, 1],          # 错误颜色 - 红色
    'white': [1, 1, 1, 1],
    'black': [0, 0, 0, 1],
    'transparent': [0, 0, 0, 0]
}

# 字体配置
FONTS = {
    'tiny': '10sp',
    'small': '12sp',
    'normal': '16sp',
    'medium': '20sp',
    'large': '24sp',
    'xlarge': '28sp',
    'title': '32sp'
}

# 测试闹钟数据
TEST_ALARMS = [
    {
        'id': 0,
        'hour': 8,
        'minute': 0,
        'label': '起床',
        'content': '新的一天开始了，该起床了！',
        'repeat_days': [0, 1, 2, 3, 4],  # 周一到周五
        'enabled': True
    },
    {
        'id': 1,
        'hour': 12,
        'minute': 0,
        'label': '午餐',
        'content': '午餐时间到了，记得吃饭哦！',
        'repeat_days': [0, 1, 2, 3, 4, 5, 6],  # 每天
        'enabled': True
    },
    {
        'id': 2,
        'hour': 18,
        'minute': 0,
        'label': '下班',
        'content': '工作时间结束，可以下班了！',
        'repeat_days': [0, 1, 2, 3, 4],  # 工作日
        'enabled': True
    },
    {
        'id': 3,
        'hour': 22,
        'minute': 30,
        'label': '睡觉',
        'content': '该睡觉了，早点休息吧！',
        'repeat_days': [0, 1, 2, 3, 4, 5, 6],  # 每天
        'enabled': True
    }
]

# 星期映射
WEEKDAYS = {
    0: '星期一',
    1: '星期二',
    2: '星期三',
    3: '星期四',
    4: '星期五',
    5: '星期六',
    6: '星期日'
}

# 星期缩写
WEEKDAYS_SHORT = {
    0: '一',
    1: '二',
    2: '三',
    3: '四',
    4: '五',
    5: '六',
    6: '日'
}

# 重复类型
REPEAT_TYPES = {
    'once': '一次性',
    'daily': '每天',
    'weekday': '工作日',
    'weekend': '周末',
    'custom': '自定义'
}

# 默认窗口位置配置
DEFAULT_WINDOW_POSITION = {
    'left': 100,
    'top': 500,
    'width': 200,
    'height': 200
}

# 默认宠物设置
DEFAULT_PET_SETTINGS = {
    'size': 150,
    'opacity': 1.0,
    'image_path': PET_IMAGE_PATH,
    'sleep_start_hour': 22,  # 晚上10点开始睡觉
    'sleep_end_hour': 6,     # 早上6点醒来
    'animation_speed': 1.0,   # 动画速度
    'enable_drag': True,      # 启用拖动
    'enable_click': True      # 启用点击
}

# 默认闹钟设置
DEFAULT_ALARM_SETTINGS = {
    'snooze_duration': 5,      # 贪睡时间（分钟）
    'max_snooze_count': 3,     # 最大贪睡次数
    'vibrate': True,           # 是否振动
    'sound_enabled': True,     # 是否播放声音
    'volume': 0.8,             # 音量（0.0-1.0）
    'banner_time': 5,          # 横幅显示时间（秒）
    'pre_alarm_minutes': 0     # 提前提醒（分钟）
}

# 默认计时器设置
DEFAULT_TIMER_SETTINGS = {
    'default_minutes': 5,
    'sound_enabled': True,
    'vibrate': True
}


def create_test_pet_image():
    """
    创建测试宠物图片
    如果找不到图片文件，可以创建一个简单的图形
    """
    try:
        for img_path in ALTERNATIVE_PET_IMAGES:
            if os.path.exists(img_path):
                return img_path
        
        print(f"警告: 宠物图片文件不存在")
        print("请创建一个150x150像素的PNG图片并命名为 'pet_default.png'")
        return None
    except Exception as e:
        print(f"检查图片文件时出错: {e}")
        return None


def get_alarm_sound_path():
    """获取闹钟声音文件路径"""
    for sound_path in ALARM_SOUND_PATHS:
        if os.path.exists(sound_path):
            return sound_path
    return None


def get_next_alarm_time_text(alarm):
    """获取下一个闹钟时间的文本描述"""
    now = datetime.now()
    alarm_time = now.replace(
        hour=alarm['hour'],
        minute=alarm['minute'],
        second=0,
        microsecond=0
    )
    
    if alarm_time < now:
        alarm_time = alarm_time.replace(day=now.day + 1)
    
    # 处理重复设置
    if alarm.get('repeat_days'):
        while alarm_time.weekday() not in alarm['repeat_days']:
            alarm_time += timedelta(days=1)
    
    time_diff = alarm_time - now
    hours = time_diff.seconds // 3600
    minutes = (time_diff.seconds % 3600) // 60
    
    if time_diff.days > 0:
        return f"{time_diff.days}天{hours}小时后"
    elif hours > 0:
        return f"{hours}小时{minutes}分钟后"
    else:
        return f"{minutes}分钟后"


def format_alarm_time(hour, minute):
    """格式化时间显示"""
    return f"{hour:02d}:{minute:02d}"


def format_time_12h(hour, minute):
    """格式化为12小时制"""
    period = '上午' if hour < 12 else '下午'
    hour_12 = hour % 12
    if hour_12 == 0:
        hour_12 = 12
    return f"{period} {hour_12}:{minute:02d}"


def get_alarm_status_text(alarm):
    """获取闹钟状态文本"""
    if alarm['enabled']:
        status = "已启用"
        if alarm.get('repeat_days'):
            days = [WEEKDAYS_SHORT[i] for i in alarm['repeat_days']]
            status += f" (重复: {''.join(days)})"
        else:
            status += " (单次)"
    else:
        status = "已禁用"
    return status


def validate_alarm_time(hour, minute):
    """验证闹钟时间是否有效"""
    if not (0 <= hour <= 23):
        return False, "小时必须在0-23之间"
    if not (0 <= minute <= 59):
        return False, "分钟必须在0-59之间"
    return True, "时间有效"


def validate_alarm_label(label):
    """验证闹钟标签"""
    label = label.strip()
    if not label:
        return False, "标签不能为空"
    if len(label) > 20:
        return False, "标签不能超过20个字符"
    return True, "标签有效"


def get_time_until_alarm(alarm):
    """获取距离闹钟触发的时间"""
    now = datetime.now()
    alarm_time = now.replace(
        hour=alarm['hour'],
        minute=alarm['minute'],
        second=0,
        microsecond=0
    )
    
    # 如果是重复闹钟，找到下一个触发时间
    if alarm.get('repeat_days'):
        while alarm_time < now or alarm_time.weekday() not in alarm['repeat_days']:
            alarm_time += timedelta(days=1)
    else:
        if alarm_time < now:
            alarm_time += timedelta(days=1)
    
    return alarm_time - now


def format_time_delta(td):
    """格式化时间差"""
    if td.days > 0:
        return f"{td.days}天{td.seconds // 3600}小时{(td.seconds % 3600) // 60}分钟"
    else:
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        else:
            return f"{minutes}分钟"


def parse_time_string(time_str):
    """解析时间字符串"""
    time_str = time_str.strip()
    
    # 支持多种格式：08:00, 8:00, 8.00, 8点00分
    patterns = [
        r'^(\d{1,2}):(\d{2})$',
        r'^(\d{1,2})\.(\d{2})$',
        r'^(\d{1,2})点(\d{1,2})分?$',
        r'^(\d{1,2}):(\d{2}):\d{2}$'
    ]
    
    for pattern in patterns:
        match = re.match(pattern, time_str)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return hour, minute
    
    return None, None


def get_pet_emotion(hour):
    """根据时间获取宠物心情"""
    if 6 <= hour < 12:
        return 'happy', '早上好！新的一天开始了！'
    elif 12 <= hour < 14:
        return 'sleepy', '午休时间到了，休息一下吧！'
    elif 14 <= hour < 18:
        return 'active', '下午好！保持专注！'
    elif 18 <= hour < 22:
        return 'relaxed', '晚上好！放松一下吧！'
    else:
        return 'sleepy', '该睡觉了，晚安！'


# 导入re模块用于正则表达式
try:
    import re
except ImportError:
    pass


if __name__ == '__main__':
    # 测试资源文件功能
    print("=" * 50)
    print("宠物闹钟资源文件测试")
    print("=" * 50)
    print(f"应用名称: {APP_CONFIG['app_name']}")
    print(f"版本: {APP_CONFIG['version']}")
    print(f"作者: {APP_CONFIG['author']}")
    
    print(f"\n时间格式化测试:")
    print(f"08:30 -> {format_alarm_time(8, 30)}")
    print(f"14:05 -> {format_alarm_time(14, 5)}")
    print(f"08:30 (12h) -> {format_time_12h(8, 30)}")
    print(f"14:05 (12h) -> {format_time_12h(14, 5)}")
    
    print(f"\n闹钟验证测试:")
    valid, msg = validate_alarm_time(25, 70)
    print(f"25:70 -> {msg}")
    valid, msg = validate_alarm_time(10, 30)
    print(f"10:30 -> {msg}")
    
    print(f"\n闹钟状态测试:")
    test_alarm = TEST_ALARMS[0]
    print(f"闹钟1: {get_alarm_status_text(test_alarm)}")
    
    print(f"\n时间差测试:")
    time_diff = get_time_until_alarm(test_alarm)
    print(f"距离闹钟: {format_time_delta(time_diff)}")
    
    print(f"\n宠物心情测试:")
    for hour in [8, 12, 15, 20, 23]:
        emotion, text = get_pet_emotion(hour)
        print(f"{hour}点: {emotion} - {text}")
    
    print(f"\n宠物图片路径: {create_test_pet_image() or '未找到'}")
    print(f"闹钟声音路径: {get_alarm_sound_path() or '未找到'}")
