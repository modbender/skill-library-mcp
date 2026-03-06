export interface TaskInput {
  prompt: string;
  relevantFiles?: string[];
  constraints?: string[];
  successCriteria?: string[];
  worktreePath: string;
  taskId?: string;
  reportPath?: string;
}
