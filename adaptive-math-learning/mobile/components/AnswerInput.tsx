import { View, Text, TouchableOpacity, TextInput } from 'react-native';
import { useState } from 'react';
import { Ionicons } from '@expo/vector-icons';

interface Question {
  question_id: string;
  expression: string;
  answer_format: string;
  options?: (string | number)[];
}

interface AnswerInputProps {
  question: Question;
  selectedAnswer: string | null;
  onSelectAnswer: (answer: string) => void;
}

export default function AnswerInput({
  question,
  selectedAnswer,
  onSelectAnswer,
}: AnswerInputProps) {
  const [textInput, setTextInput] = useState('');

  // Multiple choice
  if (question.options && question.options.length > 0) {
    return (
      <View className="mt-6">
        <Text className="text-gray-600 font-medium mb-3">Cevabini sec:</Text>
        <View className="flex-row flex-wrap">
          {question.options.map((option, index) => {
            const optionStr = String(option);
            const isSelected = selectedAnswer === optionStr;
            const letters = ['A', 'B', 'C', 'D'];

            return (
              <TouchableOpacity
                key={index}
                className={`w-1/2 p-2`}
                onPress={() => onSelectAnswer(optionStr)}
              >
                <View
                  className={`rounded-xl p-4 flex-row items-center ${
                    isSelected
                      ? 'bg-primary-600 border-2 border-primary-600'
                      : 'bg-white border-2 border-gray-200'
                  }`}
                >
                  <View
                    className={`w-8 h-8 rounded-full items-center justify-center mr-3 ${
                      isSelected ? 'bg-white' : 'bg-gray-100'
                    }`}
                  >
                    <Text
                      className={`font-bold ${
                        isSelected ? 'text-primary-600' : 'text-gray-500'
                      }`}
                    >
                      {letters[index]}
                    </Text>
                  </View>
                  <Text
                    className={`text-lg font-medium ${
                      isSelected ? 'text-white' : 'text-gray-800'
                    }`}
                  >
                    {optionStr}
                  </Text>
                </View>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>
    );
  }

  // Text input for non-multiple choice
  return (
    <View className="mt-6">
      <Text className="text-gray-600 font-medium mb-3">Cevabini yaz:</Text>
      <View className="bg-white rounded-xl border-2 border-gray-200 flex-row items-center p-2">
        <TextInput
          className="flex-1 text-xl p-3 text-gray-800"
          value={textInput}
          onChangeText={(text) => {
            setTextInput(text);
            onSelectAnswer(text);
          }}
          placeholder="Cevap..."
          keyboardType={
            question.answer_format === 'integer' ||
            question.answer_format === 'decimal'
              ? 'numeric'
              : 'default'
          }
          returnKeyType="done"
        />
        {textInput.length > 0 && (
          <TouchableOpacity
            className="p-2"
            onPress={() => {
              setTextInput('');
              onSelectAnswer('');
            }}
          >
            <Ionicons name="close-circle" size={24} color="#9CA3AF" />
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}
