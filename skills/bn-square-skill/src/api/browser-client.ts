import type { BinanceConfig } from "../config/schema";
import {
  ApiError,
  NetworkError,
  RateLimitError,
  SessionExpiredError,
  sanitizeSensitiveText
} from "../utils/errors";

type CdpPage = {
  url: string;
  webSocketDebuggerUrl: string;
};

type CdpResponse = {
  id: number;
  result?: {
    result?: {
      type?: string;
      subtype?: string;
      value?: unknown;
      description?: string;
    };
    exceptionDetails?: {
      text?: string;
      exception?: { description?: string };
    };
  };
  error?: { message: string };
};

type FetchResult = {
  status: number;
  body: string;
  headers: Record<string, string>;
};

type CdpSendFn = (method: string, params?: Record<string, unknown>) => Promise<CdpResponse>;

const BINANCE_SQUARE_URL = "https://www.binance.com/en/square";
const CDP_TIMEOUT_MS = 15_000;

const parseCdpBaseUrl = (cdpUrl: string): string => {
  const parsed = new URL(cdpUrl);
  return `${parsed.protocol}//${parsed.host}`;
};

const fetchCdpPages = async (cdpUrl: string): Promise<CdpPage[]> => {
  const baseUrl = parseCdpBaseUrl(cdpUrl);
  const response = await fetch(`${baseUrl}/json`);

  if (!response.ok) {
    throw new NetworkError(`CDP endpoint returned ${response.status}`);
  }

  return response.json() as Promise<CdpPage[]>;
};

const findBinancePage = (pages: CdpPage[]): CdpPage => {
  const binancePage = pages.find((p) => p.url.includes("binance.com"));
  const target = binancePage ?? pages[0];

  if (!target) {
    throw new NetworkError("No browser page found via CDP");
  }

  return target;
};

const createCdpConnection = (
  wsUrl: string,
  timeoutMs: number
): Promise<{ send: CdpSendFn; close: () => void }> =>
  new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    let msgId = 1;
    const pendingTimeout = setTimeout(() => {
      ws.close();
      reject(new NetworkError("CDP WebSocket connection timed out"));
    }, timeoutMs);

    ws.addEventListener("error", (event) => {
      clearTimeout(pendingTimeout);
      reject(new NetworkError(`CDP WebSocket error: ${String(event)}`));
    });

    ws.addEventListener("open", () => {
      clearTimeout(pendingTimeout);

      const send: CdpSendFn = (method, params = {}) =>
        new Promise((resolveSend, rejectSend) => {
          const id = msgId++;
          const timeout = setTimeout(() => {
            ws.removeEventListener("message", handler);
            rejectSend(new NetworkError(`CDP command "${method}" timed out`));
          }, timeoutMs);

          const handler = (evt: MessageEvent) => {
            const data = JSON.parse(String(evt.data)) as CdpResponse;
            if (data.id === id) {
              clearTimeout(timeout);
              ws.removeEventListener("message", handler);
              resolveSend(data);
            }
          };

          ws.addEventListener("message", handler);
          ws.send(JSON.stringify({ id, method, params }));
        });

      const close = () => {
        ws.close();
      };

      resolve({ send, close });
    });
  });

