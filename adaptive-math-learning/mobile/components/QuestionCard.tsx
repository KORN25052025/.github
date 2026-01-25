import { View, Text, Image } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Question {
  question_id: string;
  expression: string;
  expression_latex?: string;
  story_text?: string;
  visual_url?: string;
  difficulty_tier: string;
  question_type: string;
}

interface QuestionCardProps {
  question: Question;
}

const DIFFICULTY_COLORS: Record<string, string> = {
  NOVICE: '#22C55E',
  BEGINNER: '#84CC16',
  INTERMEDIATE: '#F59E0B',
  ADVANCED: '#EF4444',
  EXPERT: '#7C3AED',
};

const DIFFICULTY_LABELS: Record<string, string> = {
  NOVICE: 'Kolay',
  BEGINNER: 'Baslangic',
  INTERMEDIATE: 'Orta',
  ADVANCED: 'Zor',
  EXPERT: 'Uzman',
};

export default function QuestionCard({ question }: QuestionCardProps) {
  const difficultyColor = DIFFICULTY_COLORS[question.difficulty_tier] || '#9CA3AF';
  const difficultyLabel = DIFFICULTY_LABELS[question.difficulty_tier] || question.difficulty_tier;

  return (
    <View className="bg-white rounded-2xl p-6 shadow-sm">
      {/* Difficulty Badge */}
      <View className="flex-row items-center justify-between mb-4">
        <View
          className="px-3 py-1 rounded-full"
          style={{ backgroundColor: `${difficultyColor}20` }}
        >
          <Text style={{ color: difficultyColor }} className="font-medium text-sm">
            {difficultyLabel}
          </Text>
        </View>
        <Text className="text-gray-400 text-sm">#{question.question_id.slice(0, 6)}</Text>
      </View>

      {/* Visual (if available) */}
      {question.visual_url && (
        <View className="mb-4 rounded-xl overflow-hidden">
          <Image
            source={{ uri: question.visual_url }}
            className="w-full h-40"
            resizeMode="cover"
          />
        </View>
      )}

      {/* Story Text (if available) */}
      {question.story_text && (
        <View className="bg-primary-50 rounded-xl p-4 mb-4">
          <View className="flex-row items-start">
            <Ionicons name="book" size={20} color="#4F46E5" />
            <Text className="flex-1 ml-2 text-gray-700 leading-6">
              {question.story_text}
            </Text>
          </View>
        </View>
      )}

      {/* Expression */}
      <View className="bg-gray-50 rounded-xl p-6 items-center">
        <Text className="text-3xl font-bold text-gray-800 text-center">
          {question.expression}
        </Text>
      </View>
    </View>
  );
}
