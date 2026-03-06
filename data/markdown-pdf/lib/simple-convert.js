#!/usr/bin/env node

/**
 * 简单的 Markdown 转 PDF 工具
 * 使用 markdown-pdf 库
 */

const fs = require('fs');
const path = require('path');
const markdownPDF = require('markdown-pdf');

// 解析参数
const args = process.argv.slice(2);
const inputFile = args[0];
const outputFile = args[1];

if (!inputFile) {
  console.error('用法: node simple-convert.js <input.md> [output.pdf]');
  process.exit(1);
}

// 生成输出文件名
const output = outputFile || path.join(path.dirname(inputFile), path.basename(inputFile, '.md') + '.pdf');

// 转换配置
const options = {
  css: path.join(__dirname, 'style.css'),
  paperFormat: 'A4',
  paperBorder: '2cm',
  remarkable: {
    html: true,
    breaks: true
  }
};

// 转换
console.log('开始转换...');
console.log('输入:', inputFile);
console.log('输出:', output);

markdownPDF(options)
  .from(inputFile)
  .to(output, function () {
    console.log('✓ 转换成功！');
    console.log('PDF 文件:', output);
  });
