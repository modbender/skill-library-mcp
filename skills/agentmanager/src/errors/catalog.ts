export type ErrorCatalogEntry = {
  code: string;
  retryable: boolean;
  suggested_action?: 'retry' | 'upgrade' | 'downgrade' | 'replan';
  description: string;
};

export const ERROR_CATALOG: ErrorCatalogEntry[] = [
  { code: 'DAG_DEADLOCK', retryable: false, suggested_action: 'replan', description: 'No ready tasks and no running tasks were found.' },
  { code: 'PLAN_INVALID', retryable: false, description: 'The supplied plan failed validation.' },
  { code: 'RATE_LIMIT', retryable: true, suggested_action: 'retry', description: 'Rate limit exceeded for the token owner.' },
  { code: 'RUN_NOT_FOUND', retryable: false, description: 'Run id does not exist or expired.' },
  { code: 'RUN_SYNC_TIMEOUT', retryable: true, suggested_action: 'retry', description: 'Synchronous wait timed out.' },
  { code: 'RUN_SYNC_ABORTED', retryable: true, suggested_action: 'retry', description: 'Synchronous wait was aborted by the client.' },
  { code: 'RUN_CANCELLED', retryable: false, description: 'Run execution was cancelled.' },
  { code: 'BUDGET_COST', retryable: false, suggested_action: 'downgrade', description: 'Cost budget exceeded.' },
  { code: 'BUDGET_TOOL_CALLS', retryable: false, suggested_action: 'downgrade', description: 'Tool call budget exceeded.' },
  { code: 'BUDGET_LATENCY', retryable: false, suggested_action: 'replan', description: 'Latency budget exceeded.' },
  { code: 'AUTH_INVALID_TOKEN', retryable: false, description: 'Run token is missing or not allowed.' },
  { code: 'TOOL_TIMEOUT', retryable: true, suggested_action: 'retry', description: 'Tool call timed out.' },
  { code: 'TOOL_NOT_ALLOWED', retryable: false, description: 'Tool is not allowed by task or policy.' },
  { code: 'INTERNAL', retryable: false, description: 'Unexpected internal error.' }
];
