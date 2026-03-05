#!/usr/bin/env ts-node
/**
 * 数字人/虚拟形象脚本 - Dream Actor
 * 支持即梦AI数字人生成视频功能
 * 
 * 用法: ts-node dream-actor.ts --image <图片路径或URL> --prompt "提示词" [选项]
 * 
 * 选项:
 *   --image <路径/URL>       输入人物图片路径或URL（必填）
 *   --prompt <提示词>        动作/表情描述（M1模式必填）
 *   --mode <m1|m20|avatar>   数字人模式 (默认: m1)
 *   --ratio <宽高比>         视频宽高比 (默认: 9:16)
 *   --frames <121|241>       视频帧数 (默认: 121)
 *   --seed <种子>            随机种子 (可选)
 *   --debug                  开启调试模式
 * 
 * 模式说明:
 *   m1     - Dream Actor M1 基础数字人
 *   m20    - Dream Actor M20 高级数字人
 *   avatar - RealMan Avatar 形象生成
 * 
 * 示例:
 *   ts-node dream-actor.ts --image "./person.jpg" --prompt "微笑并点头"
 *   ts-node dream-actor.ts --image "https://example.com/face.jpg" --prompt "说话" --mode m20 --frames 241
 */

import * as fs from 'fs';
import * as path from 'path';
import {
  REQ_KEYS,
  VALID_VIDEO_RATIOS,
  submitTask,
  waitForTask,
  getCredentials,
  outputError
} from './common';

interface DreamActorOptions {
  image: string;
  prompt?: string;
  mode: 'm1' | 'm20' | 'avatar';
  ratio: string;
  frames?: 121 | 241;
  seed?: number;
  debug: boolean;
}

function parseArgs(): DreamActorOptions {
  const args = process.argv.slice(2);
  
  let image: string | undefined;
  let prompt: string | undefined;
  let mode: 'm1' | 'm20' | 'avatar' = 'm1';
  let ratio = '9:16';
  let frames: 121 | 241 | undefined;
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
        if (m !== 'm1' && m !== 'm20' && m !== 'avatar') {
          throw new Error(`不支持的模式: ${m}，支持的值: m1, m20, avatar`);
        }
        mode = m;
        break;
      case '--ratio':
        ratio = args[++i];
        if (!VALID_VIDEO_RATIOS.includes(ratio)) {
          throw new Error(`不支持的宽高比: ${ratio}，支持的值: ${VALID_VIDEO_RATIOS.join(', ')}`);
        }
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
    console.error('用法: ts-node dream-actor.ts --image <图片路径或URL> [--prompt "提示词"] [选项]');
    console.error('');
    console.error('选项:');
    console.error('  --image <路径/URL>       输入人物图片路径或URL（必填）');
    console.error('  --prompt <提示词>        动作/表情描述（M1/M20模式必填）');
    console.error('  --mode <m1|m20|avatar>   数字人模式 (默认: m1)');
    console.error('  --ratio <宽高比>         视频宽高比 (默认: 9:16)');
    console.error('  --frames <121|241>       视频帧数 (默认: 121)');
    console.error('  --seed <种子>            随机种子 (可选)');
    console.error('  --debug                  开启调试模式');
    console.error('');
    console.error('模式说明:');
    console.error('  m1     - Dream Actor M1 基础数字人');
    console.error('  m20    - Dream Actor M20 高级数字人');
    console.error('  avatar - RealMan Avatar 形象生成');
    console.error('');
    console.error('示例:');
    console.error('  ts-node dream-actor.ts --image "./person.jpg" --prompt "微笑并点头"');
    console.error('  ts-node dream-actor.ts --image "./face.jpg" --prompt "说话" --mode m20 --frames 241');
    process.exit(1);
  }

  if ((mode === 'm1' || mode === 'm20') && !prompt) {
    throw new Error(`${mode} 模式需要指定 --prompt 参数描述动作/表情`);
  }

  return { image, prompt, mode, ratio, frames, seed, debug };
}

/**
 * 读取图片并转换为base64
 */
async function readImageAsBase64(imagePath: string): Promise<string> {
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }

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
    const reqKeyMap = {
      'm1': REQ_KEYS.DREAM_ACTOR_M1,
      'm20': REQ_KEYS.DREAM_ACTOR_M20,
      'avatar': REQ_KEYS.REALMAN_AVATAR
    };
    const reqKey = reqKeyMap[options.mode];

    console.error('=================================');
    console.error('即梦AI - 数字人生成');
    console.error('=================================');
    console.error(`输入图片: ${options.image}`);
    if (options.prompt) {
      console.error(`提示词: ${options.prompt}`);
    }
    console.error(`模式: ${options.mode}`);
    console.error(`宽高比: ${options.ratio}`);
    if (options.frames) {
      console.error(`视频长度: ${options.frames === 121 ? '5秒' : '10秒'}`);
    }
    console.error('');

    // 读取图片
    const imageData = await readImageAsBase64(options.image);
    const isUrl = options.image.startsWith('http://') || options.image.startsWith('https://');

    // 构建请求体
    const body: Record<string, any> = {
      req_key: reqKey
    };

    if (isUrl) {
      body.image_urls = [imageData];
    } else {
      body.binary_data_base64 = [imageData];
    }

    // 根据不同模式添加参数
    if (options.mode === 'm1' || options.mode === 'm20') {
      body.prompt = options.prompt;
      body.aspect_ratio = options.ratio;
      body.frames = options.frames || 121;
      body.seed = options.seed !== undefined ? options.seed : -1;
    } else if (options.mode === 'avatar') {
      // avatar 模式可能有不同的参数结构
      body.aspect_ratio = options.ratio;
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
    const maxAttempts = options.mode === 'avatar' ? 60 : 120;
    const result = await waitForTask(accessKey, secretKey, reqKey, taskId, maxAttempts, 3000);

    // 3. 提取结果
    const videoUrl = result?.resp?.data?.video_url;
    const images = result?.resp?.data?.pe_result || result?.resp?.data?.image_urls;

    if (!videoUrl && (!images || images.length === 0)) {
      throw new Error('任务完成但未返回数据');
    }

    // 4. 输出结果
    const successResult: any = {
      success: true,
      image: options.image,
      mode: options.mode,
      taskId,
      usage: { requestId }
    };

    if (options.prompt) {
      successResult.prompt = options.prompt;
    }

    if (videoUrl) {
      successResult.videoUrl = videoUrl;
    }

    if (images && images.length > 0) {
      successResult.images = images;
    }

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