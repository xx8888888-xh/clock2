enum PetMood {
  happy('😊', '开心', '心情很好！'),
  normal('😐', '普通', '还不错~'),
  sleepy('😴', '困倦', '好困...'),
  hungry('🥺', '饥饿', '想吃东西...'),
  sick('🤒', '生病', '不太舒服...');

  const PetMood(this.emoji, this.label, this.desc);
  final String emoji;
  final String label;
  final String desc;
}

class PetState {
  PetMood mood;
  int hunger;
  int happiness;
  DateTime lastFed;
  DateTime lastInteraction;

  PetState({
    this.mood = PetMood.happy,
    this.hunger = 80,
    this.happiness = 80,
    DateTime? lastFed,
    DateTime? lastInteraction,
  })  : lastFed = lastFed ?? DateTime.now(),
        lastInteraction = lastInteraction ?? DateTime.now();

  void updateMood() {
    if (hunger < 20) {
      mood = PetMood.hungry;
    } else if (happiness < 20) {
      mood = PetMood.sick;
    } else {
      final hour = DateTime.now().hour;
      if (hour >= 23 || hour < 6) {
        mood = PetMood.sleepy;
      } else if (happiness > 60 && hunger > 50) {
        mood = PetMood.happy;
      } else {
        mood = PetMood.normal;
      }
    }
  }

  void feed() {
    hunger = (hunger + 30).clamp(0, 100);
    happiness = (happiness + 10).clamp(0, 100);
    lastFed = DateTime.now();
    lastInteraction = DateTime.now();
    updateMood();
  }

  void pet() {
    happiness = (happiness + 15).clamp(0, 100);
    lastInteraction = DateTime.now();
    updateMood();
  }

  void tick() {
    hunger = (hunger - 1).clamp(0, 100);
    happiness = (happiness - 1).clamp(0, 100);
    updateMood();
  }
}
