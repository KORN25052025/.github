import { View, Text, TouchableOpacity, Modal, ScrollView } from 'react-native';
import { useState } from 'react';
import { Ionicons } from '@expo/vector-icons';
import { useGamificationStore } from '@/stores/gamificationStore';

interface Badge {
  id: string;
  name: string;
  name_tr: string;
  description_tr: string;
  icon: string;
  rarity: string;
  earned?: boolean;
  earned_at?: string;
}

const RARITY_COLORS: Record<string, string> = {
  common: '#9CA3AF',
  uncommon: '#22C55E',
  rare: '#3B82F6',
  epic: '#8B5CF6',
  legendary: '#F59E0B',
};

const SAMPLE_BADGES: Badge[] = [
  { id: 'streak_3', name: 'Getting Started', name_tr: 'Baslangic', description_tr: 'Arka arkaya 3 dogru cevap', icon: '🔥', rarity: 'common', earned: true },
  { id: 'streak_10', name: 'On Fire', name_tr: 'Ateste', description_tr: 'Arka arkaya 10 dogru cevap', icon: '🔥🔥', rarity: 'uncommon', earned: true },
  { id: 'practice_10', name: 'Practice', name_tr: 'Pratik', description_tr: '10 soru cevapla', icon: '📚', rarity: 'common', earned: true },
  { id: 'topic_master', name: 'Master', name_tr: 'Usta', description_tr: '%90 ustalık', icon: '🏆', rarity: 'rare', earned: false },
  { id: 'perfect_session', name: 'Perfect', name_tr: 'Mukemmel', description_tr: '%100 oturum', icon: '✨', rarity: 'epic', earned: false },
  { id: 'streak_50', name: 'Legend', name_tr: 'Efsane', description_tr: '50 dogru seri', icon: '⭐', rarity: 'legendary', earned: false },
];

export default function BadgeGrid() {
  const [selectedBadge, setSelectedBadge] = useState<Badge | null>(null);
  const { earnedBadges } = useGamificationStore();

  // Merge earned status from store
  const badges = SAMPLE_BADGES.map((badge) => ({
    ...badge,
    earned: earnedBadges.includes(badge.id) || badge.earned,
  }));

  const earnedCount = badges.filter((b) => b.earned).length;

  return (
    <View>
      {/* Summary */}
      <View className="flex-row items-center justify-between mb-4">
        <Text className="text-gray-500">
          {earnedCount} / {badges.length} rozet kazanildi
        </Text>
        <View className="h-2 flex-1 bg-gray-200 rounded-full mx-4 overflow-hidden">
          <View
            className="h-full bg-primary-600 rounded-full"
            style={{ width: `${(earnedCount / badges.length) * 100}%` }}
          />
        </View>
      </View>

      {/* Badge Grid */}
      <View className="flex-row flex-wrap">
        {badges.map((badge) => (
          <TouchableOpacity
            key={badge.id}
            className="w-1/3 p-2"
            onPress={() => setSelectedBadge(badge)}
          >
            <View
              className={`items-center p-3 rounded-xl ${
                badge.earned ? 'bg-white' : 'bg-gray-100'
              }`}
              style={{
                opacity: badge.earned ? 1 : 0.5,
                borderWidth: badge.earned ? 2 : 0,
                borderColor: RARITY_COLORS[badge.rarity],
              }}
            >
              <Text className="text-3xl mb-1">{badge.icon}</Text>
              <Text
                className={`text-xs text-center font-medium ${
                  badge.earned ? 'text-gray-800' : 'text-gray-400'
                }`}
                numberOfLines={1}
              >
                {badge.name_tr}
              </Text>
            </View>
          </TouchableOpacity>
        ))}
      </View>

      {/* Badge Detail Modal */}
      <Modal
        visible={!!selectedBadge}
        transparent
        animationType="fade"
        onRequestClose={() => setSelectedBadge(null)}
      >
        <TouchableOpacity
          className="flex-1 bg-black/50 justify-center items-center p-6"
          activeOpacity={1}
          onPress={() => setSelectedBadge(null)}
        >
          {selectedBadge && (
            <View className="bg-white rounded-2xl p-6 w-full max-w-sm">
              <View className="items-center mb-4">
                <View
                  className="w-20 h-20 rounded-full items-center justify-center mb-3"
                  style={{ backgroundColor: `${RARITY_COLORS[selectedBadge.rarity]}20` }}
                >
                  <Text className="text-4xl">{selectedBadge.icon}</Text>
                </View>
                <Text className="text-xl font-bold text-gray-800">
                  {selectedBadge.name_tr}
                </Text>
                <Text
                  className="text-sm font-medium capitalize"
                  style={{ color: RARITY_COLORS[selectedBadge.rarity] }}
                >
                  {selectedBadge.rarity}
                </Text>
              </View>

              <Text className="text-gray-600 text-center mb-4">
                {selectedBadge.description_tr}
              </Text>

              {selectedBadge.earned ? (
                <View className="bg-success-50 rounded-xl p-3 flex-row items-center justify-center">
                  <Ionicons name="checkmark-circle" size={20} color="#22C55E" />
                  <Text className="text-success-600 ml-2 font-medium">Kazanildi!</Text>
                </View>
              ) : (
                <View className="bg-gray-100 rounded-xl p-3 flex-row items-center justify-center">
                  <Ionicons name="lock-closed" size={20} color="#9CA3AF" />
                  <Text className="text-gray-500 ml-2">Henuz kazanilmadi</Text>
                </View>
              )}
            </View>
          )}
        </TouchableOpacity>
      </Modal>
    </View>
  );
}
