/**
 * 即梦AI API 共享工具库
 * 提供火山引擎签名鉴权、API调用等通用功能
 */

import axios from 'axios';
import CryptoJS from 'crypto-js';

// 常量配置
export const API_ENDPOINT = 'https://visual.volcengineapi.com';
export const REGION = 'cn-north-1';
export const SERVICE = 'cv';
export const SUBMIT_ACTION = 'CVSync2AsyncSubmitTask';
export const QUERY_ACTION = 'CVSync2AsyncGetResult';
export const VERSION = '2022-08-31';

// 服务标识常量
export const REQ_KEYS = {
  // 文生图
  T2I_V30: 'jimeng_t2i_v30',
  T2I_V31: 'jimeng_t2i_v31',
  T2I_V40: 'jimeng_t2i_v40',
  // 图生图
  I2I_V30: 'jimeng_i2i_v30',
  I2I_SEED3: 'jimeng_i2i_seed3_tilesr_cvtob',
  I2I_INPAINT: 'jimeng_image2image_dream_inpaint',
  // 视频
  T2V_V30_1080P: 'jimeng_t2v_v30_1080p',
  I2V_FIRST_V30: 'jimeng_i2v_first_v30_1080',
  I2V_FIRST_TAIL_V30: 'jimeng_i2v_first_tail_v30_1080',
  TI2V_V30_PRO: 'jimeng_ti2v_v30_pro',
  // 数字人
  DREAM_ACTOR_M1: 'jimeng_dream_actor_m1_gen_video_cv',
  DREAM_ACTOR_M20: 'jimeng_dreamactor_m20_gen_video',
  REALMAN_AVATAR: 'jimeng_realman_avatar_picture_omni_v15',
  REALMAN_CREATE_ROLE: 'jimeng_realman_avatar_picture_create_role_omni_v15',
} as const;

// 支持的宽高比
export const VALID_RATIOS = ['1:1', '9:16', '16:9', '3:4', '4:3', '2:3', '3:2', '1:2', '2:1'];

// 视频支持的宽高比
export const VALID_VIDEO_RATIOS = ['16:9', '4:3', '1:1', '3:4', '9:16', '21:9'];

// 接口返回类型
export interface ApiResponse {
  ResponseMetadata?: {
    RequestId: string;
    Action: string;
    Version: string;
    Service: string;
    Region: string;
    Error?: {
      Code: string;
      Message: string;
    };
  };
  Result?: {
    task_id: string;
    status?: 'done' | 'processing' | 'failed' | 'in_queue' | 'generating' | 'not_found' | 'expired';
    resp?: {
      success?: boolean;
      data?: {
        pe_result?: Array<{
          url: string;
          uri: string;
          width: number;
          height: number;
        }>;
        binary_data_base64?: string[];
        image_urls?: string[];
        video_url?: string;
      };
    };
  };
}

export interface SuccessResult {
  success: true;
  taskId: string;
  images?: Array<{
    url: string;
    width: number;
    height: number;
  }>;
  videoUrl?: string;
  requestId: string;
}

export interface ErrorResult {
  success: false;
  error: {
    code: string;
    message: string;
  };
}

export type Result = SuccessResult | ErrorResult;

/**
 * SHA256哈希
 */
export function sha256(message: string): string {
  return CryptoJS.SHA256(message).toString(CryptoJS.enc.Hex);
}

/**
 * HMAC-SHA256签名
 */
export function hmacSha256(key: string, message: string): string {
  return CryptoJS.HmacSHA256(message, key).toString(CryptoJS.enc.Hex);
}

/**
 * 生成火山引擎签名 (AWS Signature Version 4)
 */
export function generateSignature(
  accessKey: string,
  secretKey: string,
  method: string,
  uri: string,
  queryString: string,
  headers: Record<string, string>,
  payload: string,
  datetime: string,
  date: string
): Record<string, string> {
  // 1. 创建CanonicalRequest
  const headerKeys = Object.keys(headers).sort();
  const canonicalHeaders = headerKeys.map(k => `${k.toLowerCase()}:${headers[k].trim()}\n`).join('');
  const signedHeaders = headerKeys.map(k => k.toLowerCase()).join(';');
  
  const payloadHash = sha256(payload);
  const canonicalRequest = [
    method,
    uri,
    queryString,
    canonicalHeaders,
    signedHeaders,
    payloadHash
  ].join('\n');

  // 2. 创建StringToSign
  const credentialScope = `${date}/${REGION}/${SERVICE}/request`;
  const stringToSign = [
    'HMAC-SHA256',
    datetime,
    credentialScope,
    sha256(canonicalRequest)
  ].join('\n');

  // 3. 计算签名
  const kDate = CryptoJS.HmacSHA256(date, 'HMAC-SHA256' + secretKey);
  const kRegion = CryptoJS.HmacSHA256(REGION, kDate);
  const kService = CryptoJS.HmacSHA256(SERVICE, kRegion);
  const kSigning = CryptoJS.HmacSHA256('request', kService);
  const signature = CryptoJS.HmacSHA256(stringToSign, kSigning).toString(CryptoJS.enc.Hex);

  // 4. 生成Authorization头
  const authorization = `HMAC-SHA256 Credential=${accessKey}/${credentialScope}, SignedHeaders=${signedHeaders}, Signature=${signature}`;

  return {
    'Authorization': authorization,
    'X-Date': datetime
  };
}

