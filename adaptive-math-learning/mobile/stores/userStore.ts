import { create } from 'zustand';

interface UserState {
  userId: string;
  displayName: string;
  gradeLevel: number;
  level: number;
  totalXP: number;
  xpThisLevel: number;
  xpToNextLevel: number;

  // Actions
  setDisplayName: (name: string) => void;
  setGradeLevel: (level: number) => void;
  addXP: (amount: number) => void;
  setLevel: (level: number, xpThisLevel: number, xpToNextLevel: number) => void;
  reset: () => void;
}

const calculateXPForLevel = (level: number): number => {
  return Math.floor(100 * Math.pow(level, 1.5));
};

export const useUserStore = create<UserState>((set, get) => ({
  userId: 'user_' + Math.random().toString(36).slice(2, 10),
  displayName: '',
  gradeLevel: 5,
  level: 1,
  totalXP: 0,
  xpThisLevel: 0,
  xpToNextLevel: 100,

  setDisplayName: (name) => set({ displayName: name }),

  setGradeLevel: (level) => set({ gradeLevel: level }),

  addXP: (amount) => {
    const state = get();
    let newTotalXP = state.totalXP + amount;
    let newXPThisLevel = state.xpThisLevel + amount;
    let newLevel = state.level;
    let newXPToNextLevel = state.xpToNextLevel;

    // Check for level up
    while (newXPThisLevel >= newXPToNextLevel && newLevel < 100) {
      newXPThisLevel -= newXPToNextLevel;
      newLevel++;
      newXPToNextLevel = calculateXPForLevel(newLevel);
    }

    set({
      totalXP: newTotalXP,
      xpThisLevel: newXPThisLevel,
      xpToNextLevel: newXPToNextLevel,
      level: newLevel,
    });
  },

  setLevel: (level, xpThisLevel, xpToNextLevel) =>
    set({ level, xpThisLevel, xpToNextLevel }),

  reset: () =>
    set({
      level: 1,
      totalXP: 0,
      xpThisLevel: 0,
      xpToNextLevel: 100,
    }),
}));
