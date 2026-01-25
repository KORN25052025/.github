import { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useQuestionStore } from '@/stores/questionStore';
import { useGamificationStore } from '@/stores/gamificationStore';
import QuestionCard from '@/components/QuestionCard';
import AnswerInput from '@/components/AnswerInput';
import FeedbackModal from '@/components/FeedbackModal';
import { generateQuestion, validateAnswer } from '@/services/api';

export default function PracticeScreen() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackData, setFeedbackData] = useState<any>(null);

  const {
    currentQuestion,
    selectedAnswer,
    setCurrentQuestion,
    setSelectedAnswer,
    clearQuestion,
    questionsAnswered,
    correctAnswers,
    incrementQuestions,
    incrementCorrect,
  } = useQuestionStore();

  const { addXP, incrementStreak, resetStreak, currentStreak } = useGamificationStore();

  const loadNewQuestion = async () => {
    setIsLoading(true);
    clearQuestion();
    try {
      const question = await generateQuestion({
        topic_slug: 'arithmetic',
        multiple_choice: true,
      });
      setCurrentQuestion(question);
    } catch (error) {
      console.error('Failed to load question:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadNewQuestion();
  }, []);

  const handleSubmitAnswer = async () => {
    if (!currentQuestion || !selectedAnswer) return;

    setIsLoading(true);
    try {
      const result = await validateAnswer({
        question_id: currentQuestion.question_id,
        user_answer: selectedAnswer,
      });

      incrementQuestions();

      if (result.is_correct) {
        incrementCorrect();
        incrementStreak();
        addXP(result.xp_earned || 10);
      } else {
        resetStreak();
      }

      setFeedbackData({
        isCorrect: result.is_correct,
        correctAnswer: result.correct_answer,
        feedback: result.feedback,
        xpEarned: result.xp_earned || 0,
        streak: result.streak || currentStreak,
      });
      setShowFeedback(true);
    } catch (error) {
      console.error('Failed to validate answer:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNextQuestion = () => {
    setShowFeedback(false);
    loadNewQuestion();
  };

  return (
    <View className="flex-1 bg-gray-50">
      {/* Header Stats */}
      <View className="bg-primary-600 px-4 py-3 flex-row justify-between items-center">
        <View className="flex-row items-center">
          <Ionicons name="help-circle" size={20} color="white" />
          <Text className="text-white ml-1 font-medium">
            {questionsAnswered} soru
          </Text>
        </View>
        <View className="flex-row items-center">
          <Ionicons name="checkmark-circle" size={20} color="#22C55E" />
          <Text className="text-white ml-1 font-medium">
            {correctAnswers} dogru
          </Text>
        </View>
        <View className="flex-row items-center">
          <Ionicons name="flame" size={20} color="#F59E0B" />
          <Text className="text-white ml-1 font-medium">
            {currentStreak} seri
          </Text>
        </View>
      </View>

      {/* Question Area */}
      <View className="flex-1 px-4 py-6">
        {isLoading ? (
          <View className="flex-1 justify-center items-center">
            <ActivityIndicator size="large" color="#4F46E5" />
            <Text className="text-gray-500 mt-4">Soru yukleniyor...</Text>
          </View>
        ) : currentQuestion ? (
          <>
            <QuestionCard question={currentQuestion} />

            <AnswerInput
              question={currentQuestion}
              selectedAnswer={selectedAnswer}
              onSelectAnswer={setSelectedAnswer}
            />

            <TouchableOpacity
              className={`mt-6 p-4 rounded-2xl flex-row items-center justify-center ${
                selectedAnswer
                  ? 'bg-primary-600'
                  : 'bg-gray-300'
              }`}
              onPress={handleSubmitAnswer}
              disabled={!selectedAnswer || isLoading}
            >
              <Text className="text-white text-lg font-bold">
                Cevabi Kontrol Et
              </Text>
              <Ionicons name="arrow-forward" size={24} color="white" className="ml-2" />
            </TouchableOpacity>
          </>
        ) : (
          <View className="flex-1 justify-center items-center">
            <Ionicons name="alert-circle" size={48} color="#9CA3AF" />
            <Text className="text-gray-500 mt-4">Soru yuklenemedi</Text>
            <TouchableOpacity
              className="mt-4 bg-primary-600 px-6 py-3 rounded-xl"
              onPress={loadNewQuestion}
            >
              <Text className="text-white font-medium">Tekrar Dene</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>

      {/* Feedback Modal */}
      <FeedbackModal
        visible={showFeedback}
        data={feedbackData}
        onNext={handleNextQuestion}
        onClose={() => setShowFeedback(false)}
      />
    </View>
  );
}
