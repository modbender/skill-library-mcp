import { chromium, type BrowserContext, type Page } from 'playwright';
import { ensureLoggedIn } from '../browser/auth.js';
import { saveCookies } from '../browser/auth.js';
import { getSession, type SessionState } from '../session/state.js';

/** 确保浏览器实例已启动并已登录 */
export async function ensureBrowser(sessionId?: string): Promise<{ page: Page; context: BrowserContext }> {
    const session = getSession(sessionId);

    if (session.page && !session.page.isClosed() && session.context) {
        return { page: session.page, context: session.context };
    }

    const browser = await chromium.launch({ headless: true });
    session.context = await browser.newContext();
    await ensureLoggedIn(session.context);
    session.page = await session.context.newPage();

    return { page: session.page, context: session.context };
}

/** 保存当前会话的 Cookie */
export async function persistCookies(sessionId?: string): Promise<void> {
    const session = getSession(sessionId);
    if (session.context) {
        await saveCookies(session.context);
    }
}
