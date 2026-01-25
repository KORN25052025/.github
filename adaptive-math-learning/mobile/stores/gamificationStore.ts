import { create } from 'zustand';

interface GamificationState {
  // Streaks
  currentStreak: number;
  bestStreak: number;
  dailyStreak: number;

  // Badges
  earnedBadges: string[];
  totalBadges: number;

  // Actions
  incrementStreak: () => void;
  resetStreak: () => void;
  setDailyStreak: (streak: number) => void;
  addBadge: (badgeId: string) => void;
  addXP: (amount: number) => void;
  reset: () => void;
}

export const useGamificationStore = create<GamificationState>((set, get) => ({
  currentStreak: 0,
  bestStreak: 0,
  dailyStreak: 0,
  earnedBadges: [],
  totalBadges: 0,

  incrementStreak: () => {
    const state = get();
    const newStreak = state.currentStreak + 1;
    set({
      currentStreak: newStreak,
      bestStreak: Math.max(state.bestStreak, newStreak),
    });
  },

  resetStreak: () => set({ currentStreak: 0 }),

  setDailyStreak: (streak) => set({ dailyStreak: streak }),

  addBadge: (badgeId) => {
    const state = get();
    if (!state.earnedBadges.includes(badgeId)) {
      set({
        earnedBadges: [...state.earnedBadges, badgeId],
        totalBadges: state.totalBadges + 1,
      });
    }
  },

  addXP: (amount) => {
    // This is handled by userStore, but we might want to track XP events here
  },

  reset: () =>
    set({
      currentStreak: 0,
      bestStreak: 0,
      dailyStreak: 0,
      earnedBadges: [],
      totalBadges: 0,
    }),
}));
