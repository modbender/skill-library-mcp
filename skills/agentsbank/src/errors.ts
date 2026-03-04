/**
 * AgentsBank SDK Typed Errors
 * 19 specific error codes for precise error handling
 */

export enum ErrorCode {
  // Validation Errors (4xx)
  INVALID_ADDRESS = 'INVALID_ADDRESS',
  INVALID_AMOUNT = 'INVALID_AMOUNT',
  INVALID_CHAIN = 'INVALID_CHAIN',
  INVALID_CURRENCY = 'INVALID_CURRENCY',
  INSUFFICIENT_FUNDS = 'INSUFFICIENT_FUNDS',
  
  // Authentication Errors (4xx)
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  INVALID_CREDENTIALS = 'INVALID_CREDENTIALS',
  SESSION_EXPIRED = 'SESSION_EXPIRED',
  
  // Resource Errors (4xx)
  NOT_FOUND = 'NOT_FOUND',
  RESOURCE_EXISTS = 'RESOURCE_EXISTS',
  CONFLICT = 'CONFLICT',
  
  // System Errors (5xx)
  RATE_LIMITED = 'RATE_LIMITED',
  TIMEOUT = 'TIMEOUT',
  NETWORK_ERROR = 'NETWORK_ERROR',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  
  // SDK-specific
  INSUFFICIENT_BALANCE = 'INSUFFICIENT_BALANCE',
  GUARDRAIL_VIOLATION = 'GUARDRAIL_VIOLATION',
  RETRY_FAILED = 'RETRY_FAILED',
}

/**
 * Extended AgentsBank error with typed codes
 */
export class AgentsBankError extends Error {
  public readonly code: ErrorCode;
  public readonly status: number;
  public readonly details?: Record<string, unknown>;
  public readonly retryable: boolean;

  constructor(
    message: string,
    code: ErrorCode,
    status: number = 500,
    details?: Record<string, unknown>,
    retryable: boolean = false
  ) {
    super(message);
    this.name = 'AgentsBankError';
    this.code = code;
    this.status = status;
    this.details = details;
    this.retryable = retryable;
    Object.setPrototypeOf(this, AgentsBankError.prototype);
  }

  /**
   * Check if error is retryable (transient failure)
   */
  isRetryable(): boolean {
    return (
      this.retryable ||
      this.code === ErrorCode.TIMEOUT ||
      this.code === ErrorCode.NETWORK_ERROR ||
      this.code === ErrorCode.RATE_LIMITED ||
      this.status >= 500
    );
  }

  /**
   * Convert to JSON for logging/serialization
   */
  toJSON() {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      status: this.status,
      details: this.details,
      retryable: this.retryable,
    };
  }
}

/**
 * Error factory for creating typed errors
 */
export const createError = (
  message: string,
  code: ErrorCode,
  status: number = 500,
  details?: Record<string, unknown>
): AgentsBankError => {
  const retryable =
    code === ErrorCode.TIMEOUT ||
    code === ErrorCode.NETWORK_ERROR ||
    code === ErrorCode.RATE_LIMITED;

  return new AgentsBankError(message, code, status, details, retryable);
};

/**
 * Helper to detect error code from HTTP status
 */
export const errorCodeFromStatus = (status: number): ErrorCode => {
  if (status === 400) return ErrorCode.INVALID_ADDRESS;
  if (status === 401) return ErrorCode.UNAUTHORIZED;
  if (status === 403) return ErrorCode.FORBIDDEN;
  if (status === 404) return ErrorCode.NOT_FOUND;
  if (status === 409) return ErrorCode.CONFLICT;
  if (status === 429) return ErrorCode.RATE_LIMITED;
  if (status >= 500) return ErrorCode.INTERNAL_ERROR;
  return ErrorCode.INTERNAL_ERROR;
};
