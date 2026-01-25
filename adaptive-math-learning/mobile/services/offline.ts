/**
 * Offline Storage Service for Mobile App.
 *
 * Provides offline-first functionality:
 * - Cache questions for offline practice
 * - Queue answers for later sync
 * - Store progress locally
 * - Sync when back online
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import { generateQuestion, validateAnswer } from './api';

// Storage keys
const STORAGE_KEYS = {
  CACHED_QUESTIONS: 'offline_questions',
  PENDING_ANSWERS: 'pending_answers',
  USER_PROGRESS: 'user_progress',
  LAST_SYNC: 'last_sync',
  OFFLINE_STATS: 'offline_stats',
};

// Types
interface CachedQuestion {
  id: string;
  topic_slug: string;
  difficulty_tier: number;
  question: any;
  cached_at: string;
  expires_at: string;
}

interface PendingAnswer {
  id: string;
  question_id: string;
  user_answer: string;
  response_time_ms: number;
  answered_at: string;
  topic_slug: string;
}

interface OfflineProgress {
  user_id: string;
  total_xp: number;
  level: number;
  streak: number;
  topic_mastery: Record<string, number>;
  last_updated: string;
}

interface SyncResult {
  synced_answers: number;
  failed_answers: number;
  new_xp: number;
  errors: string[];
}

class OfflineService {
  private isOnline: boolean = true;
  private syncInProgress: boolean = false;

  constructor() {
    this.setupNetworkListener();
  }

  /**
   * Set up network state listener
   */
  private setupNetworkListener(): void {
    NetInfo.addEventListener((state) => {
      const wasOffline = !this.isOnline;
      this.isOnline = state.isConnected ?? false;

      // Auto-sync when coming back online
      if (wasOffline && this.isOnline) {
        this.syncPendingAnswers();
      }
    });
  }

  /**
   * Check if device is online
   */
  async checkOnline(): Promise<boolean> {
    const state = await NetInfo.fetch();
    this.isOnline = state.isConnected ?? false;
    return this.isOnline;
  }

  // ==================== QUESTION CACHING ====================

  /**
   * Cache questions for offline use
   */
  async cacheQuestions(
    topic_slug: string,
    count: number = 10,
    difficulty_tier?: number
  ): Promise<number> {
    if (!await this.checkOnline()) {
      return 0;
    }

    const cached: CachedQuestion[] = [];
    const now = new Date();
    const expires = new Date(now.getTime() + 24 * 60 * 60 * 1000); // 24 hours

    for (let i = 0; i < count; i++) {
      try {
        const question = await generateQuestion({
          topic_slug,
          difficulty: difficulty_tier,
          multiple_choice: true,
        });

        cached.push({
          id: `cached_${Date.now()}_${i}`,
          topic_slug,
          difficulty_tier: difficulty_tier || 1,
          question,
          cached_at: now.toISOString(),
          expires_at: expires.toISOString(),
        });
      } catch (error) {
        console.warn('Failed to cache question:', error);
      }
    }

    // Get existing cache and merge
    const existing = await this.getCachedQuestions();
    const merged = [...existing, ...cached];

    // Remove expired questions
    const valid = merged.filter(
      (q) => new Date(q.expires_at) > new Date()
    );

    await AsyncStorage.setItem(
      STORAGE_KEYS.CACHED_QUESTIONS,
      JSON.stringify(valid)
    );

    return cached.length;
  }

  /**
   * Get cached questions
   */
  async getCachedQuestions(topic_slug?: string): Promise<CachedQuestion[]> {
    try {
      const data = await AsyncStorage.getItem(STORAGE_KEYS.CACHED_QUESTIONS);
      if (!data) return [];

      let questions: CachedQuestion[] = JSON.parse(data);

      // Filter expired
      const now = new Date();
      questions = questions.filter((q) => new Date(q.expires_at) > now);

      // Filter by topic if specified
      if (topic_slug) {
        questions = questions.filter((q) => q.topic_slug === topic_slug);
      }

      return questions;
    } catch (error) {
      console.error('Error getting cached questions:', error);
      return [];
    }
  }

  /**
   * Get a single cached question and remove it from cache
   */
  async getOfflineQuestion(topic_slug: string): Promise<any | null> {
    const questions = await this.getCachedQuestions(topic_slug);

    if (questions.length === 0) {
      return null;
    }

    // Get first question
    const [first, ...rest] = questions;

    // Update cache
    const allQuestions = await this.getCachedQuestions();
    const updated = allQuestions.filter((q) => q.id !== first.id);
    await AsyncStorage.setItem(
      STORAGE_KEYS.CACHED_QUESTIONS,
      JSON.stringify(updated)
    );

    return first.question;
  }

  /**
   * Get count of cached questions
   */
  async getCacheCount(topic_slug?: string): Promise<number> {
    const questions = await this.getCachedQuestions(topic_slug);
    return questions.length;
  }

  // ==================== ANSWER QUEUEING ====================

  /**
   * Queue an answer for later sync
   */
  async queueAnswer(
    question_id: string,
    user_answer: string,
    response_time_ms: number,
    topic_slug: string
  ): Promise<void> {
    const pending: PendingAnswer = {
      id: `pending_${Date.now()}`,
      question_id,
      user_answer,
      response_time_ms,
      answered_at: new Date().toISOString(),
      topic_slug,
    };

    const existing = await this.getPendingAnswers();
    existing.push(pending);

    await AsyncStorage.setItem(
      STORAGE_KEYS.PENDING_ANSWERS,
      JSON.stringify(existing)
    );

    // Update offline stats
    await this.updateOfflineStats(true);
  }

  /**
   * Get pending answers
   */
  async getPendingAnswers(): Promise<PendingAnswer[]> {
    try {
      const data = await AsyncStorage.getItem(STORAGE_KEYS.PENDING_ANSWERS);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Error getting pending answers:', error);
      return [];
    }
  }

  /**
   * Sync pending answers to server
   */
  async syncPendingAnswers(): Promise<SyncResult> {
    if (this.syncInProgress) {
      return { synced_answers: 0, failed_answers: 0, new_xp: 0, errors: ['Sync already in progress'] };
    }

    if (!await this.checkOnline()) {
      return { synced_answers: 0, failed_answers: 0, new_xp: 0, errors: ['Device is offline'] };
    }

    this.syncInProgress = true;
    const result: SyncResult = {
      synced_answers: 0,
      failed_answers: 0,
      new_xp: 0,
      errors: [],
    };

    try {
      const pending = await this.getPendingAnswers();
      const remaining: PendingAnswer[] = [];

      for (const answer of pending) {
        try {
          const response = await validateAnswer({
            question_id: answer.question_id,
            user_answer: answer.user_answer,
            response_time_ms: answer.response_time_ms,
          });

          result.synced_answers++;
          if (response.xp_earned) {
            result.new_xp += response.xp_earned;
          }
        } catch (error) {
          result.failed_answers++;
          result.errors.push(`Failed to sync answer ${answer.id}: ${error}`);
          remaining.push(answer);
        }
      }

      // Update pending with only failed ones
      await AsyncStorage.setItem(
        STORAGE_KEYS.PENDING_ANSWERS,
        JSON.stringify(remaining)
      );

      // Update last sync time
      await AsyncStorage.setItem(
        STORAGE_KEYS.LAST_SYNC,
        new Date().toISOString()
      );
    } finally {
      this.syncInProgress = false;
    }

    return result;
  }

  // ==================== PROGRESS STORAGE ====================

  /**
   * Save user progress locally
   */
  async saveProgress(progress: OfflineProgress): Promise<void> {
    await AsyncStorage.setItem(
      STORAGE_KEYS.USER_PROGRESS,
      JSON.stringify({
        ...progress,
        last_updated: new Date().toISOString(),
      })
    );
  }

  /**
   * Get locally stored progress
   */
  async getProgress(): Promise<OfflineProgress | null> {
    try {
      const data = await AsyncStorage.getItem(STORAGE_KEYS.USER_PROGRESS);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Error getting progress:', error);
      return null;
    }
  }

  /**
   * Update topic mastery locally
   */
  async updateLocalMastery(topic_slug: string, mastery: number): Promise<void> {
    const progress = await this.getProgress();
    if (progress) {
      progress.topic_mastery[topic_slug] = mastery;
      await this.saveProgress(progress);
    }
  }

  // ==================== OFFLINE STATS ====================

  /**
   * Update offline practice stats
   */
  private async updateOfflineStats(answeredQuestion: boolean): Promise<void> {
    try {
      const data = await AsyncStorage.getItem(STORAGE_KEYS.OFFLINE_STATS);
      const stats = data ? JSON.parse(data) : {
        questions_answered_offline: 0,
        last_offline_practice: null,
      };

      if (answeredQuestion) {
        stats.questions_answered_offline++;
        stats.last_offline_practice = new Date().toISOString();
      }

      await AsyncStorage.setItem(STORAGE_KEYS.OFFLINE_STATS, JSON.stringify(stats));
    } catch (error) {
      console.error('Error updating offline stats:', error);
    }
  }

  /**
   * Get offline stats
   */
  async getOfflineStats(): Promise<{
    questions_answered_offline: number;
    pending_sync: number;
    cached_questions: number;
    last_sync: string | null;
  }> {
    try {
      const [statsData, lastSync, pending, cached] = await Promise.all([
        AsyncStorage.getItem(STORAGE_KEYS.OFFLINE_STATS),
        AsyncStorage.getItem(STORAGE_KEYS.LAST_SYNC),
        this.getPendingAnswers(),
        this.getCachedQuestions(),
      ]);

      const stats = statsData ? JSON.parse(statsData) : { questions_answered_offline: 0 };

      return {
        questions_answered_offline: stats.questions_answered_offline || 0,
        pending_sync: pending.length,
        cached_questions: cached.length,
        last_sync: lastSync,
      };
    } catch (error) {
      console.error('Error getting offline stats:', error);
      return {
        questions_answered_offline: 0,
        pending_sync: 0,
        cached_questions: 0,
        last_sync: null,
      };
    }
  }

  // ==================== CACHE MANAGEMENT ====================

  /**
   * Clear all offline data
   */
  async clearAllData(): Promise<void> {
    await Promise.all([
      AsyncStorage.removeItem(STORAGE_KEYS.CACHED_QUESTIONS),
      AsyncStorage.removeItem(STORAGE_KEYS.PENDING_ANSWERS),
      AsyncStorage.removeItem(STORAGE_KEYS.USER_PROGRESS),
      AsyncStorage.removeItem(STORAGE_KEYS.OFFLINE_STATS),
    ]);
  }

  /**
   * Clear expired cache
   */
  async clearExpiredCache(): Promise<number> {
    const questions = await this.getCachedQuestions();
    const now = new Date();
    const valid = questions.filter((q) => new Date(q.expires_at) > now);
    const removed = questions.length - valid.length;

    await AsyncStorage.setItem(
      STORAGE_KEYS.CACHED_QUESTIONS,
      JSON.stringify(valid)
    );

    return removed;
  }
}

// Export singleton instance
export const offlineService = new OfflineService();
export default offlineService;
