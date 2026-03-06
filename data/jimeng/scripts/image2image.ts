#!/usr/bin/env ts-node
/**
 * 图生图脚本 - Image to Image
 * 支持即梦AI i2i_v30 / i2i_seed3 图生图API
 * 
 * 用法: ts-node image2image.ts --image <图片路径或URL> --prompt "提示词" [选项]
 * 
 * 选项:
   *   --image <路径/URL>       输入图片路径或URL（必填）
   *   --prompt <提示词>        图片编辑描述（必填）
   *   --mode <v30|seed3>       图生图模式 (默认: v30)
   *   --ratio <宽高比>         输出图片宽高比 (默认: 1:1)
   *   --scale <0-1>            文本影响程度 (默认: 0.5)
   *   --seed <种子>            随机种子 (可选)
   *   --count <数量>           生成数量 1-4 (默认: 1)
   *   --debug                  开启调试模式
   * 
   * 示例:
   *   ts-node image2image.ts --image "./input.jpg" --prompt "背景换成演唱会现场"
   *   ts-node image2image.ts --image "https://example.com/image.jpg" --prompt "转换成动漫风格" --mode seed3 --scale 0.7
   */
  
  import * as fs from 'fs';
  import * as path from 'path';
  import {
    REQ_KEYS,
    VALID_RATIOS,
    submitTask,
    waitForTask,
    getCredentials,
    outputError
  } from './common';
  
  interface Image2ImageOptions {
    image: string;
    prompt: string;
    mode: 'v30' | 'seed3';
    ratio: string;
    scale: number;
    seed?: number;
    count: number;
    debug: boolean;
  }
  
  function parseArgs(): Image2ImageOptions {
    const args = process.argv.slice(2);
    
    let image: string | undefined;
    let prompt: string | undefined;
    let mode: 'v30' | 'seed3' = 'v30';
    let ratio = '1:1';
    let scale = 0.5;
    let seed: number | undefined;
    let count = 1;
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
          if (m !== 'v30' && m !== 'seed3') {
            throw new Error(`不支持的模式: ${m}，支持的值: v30, seed3`);
          }
          mode = m;
          break;
        case '--ratio':
          ratio = args[++i];
          if (!VALID_RATIOS.includes(ratio)) {
            throw new Error(`不支持的宽高比: ${ratio}，支持的值: ${VALID_RATIOS.join(', ')}`);
          }
          break;
        case '--scale':
          scale = parseFloat(args[++i]);
          if (isNaN(scale) || scale < 0 || scale > 1) {
            throw new Error('scale 必须是 0-1 之间的数字');
          }
          break;
        case '--seed':
          seed = parseInt(args[++i], 10);
          break;
        case '--count':
          count = parseInt(args[++i], 10);
          if (isNaN(count) || count < 1 || count > 4) {
            throw new Error('count 必须是 1-4 之间的整数');
          }
          break;
        case '--debug':
          debug = true;
          process.env.DEBUG = 'true';
          break;
      }
    }
  
    if (!image) {
      console.error('用法: ts-node image2image.ts --image <图片路径或URL> --prompt "提示词" [选项]');
      console.error('');
      console.error('选项:');
      console.error('  --image <路径/URL>       输入图片路径或URL（必填）');
      console.error('  --prompt <提示词>        图片编辑描述（必填）');
      console.error('  --mode <v30|seed3>       图生图模式 (默认: v30)');
      console.error('  --ratio <宽高比>         输出图片宽高比 (默认: 1:1)');
      console.error('  --scale <0-1>            文本影响程度 (默认: 0.5)');
      console.error('  --seed <种子>            随机种子 (可选)');
      console.error('  --count <数量>           生成数量 1-4 (默认: 1)');
      console.error('  --debug                  开启调试模式');
      console.error('');
      console.error('示例:');
      console.error('  ts-node image2image.ts --image "./input.jpg" --prompt "背景换成演唱会现场"');
      console.error('  ts-node image2image.ts --image "https://example.com/image.jpg" --prompt "转换成动漫风格" --mode seed3 --scale 0.7');
      process.exit(1);
    }
  
    if (!prompt) {
      throw new Error('请使用 --prompt 指定图片编辑描述');
    }
  
    return { image, prompt, mode, ratio, scale, seed, count, debug };
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
  
      const reqKey = options.mode === 'v30' ? REQ_KEYS.I2I_V30 : REQ_KEYS.I2I_SEED3;
  
      console.error('=================================');
      console.error('即梦AI - 图生图');
      console.error('=================================');
      console.error(`输入图片: ${options.image}`);
      console.error(`提示词: ${options.prompt}`);
      console.error(`模式: ${options.mode}`);
      console.error(`宽高比: ${options.ratio}`);
      console.error(`文本影响程度: ${options.scale}`);
      console.error('');
  
      const imageData = await readImageAsBase64(options.image);
      const isUrl = options.image.startsWith('http://') || options.image.startsWith('https://');
  
      const body: Record<string, any> = {
        req_key: reqKey,
        prompt: options.prompt,
        aspect_ratio: options.ratio,
        scale: options.scale
      };
  
      if (isUrl) {
        body.image_urls = [imageData];
      } else {
        body.binary_data_base64 = [imageData];
      }
  
      if (options.seed !== undefined) {
        body.seed = options.seed;
      }
  
      if (options.mode === 'v30') {
        body.image_number = options.count;
      }
  
      if (options.debug) {
        console.error('请求体:', JSON.stringify(body, null, 2));
      }
  
      console.error('步骤1: 提交任务...');
      const { taskId, requestId } = await submitTask(accessKey, secretKey, reqKey, body);
      console.error(`任务提交成功，任务ID: ${taskId}`);
      console.error('');
  
      console.error('步骤2: 等待任务完成...');
      const result = await waitForTask(accessKey, secretKey, reqKey, taskId);
  
      const images = result?.resp?.data?.pe_result?.map((img: any) => ({
        url: img.url,
        width: img.width,
        height: img.height
      })) || [];
  
      if (images.length === 0) {
        throw new Error('任务完成但未返回图片数据');
      }
  
      const successResult = {
        success: true,
        image: options.image,
        prompt: options.prompt,
        mode: options.mode,
        ratio: options.ratio,
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