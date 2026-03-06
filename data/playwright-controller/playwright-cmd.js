const { fetchWithPlaywright, fetchElementAndScreenshot } = require('/Users/chenkuan/.openclaw/workspace/毕业论文/论文工程/playwright-crawler-v3.js');

/**
 * Playwright 命令行接口
 * 用于网页抓取和截图
 */

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    timeout: 60000,
    dir: './screenshots',
    url: null,
    selector: null
  };

  let i = 0;
  while (i < args.length) {
    const arg = args[i];

    switch (arg) {
      case '--timeout':
        options.timeout = parseInt(args[i + 1]) || 60000;
        i += 2;
        break;
      case '--dir':
        options.dir = args[i + 1];
        i += 2;
        break;
      case '--selector':
        options.selector = args[i + 1];
        i += 2;
        break;
      default:
        if (!arg.startsWith('--') && !options.url) {
          options.url = arg;
        }
        i++;
    }
  }

  return options;
}

// 生成文件名
function generateFilename(timestamp, url, suffix = '') {
  const urlHash = url
    .replace(/^https?:\/\//, '')
    .replace(/[^a-zA-Z0-9]/g, '_')
    .substring(0, 100);
  return `${timestamp}_${urlHash}${suffix}`;
}

// 主函数
async function main() {
  const options = parseArgs();

  // 验证参数
  if (!options.url) {
    console.error('❌ 错误：缺少 URL 参数');
    console.error('用法：playwright:fetch <url>');
    console.error('      playwright:fetch --timeout=120000 --dir=/path <url>');
    console.error('      playwright:fetch-element --selector=".content" <url>');
    process.exit(1);
  }

  // 确保目录存在
  const fs = require('fs');
  if (!fs.existsSync(options.dir)) {
    fs.mkdirSync(options.dir, { recursive: true });
  }

  const timestamp = Date.now();
  let result = null;

  try {
    if (options.selector) {
      // 截取特定元素
      console.log('🔍 正在截取元素...');
      console.log(`   URL: ${options.url}`);
      console.log(`   选择器: ${options.selector}\n`);

      result = await fetchElementAndScreenshot(options.url, options.selector, {
        headless: true,
        timeout: options.timeout,
        screenshotDir: options.dir
      });

      console.log(`\n✅ 成功！`);
      console.log(`   📄 标题: ${result.title}`);
      console.log(`   📝 文本长度: ${result.content.length} 字符`);
      console.log(`   📸 截图: ${result.screenshotPath}`);
      console.log(`   🕐 时间戳: ${new Date(result.timestamp).toLocaleString('zh-CN')}`);

    } else {
      // 获取整个页面
      console.log('⏳ 正在获取网页...');
      console.log(`   URL: ${options.url}`);
      console.log(`   超时: ${options.timeout}ms`);
      console.log(`   目录: ${options.dir}\n`);

      result = await fetchWithPlaywright(options.url, {
        headless: true,
        timeout: options.timeout,
        screenshotDir: options.dir
      });

      console.log(`\n✅ 成功！`);
      console.log(`   📄 标题: ${result.title}`);
      console.log(`   📝 内容长度: ${result.content.length} 字符`);
      console.log(`   📸 截图: ${result.screenshotPath}`);
      console.log(`   🕐 时间戳: ${new Date(result.timestamp).toLocaleString('zh-CN')}`);

      // 保存文本文件
      const textFilename = generateFilename(result.timestamp, options.url, '_content.txt');
      const textPath = `${options.dir}/${textFilename}`;
      fs.writeFileSync(textPath, result.content);
      console.log(`   📄 文本: ${textPath}`);
    }

    // 返回退出码 0
    process.exit(0);

  } catch (error) {
    console.error(`\n❌ 失败: ${error.message}`);

    // 保存错误截图
    try {
      const urlHash = options.url
        .replace(/^https?:\/\//, '')
        .replace(/[^a-zA-Z0-9]/g, '_')
        .substring(0, 100);
      const errorFilename = generateFilename(timestamp, options.url, '_error.png');
      const errorPath = `${options.dir}/${errorFilename}`;

      console.error(`   📸 错误截图: ${errorPath}`);

      // 创建简单的错误提示截图
      const errorContent = `ERROR: ${error.message}\nURL: ${options.url}\nTimestamp: ${new Date(timestamp).toLocaleString('zh-CN')}`;
      fs.writeFileSync(`${options.dir}/${errorFilename.replace('.png', '.txt')}`, errorContent);

    } catch (e) {
      console.error(`   ⚠️  无法保存错误截图`);
    }

    process.exit(1);
  }
}

// 执行主函数
main().catch(error => {
  console.error('❌ 未捕获的错误:', error);
  process.exit(1);
});
