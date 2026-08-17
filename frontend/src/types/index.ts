export interface Run {
  id: string;
  goal: string;
  model_provider: string;
  model_name: string;
  status: string;
  created_at: string;
  updated_at: string;
  plan_json: Record<string, unknown> | null;
  error: string | null;
  cost_usd: number;
  tokens: number;
}

export interface Step {
  id: string;
  run_id?: string;
  index: number;
  description: string;
  status: string;
  input_data: Record<string, unknown> | null;
  output_data: Record<string, unknown> | null;
  retries: number;
  error: string | null;
  started_at: string | null;
  completed_at: string | null;
  cost_usd: number;
  tokens: number;
}

export interface RunDetail extends Run {
  steps: Step[];
}

export interface Trace {
  id: string;
  run_id: string;
  step_id: string | null;
  event_type: string;
  provider: string | null;
  model: string | null;
  input_data: Record<string, unknown> | null;
  output_data: Record<string, unknown> | null;
  token_usage: { prompt_tokens?: number; completion_tokens?: number; total_tokens?: number } | null;
  duration_ms: number | null;
  cost_usd: number;
  timestamp: string;
}
