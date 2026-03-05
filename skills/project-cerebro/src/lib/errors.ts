/**
 * Custom error types with proper error codes
 */

export enum ErrorCode {
  // Database errors
  DATABASE_ERROR = 'DATABASE_ERROR',
  RECORD_NOT_FOUND = 'RECORD_NOT_FOUND',
  DUPLICATE_RECORD = 'DUPLICATE_RECORD',

  // Validation errors
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  INVALID_INPUT = 'INVALID_INPUT',

  // Brain/Task errors
  BRAIN_NOT_FOUND = 'BRAIN_NOT_FOUND',
  TASK_NOT_FOUND = 'TASK_NOT_FOUND',
  TASK_EXECUTION_FAILED = 'TASK_EXECUTION_FAILED',
  SCHEDULE_COMPUTATION_FAILED = 'SCHEDULE_COMPUTATION_FAILED',

  // Integration errors
  DISCORD_ERROR = 'DISCORD_ERROR',
  OPENCLAW_ERROR = 'OPENCLAW_ERROR',

  // Generic errors
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  NOT_IMPLEMENTED = 'NOT_IMPLEMENTED',
}

export class CerebroError extends Error {
  public readonly code: ErrorCode;
  public readonly statusCode: number;
  public readonly context?: Record<string, any>;

  constructor(
    code: ErrorCode,
    message: string,
    statusCode: number = 500,
    context?: Record<string, any>
  ) {
    super(message);
    this.name = 'CerebroError';
    this.code = code;
    this.statusCode = statusCode;
    this.context = context;
    Error.captureStackTrace(this, this.constructor);
  }
}

export class DatabaseError extends CerebroError {
  constructor(message: string, context?: Record<string, any>) {
    super(ErrorCode.DATABASE_ERROR, message, 500, context);
    this.name = 'DatabaseError';
  }
}

export class RecordNotFoundError extends CerebroError {
  constructor(entity: string, id: string | number, context?: Record<string, any>) {
    super(
      ErrorCode.RECORD_NOT_FOUND,
      `${entity} with id ${id} not found`,
      404,
      context
    );
    this.name = 'RecordNotFoundError';
  }
}

export class ValidationError extends CerebroError {
  constructor(message: string, context?: Record<string, any>) {
    super(ErrorCode.VALIDATION_ERROR, message, 400, context);
    this.name = 'ValidationError';
  }
}

export class BrainNotFoundError extends CerebroError {
  constructor(brainId: string, context?: Record<string, any>) {
    super(
      ErrorCode.BRAIN_NOT_FOUND,
      `Brain with id ${brainId} not found`,
      404,
      context
    );
    this.name = 'BrainNotFoundError';
  }
}

export class TaskNotFoundError extends CerebroError {
  constructor(taskId: string, context?: Record<string, any>) {
    super(
      ErrorCode.TASK_NOT_FOUND,
      `Task with id ${taskId} not found`,
      404,
      context
    );
    this.name = 'TaskNotFoundError';
  }
}

export class TaskExecutionError extends CerebroError {
  constructor(message: string, context?: Record<string, any>) {
    super(ErrorCode.TASK_EXECUTION_FAILED, message, 500, context);
    this.name = 'TaskExecutionError';
  }
}

export class DiscordError extends CerebroError {
  constructor(message: string, context?: Record<string, any>) {
    super(ErrorCode.DISCORD_ERROR, message, 500, context);
    this.name = 'DiscordError';
  }
}

export class OpenClawError extends CerebroError {
  constructor(message: string, context?: Record<string, any>) {
    super(ErrorCode.OPENCLAW_ERROR, message, 500, context);
    this.name = 'OpenClawError';
  }
}
