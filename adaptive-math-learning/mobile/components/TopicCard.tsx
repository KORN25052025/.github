import { View, Text, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Topic {
  id: string;
  name: string;
  icon: string;
  color: string;
}

interface TopicCardProps {
  topic: Topic;
  onPress: () => void;
  mastery?: number;
}

export default function TopicCard({ topic, onPress, mastery = 0 }: TopicCardProps) {
  const progressWidth = Math.min(mastery * 100, 100);

  return (
    <TouchableOpacity
      className="w-[48%] mb-3"
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View className="bg-white rounded-2xl p-4 shadow-sm">
        <View
          className="w-12 h-12 rounded-xl items-center justify-center mb-3"
          style={{ backgroundColor: `${topic.color}20` }}
        >
          <Ionicons name={topic.icon as any} size={24} color={topic.color} />
        </View>

        <Text className="text-gray-800 font-semibold mb-2">{topic.name}</Text>

        {/* Mastery Progress */}
        <View className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <View
            className="h-full rounded-full"
            style={{
              width: `${progressWidth}%`,
              backgroundColor: topic.color,
            }}
          />
        </View>
        <Text className="text-xs text-gray-500 mt-1">
          %{Math.round(mastery * 100)} ustalık
        </Text>
      </View>
    </TouchableOpacity>
  );
}
