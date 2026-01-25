/**
 * Speech service using expo-speech for text-to-speech functionality.
 * Implements Web Speech API compatibility for reading questions aloud.
 */

import * as Speech from 'expo-speech';

interface SpeechOptions {
  language?: string;
  pitch?: number;
  rate?: number;
  onStart?: () => void;
  onDone?: () => void;
  onError?: (error: any) => void;
}

const DEFAULT_OPTIONS: SpeechOptions = {
  language: 'tr-TR', // Turkish by default
  pitch: 1.0,
  rate: 0.9, // Slightly slower for educational content
};

/**
 * Speak text aloud using text-to-speech
 */
export const speak = async (text: string, options: SpeechOptions = {}): Promise<void> => {
  const mergedOptions = { ...DEFAULT_OPTIONS, ...options };

  // Stop any ongoing speech
  await stop();

  return new Promise((resolve, reject) => {
    Speech.speak(text, {
      language: mergedOptions.language,
      pitch: mergedOptions.pitch,
      rate: mergedOptions.rate,
      onStart: () => {
        mergedOptions.onStart?.();
      },
      onDone: () => {
        mergedOptions.onDone?.();
        resolve();
      },
      onError: (error) => {
        mergedOptions.onError?.(error);
        reject(error);
      },
    });
  });
};

/**
 * Stop any ongoing speech
 */
export const stop = async (): Promise<void> => {
  await Speech.stop();
};

/**
 * Check if speech is currently in progress
 */
export const isSpeaking = async (): Promise<boolean> => {
  return await Speech.isSpeakingAsync();
};

/**
 * Get available voices for a language
 */
export const getVoices = async (): Promise<Speech.Voice[]> => {
  return await Speech.getAvailableVoicesAsync();
};

/**
 * Get Turkish voices specifically
 */
export const getTurkishVoices = async (): Promise<Speech.Voice[]> => {
  const voices = await getVoices();
  return voices.filter((voice) => voice.language.startsWith('tr'));
};

/**
 * Speak a math question with appropriate pauses
 */
export const speakQuestion = async (
  questionText: string,
  options: SpeechOptions = {}
): Promise<void> => {
  // Add pauses for math expressions
  const processedText = questionText
    .replace(/\+/g, ' arti ')
    .replace(/-/g, ' eksi ')
    .replace(/\*/g, ' carpi ')
    .replace(/\//g, ' bolu ')
    .replace(/=/g, ' esittir ')
    .replace(/\^/g, ' uzeri ')
    .replace(/x/gi, ' iks ')
    .replace(/\(/g, ' parantez ac ')
    .replace(/\)/g, ' parantez kapat ');

  await speak(processedText, {
    ...options,
    rate: 0.85, // Even slower for math content
  });
};

/**
 * Speak feedback after answering
 */
export const speakFeedback = async (
  isCorrect: boolean,
  correctAnswer?: string
): Promise<void> => {
  if (isCorrect) {
    await speak('Dogru cevap! Tebrikler!', { rate: 1.0 });
  } else {
    const message = correctAnswer
      ? `Yanlis cevap. Dogru cevap ${correctAnswer} idi.`
      : 'Yanlis cevap. Tekrar deneyin.';
    await speak(message, { rate: 0.9 });
  }
};

/**
 * Speak a number in Turkish
 */
export const speakNumber = async (num: number): Promise<void> => {
  const turkishNumbers: Record<number, string> = {
    0: 'sifir',
    1: 'bir',
    2: 'iki',
    3: 'uc',
    4: 'dort',
    5: 'bes',
    6: 'alti',
    7: 'yedi',
    8: 'sekiz',
    9: 'dokuz',
    10: 'on',
  };

  const text = turkishNumbers[num] || num.toString();
  await speak(text);
};

export default {
  speak,
  stop,
  isSpeaking,
  getVoices,
  getTurkishVoices,
  speakQuestion,
  speakFeedback,
  speakNumber,
};
