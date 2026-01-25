import { View, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface StreakDisplayProps {
  currentStreak: number;
  bestStreak: number;
  dailyStreak: number;
}

export default function StreakDisplay({
  currentStreak,
  bestStreak,
  dailyStreak,
}: StreakDisplayProps) {
  return (
    <View className="flex-row justify-around bg-white rounded-xl p-4 shadow-sm">
      <View className="items-center">
        <View className="flex-row items-center">
          <Ionicons name="flame" size={24} color="#F59E0B" />
          <Text className="text-2xl font-bold text-gray-800 ml-1">
            {currentStreak}
          </Text>
        </View>
        <Text className="text-xs text-gray-500">Mevcut Seri</Text>
      </View>

      <View className="w-px bg-gray-200" />

      <View className="items-center">
        <View className="flex-row items-center">
          <Ionicons name="trophy" size={24} color="#FFD700" />
          <Text className="text-2xl font-bold text-gray-800 ml-1">
            {bestStreak}
          </Text>
        </View>
        <Text className="text-xs text-gray-500">En Iyi</Text>
      </View>

      <View className="w-px bg-gray-200" />

      <View className="items-center">
        <View className="flex-row items-center">
          <Ionicons name="calendar" size={24} color="#10B981" />
          <Text className="text-2xl font-bold text-gray-800 ml-1">
            {dailyStreak}
          </Text>
        </View>
        <Text className="text-xs text-gray-500">Gunluk</Text>
      </View>
    </View>
  );
}
