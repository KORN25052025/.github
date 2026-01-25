import { create } from 'zustand';

interface Question {
  question_id: string;
  question_type: string;
  operation?: string;
  expression: string;
  expression_latex?: string;
  story_text?: string;
  visual_url?: string;
  answer_format: string;
  options?: (string | number)[];
  difficulty_score: number;
  difficulty_tier: string;
  topic_name?: string;
}

interface QuestionState {
  currentQuestion: Question | null;
  selectedAnswer: string | null;
  questionsAnswered: number;
  correctAnswers: number;
  sessionStartTime: number | null;

  // Actions
  setCurrentQuestion: (question: Question) => void;
  setSelectedAnswer: (answer: string | null) => void;
  clearQuestion: () => void;
  incrementQuestions: () => void;
  incrementCorrect: () => void;
  startSession: () => void;
  endSession: () => { questionsAnswered: number; correctAnswers: number; duration: number };
  reset: () => void;
}

export const useQuestionStore = create<QuestionState>((set, get) => ({
  currentQuestion: null,
  selectedAnswer: null,
  questionsAnswered: 0,
  correctAnswers: 0,
  sessionStartTime: null,

  setCurrentQuestion: (question) =>
    set({ currentQuestion: question, selectedAnswer: null }),

  setSelectedAnswer: (answer) => set({ selectedAnswer: answer }),

  clearQuestion: () => set({ currentQuestion: null, selectedAnswer: null }),

  incrementQuestions: () =>
    set((state) => ({ questionsAnswered: state.questionsAnswered + 1 })),

  incrementCorrect: () =>
    set((state) => ({ correctAnswers: state.correctAnswers + 1 })),

  startSession: () => set({ sessionStartTime: Date.now(), questionsAnswered: 0, correctAnswers: 0 }),

  endSession: () => {
    const state = get();
    const duration = state.sessionStartTime
      ? Math.floor((Date.now() - state.sessionStartTime) / 1000)
      : 0;

    return {
      questionsAnswered: state.questionsAnswered,
      correctAnswers: state.correctAnswers,
      duration,
    };
  },

  reset: () =>
    set({
      currentQuestion: null,
      selectedAnswer: null,
      questionsAnswered: 0,
      correctAnswers: 0,
      sessionStartTime: null,
    }),
}));
