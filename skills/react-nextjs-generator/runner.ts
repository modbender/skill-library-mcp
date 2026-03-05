#!/usr/bin/env node

import ReactProjectGenerator from './generator.ts';
import fs from 'fs/promises';
import path from 'path';

async function main() {
  // 从命令行参数获取项目名称和输出目录
  const [, , requirementsDocPath, uiImagePath, projectName = 'generated-app', outputDir = './output'] = process.argv;
  
  if (!requirementsDocPath) {
    console.error('用法: node runner.js <需求文档路径> [UI图像路径] [项目名称] [输出目录]');
    process.exit(1);
  }
  
  try {
    // 读取需求文档
    const requirementsDoc = await fs.readFile(requirementsDocPath, 'utf-8');
    
    // 创建项目生成器实例
    const generator = new ReactProjectGenerator(projectName, outputDir);
    
    // 生成项目
    console.log('正在根据需求文档和UI图生成项目...');
    const projectPath = await generator.generateFromRequirements(requirementsDoc, uiImagePath);
    
    console.log(`\n项目已成功生成在: ${projectPath}`);
    console.log('\n要启动项目，请运行:');
    console.log(`cd ${projectPath}`);
    console.log('npm install');
    console.log('npm run dev');
    
  } catch (error) {
    console.error('生成项目时出错:', error);
    process.exit(1);
  }
}

// 如果此文件被直接运行，则执行main函数
if (typeof require !== 'undefined' && require.main === module) {
  main();
}

export default main;