import { chromium, type BrowserContext, type Browser, type Page } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const COOKIE_DIR = path.join(os.homedir(), '.openclaw', 'skills', 'gaoding-template');
const COOKIE_PATH = path.join(COOKIE_DIR, 'cookies.json');
const MAX_COOKIE_AGE = 7 * 24 * 60 * 60 * 1000; // 7 天

/** 确保 Cookie 存储目录存在 */
function ensureCookieDir() {
    if (!fs.existsSync(COOKIE_DIR)) {
        fs.mkdirSync(COOKIE_DIR, { recursive: true });
    }
}

/** 加载已保存的 Cookie 到浏览器上下文 */
export async function loadCookies(context: BrowserContext): Promise<boolean> {
    ensureCookieDir();
    if (!fs.existsSync(COOKIE_PATH)) return false;

    try {
        const raw = fs.readFileSync(COOKIE_PATH, 'utf-8');
        const cookies = JSON.parse(raw);
        await context.addCookies(cookies);
        return true;
    } catch {
        return false;
    }
}

/** 保存当前浏览器上下文的 Cookie */
export async function saveCookies(context: BrowserContext): Promise<void> {
    ensureCookieDir();
    const cookies = await context.cookies();
    fs.writeFileSync(COOKIE_PATH, JSON.stringify(cookies, null, 2));
}

/** 检查 Cookie 文件是否存在且未过期 */
export function isCookieFresh(): boolean {
    if (!fs.existsSync(COOKIE_PATH)) return false;
    try {
        const stat = fs.statSync(COOKIE_PATH);
        return (Date.now() - stat.mtimeMs) < MAX_COOKIE_AGE;
    } catch {
        return false;
    }
}

/** 加载 .env 中的稿定账号凭证 */
function loadCredentials(): { username: string; password: string } | null {
    const skillDir = path.join(os.homedir(), '.openclaw', 'skills', 'gaoding-template-recommend');
    const envPath = path.join(skillDir, '.env');
    if (fs.existsSync(envPath)) {
        process.loadEnvFile(envPath);
    }
    const username = process.env.GAODING_USERNAME;
    const password = process.env.GAODING_PASSWORD;
    if (!username || !password) return null;
    return { username, password };
}

/** 通过 Playwright 自动登录稿定 */
export async function autoLogin(context: BrowserContext): Promise<boolean> {
    const creds = loadCredentials();
    if (!creds) {
        console.warn('[auth] 未配置 GAODING_USERNAME / GAODING_PASSWORD，无法自动登录');
        return false;
    }

    const page = await context.newPage();
    try {
        await page.goto('https://www.gaoding.com/login', { waitUntil: 'networkidle', timeout: 30000 });

        // 填写账号密码
        const accountInput = page.locator('input[placeholder*="手机号"], input[placeholder*="邮箱"], input[name="account"]').first();
        await accountInput.fill(creds.username);

        const passwordInput = page.locator('input[type="password"]').first();
        await passwordInput.fill(creds.password);

        // 点击登录按钮
        const loginBtn = page.locator('button:has-text("登录"), button[type="submit"]').first();
        await loginBtn.click();

        // 等待登录完成（URL 跳转离开 /login）
        await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 15000 });

        await saveCookies(context);
        console.warn('[auth] 自动登录成功');
        return true;
    } catch (err: any) {
        console.warn('[auth] 自动登录失败:', err.message);
        return false;
    } finally {
        await page.close();
    }
}

/** 确保浏览器上下文已登录：优先加载 Cookie，过期则自动重登录 */
export async function ensureLoggedIn(context: BrowserContext): Promise<boolean> {
    if (isCookieFresh()) {
        const loaded = await loadCookies(context);
        if (loaded) return true;
    }
    return autoLogin(context);
}
