/**
 * 用户类型定义
 */
export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

/**
 * 小说类型定义
 */
export interface Novel {
  id: number;
  title: string;
  genre?: string;
  description?: string;
  worldview?: string;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

export interface StyleSample {
  id: number;
  novel_id: number;
  name: string;
  sample_preview: string;
  style_features: string[];
  created_at: string;
}

/**
 * 章节类型定义
 */
export interface Chapter {
  id: number;
  novel_id: number;
  chapter_number: number;
  title: string;
  content: string;
  word_count: number;
  created_at: string;
  updated_at?: string;
}

/**
 * 登录请求
 */
export interface LoginRequest {
  username: string;
  password: string;
}

/**
 * 注册请求
 */
export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

/**
 * 认证响应
 */
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

/**
 * 小说创建请求
 */
export interface NovelCreate {
  title: string;
  genre?: string;
  description?: string;
  worldview?: string;
}

/**
 * 章节创建请求
 */
export interface ChapterCreate {
  chapter_number: number;
  title: string;
  content: string;
}

/**
 * Agent工作流中单个步骤
 */
export interface AgentWorkflowStep {
  id: string;
  parent_id?: string | null;
  type: string;
  agent_name?: string | null;
  title: string;
  description?: string | null;
  input: Record<string, any>;
  output: Record<string, any>;
  data_sources: Record<string, any>;
  llm: Record<string, any>;
  status: string;
  started_at?: string | null;
  finished_at?: string | null;
  duration_ms?: number | null;
}

/**
 * 单次Agent工作流运行的完整追踪
 */
export interface AgentWorkflowTrace {
  run_id: string;
  trigger: string;
  novel_id?: number | null;
  chapter_id?: number | null;
  user_id?: number | null;
  summary?: string | null;
  steps: AgentWorkflowStep[];
  created_at: string;
}
