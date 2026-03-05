#!/usr/bin/env ts-node
/**
 * 文生图脚本 - Text to Image
 * 支持即梦AI v3.0/v3.1/v4.0 文生图API
 *
 * 用法: ts-node text2image.ts "提示词" [选项]
 *
 * 选项:
 *   --version <v30|v31|v40>  API版本 (默认: v31)
 *   --ratio <宽高比>         图片宽高比 (默认: 9:16)
 *   --count <数量>           生成数量 1-4 (默认: 1)
 *   --width <宽度>           指定宽度 (可选)
 *   --height <高度>          指定高度 (可选)
 *   --size <面积>            指定面积 (可选, 如 4194304 表示 2048x2048)
 *   --seed <种子>            随机种子 (可选)
 *   --output <目录>          图片下载目录 (默认: ./output)
 *   --no-download            不下载图片，只返回URL
 *   --debug                  开启调试模式
 *
 * 示例:
 *   ts-node text2image.ts "一只可爱的猫咪"
 *   ts-node text2image.ts "山水风景画" --version v40 --ratio 16:9 --count 2
 *   ts-node text2image.ts "科幻城市" --width 2048 --height 1152 --output ~/Pictures
 */

import * as path from 'path';
import * as fs from 'fs';
import * as crypto from 'crypto';
import {
  REQ_KEYS,
  VALID_RATIOS,
  submitTask,
  waitForTask,
  getCredentials,
  outputError
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
  outputDir: string;
  download: boolean;
  debug: boolean;
}

function parseArgs(): Text2ImageOptions {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.error('用法: ts-node text2image.ts "提示词" [选项]');
    console.error('');
    console.error('选项:');
    console.error('  --version <v30|v31|v40>  API版本 (默认: v31)');
    console.error('  --ratio <宽高比>         图片宽高比 (默认: 9:16)');
    console.error('  --count <数量>           生成数量 1-4 (默认: 1)');
    console.error('  --width <宽度>           指定宽度 (可选)');
    console.error('  --height <高度>          指定高度 (可选)');
    console.error('  --size <面积>            指定面积 (可选)');
    console.error('  --seed <种子>            随机种子 (可选)');
    console.error('  --output <目录>          图片下载目录 (默认: ./output)');
    console.error('  --no-download            不下载图片，只返回URL');
    console.error('  --debug                  开启调试模式');
    console.error('');
    console.error('支持的宽高比: ' + VALID_RATIOS.join(', '));
    console.error('');
    console.error('环境变量:');
    console.error('  VOLCENGINE_AK  火山引擎 Access Key');
    console.error('  VOLCENGINE_SK  火山引擎 Secret Key');
    process.exit(1);
  }

  const prompt = args[0];
  let version: 'v30' | 'v31' | 'v40' = 'v31';
  let ratio = '16:9';
  let count = 1;
  let width: number | undefined;
  let height: number | undefined;
  let size: number | undefined;
  let seed: number | undefined;
  let outputDir = './output';
  let download = true;
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
      case '--output':
        outputDir = args[++i];
        break;
      case '--no-download':
        download = false;
        break;
      case '--debug':
        debug = true;
        process.env.DEBUG = 'true';
        break;
    }
  }

  return { prompt, version, ratio, count, width, height, size, seed, outputDir, download, debug };
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
 * 使用 md5(提示词) 作为子文件夹名
 * 包含路径遍历防护
 */
