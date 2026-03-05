const fs = require('fs');
const path = require('path');
const readline = require('readline');
const { chromium } = require('/opt/homebrew/lib/node_modules/playwright');

const cwd = __dirname;
const artifactsDir = path.resolve(cwd, 'verification-artifacts');
const userDataDir = path.resolve(cwd, '.pw-user-data-taobao');
const statePath = path.resolve(artifactsDir, 'taobao-storage-state.json');

function waitForEnter(promptText) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question(promptText, () => {
      rl.close();
      resolve();
    });
  });
}

async function main() {
  fs.mkdirSync(artifactsDir, { recursive: true });
  fs.mkdirSync(userDataDir, { recursive: true });

  const context = await chromium.launchPersistentContext(userDataDir, {
    headless: false,
    locale: 'zh-CN',
    viewport: { width: 1440, height: 900 }
  });

  const pages = context.pages();
  const page = pages.length > 0 ? pages[0] : await context.newPage();

  await page.goto('https://www.taobao.com', { waitUntil: 'domcontentloaded', timeout: 90000 });

  console.log('\n淘宝页面已打开。');
  console.log('请在浏览器里完成登录，看到已登录状态后，回到终端按回车保存 cookie。\n');

  await waitForEnter('登录完成后按回车保存：');

  await context.storageState({ path: statePath });
  console.log(`\n已保存登录态到: ${statePath}`);

  await context.close();
}

main().catch((err) => {
  console.error('保存 cookie 失败:', err.message || err);
  process.exit(1);
});
