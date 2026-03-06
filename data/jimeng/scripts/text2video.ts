#!/usr/bin/env ts-node
/**
 * 文生视频脚本 - Text to Video
 * 支持即梦AI t2v_v30_1080p 文生视频API
 * 
 * 用法: ts-node text2video.ts "提示词" [选项]
 * 
 * 选项:
 *   --ratio <宽高比>         视频宽高比 (默认: 16:9)
 *   --frames <121|241>       视频帧数: 121=5秒, 241=10秒 (默认: 121)
 *   --seed <种子>            随机种子 (可选)
 *   --debug                  开启调试模式
 * 
 * 支持的宽高比: 16:9, 4:3, 1:1, 3:4, 9:16, 21:9
 * 
 * 示例:
 *   ts-node text2video.ts "千军万马在草原上奔腾"
 *   ts-node text2video.ts "科幻城市夜景" --ratio 9:16 --frames 241
 */

import {
  REQ_KEYS,
  VALID_VIDEO_RATIOS,
  submitTask,
  waitForTask,
  getCredentials,
  outputError
} from './common';

interface Text2VideoOptions {
  prompt: string;
  ratio: string;
  frames: 121 | 241;
  seed?: number;
  debug: boolean;
}

function parseArgs(): Text2VideoOptions {
  const args = process.argv.slice(2);
  
  if (args.length < 1) {
    console.error('用法: ts-node text2video.ts "提示词" [选项]');
    console.error('');
    console.error('选项:');
    console.error('  --ratio <宽高比>         视频宽高比 (默认: 16:9)');
    console.error('  --frames <121|241>       视频帧数: 121=5秒, 241=10秒 (默认: 121)');
    console.error('  --seed <种子>            随机种子 (可选)');
    console.error('  --debug                  开启调试模式');
    console.error('');
    console.error('支持的宽高比: ' + VALID_VIDEO_RATIOS.join(', '));
    console.error('');
    console.error('环境变量:');
    console.error('  VOLC_ACCESS_KEY  火山引擎 Access Key');
    console.error('  VOLC_SECRET_KEY  火山引擎 Secret Key');
    process.exit(1);
  }

  const prompt = args[0];
  let ratio = '16:9';
  let frames: 121 | 241 = 121;
  let seed: number | undefined;
  let debug = false;

  for (let i = 1; i < args.length; i++) {
    switch (args[i]) {
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

  return { prompt, ratio, frames, seed, debug };
}

async function main(): Promise<void> {
  try {
    const { accessKey, secretKey } = getCredentials();
    const options = parseArgs();

    const reqKey = REQ_KEYS.T2V_V30_1080P;

    console.error('=================================');
    console.error('即梦AI - 文生视频');
    console.error('=================================');
    console.error(`提示词: ${options.prompt}`);
    console.error(`宽高比: ${options.ratio}`);
    console.error(`视频长度: ${options.frames === 121 ? '5秒' : '10秒'}`);
    console.error('');

    // 构建请求体
    const body: Record<string, any> = {
      req_key: reqKey,
      prompt: options.prompt,
      aspect_ratio: options.ratio,
      frames: options.frames
    };

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
      prompt: options.prompt,
      ratio: options.ratio,
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