const escapeForJs = (value: string): string =>
  value.replace(/\\/g, "\\\\").replace(/'/g, "\\'").replace(/\n/g, "\\n").replace(/\r/g, "\\r");

const injectCookies = async (send: CdpSendFn, cookieHeader: string): Promise<void> => {
  const segments = cookieHeader
    .split(";")
    .map((s) => s.trim())
    .filter((s) => s.length > 0);

  for (const segment of segments) {
    const eqIndex = segment.indexOf("=");
    if (eqIndex <= 0) continue;

    const name = segment.slice(0, eqIndex).trim();
    const value = segment.slice(eqIndex + 1).trim();

    await send("Network.setCookie", {
      name,
      value,
      domain: ".binance.com",
      path: "/",
      httpOnly: false,
      secure: true
    });
  }
};

const navigateAndWait = async (send: CdpSendFn, url: string): Promise<void> => {
  await send("Page.enable");
  await send("Page.navigate", { url });

  // Wait for page load via Runtime.evaluate polling
  const waitExpression = `
    new Promise(resolve => {
      if (document.readyState === 'complete') return resolve(true);
      window.addEventListener('load', () => resolve(true), { once: true });
      setTimeout(() => resolve(true), 5000);
    })
  `;
  await send("Runtime.evaluate", {
    expression: waitExpression,
    awaitPromise: true,
    returnByValue: true
  });
};

const buildFetchExpression = (
  path: string,
  method: string,
  bodyExpression: string,
  csrfToken: string | undefined
): string => {
  const headers: Record<string, string> = {
    "content-type": "application/json",
    clienttype: "web"
  };
  if (csrfToken) {
    headers["csrftoken"] = "${csrfToken}";
  }

  // We build the JS expression as a string template
  const headersJson = JSON.stringify(headers).replace('"${csrfToken}"', `'${escapeForJs(csrfToken ?? "")}'`);

  return `
    (async () => {
      const resp = await fetch('${escapeForJs(path)}', {
        method: '${method}',
        headers: ${headersJson},
        credentials: 'include',
        body: ${bodyExpression}
      });
      const text = await resp.text();
      const respHeaders = {};
      resp.headers.forEach((v, k) => { respHeaders[k] = v; });
      return { status: resp.status, body: text, headers: respHeaders };
    })()
  `;
};

const buildFormDataFetchExpression = (
  path: string,
  fieldName: string,
  base64Data: string,
  fileName: string,
  mimeType: string,
  csrfToken: string | undefined
): string => {
  const csrfHeader = csrfToken ? `headers['csrftoken'] = '${escapeForJs(csrfToken)}';` : "";

  return `
    (async () => {
      const b64 = '${base64Data}';
      const binary = atob(b64);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
      const blob = new Blob([bytes], { type: '${escapeForJs(mimeType)}' });
      const fd = new FormData();
      fd.append('${escapeForJs(fieldName)}', blob, '${escapeForJs(fileName)}');
      const headers = { clienttype: 'web' };
      ${csrfHeader}
      const resp = await fetch('${escapeForJs(path)}', {
        method: 'POST',
        headers,
        credentials: 'include',
        body: fd
      });
      const text = await resp.text();
      const respHeaders = {};
      resp.headers.forEach((v, k) => { respHeaders[k] = v; });
      return { status: resp.status, body: text, headers: respHeaders };
    })()
  `;
};

const evaluateFetch = async (send: CdpSendFn, expression: string, timeoutMs: number): Promise<FetchResult> => {
  const result = await send("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
    timeout: timeoutMs
  });

  if (result.error) {
    throw new NetworkError(`CDP evaluate error: ${result.error.message}`);
  }

  const exceptionDetails = result.result?.exceptionDetails;
  if (exceptionDetails) {
    const exceptionText =
      exceptionDetails.exception?.description ?? exceptionDetails.text ?? "Unknown browser error";
    throw new NetworkError(`Browser fetch failed: ${sanitizeSensitiveText(exceptionText)}`);
  }

  const value = result.result?.result?.value as FetchResult | undefined;
  if (!value || typeof value.status !== "number") {
    throw new NetworkError("CDP evaluate returned unexpected result");
  }

  return value;
};

const handleFetchResult = (fetchResult: FetchResult, method: string, path: string): unknown => {
  const { status, body } = fetchResult;

  if (status === 401 || status === 403) {
    const preview = body.length > 240 ? `${body.slice(0, 240)}...` : body;
    throw new SessionExpiredError(
      `Request failed (${status}) for ${method} ${path}: ${sanitizeSensitiveText(preview)}`,
      status
    );
  }

  if (status === 429) {
    throw new RateLimitError(
      `Request failed (${status}) for ${method} ${path}`,
      status
    );
  }

  if (status < 200 || status >= 300) {
    const preview = body.length > 240 ? `${body.slice(0, 240)}...` : body;
    throw new ApiError(
      `Request failed (${status}) for ${method} ${path}: ${sanitizeSensitiveText(preview)}`,
      status
    );
  }

  try {
    return JSON.parse(body) as unknown;
  } catch {
    return body;
  }
};

