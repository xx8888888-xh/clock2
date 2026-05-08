import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TouchableOpacity,
  PanResponder,
  Animated,
  Dimensions,
  Alert,
  Modal
} from 'react-native';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

const App = () => {
  const [time, setTime] = useState('');
  const [date, setDate] = useState('');
  const [petMood, setPetMood] = useState('happy');
  const [alarms, setAlarms] = useState([]);
  const [weather, setWeather] = useState('sunny');
  const [position, setPosition] = useState({ x: 50, y: 100 });
  const [isSleeping, setIsSleeping] = useState(false);
  const [showAlarmModal, setShowAlarmModal] = useState(false);
  const [pan] = useState(new Animated.ValueXY());

  useEffect(() => {
    // 更新时间
    const updateDateTime = () => {
      const now = new Date();
      setTime(now.toLocaleTimeString('zh-CN'));
      setDate(now.toLocaleDateString('zh-CN', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        weekday: 'long'
      }));
      
      // 检查宠物睡眠时间 (22:00 - 07:00)
      const hour = now.getHours();
      setIsSleeping(hour >= 22 || hour < 7);
      
      // 更新宠物心情（根据时间变化）
      updatePetMood(hour);
    };
    
    updateDateTime();
    const interval = setInterval(updateDateTime, 1000);
    
    // 初始化示例闹钟
    setAlarms([
      { id: 1, time: '08:00', label: '起床', enabled: true },
      { id: 2, time: '12:30', label: '午餐', enabled: true },
      { id: 3, time: '18:00', label: '晚餐', enabled: false },
      { id: 4, time: '23:00', label: '睡觉', enabled: true },
    ]);
    
    // 初始化天气
    setWeather(getWeatherByTime());
    
    return () => clearInterval(interval);
  }, []);

  const updatePetMood = (hour) => {
    let mood = 'happy';
    if (hour >= 22 || hour < 7) {
      mood = 'sleeping';
    } else if (hour >= 12 && hour < 14) {
      mood = 'hungry';
    } else if (hour >= 17 && hour < 19) {
      mood = 'playful';
    }
    setPetMood(mood);
  };

  const getWeatherByTime = () => {
    const hour = new Date().getHours();
    if (hour >= 6 && hour < 18) {
      return Math.random() > 0.5 ? 'sunny' : 'cloudy';
    } else {
      return 'night';
    }
  };

  const getPetEmoji = () => {
    switch(petMood) {
      case 'happy': return '🐶';
      case 'sleeping': return '😴';
      case 'hungry': return '🍖';
      case 'playful': return '🎾';
      default: return '🐾';
    }
  };

  const getWeatherEmoji = () => {
    switch(weather) {
      case 'sunny': return '☀️';
      case 'cloudy': return '☁️';
      case 'rainy': return '🌧️';
      case 'night': return '🌙';
      default: return '🌤️';
    }
  };

  const panResponder = PanResponder.create({
    onStartShouldSetPanResponder: () => true,
    onPanResponderMove: Animated.event([
      null,
      { dx: pan.x, dy: pan.y }
    ], { useNativeDriver: false }),
    onPanResponderRelease: () => {
      pan.extractOffset();
    }
  });

  const addAlarm = () => {
    setShowAlarmModal(true);
  };

  const toggleAlarm = (id) => {
    setAlarms(alarms.map(alarm => 
      alarm.id === id ? { ...alarm, enabled: !alarm.enabled } : alarm
    ));
  };

  return (
    <View style={styles.container}>
      {/* 悬浮窗宠物闹钟 */}
      <Animated.View
        style={[
          styles.floatingWindow,
          {
            transform: [{ translateX: pan.x }, { translateY: pan.y }],
            left: position.x,
            top: position.y,
          }
        ]}
        {...panResponder.panHandlers}
      >
        <View style={styles.header}>
          <Text style={styles.title}>宠物闹钟</Text>
          <Text style={styles.weather}>{getWeatherEmoji()}</Text>
        </View>
        
        <View style={styles.petContainer}>
          <Text style={styles.petEmoji}>{getPetEmoji()}</Text>
          <Text style={styles.petStatus}>
            {isSleeping ? 'Zzz...' : petMood === 'happy' ? '开心!' : '活跃中'}
          </Text>
        </View>
        
        <View style={styles.timeContainer}>
          <Text style={styles.timeText}>{time}</Text>
          <Text style={styles.dateText}>{date}</Text>
        </View>

        <View style={styles.footer}>
          <TouchableOpacity 
            style={styles.button}
            onPress={addAlarm}
          >
            <Text style={styles.buttonText}>⏰ 闹钟</Text>
            <Text style={styles.buttonSubtext}>{alarms.filter(a => a.enabled).length}个活跃</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.button}>
            <Text style={styles.buttonText}>⚙️ 设置</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.button}>
            <Text style={styles.buttonText}>📅 日历</Text>
          </TouchableOpacity>
        </View>
      </Animated.View>

      {/* 闹钟设置模态框 */}
      <Modal
        visible={showAlarmModal}
        transparent
        animationType="slide"
        onRequestClose={() => setShowAlarmModal(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>闹钟设置</Text>
            {alarms.map(alarm => (
              <View key={alarm.id} style={styles.alarmItem}>
                <Text style={styles.alarmTime}>{alarm.time}</Text>
                <Text style={styles.alarmLabel}>{alarm.label}</Text>
                <TouchableOpacity
                  style={[styles.alarmToggle, alarm.enabled && styles.alarmToggleOn]}
                  onPress={() => toggleAlarm(alarm.id)}
                >
                  <Text style={styles.alarmToggleText}>
                    {alarm.enabled ? '开' : '关'}
                  </Text>
                </TouchableOpacity>
              </View>
            ))}
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setShowAlarmModal(false)}
            >
              <Text style={styles.closeButtonText}>关闭</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'transparent',
  },
  floatingWindow: {
    position: 'absolute',
    width: 240,
    height: 300,
    backgroundColor: '#8FB1FF',
    borderRadius: 25,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 10,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
  },
  weather: {
    fontSize: 24,
  },
  petContainer: {
    alignItems: 'center',
    marginBottom: 15,
  },
  petEmoji: {
    fontSize: 60,
    marginBottom: 5,
  },
  petStatus: {
    fontSize: 14,
    color: 'white',
    opacity: 0.9,
  },
  timeContainer: {
    alignItems: 'center',
    marginBottom: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    padding: 15,
    borderRadius: 15,
  },
  timeText: {
    fontSize: 34,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  dateText: {
    fontSize: 16,
    color: 'white',
    opacity: 0.8,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  button: {
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 15,
    minWidth: 70,
  },
  buttonText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 16,
  },
  buttonSubtext: {
    color: 'white',
    fontSize: 10,
    opacity: 0.8,
    marginTop: 2,
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 20,
    padding: 25,
    width: '80%',
    maxHeight: '70%',
  },
  modalTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  alarmItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  alarmTime: {
    fontSize: 18,
    fontWeight: 'bold',
    width: 60,
  },
  alarmLabel: {
    fontSize: 16,
    flex: 1,
    marginLeft: 15,
  },
  alarmToggle: {
    paddingHorizontal: 15,
    paddingVertical: 6,
    borderRadius: 15,
    backgroundColor: '#ddd',
  },
  alarmToggleOn: {
    backgroundColor: '#4CAF50',
  },
  alarmToggleText: {
    color: 'white',
    fontWeight: 'bold',
  },
  closeButton: {
    marginTop: 20,
    backgroundColor: '#8FB1FF',
    padding: 12,
    borderRadius: 15,
    alignItems: 'center',
  },
  closeButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
});

export default App;
