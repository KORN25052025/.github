import { View, Text, ScrollView, TouchableOpacity, Image } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useUserStore } from '@/stores/userStore';
import { useGamificationStore } from '@/stores/gamificationStore';
import XPBar from '@/components/XPBar';
import StreakDisplay from '@/components/StreakDisplay';
import TopicCard from '@/components/TopicCard';

const TOPICS = [
  { id: 'arithmetic', name: 'Aritmetik', icon: 'calculator', color: '#4F46E5' },
  { id: 'fractions', name: 'Kesirler', icon: 'pie-chart', color: '#10B981' },
  { id: 'percentages', name: 'Yuzdeler', icon: 'analytics', color: '#F59E0B' },
  { id: 'algebra', name: 'Cebir', icon: 'code-slash', color: '#EF4444' },
  { id: 'geometry', name: 'Geometri', icon: 'shapes', color: '#8B5CF6' },
  { id: 'ratios', name: 'Oranlar', icon: 'git-compare', color: '#06B6D4' },
];

export default function HomeScreen() {
  const router = useRouter();
  const { displayName, level, totalXP } = useUserStore();
  const { currentStreak, dailyStreak } = useGamificationStore();

  return (
    <ScrollView className="flex-1 bg-gray-50">
      {/* Header */}
      <View className="bg-primary-600 px-4 pt-4 pb-8 rounded-b-3xl">
        <View className="flex-row items-center justify-between mb-4">
          <View>
            <Text className="text-white text-lg">Merhaba,</Text>
            <Text className="text-white text-2xl font-bold">{displayName || 'Ogrenci'}</Text>
          </View>
          <View className="bg-white/20 rounded-full p-2">
            <Ionicons name="notifications" size={24} color="white" />
          </View>
        </View>

        {/* XP Bar */}
        <XPBar />
      </View>

      {/* Stats Row */}
      <View className="flex-row justify-around px-4 -mt-4">
        <View className="bg-white rounded-xl p-4 shadow-sm flex-1 mx-1 items-center">
          <Ionicons name="flame" size={28} color="#F59E0B" />
          <Text className="text-2xl font-bold text-gray-800">{currentStreak}</Text>
          <Text className="text-xs text-gray-500">Seri</Text>
        </View>
        <View className="bg-white rounded-xl p-4 shadow-sm flex-1 mx-1 items-center">
          <Ionicons name="calendar" size={28} color="#10B981" />
          <Text className="text-2xl font-bold text-gray-800">{dailyStreak}</Text>
          <Text className="text-xs text-gray-500">Gun</Text>
        </View>
        <View className="bg-white rounded-xl p-4 shadow-sm flex-1 mx-1 items-center">
          <Ionicons name="star" size={28} color="#4F46E5" />
          <Text className="text-2xl font-bold text-gray-800">{level}</Text>
          <Text className="text-xs text-gray-500">Seviye</Text>
        </View>
      </View>

      {/* Quick Practice Button */}
      <TouchableOpacity
        className="bg-primary-600 mx-4 mt-6 p-4 rounded-2xl flex-row items-center justify-center"
        onPress={() => router.push('/practice')}
      >
        <Ionicons name="play-circle" size={32} color="white" />
        <Text className="text-white text-lg font-bold ml-2">Hizli Pratik Baslat</Text>
      </TouchableOpacity>

      {/* Topics Section */}
      <View className="px-4 mt-6">
        <Text className="text-xl font-bold text-gray-800 mb-4">Konular</Text>
        <View className="flex-row flex-wrap justify-between">
          {TOPICS.map((topic) => (
            <TopicCard
              key={topic.id}
              topic={topic}
              onPress={() => router.push(`/topic/${topic.id}`)}
            />
          ))}
        </View>
      </View>

      {/* Recent Activity */}
      <View className="px-4 mt-6 mb-8">
        <Text className="text-xl font-bold text-gray-800 mb-4">Son Aktivite</Text>
        <View className="bg-white rounded-xl p-4 shadow-sm">
          <View className="flex-row items-center">
            <View className="bg-success-50 rounded-full p-2">
              <Ionicons name="checkmark-circle" size={24} color="#22C55E" />
            </View>
            <View className="ml-3 flex-1">
              <Text className="text-gray-800 font-medium">Aritmetik pratiği tamamlandı</Text>
              <Text className="text-gray-500 text-sm">5 soru - %80 doğru</Text>
            </View>
            <Text className="text-primary-600 font-bold">+50 XP</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}