/**
 * 提交任务
 */
export async function submitTask(
  accessKey: string,
  secretKey: string,
  reqKey: string,
  body: Record<string, any>
): Promise<{ taskId: string; requestId: string }> {
  const datetime = new Date().toISOString().replace(/[:-]|\.\d{3}/g, '');
  const date = datetime.substring(0, 8);

  const payload = JSON.stringify(body);
  const contentType = 'application/json';

  const headers: Record<string, string> = {
    'Host': 'visual.volcengineapi.com',
    'Content-Type': contentType,
    'X-Content-Sha256': sha256(payload),
  };

  const signatureHeaders = generateSignature(
    accessKey,
    secretKey,
    'POST',
    '/',
    `Action=${SUBMIT_ACTION}&Version=${VERSION}`,
    headers,
    payload,
    datetime,
    date
  );

  const requestHeaders = {
    ...headers,
    ...signatureHeaders
  };

  const response = await axios.post<ApiResponse>(
    `${API_ENDPOINT}?Action=${SUBMIT_ACTION}&Version=${VERSION}`,
    payload,
    {
      headers: requestHeaders,
      timeout: 30000
    }
  );

  const requestId = response.data.ResponseMetadata?.RequestId || '';

  if (response.data.ResponseMetadata?.Error) {
    const error = response.data.ResponseMetadata.Error;
    throw new Error(`${error.Code}: ${error.Message}`);
  }

  const taskId = response.data.Result?.task_id;
  if (!taskId) {
    throw new Error('提交任务失败：响应中未包含 task_id');
  }

  return { taskId, requestId };
}

/**
 * 查询任务状态
 */
export async function queryTask(
  accessKey: string,
  secretKey: string,
  reqKey: string,
  taskId: string,
  reqJson?: string
): Promise<ApiResponse['Result']> {
  const datetime = new Date().toISOString().replace(/[:-]|\.\d{3}/g, '');
  const date = datetime.substring(0, 8);

  const body: Record<string, any> = {
    req_key: reqKey,
    task_id: taskId
  };
  
  if (reqJson) {
    body.req_json = reqJson;
  }

  const payload = JSON.stringify(body);
  const contentType = 'application/json';

  const headers: Record<string, string> = {
    'Host': 'visual.volcengineapi.com',
    'Content-Type': contentType,
    'X-Content-Sha256': sha256(payload),
  };

  const signatureHeaders = generateSignature(
    accessKey,
    secretKey,
    'POST',
    '/',
    `Action=${QUERY_ACTION}&Version=${VERSION}`,
    headers,
    payload,
    datetime,
    date
  );

  const requestHeaders = {
    ...headers,
    ...signatureHeaders
  };

  const response = await axios.post<ApiResponse>(
    `${API_ENDPOINT}?Action=${QUERY_ACTION}&Version=${VERSION}`,
    payload,
    {
      headers: requestHeaders,
      timeout: 30000
    }
  );

  if (response.data.ResponseMetadata?.Error) {
    const error = response.data.ResponseMetadata.Error;
    throw new Error(`${error.Code}: ${error.Message}`);
  }

  return response.data.Result;
}

/**
 * 轮询等待任务完成
 */
export async function waitForTask(
  accessKey: string,
  secretKey: string,
  reqKey: string,
  taskId: string,
  maxAttempts: number = 60,
  intervalMs: number = 2000,
  reqJson?: string
): Promise<ApiResponse['Result']> {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    if (process.env.DEBUG) {
      console.error(`[${attempt}/${maxAttempts}] 查询任务状态...`);
    }
    
    const result = await queryTask(accessKey, secretKey, reqKey, taskId, reqJson);
    
    if (result?.status === 'done') {
      if (process.env.DEBUG) {
        console.error('任务完成！');
      }
      return result;
    }
    
    if (result?.status === 'failed') {
      throw new Error('任务执行失败');
    }
    
    if (attempt < maxAttempts) {
      if (process.env.DEBUG) {
        console.error(`任务处理中，${intervalMs / 1000}秒后重试...`);
      }
      await new Promise(resolve => setTimeout(resolve, intervalMs));
    }
  }
  
  throw new Error(`任务超时，在 ${maxAttempts} 次尝试后仍未完成`);
}

/**
 * 获取环境变量凭证
 */
export function getCredentials(): { accessKey: string; secretKey: string } {
  const accessKey = process.env.VOLC_ACCESS_KEY;
  const secretKey = process.env.VOLC_SECRET_KEY;

  if (!accessKey || !secretKey) {
    throw new Error('MISSING_CREDENTIALS');
  }

  return { accessKey, secretKey };
}

/**
 * 输出错误结果
 */
export function outputError(code: string, message: string): void {
  const result: ErrorResult = {
    success: false,
    error: {
      code,
      message
    }
  };
  console.error(JSON.stringify(result, null, 2));
  process.exit(1);
}