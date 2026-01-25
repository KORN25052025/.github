import { View, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Topic {
  id: string;
  name: string;
  icon: string;
  color: string;
}

interface MasteryProgressProps {
  topic: Topic;
  mastery: number;
  level: string;
  attempts: number;
}

const LEVEL_LABELS: Record<string, string> = {
  NOVICE: 'Acemi',
  BEGINNER: 'Baslangic',
  INTERMEDIATE: 'Orta',
  ADVANCED: 'Ileri',
  EXPERT: 'Uzman',
};

export default function MasteryProgress({
  topic,
  mastery,
  level,
  attempts,
}: MasteryProgressProps) {
  const progressWidth = Math.min(mastery * 100, 100);
  const levelLabel = LEVEL_LABELS[level] || level;

  return (
    <View className="bg-white rounded-xl p-4 mb-3 shadow-sm">
      <View className="flex-row items-center mb-3">
        <View
          className="w-10 h-10 rounded-xl items-center justify-center"
          style={{ backgroundColor: `${topic.color}20` }}
        >
          <Ionicons name={topic.icon as any} size={20} color={topic.color} />
        </View>
        <View className="flex-1 ml-3">
          <Text className="text-gray-800 font-semibold">{topic.name}</Text>
          <Text className="text-gray-500 text-sm">{levelLabel}</Text>
        </View>
        <Text className="text-2xl font-bold" style={{ color: topic.color }}>
          %{Math.round(mastery * 100)}
        </Text>
      </View>

      {/* Progress Bar */}
      <View className="h-3 bg-gray-100 rounded-full overflow-hidden">
        <View
          className="h-full rounded-full"
          style={{
            width: `${progressWidth}%`,
            backgroundColor: topic.color,
          }}
        />
      </View>

      <View className="flex-row justify-between mt-2">
        <Text className="text-xs text-gray-400">{attempts} soru cevaplandi</Text>
        <Text className="text-xs text-gray-400">
          {mastery >= 0.95 ? 'Tamamlandi!' : `${Math.round((0.95 - mastery) * 100)}% kaldi`}
        </Text>
      </View>
    </View>
  );
}
