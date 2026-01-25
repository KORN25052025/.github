import { View, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useUserStore } from '@/stores/userStore';

export default function XPBar() {
  const { level, xpThisLevel, xpToNextLevel, totalXP } = useUserStore();
  const progress = xpToNextLevel > 0 ? (xpThisLevel / xpToNextLevel) * 100 : 100;

  return (
    <View className="bg-white/20 rounded-xl p-3">
      <View className="flex-row items-center justify-between mb-2">
        <View className="flex-row items-center">
          <View className="bg-yellow-400 rounded-full p-1">
            <Ionicons name="star" size={16} color="#fff" />
          </View>
          <Text className="text-white font-bold ml-2">Seviye {level}</Text>
        </View>
        <Text className="text-white/80 text-sm">
          {xpThisLevel} / {xpToNextLevel} XP
        </Text>
      </View>

      {/* Progress Bar */}
      <View className="h-3 bg-white/30 rounded-full overflow-hidden">
        <View
          className="h-full bg-yellow-400 rounded-full"
          style={{ width: `${progress}%` }}
        />
      </View>

      <View className="flex-row justify-between mt-1">
        <Text className="text-white/60 text-xs">Toplam: {totalXP} XP</Text>
        <Text className="text-white/60 text-xs">
          {Math.round(progress)}% tamamlandi
        </Text>
      </View>
    </View>
  );
}
