#!/usr/bin/env ts-node
/**
 * 文生视频脚本 - Text to Video
 * 支持即梦AI v3.0 文生视频API
 *
 * 用法: ts-node text2video.ts "提示词" [选项]
 *
 * 选项:
 *   --ratio <宽高比>         视频宽高比 (默认: 9:16)
 *   --duration <时长>        视频时长: 5 或 10 秒 (默认: 5)
 *   --fps <帧率>             视频帧率: 24 或 30 (默认: 24)
 *   --output <目录>          视频下载目录 (默认: ./output)
 *   --no-download            不下载视频，只返回URL
 *   --wait                   等待任务完成
 *   --debug                  开启调试模式
 *
 * 示例:
 *   ts-node text2video.ts "一只可爱的猫咪在草地上奔跑"
 *   ts-node text2video.ts "元宵节灯笼" --ratio 9:16 --duration 5
 *   ts-node text2video.ts "科幻城市夜景" --ratio 16:9 --duration 10 --fps 30
 */

import * as path from 'path';
import * as fs from 'fs';
import * as crypto from 'crypto';
import axios from 'axios';
import {
  REQ_KEYS,
  VALID_VIDEO_RATIOS,
  getCredentials,
  outputError,
  generateOpenApiSignature,
  jsonStringify,
  API_ENDPOINT,
  VERSION
} from './common';

// 视频使用与图片相同的 API Action，通过 req_key 区分服务类型
const VIDEO_SUBMIT_ACTION = 'JimengT2IV31SubmitTask';
const VIDEO_QUERY_ACTION = 'JimengT2IV31GetResult';

// 视频 API 响应类型
interface VideoApiResponse {
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
      task_id?: string;
      status?: 'done' | 'processing' | 'failed' | 'in_queue' | 'generating' | 'not_found' | 'expired';
      video_url?: string;
      // 其他可能的字段
      resp_data?: string;
      urls?: string[];
      vid?: string[];
      aigc_meta_tagged?: boolean;
      binary_data_base64?: string[];
      image_urls?: string[] | null;
    };
  };
}

interface Text2VideoOptions {
  prompt: string;
  ratio: string;
  duration: 5 | 10;
  fps: 24 | 30;
  outputDir: string;
  download: boolean;
  wait: boolean;
  debug: boolean;
}

/**
 * 提交视频任务
 */
