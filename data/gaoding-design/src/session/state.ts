import type { BrowserContext, Page } from 'playwright';
import type { TemplateInfo } from '../browser/search.js';

/** 单个会话的状态 */
export interface SessionState {
    lastSearchResults: TemplateInfo[];
    selectedTemplateId: string | null;
    context: BrowserContext | null;
    page: Page | null;
}

/** 创建空的会话状态 */
export function createSessionState(): SessionState {
    return {
        lastSearchResults: [],
        selectedTemplateId: null,
        context: null,
        page: null,
    };
}

/** 会话管理器：按 sessionId 隔离状态 */
const sessions = new Map<string, SessionState>();

const DEFAULT_SESSION = 'default';

export function getSession(sessionId: string = DEFAULT_SESSION): SessionState {
    let session = sessions.get(sessionId);
    if (!session) {
        session = createSessionState();
        sessions.set(sessionId, session);
    }
    return session;
}

export function clearSession(sessionId: string = DEFAULT_SESSION): void {
    const session = sessions.get(sessionId);
    if (session?.page && !session.page.isClosed()) {
        session.page.close().catch(() => {});
    }
    sessions.delete(sessionId);
}
