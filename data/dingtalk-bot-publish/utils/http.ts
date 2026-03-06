// HTTP请求工具模块
// 用于统一处理钉钉API的HTTP请求

import * as https from 'https';

/**
 * 钉钉API请求选项接口
 */
interface DingTalkRequestOptions {
  method: string;
  path: string;
  accessToken: string;
  body?: any;
  headers?: Record<string, string>;
}

/**
 * 执行钉钉API请求
 * @param options 请求选项
 * @returns Promise<any> API响应数据
 */
export async function dingtalkRequest(options: DingTalkRequestOptions): Promise<any> {
  const { method, path, accessToken, body, headers = {} } = options;

  return new Promise((resolve, reject) => {
    const requestOptions = {
      hostname: 'oapi.dingtalk.com',
      path: `${path}?access_token=${accessToken}`,
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
    };

    const req = https.request(requestOptions, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          
          // 检查钉钉API错误码
          if (parsed.errcode !== undefined && parsed.errcode !== 0) {
            reject({
              code: parsed.errcode,
              message: parsed.errmsg || 'Unknown error',
              requestId: parsed.requestId || null,
            });
          } else if (res.statusCode && res.statusCode >= 400) {
            reject({
              code: res.statusCode,
              message: `HTTP ${res.statusCode} error`,
              data: parsed,
            });
          } else {
            resolve(parsed);
          }
        } catch (error) {
          reject(new Error(`Invalid JSON response: ${data}`));
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    if (body) {
      req.write(JSON.stringify(body));
    }
    req.end();
  });
}

/**
 * 构建标准的成功响应
 * @param data 响应数据
 * @returns 标准化成功响应对象
 */
export function createSuccessResponse(data: any): any {
  return {
    success: true,
    ...data,
  };
}

/**
 * 构建标准的错误响应
 * @param error 错误信息
 * @param userId 可选的用户ID
 * @returns 标准化错误响应对象
 */
export function createErrorResponse(error: any, userId?: string): any {
  return {
    success: false,
    ...(userId ? { userId } : {}),
    error: {
      code: error.code || 'UNKNOWN_ERROR',
      message: error.message || error.msg || JSON.stringify(error),
      description: error.description || null,
      requestId: error.requestId || null,
    },
  };
}