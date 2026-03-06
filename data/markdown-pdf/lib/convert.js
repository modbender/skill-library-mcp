#!/usr/bin/env node

/**
 * Markdown 转 PDF 核心转换库
 * 使用 Puppeteer 无头浏览器渲染 HTML 为 PDF
 */

const fs = require('fs');
const path = require('path');
const { marked } = require('marked');
const puppeteer = require('puppeteer');

// 解析命令行参数
const args = process.argv.slice(2);
const inputFile = args[0];
const outputFile = args[1];

const options = {
  theme: getArg('--theme', 'github'),
  font: getArg('--font', 'Noto Sans CJK SC'),
  toc: getArg('--toc', 'false') === 'true',
  header: getArg('--header', ''),
  footer: getArg('--footer', ''),
  margin: parseInt(getArg('--margin', '20'))
};

function getArg(name, defaultValue) {
  const index = args.indexOf(name);
  if (index !== -1 && index + 1 < args.length) {
    return args[index + 1];
  }
  return defaultValue;
}

// HTML 模板
function getTemplate(content, options) {
  const { theme, font, toc, header, footer } = options;

  return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Markdown to PDF</title>
  <style>
    /* 全局样式 */
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: '${font}', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
      font-size: 14px;
      line-height: 1.6;
      color: #333;
      background: #fff;
      padding: ${options.margin}px;
    }

    /* 标题样式 */
    h1, h2, h3, h4, h5, h6 {
      margin-top: 24px;
      margin-bottom: 16px;
      font-weight: 600;
      line-height: 1.25;
    }

    h1 {
      font-size: 2em;
      border-bottom: 1px solid #eaecef;
      padding-bottom: 0.3em;
      margin-bottom: 24px;
    }

    h2 {
      font-size: 1.5em;
      border-bottom: 1px solid #eaecef;
      padding-bottom: 0.3em;
    }

    h3 {
      font-size: 1.25em;
    }

    h4 {
      font-size: 1em;
    }

    /* 段落样式 */
    p {
      margin-bottom: 16px;
    }

    /* 列表样式 */
    ul, ol {
      padding-left: 2em;
      margin-bottom: 16px;
    }

    li {
      margin-bottom: 4px;
    }

    /* 代码块样式 */
    pre {
      background: #f6f8fa;
      border-radius: 6px;
      padding: 16px;
      overflow: auto;
      margin-bottom: 16px;
    }

    code {
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
      font-size: 0.9em;
      background: rgba(175, 184, 193, 0.2);
      padding: 0.2em 0.4em;
      border-radius: 3px;
    }

    pre code {
      background: transparent;
      padding: 0;
    }

    /* 表格样式 */
    table {
      border-collapse: collapse;
      width: 100%;
      margin-bottom: 16px;
    }

    table th,
    table td {
      border: 1px solid #d0d7de;
      padding: 6px 13px;
    }

    table th {
      background: #f6f8fa;
      font-weight: 600;
    }

    table tr:nth-child(2n) {
      background: #f6f8fa;
    }

    /* 引用样式 */
    blockquote {
      padding: 0 1em;
      color: #656d76;
      border-left: 0.25em solid #d0d7de;
      margin-bottom: 16px;
    }

    /* 链接样式 */
    a {
      color: #0969da;
      text-decoration: none;
    }

    a:hover {
      text-decoration: underline;
    }

    /* 水平线 */
    hr {
      height: 0.25em;
      padding: 0;
      margin: 24px 0;
      background: #d0d7de;
      border: 0;
    }

    /* 图片 */
    img {
      max-width: 100%;
      height: auto;
      display: block;
      margin: 16px 0;
    }

    /* 目录样式 */
    .toc {
      background: #f6f8fa;
      border: 1px solid #d0d7de;
      border-radius: 6px;
      padding: 16px;
      margin-bottom: 24px;
    }

    .toc-title {
      font-size: 1.2em;
      font-weight: 600;
      margin-bottom: 12px;
    }

    .toc ul {
      list-style: none;
      padding-left: 0;
    }

    .toc li {
      margin-bottom: 4px;
    }

    .toc a {
      color: #0969da;
    }

    /* 主题样式 */
    ${getThemeStyles(theme)}
  </style>
</head>
<body>
  ${toc ? generateTableOfContents(content) : ''}
  <div class="content">
    ${content}
  </div>
</body>
</html>
  `;
}

// 主题样式
function getThemeStyles(theme) {
  const themes = {
    github: `
      h1, h2 { border-bottom-color: #d0d7de; }
      pre { background: #f6f8fa; }
      table th { background: #f6f8fa; }
      table tr:nth-child(2n) { background: #f6f8fa; }
    `,
    vue: `
      h1, h2 { border-bottom-color: #42b883; }
      h1 { color: #42b883; }
      pre { background: #f8f9fa; }
      a { color: #42b883; }
    `,
    light: `
      body { background: #fff; }
      h1, h2 { border-bottom-color: #e0e0e0; }
      pre { background: #f5f5f5; }
    `,
    dark: `
      body { background: #1e1e1e; color: #d4d4d4; }
      h1, h2 { border-bottom-color: #3e3e3e; color: #fff; }
      pre { background: #2d2d2d; }
      code { background: rgba(255,255,255,0.1); }
      table th { background: #2d2d2d; }
      table tr:nth-child(2n) { background: #2d2d2d; }
      a { color: #4fc3f7; }
    `
  };

  return themes[theme] || themes.github;
}

// 生成目录
function generateTableOfContents(markdown) {
  const headings = markdown.match(/^#{1,6}\s+.+$/gm) || [];

  if (headings.length === 0) return '';

  const toc = headings.map(heading => {
    const level = heading.match(/^#+/)[0].length;
    const text = heading.replace(/^#+\s+/, '');
    const indent = (level - 1) * 16;
    return `<li style="padding-left: ${indent}px"><a href="#">${text}</a></li>`;
  }).join('\n');

  return `
    <div class="toc">
      <div class="toc-title">目录</div>
      <ul>${toc}</ul>
    </div>
  `;
}

// 主转换函数
async function convertToPdf() {
  try {
    // 读取 Markdown 文件
    const markdown = fs.readFileSync(inputFile, 'utf-8');

    // 转换为 HTML
    const html = marked(markdown);

    // 生成完整 HTML
    const fullHtml = getTemplate(html, options);

    // 启动 Puppeteer
    const browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();

    // 设置内容
    await page.setContent(fullHtml, { waitUntil: 'networkidle0' });

    // 生成 PDF
    await page.pdf({
      path: outputFile,
      format: 'A4',
      printBackground: true,
      margin: {
        top: `${options.margin}px`,
        right: `${options.margin}px`,
        bottom: `${options.margin}px`,
        left: `${options.margin}px`
      },
      displayHeaderFooter: options.header || options.footer ? true : false,
      headerTemplate: options.header ? `
        <div style="font-size: 10px; color: #666; padding: 10px ${options.margin}px; text-align: center;">
          ${options.header}
        </div>
      ` : '',
      footerTemplate: options.footer ? `
        <div style="font-size: 10px; color: #666; padding: 10px ${options.margin}px; text-align: center;">
          ${options.footer.replace('%PAGE%', '<span class="pageNumber"></span>').replace('%TOTAL%', '<span class="totalPages"></span>')}
        </div>
      ` : ''
    });

    await browser.close();

    console.log('转换成功');
  } catch (error) {
    console.error('转换失败:', error.message);
    process.exit(1);
  }
}

// 运行转换
convertToPdf();
