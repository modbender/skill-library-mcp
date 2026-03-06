/**
 * Playwright CDP Adapter
 *
 * Provides CDPTransport implementation for Playwright pages,
 * enabling use of @predicatesystems/runtime backends with plain Playwright.
 */

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type PlaywrightPage = any;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type CDPSession = any;

/**
 * CDPTransport interface from @predicatesystems/runtime
 */
export interface CDPTransport {
  send(method: string, params?: Record<string, unknown>): Promise<Record<string, unknown>>;
}

/**
 * Wraps Playwright's CDP session to provide CDPTransport interface.
 *
 * Usage:
 *   const page = await browser.newPage();
 *   const adapter = new PlaywrightCDPAdapter(page);
 *   const transport = await adapter.createTransport();
 *   const backend = new CDPBackend(transport);
 */
export class PlaywrightCDPAdapter {
  private page: PlaywrightPage;
  private cdpSession: CDPSession | null = null;

  constructor(page: PlaywrightPage) {
    this.page = page;
  }

  /**
   * Create CDP transport from Playwright page.
   *
   * @returns CDPTransport instance
   */
  async createTransport(): Promise<CDPTransport> {
    // Create CDP session via Playwright's context
    const context = this.page.context();
    this.cdpSession = await context.newCDPSession(this.page);

    return {
      send: async (method: string, params?: Record<string, unknown>): Promise<Record<string, unknown>> => {
        if (!this.cdpSession) {
          throw new Error('CDP session not initialized');
        }
        const result = await this.cdpSession.send(method, params || {});
        return result as Record<string, unknown>;
      },
    };
  }

  /**
   * Detach the CDP session when done.
   */
  async detach(): Promise<void> {
    if (this.cdpSession) {
      await this.cdpSession.detach();
      this.cdpSession = null;
    }
  }
}

/**
 * Create a browser-use compatible session wrapper from Playwright page.
 *
 * This wrapper provides the getOrCreateCdpSession method expected by
 * @predicatesystems/runtime's BrowserUseAdapter.
 *
 * Usage:
 *   const page = await browser.newPage();
 *   const session = createBrowserUseSession(page);
 *   const ctx = new PredicateContext({ predicateApiKey: 'xxx' });
 *   const result = await ctx.build(session);
 */
export function createBrowserUseSession(page: PlaywrightPage): {
  getOrCreateCdpSession: () => Promise<{ cdpClient: { send: Record<string, Record<string, (options: { params?: unknown; session_id?: string }) => Promise<unknown>>> }; sessionId: string }>;
} {
  let cdpSession: CDPSession | null = null;

  return {
    async getOrCreateCdpSession() {
      if (!cdpSession) {
        const context = page.context();
        cdpSession = await context.newCDPSession(page);
      }

      // Create a proxy object that matches browser-use's CDP client interface
      // The SDK's BrowserUseCDPTransport expects: cdpClient.send[domain][method]({ params, session_id })
      // Note: The SDK passes { params, session_id } as a single options object!
      const cdpClient = {
        send: new Proxy(
          {},
          {
            get(_target, domain: string) {
              return new Proxy(
                {},
                {
                  get(_innerTarget, method: string) {
                    return async (options: { params?: unknown; session_id?: string }) => {
                      const fullMethod = `${domain}.${method}`;
                      const result = await cdpSession.send(fullMethod, options.params || {});
                      return result;
                    };
                  },
                }
              );
            },
          }
        ) as Record<string, Record<string, (options: { params?: unknown; session_id?: string }) => Promise<unknown>>>,
      };

      // Generate a unique session ID
      const sessionId = `playwright-${Date.now()}`;

      return { cdpClient, sessionId };
    },
  };
}
