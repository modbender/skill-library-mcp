#!/usr/bin/env node

/**
 * 卸载脚本 - 在用户卸载skill时自动执行
 */

const fs = require('fs-extra');
const path = require('path');
const chalk = require('chalk');

console.log(chalk.bold.yellow('🧠 卸载 Claw Memory Guardian...'));

// 获取安装路径
const workspacePath = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME, '.openclaw/workspace');
const targetPath = path.join(workspacePath, 'skills', 'claw-memory-guardian');
const binPath = path.join(workspacePath, 'bin', 'memory-guardian');

// 检查是否已安装
if (!fs.existsSync(targetPath)) {
  console.log(chalk.yellow('⚠️  未检测到已安装的记忆守护者'));
  process.exit(0);
}

// 询问用户是否保留记忆数据
console.log(chalk.cyan('\n📊 卸载选项:'));
console.log('1. 完全删除（包括记忆数据）');
console.log('2. 仅删除程序，保留记忆数据');
console.log('3. 取消卸载');

// 简化处理：默认保留记忆数据
console.log(chalk.yellow('\n⚠️  默认：仅删除程序文件，保留记忆数据'));
console.log(chalk.gray('你的记忆文件保存在 memory/ 目录中，不会被删除'));

// 删除程序文件
try {
  // 删除skill目录
  fs.removeSync(targetPath);
  console.log(chalk.green('✅ 删除程序文件'));
  
  // 删除可执行文件
  if (fs.existsSync(binPath)) {
    fs.removeSync(binPath);
    console.log(chalk.green('✅ 删除可执行文件'));
  }
  
  // 检查是否有自动保存进程在运行
  console.log(chalk.yellow('\n⚠️  注意：'));
  console.log('1. 自动保存脚本可能仍在运行');
  console.log('2. 如需完全停止，请手动结束相关进程');
  console.log('3. 你的记忆数据已保留在 memory/ 目录中');
  
  console.log(chalk.bold.green('\n🎉 卸载完成！'));
  console.log(chalk.gray('感谢使用 Claw Memory Guardian'));
  
} catch (error) {
  console.error(chalk.red('❌ 卸载失败:'), error.message);
  process.exit(1);
}