/**
 * Supabase client configuration for the mobile app.
 * Provides authentication, database access, and realtime subscriptions.
 */

import { createClient } from '@supabase/supabase-js';
import * as SecureStore from 'expo-secure-store';
import Constants from 'expo-constants';

// Get Supabase credentials from app config
const supabaseUrl = Constants.expoConfig?.extra?.supabaseUrl || 'https://your-project.supabase.co';
const supabaseAnonKey = Constants.expoConfig?.extra?.supabaseAnonKey || 'your-anon-key';

// Custom storage adapter using expo-secure-store
const ExpoSecureStoreAdapter = {
  getItem: async (key: string): Promise<string | null> => {
    try {
      return await SecureStore.getItemAsync(key);
    } catch (error) {
      console.warn('SecureStore getItem error:', error);
      return null;
    }
  },
  setItem: async (key: string, value: string): Promise<void> => {
    try {
      await SecureStore.setItemAsync(key, value);
    } catch (error) {
      console.warn('SecureStore setItem error:', error);
    }
  },
  removeItem: async (key: string): Promise<void> => {
    try {
      await SecureStore.deleteItemAsync(key);
    } catch (error) {
      console.warn('SecureStore removeItem error:', error);
    }
  },
};

// Create Supabase client with secure storage
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    storage: ExpoSecureStoreAdapter,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
});

// Database types (generated from Supabase schema)
export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string;
          email: string;
          display_name: string;
          grade_level: number;
          created_at: string;
          ab_group: 'control' | 'treatment';
        };
        Insert: Omit<Database['public']['Tables']['users']['Row'], 'id' | 'created_at'>;
        Update: Partial<Database['public']['Tables']['users']['Insert']>;
      };
      mastery: {
        Row: {
          id: number;
          user_id: string;
          topic_id: number;
          p_l: number;
          p_t: number;
          p_g: number;
          p_s: number;
          attempts: number;
          correct: number;
          updated_at: string;
        };
        Insert: Omit<Database['public']['Tables']['mastery']['Row'], 'id' | 'updated_at'>;
        Update: Partial<Database['public']['Tables']['mastery']['Insert']>;
      };
      sessions: {
        Row: {
          id: number;
          user_id: string;
          topic_id: number;
          started_at: string;
          ended_at: string | null;
          questions_attempted: number;
          questions_correct: number;
        };
        Insert: Omit<Database['public']['Tables']['sessions']['Row'], 'id'>;
        Update: Partial<Database['public']['Tables']['sessions']['Insert']>;
      };
      responses: {
        Row: {
          id: number;
          session_id: number;
          question_id: string;
          user_answer: string;
          is_correct: boolean;
          response_time_ms: number;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['responses']['Row'], 'id' | 'created_at'>;
        Update: Partial<Database['public']['Tables']['responses']['Insert']>;
      };
    };
  };
}

// Auth helpers
export const signUp = async (email: string, password: string, displayName: string, gradeLevel: number) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: {
        display_name: displayName,
        grade_level: gradeLevel,
      },
    },
  });
  return { data, error };
};

export const signIn = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });
  return { data, error };
};

export const signOut = async () => {
  const { error } = await supabase.auth.signOut();
  return { error };
};

export const getCurrentUser = async () => {
  const { data: { user }, error } = await supabase.auth.getUser();
  return { user, error };
};

// Session listener
export const onAuthStateChange = (callback: (event: string, session: any) => void) => {
  return supabase.auth.onAuthStateChange(callback);
};

// Database helpers
export const getUserMastery = async (userId: string) => {
  const { data, error } = await supabase
    .from('mastery')
    .select('*, topics(*)')
    .eq('user_id', userId);
  return { data, error };
};

export const updateMastery = async (
  userId: string,
  topicId: number,
  updates: Partial<Database['public']['Tables']['mastery']['Update']>
) => {
  const { data, error } = await supabase
    .from('mastery')
    .upsert({
      user_id: userId,
      topic_id: topicId,
      ...updates,
    })
    .select();
  return { data, error };
};

export const recordResponse = async (response: Database['public']['Tables']['responses']['Insert']) => {
  const { data, error } = await supabase
    .from('responses')
    .insert(response)
    .select();
  return { data, error };
};

// Realtime subscriptions
export const subscribeToLeaderboard = (callback: (payload: any) => void) => {
  return supabase
    .channel('leaderboard')
    .on('postgres_changes', { event: '*', schema: 'public', table: 'users' }, callback)
    .subscribe();
};

export default supabase;
