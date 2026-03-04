#!/usr/bin/env ts-node
/**
 * 文生图脚本 - Text to Image
 * 支持即梦AI v3.0/v3.1/v4.0 文生图API
 * 
 * 用法: ts-node text2image.ts "提示词" [选项]
 * 
 * 选项:
 *   --version <v30|v31|v40>  API版本 (默认: v40)
 *   --ratio <宽高比>         图片宽高比 (默认: 1:1)
 *   --count <数量>           生成数量 1-4 (默认: 1)
 *   --width <宽度>           指定宽度 (可选)
 *   --height <高度>          指定高度 (可选)
 *   --size <面积>            指定面积 (可选, 如 4194304 表示 2048x2048)
 *   --seed <种子>            随机种子 (可选)
 *   --debug                  开启调试模式
 * 
 * 示例:
 *   ts-node text2image.ts "一只可爱的猫咪"
 *   ts-node text2image.ts "山水风景画" --version v40 --ratio 16:9 --count 2
 *   ts-node text2image.ts "科幻城市" --width 2048 --height 1152
 */

import {
  REQ_KEYS,
  VALID_RATIOS,
  submitTask,
  waitForTask,
  getCredentials,
  outputError,
  Result
} from './common';

interface Text2ImageOptions {
  prompt: string;
  version: 'v30' | 'v31' | 'v40';
  ratio: string;
  count: number;
  width?: number;
  height?: number;
  size?: number;
  seed?: number;
  debug: boolean;
}

function parseArgs(): Text2ImageOptions {
  const args = process.argv.slice(2);
  
  if (args.length < 1) {
    console.error('用法: ts-node text2image.ts "提示词" [选项]');
    console.error('');
    console.error('选项:');
    console.error('  --version <v30|v31|v40>  API版本 (默认: v40)');
    console.error('  --ratio <宽高比>         图片宽高比 (默认: 1:1)');
    console.error('  --count <数量>           生成数量 1-4 (默认: 1)');
    console.error('  --width <宽度>           指定宽度 (可选)');
    console.error('  --height <高度>          指定高度 (可选)');
    console.error('  --size <面积>            指定面积 (可选)');
    console.error('  --seed <种子>            随机种子 (可选)');
    console.error('  --debug                  开启调试模式');
    console.error('');
    console.error('支持的宽高比: ' + VALID_RATIOS.join(', '));
    console.error('');
    console.error('环境变量:');
    console.error('  VOLC_ACCESS_KEY  火山引擎 Access Key');
    console.error('  VOLC_SECRET_KEY  火山引擎 Secret Key');
    process.exit(1);
  }

  const prompt = args[0];
  let version: 'v30' | 'v31' | 'v40' = 'v40';
  let ratio = '1:1';
  let count = 1;
  let width: number | undefined;
  let height: number | undefined;
  let size: number | undefined;
  let seed: number | undefined;
  let debug = false;

  for (let i = 1; i < args.length; i++) {
    switch (args[i]) {
      case '--version':
        const v = args[++i];
        if (v !== 'v30' && v !== 'v31' && v !== 'v40') {
          throw new Error(`不支持的版本: ${v}，支持的值: v30, v31, v40`);
        }
        version = v;
        break;
      case '--ratio':
        ratio = args[++i];
        if (!VALID_RATIOS.includes(ratio)) {
          throw new Error(`不支持的宽高比: ${ratio}，支持的值: ${VALID_RATIOS.join(', ')}`);
        }
        break;
      case '--count':
        count = parseInt(args[++i], 10);
        if (isNaN(count) || count < 1 || count > 4) {
          throw new Error('count 必须是 1-4 之间的整数');
        }
        break;
      case '--width':
        width = parseInt(args[++i], 10);
        break;
      case '--height':
        height = parseInt(args[++i], 10);
        break;
      case '--size':
        size = parseInt(args[++i], 10);
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

  return { prompt, version, ratio, count, width, height, size, seed, debug };
}

async function main(): Promise<void> {
  try {
    const { accessKey, secretKey } = getCredentials();
    const options = parseArgs();

    // 根据版本选择 req_key
    const reqKeyMap = {
      'v30': REQ_KEYS.T2I_V30,
      'v31': REQ_KEYS.T2I_V31,
      'v40': REQ_KEYS.T2I_V40
    };
    const reqKey = reqKeyMap[options.version];

    console.error('=================================');
    console.error('即梦AI - 文生图');
    console.error('=================================');
    console.error(`提示词: ${options.prompt}`);
    console.error(`版本: ${options.version}`);
    console.error(`宽高比: ${options.ratio}`);
    console.error(`生成数量: ${options.count}`);
    if (options.width && options.height) {
      console.error(`指定尺寸: ${options.width}x${options.height}`);
    }
    console.error('');

    // 构建请求体
    const body: Record<string, any> = {
      req_key: reqKey,
      prompt: options.prompt,
      aspect_ratio: options.ratio,
      image_number: options.count
    };

    if (options.seed !== undefined) {
      body.seed = options.seed;
    } else {
      body.seed = Math.floor(Math.random() * 1000000000);
    }

    if (options.width && options.height) {
      body.width = options.width;
      body.height = options.height;
    }

    if (options.size) {
      body.size = options.size;
    }

    // v40 特有参数支持
    if (options.version === 'v40') {
      // 可以根据需要添加 v40 特有参数
      body.force_single = options.count === 1;
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
    console.error('步骤2: 等待任务完成...');
    const result = await waitForTask(accessKey, secretKey, reqKey, taskId);

    // 3. 提取图片URL
    const images = result?.resp?.data?.pe_result?.map(img => ({
      url: img.url,
      width: img.width,
      height: img.height
    })) || [];

    if (images.length === 0) {
      throw new Error('任务完成但未返回图片数据');
    }

    // 4. 输出结果
    const successResult = {
      success: true,
      prompt: options.prompt,
      version: options.version,
      ratio: options.ratio,
      count: options.count,
      taskId,
      images,
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