export class BrowserClient {
  private readonly config: BinanceConfig;
  private cdpSend: CdpSendFn | undefined;
  private cdpClose: (() => void) | undefined;

  public constructor(config: BinanceConfig) {
    this.config = config;
  }

  public async connect(): Promise<void> {
    if (!this.config.cdpUrl) {
      throw new NetworkError("BrowserClient requires cdpUrl to be configured");
    }
    const pages = await fetchCdpPages(this.config.cdpUrl);
    const target = findBinancePage(pages);

    const { send, close } = await createCdpConnection(
      target.webSocketDebuggerUrl,
      CDP_TIMEOUT_MS
    );
    this.cdpSend = send;
    this.cdpClose = close;

    await injectCookies(send, this.config.cookieHeader);

    // Only navigate if not already on Binance
    if (!target.url.includes("binance.com")) {
      await navigateAndWait(send, BINANCE_SQUARE_URL);
    }
  }

  public disconnect(): void {
    if (this.cdpClose) {
      this.cdpClose();
      this.cdpClose = undefined;
      this.cdpSend = undefined;
    }
  }

  public async getJson<T>(
    path: string,
    options?: { query?: Record<string, string> }
  ): Promise<T> {
    const fullPath = this.buildPath(path, options?.query);
    const expression = buildFetchExpression(fullPath, "GET", "undefined", this.config.csrfToken);
    const result = await evaluateFetch(this.getSend(), expression, this.config.requestTimeoutMs);
    return handleFetchResult(result, "GET", path) as T;
  }

  public async postJson<T>(path: string, body: unknown): Promise<T> {
    const bodyStr = JSON.stringify(body);
    const expression = buildFetchExpression(
      path,
      "POST",
      `'${escapeForJs(bodyStr)}'`,
      this.config.csrfToken
    );
    const result = await evaluateFetch(this.getSend(), expression, this.config.requestTimeoutMs);
    return handleFetchResult(result, "POST", path) as T;
  }

  public async postFormData<T>(path: string, formData: FormData): Promise<T> {
    const send = this.getSend();

    // Extract the first file entry from FormData
    let fieldName = "file";
    let fileBlob: Blob | undefined;
    let fileName = "upload";

    for (const [key, value] of formData.entries()) {
      if (typeof value !== "string") {
        fieldName = key;
        fileBlob = value as Blob;
        fileName = (value as File).name ?? "upload";
        break;
      }
    }

    if (!fileBlob) {
      throw new ApiError("FormData does not contain a file entry");
    }

    const arrayBuffer = await fileBlob.arrayBuffer();
    const bytes = new Uint8Array(arrayBuffer);

    // Convert to base64
    let binary = "";
    for (let i = 0; i < bytes.length; i++) {
      binary += String.fromCharCode(bytes[i]!);
    }
    const base64 = btoa(binary);

    const expression = buildFormDataFetchExpression(
      path,
      fieldName,
      base64,
      fileName,
      fileBlob.type || "application/octet-stream",
      this.config.csrfToken
    );

    const result = await evaluateFetch(send, expression, this.config.requestTimeoutMs);
    return handleFetchResult(result, "POST", path) as T;
  }

  private getSend(): CdpSendFn {
    if (!this.cdpSend) {
      throw new NetworkError("BrowserClient is not connected. Call connect() first.");
    }
    return this.cdpSend;
  }

  private buildPath(path: string, query?: Record<string, string>): string {
    if (!query || Object.keys(query).length === 0) {
      return path;
    }

    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(query)) {
      params.set(key, value);
    }

    return `${path}?${params.toString()}`;
  }
}
