#!/usr/bin/env node
/**
 * MiniMax Vision Captcha - 自动识别验证码
 * 
 * 使用MiniMax视觉模型识别图片中的验证码、滑块位置等
 * 
 * 使用方式:
 *   node scripts/solve-captcha.js --screenshot /path/to/image.png
 *   node scripts/solve-captcha.js --prompt "描述图片内容" --image /path/to/image.png
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// 解析命令行参数
const args = process.argv.slice(2);
let prompt = '请描述这张图片的内容';
let imagePath = null;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--prompt' || args[i] === '-p') {
    prompt = args[i + 1];
    i++;
  } else if (args[i] === '--image' || args[i] === '-i') {
    imagePath = args[i + 1];
    i++;
  } else if (args[i] === '--screenshot' || args[i] === '-s') {
    imagePath = args[i + 1];
  } else if (args[i] === '--help' || args[i] === '-h') {
    console.log(`
MiniMax Vision Captcha - 验证码识别工具

用法:
  node solve-captcha.js [选项]

选项:
  -p, --prompt <文本>   识别提示（可选）
  -i, --image <路径>    图片路径（可选）
  -s, --screenshot      使用最新截图
  -h, --help            显示帮助

示例:
  node solve-captcha.js --screenshot /tmp/captcha.png
  node solve-captcha.js --prompt "识别滑块位置" --image /tmp/img.png
`);
    process.exit(0);
  }
}

// 如果没有指定图片，查找最新的截图
if (!imagePath) {
  const mediaDir = '/root/.openclaw/media/browser';
  try {
    const files = fs.readdirSync(mediaDir)
      .filter(f => f.endsWith('.png'))
      .map(f => ({ name: f, time: fs.statSync(path.join(mediaDir, f)).mtime }))
      .sort((a, b) => b.time - a.time);
    
    if (files.length > 0) {
      imagePath = path.join(mediaDir, files[0].name);
      console.log('使用最新截图:', files[0].name);
    }
  } catch (e) {
    console.error('查找截图失败:', e.message);
    process.exit(1);
  }
}

if (!imagePath || !fs.existsSync(imagePath)) {
  console.error('图片不存在:', imagePath);
  process.exit(1);
}

// 调用MiniMax视觉识别
console.log('正在调用MiniMax视觉识别...');
console.log('图片路径:', imagePath);
console.log('提示词:', prompt);

try {
  const cmd = `mcporter call minimax-coding-plan.understand_image prompt="${prompt}" image_source="${imagePath}"`;
  const result = execSync(cmd, { encoding: 'utf-8', timeout: 30000 });
  console.log('\n===== 识别结果 =====\n');
  console.log(result);
} catch (e) {
  console.error('识别失败:', e.message);
  process.exit(1);
}
