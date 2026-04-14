// ===== Course & Lesson Types =====

export interface Course {
  id: string;
  title: string;
  description: string;
  grade_range: string; // e.g. "6-8"
  order: number;
  status: 'draft' | 'published' | 'archived';
  created_at: string;
  updated_at: string;
}

export interface Lesson {
  id: string;
  course_id: string;
  title: string;
  description: string;
  order: number;
  status: 'draft' | 'published';
  teaching_methods: TeachingMethod[];
  animation_data: AnimationData;
  exercises: Exercise[];
  created_at: string;
  updated_at: string;
}

// ===== Animation System Types =====

export type TeachingMethod = 'make_ten' | 'break_ten' | 'number_line' | 'counting' | 'step_by_step' | 'comparison';

export interface AnimationData {
  expression: string;
  methods: MethodAnimation[];
}

export interface MethodAnimation {
  type: TeachingMethod;
  title: string;
  steps: AnimationStep[];
}

export interface AnimationStep {
  action: string;
  narration: string;
  [key: string]: any;
}

// ===== Exercise Types =====

export interface Exercise {
  id: string;
  lesson_id: string;
  type: 'choice' | 'fill_blank' | 'drag_drop' | 'true_false';
  question: string;
  expression: string;
  options?: string[];
  correct_answer: string | number;
  solutions: Solution[];
  hints: string[];
  difficulty: 1 | 2 | 3;
  order: number;
}

export interface Solution {
  method: TeachingMethod;
  steps: string[];
}

// ===== Progress Types =====

export interface UserProgress {
  user_id: string;
  lesson_id: string;
  stars: 0 | 1 | 2 | 3;
  correct_count: number;
  total_count: number;
  time_spent: number; // seconds
  completed_at?: string;
}

// ===== AI Config Types =====

export type AIProvider = 'openai' | 'claude' | 'grok' | 'kimi' | 'custom';

export interface AIConfig {
  provider: AIProvider;
  api_key: string;
  base_url: string;
  model: string;
}
