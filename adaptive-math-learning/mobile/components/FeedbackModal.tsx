import { View, Text, Modal, TouchableOpacity, Animated } from 'react-native';
import { useEffect, useRef } from 'react';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';

interface FeedbackData {
  isCorrect: boolean;
  correctAnswer: string;
  feedback: string;
  xpEarned: number;
  streak: number;
}

interface FeedbackModalProps {
  visible: boolean;
  data: FeedbackData | null;
  onNext: () => void;
  onClose: () => void;
}

export default function FeedbackModal({
  visible,
  data,
  onNext,
  onClose,
}: FeedbackModalProps) {
  const scaleAnim = useRef(new Animated.Value(0.5)).current;
  const opacityAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (visible && data) {
      // Haptic feedback
      if (data.isCorrect) {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      } else {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      }

      // Animation
      Animated.parallel([
        Animated.spring(scaleAnim, {
          toValue: 1,
          useNativeDriver: true,
          tension: 100,
          friction: 8,
        }),
        Animated.timing(opacityAnim, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true,
        }),
      ]).start();
    } else {
      scaleAnim.setValue(0.5);
      opacityAnim.setValue(0);
    }
  }, [visible, data]);

  if (!data) return null;

  return (
    <Modal
      visible={visible}
      transparent
      animationType="none"
      onRequestClose={onClose}
    >
      <Animated.View
        className="flex-1 justify-center items-center bg-black/50 px-6"
        style={{ opacity: opacityAnim }}
      >
        <Animated.View
          className={`w-full rounded-3xl p-6 ${
            data.isCorrect ? 'bg-success-50' : 'bg-error-50'
          }`}
          style={{ transform: [{ scale: scaleAnim }] }}
        >
          {/* Icon */}
          <View className="items-center mb-4">
            <View
              className={`w-20 h-20 rounded-full items-center justify-center ${
                data.isCorrect ? 'bg-success-500' : 'bg-error-500'
              }`}
            >
              <Ionicons
                name={data.isCorrect ? 'checkmark' : 'close'}
                size={48}
                color="white"
              />
            </View>
          </View>

          {/* Title */}
          <Text
            className={`text-2xl font-bold text-center mb-2 ${
              data.isCorrect ? 'text-success-600' : 'text-error-600'
            }`}
          >
            {data.isCorrect ? 'Dogru!' : 'Yanlis'}
          </Text>

          {/* Feedback */}
          <Text className="text-gray-700 text-center text-lg mb-4">
            {data.feedback}
          </Text>

          {/* Correct Answer (if wrong) */}
          {!data.isCorrect && (
            <View className="bg-white rounded-xl p-4 mb-4">
              <Text className="text-gray-500 text-center">Dogru cevap:</Text>
              <Text className="text-gray-800 text-xl font-bold text-center">
                {data.correctAnswer}
              </Text>
            </View>
          )}

          {/* XP Earned */}
          {data.isCorrect && data.xpEarned > 0 && (
            <View className="bg-white rounded-xl p-4 mb-4 flex-row items-center justify-center">
              <Ionicons name="star" size={24} color="#FFD700" />
              <Text className="text-xl font-bold text-gray-800 ml-2">
                +{data.xpEarned} XP
              </Text>
            </View>
          )}

          {/* Streak */}
          {data.isCorrect && data.streak >= 3 && (
            <View className="flex-row items-center justify-center mb-4">
              <Ionicons name="flame" size={24} color="#F59E0B" />
              <Text className="text-warning-600 font-bold ml-1">
                {data.streak} Seri!
              </Text>
            </View>
          )}

          {/* Next Button */}
          <TouchableOpacity
            className={`p-4 rounded-2xl items-center ${
              data.isCorrect ? 'bg-success-500' : 'bg-primary-600'
            }`}
            onPress={onNext}
          >
            <Text className="text-white text-lg font-bold">Sonraki Soru</Text>
          </TouchableOpacity>
        </Animated.View>
      </Animated.View>
    </Modal>
  );
}
