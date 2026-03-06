#!/usr/bin/env ts-node
/**
 * 图生视频脚本 - Image to Video
 * 支持即梦AI i2v_first_v30_1080 图生视频API（首帧）
 * 
 * 用法: ts-node image2video.ts --image <图片路径或URL> --prompt "提示词" [选项]
 * 
 * 选项:
 *   --image <路径/URL>       输入图片路径或URL（必填）
 *   --prompt <提示词>        视频描述提示词（必填）
 *   --mode <first|first-tail> 模式: first=首帧, first-tail=首尾帧 (默认: first)
 *   --frames <121|241>       视频帧数: 121=5秒, 241=10秒 (默认: 121)
 *   --seed <种子>            随机种子 (可选)
 *   --debug                  开启调试模式
 * 
 * 示例:
 *   ts-node image2video.ts --image "./input.jpg" --prompt "让图片中的风景动起来"
 *   ts-node image2video.ts --image "https://example.com/image.jpg" --prompt "千军万马" --frames 241
 */

import * as fs from 'fs';
import * as path from 'path';
import {
  REQ_KEYS,
  submitTask,
  waitForTask,
  getCredentials,
  outputError
} from './common';

interface Image2VideoOptions {
  image: string;
  prompt: string;
  mode: 'first' | 'first-tail';
  frames: 121 | 241;
  seed?: number;
  debug: boolean;
}

function parseArgs(): Image2VideoOptions {
  const args = process.argv.slice(2);
  
  let image: string | undefined;
  let prompt: string | undefined;
  let mode: 'first' | 'first-tail' = 'first';
  let frames: 121 | 241 = 121;
  let seed: number | undefined;
  let debug = false;

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--image':
        image = args[++i];
        break;
      case '--prompt':
        prompt = args[++i];
        break;
      case '--mode':
        const m = args[++i];
        if (m !== 'first' && m !== 'first-tail') {
          throw new Error(`不支持的模式: ${m}，支持的值: first, first-tail`);
        }
        mode = m;
        break;
      case '--frames':
        const f = parseInt(args[++i], 10);
        if (f !== 121 && f !== 241) {
          throw new Error('frames 必须是 121 (5秒) 或 241 (10秒)');
        }
        frames = f as 121 | 241;
        break;
      case '--seed':
        seed = parseInt(args[++i], 10);
        break;
      case '--debug':
        debug = true;
        process.env.DEBUG = 'true';
        break;
    }
  }

  if (!image) {
    console.error('用法: ts-node image2video.ts --image <图片路径或URL> --prompt "提示词" [选项]');
    console.error('');
    console.error('选项:');
    console.error('  --image <路径/URL>       输入图片路径或URL（必填）');
    console.error('  --prompt <提示词>        视频描述提示词（必填）');
    console.error('  --mode <first|first-tail> 模式: first=首帧, first-tail=首尾帧 (默认: first)');
    console.error('  --frames <121|241>       视频帧数: 121=5秒, 241=10秒 (默认: 121)');
    console.error('  --seed <种子>            随机种子 (可选)');
    console.error('  --debug                  开启调试模式');
    console.error('');
    console.error('示例:');
    console.error('  ts-node image2video.ts --image "./input.jpg" --prompt "让图片中的风景动起来"');
    console.error('  ts-node image2video.ts --image "https://example.com/image.jpg" --prompt "千军万马" --frames 241');
    process.exit(1);
  }

  if (!prompt) {
    throw new Error('请使用 --prompt 指定视频描述提示词');
  }

  return { image, prompt, mode, frames, seed, debug };
}

/**
 * 读取图片并转换为base64
 */
async function readImageAsBase64(imagePath: string): Promise<string> {
  // 检查是否是URL
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    // 如果是URL，直接返回（API支持URL格式）
    return imagePath;
  }

  // 本地文件
  const fullPath = path.resolve(imagePath);
  if (!fs.existsSync(fullPath)) {
    throw new Error(`图片文件不存在: ${fullPath}`);
  }

  const buffer = fs.readFileSync(fullPath);
  return buffer.toString('base64');
}

async function main(): Promise<void> {
  try {
    const { accessKey, secretKey } = getCredentials();
    const options = parseArgs();

    // 根据模式选择 req_key
    const reqKey = options.mode === 'first' 
      ? REQ_KEYS.I2V_FIRST_V30 
      : REQ_KEYS.I2V_FIRST_TAIL_V30;

    console.error('=================================');
    console.error('即梦AI - 图生视频');
    console.error('=================================');
    console.error(`输入图片: ${options.image}`);
    console.error(`提示词: ${options.prompt}`);
    console.error(`模式: ${options.mode}`);
    console.error(`视频长度: ${options.frames === 121 ? '5秒' : '10秒'}`);
    console.error('');

    // 读取图片
    const imageData = await readImageAsBase64(options.image);
    const isUrl = options.image.startsWith('http://') || options.image.startsWith('https://');

    // 构建请求体
    const body: Record<string, any> = {
      req_key: reqKey,
      prompt: options.prompt,
      frames: options.frames
    };

    if (isUrl) {
      body.image_urls = [imageData];
    } else {
      body.binary_data_base64 = [imageData];
    }

    if (options.seed !== undefined) {
      body.seed = options.seed;
    } else {
      body.seed = -1; // 随机种子
    }

    if (options.debug) {
      console.error('请求体:', JSON.stringify(body, null, 2));
    }

    // 1. 提交任务
    console.error('步骤1: 提交任务...');
    const { taskId, requestId } = await submitTask(accessKey, secretKey, reqKey, body);
    console.error(`任务提交成功，任务ID: ${taskId}`);
    console.error('');

    // 2. 轮询等待任务完成
    console.error('步骤2: 等待任务完成（这可能需要几分钟）...');
    const result = await waitForTask(accessKey, secretKey, reqKey, taskId, 120, 3000);

    // 3. 提取视频URL
    const videoUrl = result?.resp?.data?.video_url;

    if (!videoUrl) {
      throw new Error('任务完成但未返回视频数据');
    }

    // 4. 输出结果
    const successResult = {
      success: true,
      image: options.image,
      prompt: options.prompt,
      mode: options.mode,
      frames: options.frames,
      taskId,
      videoUrl,
      usage: { requestId }
    };

    console.log(JSON.stringify(successResult, null, 2));

  } catch (err: any) {
    if (err.message === 'MISSING_CREDENTIALS') {
      outputError('MISSING_CREDENTIALS', '请设置环境变量 VOLC_ACCESS_KEY 和 VOLC_SECRET_KEY');
    } else {
      outputError(err.code || 'UNKNOWN_ERROR', err.message || '未知错误');
    }
  }
}

main();