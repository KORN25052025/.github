import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { getTopicMastery } from '@/services/api';
import MasteryProgress from '@/components/MasteryProgress';

const TOPIC_INFO: Record<string, { name: string; icon: string; color: string; description: string }> = {
  arithmetic: {
    name: 'Aritmetik',
    icon: 'calculator',
    color: '#4F46E5',
    description: 'Toplama, cikarma, carpma ve bolme islemleri',
  },
  fractions: {
    name: 'Kesirler',
    icon: 'pie-chart',
    color: '#10B981',
    description: 'Kesir islemleri ve sadestirme',
  },
  percentages: {
    name: 'Yuzdeler',
    icon: 'analytics',
    color: '#F59E0B',
    description: 'Yuzde hesaplamalari',
  },
  algebra: {
    name: 'Cebir',
    icon: 'code-slash',
    color: '#EF4444',
    description: 'Denklem cozme ve degiskenler',
  },
  geometry: {
    name: 'Geometri',
    icon: 'shapes',
    color: '#8B5CF6',
    description: 'Alan, cevre ve hacim hesaplamalari',
  },
  ratios: {
    name: 'Oranlar',
    icon: 'git-compare',
    color: '#06B6D4',
    description: 'Oran ve orantilar',
  },
};

export default function TopicScreen() {
  const { slug } = useLocalSearchParams<{ slug: string }>();
  const router = useRouter();

  const topic = TOPIC_INFO[slug || ''] || {
    name: 'Konu',
    icon: 'book',
    color: '#4F46E5',
    description: '',
  };

  const { data: mastery, isLoading } = useQuery({
    queryKey: ['topic-mastery', slug],
    queryFn: () => getTopicMastery(slug || 'arithmetic'),
    enabled: !!slug,
  });

  const startPractice = (difficulty?: string) => {
    router.push({
      pathname: '/practice',
      params: { topic: slug, difficulty },
    });
  };

  return (
    <ScrollView className="flex-1 bg-gray-50">
      {/* Header */}
      <View
        className="px-4 pt-6 pb-8 rounded-b-3xl"
        style={{ backgroundColor: topic.color }}
      >
        <View className="items-center">
          <View className="bg-white/20 rounded-full p-4 mb-4">
            <Ionicons name={topic.icon as any} size={48} color="white" />
          </View>
          <Text className="text-white text-2xl font-bold">{topic.name}</Text>
          <Text className="text-white/80 text-center mt-2">{topic.description}</Text>
        </View>
      </View>

      {/* Mastery Progress */}
      <View className="px-4 -mt-4">
        <MasteryProgress
          topic={{ id: slug || '', name: topic.name, icon: topic.icon, color: topic.color }}
          mastery={mastery?.mastery_score || 0.1}
          level={mastery?.level || 'NOVICE'}
          attempts={mastery?.attempts || 0}
        />
      </View>

      {/* Practice Options */}
      <View className="px-4 mt-6">
        <Text className="text-xl font-bold text-gray-800 mb-4">Pratik Yap</Text>

        <TouchableOpacity
          className="bg-white rounded-xl p-4 mb-3 flex-row items-center shadow-sm"
          onPress={() => startPractice()}
        >
          <View
            className="w-12 h-12 rounded-xl items-center justify-center"
            style={{ backgroundColor: `${topic.color}20` }}
          >
            <Ionicons name="play" size={24} color={topic.color} />
          </View>
          <View className="flex-1 ml-4">
            <Text className="text-gray-800 font-semibold">Adaptif Pratik</Text>
            <Text className="text-gray-500 text-sm">
              Seviyene gore sorular
            </Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>

        <TouchableOpacity
          className="bg-white rounded-xl p-4 mb-3 flex-row items-center shadow-sm"
          onPress={() => startPractice('NOVICE')}
        >
          <View className="w-12 h-12 rounded-xl items-center justify-center bg-green-100">
            <Ionicons name="leaf" size={24} color="#22C55E" />
          </View>
          <View className="flex-1 ml-4">
            <Text className="text-gray-800 font-semibold">Kolay Seviye</Text>
            <Text className="text-gray-500 text-sm">Temel sorular</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>

        <TouchableOpacity
          className="bg-white rounded-xl p-4 mb-3 flex-row items-center shadow-sm"
          onPress={() => startPractice('INTERMEDIATE')}
        >
          <View className="w-12 h-12 rounded-xl items-center justify-center bg-yellow-100">
            <Ionicons name="fitness" size={24} color="#F59E0B" />
          </View>
          <View className="flex-1 ml-4">
            <Text className="text-gray-800 font-semibold">Orta Seviye</Text>
            <Text className="text-gray-500 text-sm">Zorlayici sorular</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>

        <TouchableOpacity
          className="bg-white rounded-xl p-4 mb-3 flex-row items-center shadow-sm"
          onPress={() => startPractice('EXPERT')}
        >
          <View className="w-12 h-12 rounded-xl items-center justify-center bg-purple-100">
            <Ionicons name="flash" size={24} color="#8B5CF6" />
          </View>
          <View className="flex-1 ml-4">
            <Text className="text-gray-800 font-semibold">Uzman Seviye</Text>
            <Text className="text-gray-500 text-sm">En zor sorular</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>
      </View>

      {/* Stats */}
      <View className="px-4 mt-6 mb-8">
        <Text className="text-xl font-bold text-gray-800 mb-4">Istatistikler</Text>

        <View className="bg-white rounded-xl p-4 shadow-sm">
          <View className="flex-row justify-between py-3 border-b border-gray-100">
            <Text className="text-gray-500">Toplam Soru</Text>
            <Text className="text-gray-800 font-semibold">
              {mastery?.attempts || 0}
            </Text>
          </View>
          <View className="flex-row justify-between py-3 border-b border-gray-100">
            <Text className="text-gray-500">Dogru Cevap</Text>
            <Text className="text-gray-800 font-semibold">
              {mastery?.correct || 0}
            </Text>
          </View>
          <View className="flex-row justify-between py-3 border-b border-gray-100">
            <Text className="text-gray-500">Dogruluk Orani</Text>
            <Text className="text-gray-800 font-semibold">
              %{Math.round((mastery?.accuracy || 0) * 100)}
            </Text>
          </View>
          <View className="flex-row justify-between py-3">
            <Text className="text-gray-500">En Iyi Seri</Text>
            <Text className="text-gray-800 font-semibold">
              {mastery?.best_streak || 0}
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}