async function submitVideoTask(
  accessKey: string,
  secretKey: string,
  reqKey: string,
  body: Record<string, any>,
  securityToken?: string
): Promise<{ taskId: string; requestId: string }> {
  const datetime = new Date().toISOString().replace(/[:-]|\.\d{3}/g, '');
  const date = datetime.substring(0, 8);

  const payload = jsonStringify(body);

  const queryString = generateOpenApiSignature(
    accessKey, secretKey, VIDEO_SUBMIT_ACTION, VERSION, body, datetime, date, securityToken
  );

  const url = `${API_ENDPOINT}?${queryString}`;

  if (process.env.DEBUG) {
    console.error('Debug - Request URL:', url.slice(0, 200) + '...');
    console.error('Debug - Request Body:', payload);
  }

  let response: any;
  try {
    response = await axios.post<VideoApiResponse>(
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
 * 查询视频任务状态
 */
async function queryVideoTask(
  accessKey: string,
  secretKey: string,
  reqKey: string,
  taskId: string,
  securityToken?: string
): Promise<VideoApiResponse['Result']> {
  const datetime = new Date().toISOString().replace(/[:-]|\.\d{3}/g, '');
  const date = datetime.substring(0, 8);

  // 查询时需要 task_id 和 req_key
  const body: Record<string, any> = {
    req_key: reqKey,
    task_id: taskId
  };

  const payload = jsonStringify(body);

  if (process.env.DEBUG) {
    console.error('Debug - Query Body:', payload);
  }

  const queryString = generateOpenApiSignature(
    accessKey, secretKey, VIDEO_QUERY_ACTION, VERSION, body, datetime, date, securityToken
  );

  const url = `${API_ENDPOINT}?${queryString}`;

  try {
    const response = await axios.post<VideoApiResponse>(
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
  } catch (err: any) {
    if (err.response) {
      console.error('Query Error Response:', JSON.stringify(err.response.data, null, 2));
    }
    throw err;
  }
}

/**
 * 轮询等待视频任务完成
 */
async function waitForVideoTask(
  accessKey: string,
  secretKey: string,
  reqKey: string,
  taskId: string,
  securityToken?: string,
  maxAttempts: number = 60,
  intervalMs: number = 5000
): Promise<VideoApiResponse['Result']> {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    if (process.env.DEBUG) {
      console.error(`[${attempt}/${maxAttempts}] 查询任务状态...`);
    }

    const result = await queryVideoTask(accessKey, secretKey, reqKey, taskId, securityToken);

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

function parseArgs(): Text2VideoOptions {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.error('用法: ts-node text2video.ts "提示词" [选项]');
    console.error('');
    console.error('选项:');
    console.error('  --ratio <宽高比>         视频宽高比 (默认: 9:16)');
    console.error('  --duration <时长>        视频时长: 5 或 10 秒 (默认: 5)');
    console.error('  --fps <帧率>             视频帧率: 24 或 30 (默认: 24)');
    console.error('  --output <目录>          视频下载目录 (默认: ./output)');
    console.error('  --no-download            不下载视频，只返回URL');
    console.error('  --wait                   等待任务完成');
    console.error('  --debug                  开启调试模式');
    console.error('');
    console.error('支持的宽高比: ' + VALID_VIDEO_RATIOS.join(', '));
    console.error('');
    console.error('环境变量:');
    console.error('  VOLCENGINE_AK  火山引擎 Access Key');
    console.error('  VOLCENGINE_SK  火山引擎 Secret Key');
    process.exit(1);
  }

  const prompt = args[0];
  let ratio = '9:16';
  let duration: 5 | 10 = 5;
  let fps: 24 | 30 = 24;
  let outputDir = './output';
  let download = true;
  let wait = false;
  let debug = false;

  for (let i = 1; i < args.length; i++) {
    switch (args[i]) {
      case '--ratio':
        ratio = args[++i];
        if (!VALID_VIDEO_RATIOS.includes(ratio)) {
          throw new Error(`不支持的宽高比: ${ratio}，支持的值: ${VALID_VIDEO_RATIOS.join(', ')}`);
        }
        break;
      case '--duration':
        const d = parseInt(args[++i], 10);
        if (d !== 5 && d !== 10) {
          throw new Error('duration 必须是 5 或 10');
        }
        duration = d as 5 | 10;
        break;
      case '--fps':
        const f = parseInt(args[++i], 10);
        if (f !== 24 && f !== 30) {
          throw new Error('fps 必须是 24 或 30');
        }
        fps = f as 24 | 30;
        break;
      case '--output':
        outputDir = args[++i];
        break;
      case '--no-download':
        download = false;
        break;
      case '--wait':
        wait = true;
        break;
      case '--debug':
        debug = true;
        process.env.DEBUG = 'true';
        break;
    }
  }

  return { prompt, ratio, duration, fps, outputDir, download, wait, debug };
}

/**
 * 计算字符串的 MD5 哈希值
 */
function md5Hash(str: string): string {
  return crypto.createHash('md5').update(str, 'utf8').digest('hex');
}

/**
 * 清理路径，防止路径遍历攻击
 * 移除 ../ 和 ./ 等危险路径段
 */
function sanitizePath(inputPath: string): string {
  // 规范化路径
  const normalized = path.normalize(inputPath);
  // 移除任何以 .. 开头的路径（尝试跳出目录）
  const cleaned = normalized.replace(/^(\.\.[\/\\])+/, '');
  // 确保路径不以 / 或 \ 开头（绝对路径）
  if (cleaned.startsWith('/') || cleaned.startsWith('\\')) {
    throw new Error('不允许使用绝对路径');
  }
  return cleaned;
}

/**
 * 获取任务文件夹路径
 * 使用 md5(提示词+参数) 作为子文件夹名
 * 包含路径遍历防护
 */
function getTaskFolderPath(prompt: string, ratio: string, duration: number, fps: number, baseOutputDir: string): string {
  const hashInput = `${prompt}_${ratio}_${duration}_${fps}`;
  const hash = md5Hash(hashInput);
  const cwd = process.cwd();
  // 清理用户输入的路径，防止路径遍历
  const safeOutputDir = sanitizePath(baseOutputDir);
  const fullPath = path.join(cwd, safeOutputDir, 'video', hash);
  // 验证最终路径确实在 cwd 之下（额外的安全检查）
  const resolvedCwd = path.resolve(cwd);
  const resolvedPath = path.resolve(fullPath);
  if (!resolvedPath.startsWith(resolvedCwd + path.sep) && resolvedPath !== resolvedCwd) {
    throw new Error('路径安全检查失败：输出目录必须在当前工作目录内');
  }
  return fullPath;
}

/**
 * 保存任务信息到文件夹
 */
function saveTaskInfo(folderPath: string, params: any, response: any, taskId: string): void {
  if (!fs.existsSync(folderPath)) {
    fs.mkdirSync(folderPath, { recursive: true });
  }

  const paramPath = path.join(folderPath, 'param.json');
  fs.writeFileSync(paramPath, JSON.stringify(params, null, 2), 'utf8');

  const responsePath = path.join(folderPath, 'response.json');
  fs.writeFileSync(responsePath, JSON.stringify(response, null, 2), 'utf8');

  const taskIdPath = path.join(folderPath, 'taskId.txt');
  fs.writeFileSync(taskIdPath, taskId, 'utf8');
}

/**
 * 读取已保存的任务ID
 */
function loadTaskId(folderPath: string): string | null {
  const taskIdPath = path.join(folderPath, 'taskId.txt');
  if (fs.existsSync(taskIdPath)) {
    return fs.readFileSync(taskIdPath, 'utf8').trim();
  }
  return null;
}

/**
 * 检查文件夹中是否已有视频文件
 */
function hasVideo(folderPath: string): boolean {
  if (!fs.existsSync(folderPath)) {
    return false;
  }
  const files = fs.readdirSync(folderPath);
  return files.some(file => {
    const ext = path.extname(file).toLowerCase();
    return ext === '.mp4' || ext === '.mov' || ext === '.avi';
  });
}

/**
 * 获取文件夹中的视频文件路径
 */
function getVideoInFolder(folderPath: string): string | null {
  if (!fs.existsSync(folderPath)) {
    return null;
  }
  const files = fs.readdirSync(folderPath);
  const videoFiles = files.filter(file => {
    const ext = path.extname(file).toLowerCase();
    return ext === '.mp4' || ext === '.mov' || ext === '.avi';
  });
  return videoFiles.length > 0 ? path.join(folderPath, videoFiles[0]) : null;
}

/**
 * 下载视频到本地
 */
async function downloadVideo(url: string, outputPath: string): Promise<string> {
  const response = await axios.get(url, {
    responseType: 'arraybuffer',
    timeout: 120000
  });

  const dir = path.dirname(outputPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  fs.writeFileSync(outputPath, Buffer.from(response.data));
  return outputPath;
}

async function main(): Promise<void> {
  try {
    const { accessKey, secretKey, securityToken } = getCredentials();
    const options = parseArgs();

    // 文生视频使用固定的 req_key
    const reqKey = REQ_KEYS.T2V_V30_1080P;

    // 构建请求体 - 文生视频
    // aspect_ratio 需要是字符串格式，如 "9:16"
    const body: Record<string, any> = {
      req_key: reqKey,
      prompt: options.prompt,
      aspect_ratio: options.ratio,
      duration: options.duration,
      fps: options.fps
    };

    // 计算任务文件夹路径（用于保存任务状态）
    const taskFolderPath = getTaskFolderPath(
      options.prompt,
      options.ratio,
      options.duration,
      options.fps,
      options.outputDir
    );

    // 检查任务文件夹是否已存在
    if (fs.existsSync(taskFolderPath)) {
      const taskId = loadTaskId(taskFolderPath);
      if (taskId) {
        console.error(`发现已有任务，TaskId: ${taskId}，正在查询状态...`);

        try {
          const result = await queryVideoTask(accessKey, secretKey, reqKey, taskId, securityToken);
          const status = result?.data?.status;
          const videoUrl = result?.data?.video_url;

          if (status === 'done' && videoUrl) {
            const successResult = {
              success: true,
              prompt: options.prompt,
              ratio: options.ratio,
              duration: options.duration,
              fps: options.fps,
              taskId,
              videoUrl,
              data: result?.data
            };
            console.log(JSON.stringify(successResult, null, 2));
            return;
          } else if (status === 'processing' || status === 'in_queue' || status === 'generating') {
            console.error(`任务处理中，当前状态: ${status}，TaskId: ${taskId}`);
            const pendingResult = {
              success: true,
              pending: true,
              prompt: options.prompt,
              ratio: options.ratio,
              duration: options.duration,
              fps: options.fps,
              taskId,
              status,
              message: '任务处理中，请稍后使用相同提示词查询结果'
            };
            console.log(JSON.stringify(pendingResult, null, 2));
            return;
          }
        } catch (err: any) {
          // 查询失败，继续提交新任务
          console.error('查询已有任务失败，将提交新任务...');
        }
      }
    }

    // 新任务 - 提交
    if (options.debug) {
      console.error('请求体:', JSON.stringify(body, null, 2));
    }

    console.error('提交新任务...');
    const { taskId, requestId } = await submitVideoTask(accessKey, secretKey, reqKey, body, securityToken);

    // 创建文件夹并保存任务信息
    fs.mkdirSync(taskFolderPath, { recursive: true });

    const paramData = {
      prompt: options.prompt,
      ratio: options.ratio,
      duration: options.duration,
      fps: options.fps,
      req_key: reqKey,
      timestamp: new Date().toISOString()
    };

    saveTaskInfo(taskFolderPath, paramData, { taskId, requestId }, taskId);

    console.error(`任务已提交，TaskId: ${taskId}`);

    // 如果指定了 --wait，等待任务完成
    if (options.wait) {
      console.error('等待任务完成...');
      try {
        const result = await waitForVideoTask(accessKey, secretKey, reqKey, taskId, securityToken);

        const videoUrl = result?.data?.video_url;
        if (videoUrl) {
          const successResult = {
            success: true,
            prompt: options.prompt,
            ratio: options.ratio,
            duration: options.duration,
            fps: options.fps,
            taskId,
            videoUrl,
            data: result?.data
          };
          console.log(JSON.stringify(successResult, null, 2));
        } else {
          console.error(`任务未完成，TaskId: ${taskId}`);
          const pendingResult = {
            success: true,
            pending: true,
            prompt: options.prompt,
            ratio: options.ratio,
            duration: options.duration,
            fps: options.fps,
            taskId,
            message: '任务未完成，请稍后使用相同提示词查询结果'
          };
          console.log(JSON.stringify(pendingResult, null, 2));
        }
      } catch (waitErr: any) {
        console.error(`任务未完成，TaskId: ${taskId}`);
        process.exit(0);
      }
    } else {
      // 只提交，不等待
      const result = {
        success: true,
        submitted: true,
        prompt: options.prompt,
        ratio: options.ratio,
        duration: options.duration,
        fps: options.fps,
        taskId,
        folder: taskFolderPath,
        message: '任务已提交，请稍后使用相同提示词查询结果'
      };
      console.log(JSON.stringify(result, null, 2));
    }

  } catch (err: any) {
    if (err.message === 'MISSING_CREDENTIALS') {
      outputError('MISSING_CREDENTIALS', '请设置环境变量 VOLCENGINE_AK 和 VOLCENGINE_SK');
    } else {
      outputError(err.code || 'UNKNOWN_ERROR', err.message || '未知错误');
    }
  }
}

main();
