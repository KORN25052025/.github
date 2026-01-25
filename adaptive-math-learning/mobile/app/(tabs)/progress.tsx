import { View, Text, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { getMasteryProgress, getStatistics } from '@/services/api';
import MasteryProgress from '@/components/MasteryProgress';
import BadgeGrid from '@/components/BadgeGrid';

const TOPICS = [
  { id: 'arithmetic', name: 'Aritmetik', icon: 'calculator', color: '#4F46E5' },
  { id: 'fractions', name: 'Kesirler', icon: 'pie-chart', color: '#10B981' },
  { id: 'percentages', name: 'Yuzdeler', icon: 'analytics', color: '#F59E0B' },
  { id: 'algebra', name: 'Cebir', icon: 'code-slash', color: '#EF4444' },
  { id: 'geometry', name: 'Geometri', icon: 'shapes', color: '#8B5CF6' },
  { id: 'ratios', name: 'Oranlar', icon: 'git-compare', color: '#06B6D4' },
];

export default function ProgressScreen() {
  const { data: mastery, isLoading: masteryLoading } = useQuery({
    queryKey: ['mastery'],
    queryFn: getMasteryProgress,
  });

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['statistics'],
    queryFn: getStatistics,
  });

  return (
    <ScrollView className="flex-1 bg-gray-50">
      {/* Stats Overview */}
      <View className="bg-primary-600 px-4 pt-4 pb-8 rounded-b-3xl">
        <Text className="text-white text-xl font-bold mb-4">Genel Istatistikler</Text>

        <View className="flex-row flex-wrap">
          <View className="w-1/2 p-2">
            <View className="bg-white/20 rounded-xl p-4">
              <View className="flex-row items-center">
                <Ionicons name="help-circle" size={24} color="white" />
                <Text className="text-white/80 ml-2">Toplam Soru</Text>
              </View>
              <Text className="text-white text-3xl font-bold mt-2">
                {stats?.total_questions || 0}
              </Text>
            </View>
          </View>

          <View className="w-1/2 p-2">
            <View className="bg-white/20 rounded-xl p-4">
              <View className="flex-row items-center">
                <Ionicons name="checkmark-circle" size={24} color="#22C55E" />
                <Text className="text-white/80 ml-2">Dogruluk</Text>
              </View>
              <Text className="text-white text-3xl font-bold mt-2">
                %{((stats?.overall_accuracy || 0) * 100).toFixed(0)}
              </Text>
            </View>
          </View>

          <View className="w-1/2 p-2">
            <View className="bg-white/20 rounded-xl p-4">
              <View className="flex-row items-center">
                <Ionicons name="flame" size={24} color="#F59E0B" />
                <Text className="text-white/80 ml-2">En Iyi Seri</Text>
              </View>
              <Text className="text-white text-3xl font-bold mt-2">
                {stats?.best_streak || 0}
              </Text>
            </View>
          </View>

          <View className="w-1/2 p-2">
            <View className="bg-white/20 rounded-xl p-4">
              <View className="flex-row items-center">
                <Ionicons name="star" size={24} color="#FFD700" />
                <Text className="text-white/80 ml-2">Ortalama</Text>
              </View>
              <Text className="text-white text-3xl font-bold mt-2">
                %{((stats?.average_mastery || 0) * 100).toFixed(0)}
              </Text>
            </View>
          </View>
        </View>
      </View>

      {/* Topic Mastery */}
      <View className="px-4 mt-6">
        <Text className="text-xl font-bold text-gray-800 mb-4">Konu Ustaligi</Text>

        {TOPICS.map((topic) => {
          const topicMastery = mastery?.find((m: any) => m.topic_slug === topic.id);
          return (
            <MasteryProgress
              key={topic.id}
              topic={topic}
              mastery={topicMastery?.mastery_score || 0.1}
              level={topicMastery?.level || 'NOVICE'}
              attempts={topicMastery?.attempts || 0}
            />
          );
        })}
      </View>

      {/* Badges Section */}
      <View className="px-4 mt-6 mb-8">
        <Text className="text-xl font-bold text-gray-800 mb-4">Rozetler</Text>
        <BadgeGrid />
      </View>
    </ScrollView>
  );
}
