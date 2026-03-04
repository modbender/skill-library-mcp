#!/usr/bin/env node
/**
 * 短视频黄金 3 秒钩子生成器 - ClawHub 技能入口
 */

const path = require('path');
const { spawn } = require('child_process');

/**
 * 执行 Python 脚本
 */
async function executePython(command, args = {}) {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(__dirname, 'main.py');
    
    const pythonProcess = spawn('python3', [scriptPath, command, JSON.stringify(args)]);
    
    let output = '';
    let error = '';
    
    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      error += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (code === 0) {
        resolve(output);
      } else {
        reject(new Error(error || 'Python script failed'));
      }
    });
  });
}

/**
 * 技能处理函数
 */
async function handle(context) {
  const { message, args } = context;
  
  try {
    // 解析命令
    const command = args[0] || '帮助';
    const params = {};
    
    // 解析参数
    for (let i = 1; i < args.length; i++) {
      const arg = args[i];
      if (arg.includes('=')) {
        const [key, value] = arg.split('=');
        params[key] = value;
      } else if (i === 1) {
        params.topic = arg;
      }
    }
    
    // 执行 Python 脚本
    const result = await executePython(command, params);
    
    return {
      success: true,
      message: result
    };
    
  } catch (err) {
    return {
      success: false,
      message: `❌ 执行失败：${err.message}`
    };
  }
}

module.exports = {
  name: 'shortvideo-hook',
  version: '1.0.0',
  description: '短视频黄金 3 秒钩子生成器',
  handle
};
