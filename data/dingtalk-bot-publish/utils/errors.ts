/**
 * 错误处理工具模块
 */

export interface ApiError {
  code: string;
  message: string;
  description?: string | null;
  requestId?: string | null;
}

export interface SuccessResult<T = any> {
  success: true;
  data: T;
}

export interface ErrorResult {
  success: false;
  error: ApiError;
}

/**
 * 创建认证错误结果
 */
export function createAuthError(message: string): ErrorResult {
  return {
    success: false,
    error: {
      code: 'AUTH_FAILED',
      message: message,
    }
  };
}

/**
 * 创建参数错误结果
 */
export function createInvalidArgumentsError(message: string, usage?: string): ErrorResult {
  const result: ErrorResult = {
    success: false,
    error: {
      code: 'INVALID_ARGUMENTS',
      message: message,
    }
  };
  
  if (usage) {
    (result.error as any).usage = usage;
  }
  
  return result;
}

/**
 * 创建凭证缺失错误结果
 */
export function createMissingCredentialsError(): ErrorResult {
  return {
    success: false,
    error: {
      code: 'MISSING_CREDENTIALS',
      message: '缺少钉钉应用凭证，请设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET',
      usage: 'export DINGTALK_APP_KEY=your-app-key && export DINGTALK_APP_SECRET=your-app-secret'
    }
  };
}

/**
 * 创建通用API错误结果
 */
export function createApiError(code: string, message: string): ErrorResult {
  return {
    success: false,
    error: {
      code: code || 'UNKNOWN_ERROR',
      message: message || '未知错误',
    }
  };
}