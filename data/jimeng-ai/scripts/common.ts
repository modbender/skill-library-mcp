/**
 * 即梦AI API 共享工具库
 * 提供火山引擎签名鉴权、API调用等通用功能
 * OpenAPI 格式 - 基于 URL 参数签名
 */

import axios from 'axios';
import * as crypto from 'crypto';

// 常量配置 - OpenAPI 格式
export const API_ENDPOINT = 'https://open.volcengineapi.com/';
export const REGION = 'cn-beijing';
export const SERVICE = 'cv';
export const SUBMIT_ACTION = 'JimengT2IV31SubmitTask';
export const QUERY_ACTION = 'JimengT2IV31GetResult';
export const VERSION = '2024-06-06';

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
    code: number;
    message: string;
    request_id: string;
    status: number;
    time_elapsed: string;
    data: {
      task_id: string;
      status?: 'done' | 'processing' | 'failed' | 'in_queue' | 'generating' | 'not_found' | 'expired';
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
 * 将字符串中的非ASCII字符转义为 \uXXXX 格式 (兼容Python json.dumps默认行为)
 */
export function escapeUnicode(str: string): string {
  return str.replace(/[^\x00-\x7F]/g, (char) => {
    const hex = char.charCodeAt(0).toString(16).padStart(4, '0');
    return '\\u' + hex;
  });
}

/**
 * JSON序列化 (兼容Python SDK默认行为)
 * Python SDK默认: separators=(', ', ': '), ensure_ascii=True
 */
export function jsonStringify(obj: any): string {
  // 使用自定义序列化来匹配Python SDK格式
  if (obj === null) return 'null';
  if (typeof obj === 'boolean') return obj ? 'true' : 'false';
  if (typeof obj === 'number') return String(obj);
  if (typeof obj === 'string') {
    // 转义字符串并处理Unicode（匹配Python json.dumps ensure_ascii=True）
    let escaped = obj
      .replace(/\\/g, '\\\\')
      .replace(/"/g, '\\"')
      .replace(/\n/g, '\\n')
      .replace(/\r/g, '\\r')
      .replace(/\t/g, '\\t');
    // 转义非ASCII字符
    escaped = escapeUnicode(escaped);
    return '"' + escaped + '"';
  }
  if (Array.isArray(obj)) {
    return '[' + obj.map(jsonStringify).join(', ') + ']';
  }
  if (typeof obj === 'object') {
    const pairs = Object.keys(obj).map(key => {
      return jsonStringify(key) + ': ' + jsonStringify(obj[key]);
    });
    return '{' + pairs.join(', ') + '}';
  }
  return String(obj);
}

export function sha256(message: string): string {
  return crypto.createHash('sha256').update(message, 'utf8').digest('hex');
}

/**
 * HMAC-SHA256签名
 */
export function hmacSha256(key: string | Buffer, message: string): Buffer {
  return crypto.createHmac('sha256', key).update(message, 'utf8').digest();
}

/**
 * URI 编码 (与 Python SDK Util.quote(key, safe='-_.~') 行为一致)
 */
function uriEscape(str: string): string {
  try {
    return encodeURIComponent(str)
      .replace(/[^A-Za-z0-9_.~\-%]+/g, escape)
      .replace(/[*]/g, (ch) => `%${ch.charCodeAt(0).toString(16).toUpperCase()}`);
  } catch (e) {
    return '';
  }
}

/**
 * 将参数对象按 key 排序后转为查询字符串 (与 Python SDK Util.norm_query 一致)
 */
function normQuery(params: Record<string, string>): string {
  return Object.keys(params)
    .sort()
    .map((key) => `${uriEscape(key)}=${uriEscape(params[key])}`)
    .join('&');
}

/**
 * 生成火山引擎 OpenAPI 签名 (URL 参数格式)
 * 严格对齐 Python SDK SignerV4.sign_url 方法
 * 参考: https://www.volcengine.com/docs/6369/67269
 */
export function generateOpenApiSignature(
  accessKey: string,
  secretKey: string,
  action: string,
  version: string,
  body: Record<string, any>,
  datetime: string,
  date: string,
  securityToken?: string,
  expires: number = 3600
): string {
  const credentialScope = `${date}/${REGION}/${SERVICE}/request`;
  const credential = `${accessKey}/${credentialScope}`;

  // 1. 构建 query 参数（对齐 Python SDK sign_url 流程）
  const query: Record<string, string> = {
    'Action': action,
    'Version': version,
  };

  query['X-Date'] = datetime;
  query['X-NotSignBody'] = '1';
  query['X-Credential'] = credential;
  query['X-Algorithm'] = 'HMAC-SHA256';
  query['X-SignedHeaders'] = '';
  query['X-Expires'] = expires.toString();

  if (securityToken) {
    query['X-Security-Token'] = securityToken;
  }

  // X-SignedQueries: 先设为空再覆盖为所有 key 的排序分号列表
  // 这样 X-SignedQueries 自身也在列表中，且参与签名计算
  query['X-SignedQueries'] = '';
  query['X-SignedQueries'] = Object.keys(query).sort().join(';');

  // 2. 构建 Canonical Request (对齐 Python SDK hashed_simple_canonical_request_v4)
  // canonical_request = '\n'.join([method, norm_uri(path), norm_query(query), '\n', signed_headers, body_hash])
  const canonicalQueryString = normQuery(query);
  const bodyHash = sha256('');
  const canonicalRequest = [
    'POST',
    '/',
    canonicalQueryString,
    '\n',           // Python SDK: '\n' 作为独立元素 (canonical headers 为空 + 尾部换行)
    '',             // signed_headers = ''
    bodyHash
  ].join('\n');

  // 3. 构建 String to Sign
  const stringToSign = [
    'HMAC-SHA256',
    datetime,
    credentialScope,
    sha256(canonicalRequest)
  ].join('\n');

  // 4. 计算签名密钥（无前缀，直接使用 secretKey）
  const kDate = hmacSha256(secretKey, date);
  const kRegion = hmacSha256(kDate, REGION);
  const kService = hmacSha256(kRegion, SERVICE);
  const kSigning = hmacSha256(kService, 'request');

  // 5. 计算签名
  const signature = hmacSha256(kSigning, stringToSign).toString('hex');

  // 6. 添加 X-Signature，用 normQuery 编码输出
  query['X-Signature'] = signature;
  return normQuery(query);
}

/**
 * 提交任务 - OpenAPI 格式
 */
export async function submitTask(
  accessKey: string,
  secretKey: string,
  reqKey: string,
  body: Record<string, any>,
  securityToken?: string
): Promise<{ taskId: string; requestId: string }> {
  const datetime = new Date().toISOString().replace(/[:-]|\.\d{3}/g, '');
  const date = datetime.substring(0, 8);

  const payload = jsonStringify(body);

  // 构建签名 URL 参数
  const queryString = generateOpenApiSignature(
    accessKey, secretKey, SUBMIT_ACTION, VERSION, body, datetime, date, securityToken
  );

  const url = `${API_ENDPOINT}?${queryString}`;

  // 仅在 DEBUG 模式下打印调试信息，避免泄露凭证到日志
  if (process.env.DEBUG) {
    console.error('Debug - Request URL:', url.slice(0, 200) + '...');
    console.error('Debug - Request Body:', payload);
  }

  let response: any;
  try {
    response = await axios.post<ApiResponse>(
      url,
      payload,
      {
        headers: {
          'Content-Type': 'application/json; charset=utf-8'
        },
        timeout: 30000
      }
    );
  } catch (err: any) {
    if (err.response) {
      console.error('Response Status:', err.response.status);
      console.error('Response Body:', JSON.stringify(err.response.data, null, 2));
      const respData = err.response.data;
      if (respData?.ResponseMetadata?.Error) {
        const error = respData.ResponseMetadata.Error;
        throw new Error(`${error.Code}: ${error.Message}`);
      }
    }
    throw err;
  }

  const requestId = response.data.ResponseMetadata?.RequestId || '';

  if (response.data.ResponseMetadata?.Error) {
    const error = response.data.ResponseMetadata.Error;
    throw new Error(`${error.Code}: ${error.Message}`);
  }

  const taskId = response.data.Result?.data?.task_id;
  if (!taskId) {
    console.error('Response Body:', JSON.stringify(response.data, null, 2));
    throw new Error('提交任务失败：响应中未包含 task_id');
  }

  return { taskId, requestId };
}

/**
 * 查询任务状态 - OpenAPI 格式
 */
export async function queryTask(
  accessKey: string,
  secretKey: string,
  reqKey: string,
  taskId: string,
  securityToken?: string
): Promise<ApiResponse['Result']> {
  const datetime = new Date().toISOString().replace(/[:-]|\.\d{3}/g, '');
  const date = datetime.substring(0, 8);

  const body: Record<string, any> = {
    req_key: reqKey,
    task_id: taskId
  };

  const payload = jsonStringify(body);

  // 构建签名 URL 参数
  const queryString = generateOpenApiSignature(
    accessKey, secretKey, QUERY_ACTION, VERSION, body, datetime, date, securityToken
  );

  const url = `${API_ENDPOINT}?${queryString}`;

  const response = await axios.post<ApiResponse>(
    url,
    payload,
    {
      headers: {
        'Content-Type': 'application/json; charset=utf-8'
      },
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
  securityToken?: string,
  maxAttempts: number = 60,
  intervalMs: number = 2000
): Promise<ApiResponse['Result']> {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    if (process.env.DEBUG) {
      console.error(`[${attempt}/${maxAttempts}] 查询任务状态...`);
    }

    const result = await queryTask(accessKey, secretKey, reqKey, taskId, securityToken);

    if (result?.data?.status === 'done') {
      if (process.env.DEBUG) {
        console.error('任务完成！');
      }
      return result;
    }

    if (result?.data?.status === 'failed') {
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
 * 使用 VOLCENGINE_AK 和 VOLCENGINE_SK
 * 可选: VOLCENGINE_TOKEN (Security Token，用于临时凭证)
 *
 * 注意：临时凭证(AKTP开头)可以只使用 AK + Token，不需要 SK
 */
export function getCredentials(): { accessKey: string; secretKey: string; securityToken?: string } {
  const accessKey = process.env.VOLCENGINE_AK;
  const secretKey = process.env.VOLCENGINE_SK || '';
  const securityToken = process.env.VOLCENGINE_TOKEN;

  if (!accessKey) {
    throw new Error('MISSING_CREDENTIALS');
  }

  if (!secretKey && !securityToken) {
    throw new Error('MISSING_CREDENTIALS');
  }

  return { accessKey, secretKey, securityToken };
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

/**
 * 下载图片到本地
 * @param url 图片URL
 * @param outputPath 保存路径
 * @returns 下载后的本地路径
 */
export async function downloadImage(url: string, outputPath: string): Promise<string> {
  const response = await axios.get(url, {
    responseType: 'arraybuffer',
    timeout: 60000
  });

  const fs = require('fs');
  const path = require('path');

  // 确保目录存在
  const dir = path.dirname(outputPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  fs.writeFileSync(outputPath, Buffer.from(response.data));
  return outputPath;
}
