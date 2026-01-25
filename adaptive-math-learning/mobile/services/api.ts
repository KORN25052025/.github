import axios from 'axios';

// Base URL - change this for production
const API_BASE_URL = __DEV__
  ? 'http://localhost:8000/api/v1'
  : 'https://your-production-api.com/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    if (__DEV__) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (__DEV__) {
      console.error('[API Error]', error.message);
    }
    return Promise.reject(error);
  }
);

// Types
interface GenerateQuestionParams {
  topic_slug?: string;
  topic_id?: number;
  difficulty?: number;
  operation?: string;
  multiple_choice?: boolean;
}

interface ValidateAnswerParams {
  question_id: string;
  user_answer: string;
  response_time_ms?: number;
}

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

interface AnswerResult {
  is_correct: boolean;
  user_answer: string;
  correct_answer: string;
  feedback: string;
  new_mastery_score?: number;
  mastery_change?: number;
  streak: number;
  xp_earned?: number;
}

interface MasteryData {
  topic_id: number;
  topic_slug: string;
  topic_name: string;
  mastery_score: number;
  level: string;
  attempts: number;
  correct: number;
  accuracy: number;
  streak: number;
  best_streak: number;
}

interface Statistics {
  total_questions: number;
  total_correct: number;
  overall_accuracy: number;
  total_sessions: number;
  current_streak: number;
  best_streak: number;
  topics_practiced: number;
  average_mastery: number;
}

// API Functions

/**
 * Generate a new question
 */
export async function generateQuestion(
  params: GenerateQuestionParams
): Promise<Question> {
  const response = await api.post('/questions/generate', params);

  // Store question for validation
  if (response.data.question_id) {
    await storeQuestionForValidation(
      response.data.question_id,
      response.data.correct_answer || '',
      params.topic_slug || 'arithmetic'
    );
  }

  return response.data;
}

/**
 * Store question data for validation
 */
async function storeQuestionForValidation(
  questionId: string,
  correctAnswer: string,
  topic: string
): Promise<void> {
  try {
    await api.post('/answers/store', null, {
      params: { question_id: questionId, correct_answer: correctAnswer, topic },
    });
  } catch (error) {
    // Non-critical, continue without storing
    console.warn('Failed to store question for validation');
  }
}

/**
 * Validate an answer
 */
export async function validateAnswer(
  params: ValidateAnswerParams
): Promise<AnswerResult> {
  const response = await api.post('/answers/validate', params);
  return response.data;
}

/**
 * Get mastery progress for all topics
 */
export async function getMasteryProgress(): Promise<MasteryData[]> {
  const response = await api.get('/progress/mastery');
  return response.data;
}

/**
 * Get mastery for a specific topic
 */
export async function getTopicMastery(topicSlug: string): Promise<MasteryData> {
  const response = await api.get(`/progress/mastery/${topicSlug}`);
  return response.data;
}

/**
 * Get overall statistics
 */
export async function getStatistics(): Promise<Statistics> {
  const response = await api.get('/progress/statistics');
  return response.data;
}

/**
 * Get topic recommendations
 */
export async function getRecommendations(): Promise<any[]> {
  const response = await api.get('/progress/recommendations');
  return response.data;
}

/**
 * Get all available topics
 */
export async function getTopics(): Promise<any[]> {
  const response = await api.get('/topics');
  return response.data;
}

/**
 * Start a new session
 */
export async function startSession(params: {
  topic_id?: number;
  session_type?: string;
}): Promise<{ session_key: string }> {
  const response = await api.post('/sessions/start', params);
  return response.data;
}

/**
 * End a session
 */
export async function endSession(sessionKey: string): Promise<any> {
  const response = await api.post(`/sessions/${sessionKey}/end`);
  return response.data;
}

/**
 * Check API health
 */
export async function checkHealth(): Promise<{ status: string }> {
  const response = await api.get('/health');
  return response.data;
}

// ==================== GAMIFICATION API ====================

interface XPData {
  user_id: string;
  total_xp: number;
  level: number;
  xp_this_level: number;
  xp_to_next_level: number;
  level_name: string;
}

interface StreakData {
  user_id: string;
  current_streak: number;
  best_streak: number;
  last_activity: string | null;
  streak_alive: boolean;
}

interface Badge {
  badge_type: string;
  name: string;
  description: string;
  icon: string;
  earned: boolean;
  earned_at: string | null;
  progress: number | null;
}

interface LeaderboardEntry {
  rank: number;
  user_id: string;
  display_name: string;
  total_xp: number;
  level: number;
}

interface GamificationSummary {
  user_id: string;
  xp: {
    total: number;
    level: number;
    level_name: string;
    progress_to_next: number;
  };
  streak: {
    current: number;
    best: number;
    alive: boolean;
  };
  badges: {
    earned_count: number;
    total_count: number;
    recent: Badge[];
  };
  rank: number;
}

/**
 * Get user XP and level info
 */
export async function getUserXP(userId: string): Promise<XPData> {
  const response = await api.get(`/gamification/xp/${userId}`);
  return response.data;
}

/**
 * Award XP to user
 */
export async function awardXP(
  userId: string,
  xpAmount: number,
  reason: string
): Promise<{ success: boolean; xp_awarded: number; new_total: number; level_up: boolean; new_level: number }> {
  const response = await api.post('/gamification/xp/award', {
    user_id: userId,
    xp_amount: xpAmount,
    reason: reason,
  });
  return response.data;
}

/**
 * Get user badges
 */
export async function getUserBadges(userId: string): Promise<{ user_id: string; badges: Badge[] }> {
  const response = await api.get(`/gamification/badges/${userId}`);
  return response.data;
}

/**
 * Check and award new badges
 */
export async function checkBadges(userId: string): Promise<{ new_badges: Badge[]; badges_earned: number }> {
  const response = await api.post(`/gamification/badges/check/${userId}`);
  return response.data;
}

/**
 * Get user streak info
 */
export async function getUserStreak(userId: string): Promise<StreakData> {
  const response = await api.get(`/gamification/streak/${userId}`);
  return response.data;
}

/**
 * Update streak on activity
 */
export async function updateStreak(userId: string): Promise<{
  success: boolean;
  current_streak: number;
  streak_extended: boolean;
  streak_bonus_xp: number;
}> {
  const response = await api.post(`/gamification/streak/${userId}/update`);
  return response.data;
}

/**
 * Get leaderboard
 */
export async function getLeaderboard(
  limit: number = 10,
  offset: number = 0
): Promise<{ entries: LeaderboardEntry[]; total_users: number }> {
  const response = await api.get('/gamification/leaderboard', {
    params: { limit, offset },
  });
  return response.data;
}

/**
 * Get user rank on leaderboard
 */
export async function getUserRank(userId: string): Promise<{
  user_id: string;
  rank: number;
  total_xp: number;
  percentile: number;
}> {
  const response = await api.get(`/gamification/leaderboard/${userId}/rank`);
  return response.data;
}

/**
 * Get complete gamification summary for user
 */
export async function getGamificationSummary(userId: string): Promise<GamificationSummary> {
  const response = await api.get(`/gamification/summary/${userId}`);
  return response.data;
}

export default api;
