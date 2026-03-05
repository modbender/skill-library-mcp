# Web 端 TypeScript 格式示例脚本

## 示例：Joyspace基础操作

```typescript
import { chromium, Browser, BrowserContext, Page } from "playwright";
import { PlaywrightAgent } from "@midscene/web/playwright";
import "dotenv/config";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const storageStatePath = path.resolve(__dirname, "../../storage/state.json");

export const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export interface JoyspaceOptions {
  headless?: boolean;
  url: string;
  waitTime?: number;
}

export class JoyspaceBase {
  private browser: Browser | null = null;
  private context: BrowserContext | null = null;
  private page: Page | null = null;
  private agent: PlaywrightAgent | null = null;

  async init(options: JoyspaceOptions): Promise<void> {
    // 启动浏览器
    this.browser = await chromium.launch({
      headless: options.headless ?? false,
      args: ["--no-sandbox", "--disable-setuid-sandbox"],
    });

    // 创建上下文选项
    const contextOptions: any = {};
    
    // 处理存储状态
    if (fs.existsSync(storageStatePath)) {
      console.log("使用存储的登录状态...");
      contextOptions.storageState = storageStatePath;
    } else {
      console.log("未找到存储状态，请先运行: npm run auth:save");
    }

    this.context = await this.browser.newContext(contextOptions);
    this.page = await this.context.newPage();
    
    // 导航到指定URL
    await this.page.goto(options.url);
    
    // 等待页面加载
    const waitTime = options.waitTime ?? 3000;
    await sleep(waitTime);
    
    // 初始化Midscene agent
    this.agent = new PlaywrightAgent(this.page);
  }

  getAgent(): PlaywrightAgent {
    if (!this.agent) {
      throw new Error("Agent not initialized. Call init() first.");
    }
    return this.agent;
  }

  getPage(): Page {
    if (!this.page) {
      throw new Error("Page not initialized. Call init() first.");
    }
    return this.page;
  }

  async close(): Promise<void> {
    if (this.browser) {
      await this.browser.close();
    }
  }
}
```

## 支持的 Web 操作（TypeScript）

| 操作 | TypeScript 语法 | 说明 |
|------|----------------|------|
| 导航 | `await page.goto('URL')` | 打开指定 URL |
| 点击 | `await aiTap('按钮文本')` | 点击指定文本的元素 |
| 输入 | `await aiInput('输入框', '内容')` | 在指定输入框输入内容 |
| 断言 | `await aiAssert('验证条件')` | 验证页面状态 |
| 查询 | `await aiQuery<string>('查询')` | 提取页面信息 |
| 等待 | `await aiWaitFor('等待条件')` | 等待指定条件 |
| 悬停 | `await aiHover('元素')` | 鼠标悬停 |
| 滚动 | `await aiScroll('down')` | 滚动页面 |
| 键盘 | `await aiKeyboardPress('Enter')` | 按下键盘按键 |
| 截图 | `await page.screenshot({ path: '路径' })` | 保存截图 |
| 等待 | `await page.waitForTimeout(1000)` | 等待指定毫秒 |
