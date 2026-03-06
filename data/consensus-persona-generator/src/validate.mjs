const TOP_LEVEL_KEYS = new Set([
  'board_id',
  'task_context',
  'n_personas',
  'persona_pack',
  'force_regenerate'
]);

const TASK_CONTEXT_KEYS = new Set(['goal', 'audience', 'risk_tolerance', 'constraints', 'domain']);

export function validateInput(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) return 'input must be an object';
  for (const k of Object.keys(input)) {
    if (!TOP_LEVEL_KEYS.has(k)) return `unknown field: ${k}`;
  }
  if (typeof input.board_id !== 'string' || !input.board_id.trim()) return 'board_id is required';
  if (!input.task_context || typeof input.task_context !== 'object' || Array.isArray(input.task_context)) return 'task_context is required';
  for (const k of Object.keys(input.task_context)) {
    if (!TASK_CONTEXT_KEYS.has(k)) return `unknown task_context field: ${k}`;
  }
  const tc = input.task_context;
  if (typeof tc.goal !== 'string') return 'task_context.goal is required';
  if (typeof tc.audience !== 'string') return 'task_context.audience is required';
  if (!['low', 'medium', 'high'].includes(tc.risk_tolerance)) return 'task_context.risk_tolerance must be low|medium|high';
  if (!Array.isArray(tc.constraints) || tc.constraints.some((x) => typeof x !== 'string')) return 'task_context.constraints must be string[]';
  if (input.n_personas !== undefined && (typeof input.n_personas !== 'number' || Number.isNaN(input.n_personas))) return 'n_personas must be a number';
  if (input.persona_pack !== undefined && typeof input.persona_pack !== 'string') return 'persona_pack must be string';
  if (input.force_regenerate !== undefined && typeof input.force_regenerate !== 'boolean') return 'force_regenerate must be boolean';
  return null;
}