function getTaskFolderPath(prompt: string, baseOutputDir: string): string {
  const hash = md5Hash(prompt);
  const cwd = process.cwd();
  // 清理用户输入的路径，防止路径遍历
  const safeOutputDir = sanitizePath(baseOutputDir);
  const fullPath = path.join(cwd, safeOutputDir, hash);
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
  // 确保文件夹存在
  if (!fs.existsSync(folderPath)) {
    fs.mkdirSync(folderPath, { recursive: true });
  }

  // 保存请求参数
  const paramPath = path.join(folderPath, 'param.json');
  fs.writeFileSync(paramPath, JSON.stringify(params, null, 2), 'utf8');

  // 保存 API 响应
  const responsePath = path.join(folderPath, 'response.json');
  fs.writeFileSync(responsePath, JSON.stringify(response, null, 2), 'utf8');

  // 保存任务ID
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
 * 检查文件夹中是否有图片文件
 */
function hasImages(folderPath: string): boolean {
  if (!fs.existsSync(folderPath)) {
    return false;
  }
  const files = fs.readdirSync(folderPath);
  return files.some(file => {
    const ext = path.extname(file).toLowerCase();
    return ext === '.jpg' || ext === '.jpeg' || ext === '.png' || ext === '.gif' || ext === '.webp';
  });
}

/**
 * 获取文件夹中的图片文件路径列表
 */
function getImagesInFolder(folderPath: string): string[] {
  if (!fs.existsSync(folderPath)) {
    return [];
  }
  const files = fs.readdirSync(folderPath);
  const imageFiles = files.filter(file => {
    const ext = path.extname(file).toLowerCase();
    return ext === '.jpg' || ext === '.jpeg' || ext === '.png' || ext === '.gif' || ext === '.webp';
  });
  return imageFiles.map(file => path.join(folderPath, file));
}

/**
 * 将 base64 数据解码保存为图片文件
 * @returns 保存的图片文件路径列表
 */
function saveBase64Images(folderPath: string, base64Data: string[]): string[] {
  // 确保输出目录存在
  if (!fs.existsSync(folderPath)) {
    fs.mkdirSync(folderPath, { recursive: true });
  }

  const savedPaths: string[] = [];

  for (let i = 0; i < base64Data.length; i++) {
    const base64String = base64Data[i];
    const filename = `${i + 1}.jpg`;
    const outputPath = path.join(folderPath, filename);

    try {
      // 解码 base64 数据并保存
      const buffer = Buffer.from(base64String, 'base64');
      fs.writeFileSync(outputPath, buffer);
      savedPaths.push(outputPath);
    } catch (err: any) {
      console.error(`  保存图片失败: ${err.message}`);
    }
  }

  return savedPaths;
}

async function main(): Promise<void> {
  try {
    const { accessKey, secretKey, securityToken } = getCredentials();
    const options = parseArgs();

    // 根据版本选择 req_key
    const reqKeyMap = {
      'v30': REQ_KEYS.T2I_V30,
      'v31': REQ_KEYS.T2I_V31,
      'v40': REQ_KEYS.T2I_V40
    };
    const reqKey = reqKeyMap[options.version];

    // 构建请求体 - OpenAPI 格式
    const ratioMap: Record<string, { width: number; height: number }> = {
      '1:1': { width: 2048, height: 2048 },
      '9:16': { width: 1440, height: 2560 },
      '16:9': { width: 2560, height: 1440 },
      '3:4': { width: 1728, height: 2304 },
      '4:3': { width: 2304, height: 1728 },
      '2:3': { width: 1664, height: 2496 },
      '3:2': { width: 2496, height: 1664 },
      '1:2': { width: 1440, height: 2880 },
      '2:1': { width: 2880, height: 1440 }
    };

    const ratioValue = ratioMap[options.ratio] || { width: 1440, height: 2560 };
    const body: Record<string, any> = {
      req_key: reqKey,
      prompt: options.prompt,
      force_single: options.count === 1,
      count: options.count || 1,
      width: options.width || ratioValue.width,
      height: options.height || ratioValue.height,
      scale: 0.5
    };

    if (options.seed !== undefined) {
      body.seed = options.seed;
    }

    // 计算任务文件夹路径
    const taskFolderPath = getTaskFolderPath(options.prompt, options.outputDir);

    // 检查任务文件夹是否已存在
    if (fs.existsSync(taskFolderPath)) {
      // 已有任务 - 异步查询流程
      console.error('发现已有任务，正在查询状态...');

      const taskId = loadTaskId(taskFolderPath);
      if (!taskId) {
        throw new Error('任务文件夹存在但未找到 taskId.txt');
      }

      // 检查是否已有图片文件
      if (hasImages(taskFolderPath)) {
        const existingImages = getImagesInFolder(taskFolderPath);
        console.error(`任务已完成，图片已存在:`);
        existingImages.forEach(img => console.error(`  - ${img}`));

        const successResult = {
          success: true,
          prompt: options.prompt,
          version: options.version,
          ratio: options.ratio,
          count: options.count,
          taskId,
          images: existingImages,
          outputDir: taskFolderPath
        };
        console.log(JSON.stringify(successResult, null, 2));
        return;
      }

      // 无图片，查询任务状态
      console.error(`任务ID: ${taskId}`);
      console.error('正在查询任务状态...');

      try {
        const result = await waitForTask(accessKey, secretKey, reqKey, taskId, securityToken);

        // 检查是否有 base64 图片数据
        const base64Data = result?.data?.binary_data_base64;
        if (base64Data && base64Data.length > 0) {
          console.error(`任务完成，正在保存 ${base64Data.length} 张图片...`);
          const savedPaths = saveBase64Images(taskFolderPath, base64Data);

          console.error('任务已完成，图片保存路径:');
          savedPaths.forEach(p => console.error(`  - ${p}`));

          const successResult = {
            success: true,
            prompt: options.prompt,
            version: options.version,
            ratio: options.ratio,
            count: options.count,
            taskId,
            images: savedPaths,
            outputDir: taskFolderPath
          };
          console.log(JSON.stringify(successResult, null, 2));
        } else {
          console.error('任务完成但未返回图片数据');
          const successResult = {
            success: true,
            prompt: options.prompt,
            version: options.version,
            ratio: options.ratio,
            count: options.count,
            taskId,
            images: [],
            outputDir: taskFolderPath
          };
          console.log(JSON.stringify(successResult, null, 2));
        }
      } catch (waitErr: any) {
        if (waitErr.message?.includes('超时')) {
          console.error(`任务未完成，TaskId: ${taskId}`);
          process.exit(0);
        } else {
          throw waitErr;
        }
      }
    } else {
      // 新任务 - 提交但不等待
      if (options.debug) {
        console.error('请求体:', JSON.stringify(body, null, 2));
      }

      console.error('提交新任务...');
      const { taskId, requestId } = await submitTask(accessKey, secretKey, reqKey, body, securityToken);

      // 创建文件夹并保存任务信息
      fs.mkdirSync(taskFolderPath, { recursive: true });

      const paramData = {
        prompt: options.prompt,
        version: options.version,
        ratio: options.ratio,
        count: options.count,
        req_key: reqKey,
        timestamp: new Date().toISOString()
      };

      saveTaskInfo(taskFolderPath, paramData, { taskId, requestId }, taskId);

      console.error(`任务已提交，TaskId: ${taskId}`);

      // 如果需要等待任务完成（可以添加 --wait 选项）
      // 但目前按照需求只提交不等待
      const result = {
        success: true,
        submitted: true,
        prompt: options.prompt,
        version: options.version,
        ratio: options.ratio,
        count: options.count,
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
