#!/usr/bin/env node

/**
 * 使用浏览器控制 API 将 HTML 转换为 PDF
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 解析参数
const args = process.argv.slice(2);
const mdFile = args[0];
const pdfFile = args[1] || mdFile.replace(/\.md$/, '.pdf');

if (!mdFile || !fs.existsSync(mdFile)) {
  console.error('用法: node browser-convert.js <input.md> [output.pdf]');
  process.exit(1);
}

// 读取 Markdown
const markdown = fs.readFileSync(mdFile, 'utf-8');

// 简单的 Markdown 转 HTML
function mdToHtml(md) {
  let html = md;

  // 标题
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

  // 粗体
  html = html.replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>');

  // 斜体
  html = html.replace(/\*(.*)\*/gim, '<em>$1</em>');

  // 代码块
  html = html.replace(/```(\w+)?\n([\s\S]*?)```/gim, '<pre><code>$2</code></pre>');

  // 行内代码
  html = html.replace(/`([^`]+)`/gim, '<code>$1</code>');

  // 链接
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2">$1</a>');

  // 图片
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/gim, '<img src="$2" alt="$1">');

  // 水平线
  html = html.replace(/^---$/gim, '<hr>');

  // 段落
  html = html.replace(/\n\n/g, '</p><p>');
  html = '<p>' + html + '</p>';

  // 列表（简化处理）
  html = html.replace(/^- (.*$)/gim, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/gim, '<ul>$&</ul>');

  // 表格（简化处理）
  html = html.replace(/\|(.+)\|/gim, (match) => {
    const cells = match.split('|').filter(c => c.trim());
    return '<tr>' + cells.map(c => `<td>${c.trim()}</td>`).join('') + '</tr>';
  });
  html = html.replace(/(<tr>.*<\/tr>\n?)+/gim, '<table>$&</table>');

  return html;
}

const htmlContent = mdToHtml(markdown);

// 完整的 HTML
const fullHtml = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${path.basename(mdFile, '.md')}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans CJK SC", sans-serif;
      font-size: 14px;
      line-height: 1.6;
      color: #333;
      max-width: 800px;
      margin: 40px auto;
      padding: 0 20px;
    }
    h1, h2, h3 { margin-top: 1.5em; margin-bottom: 0.5em; }
    h1 { font-size: 2em; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    h2 { font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    h3 { font-size: 1.25em; }
    p { margin-bottom: 1em; }
    pre { background: #f6f8fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
    code { font-family: monospace; background: #f6f8fa; padding: 2px 5px; border-radius: 3px; }
    pre code { background: transparent; padding: 0; }
    table { border-collapse: collapse; width: 100%; margin: 20px 0; }
    table td, table th { border: 1px solid #ddd; padding: 8px; }
    table th { background: #f6f8fa; }
    ul { padding-left: 20px; }
    a { color: #0969da; }
    img { max-width: 100%; }
    hr { border: none; border-top: 1px solid #eee; margin: 20px 0; }
  </style>
</head>
<body>
  ${htmlContent}
</body>
</html>
`;

// 保存 HTML 文件
const tempHtml = '/tmp/md-to-pdf-temp.html';
fs.writeFileSync(tempHtml, fullHtml);

console.log('HTML 文件已生成:', tempHtml);
console.log('请使用浏览器打开该文件，然后打印为 PDF');
console.log('');
console.log('或者在安装了 chromium/wkhtmltopdf 后重新运行');
