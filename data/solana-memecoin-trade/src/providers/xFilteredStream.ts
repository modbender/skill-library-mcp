import { logger } from "../logger.js";

export type XStreamEvent = {
  id?: string;
  text?: string;
  created_at?: string;
  author_id?: string;
  public_metrics?: any;
  matching_rules?: Array<{ id: string; tag?: string }>;
};

function xBase(): string {
  return process.env.X_API_BASE_URL || "https://api.x.com";
}

function bearer(): string {
  const t = process.env.X_BEARER_TOKEN;
  if (!t) throw new Error("Missing X_BEARER_TOKEN");
  return t;
}

async function xFetch(url: string, init?: RequestInit): Promise<Response> {
  return await fetch(url, {
    ...init,
    headers: {
      "Authorization": `Bearer ${bearer()}`,
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
}

export async function xGetRules(): Promise<any> {
  const url = `${xBase()}/2/tweets/search/stream/rules`;
  const res = await xFetch(url);
  if (!res.ok) throw new Error(`X rules GET failed: HTTP ${res.status}`);
  return await res.json();
}

export async function xAddRules(rules: Array<{ value: string; tag?: string }>): Promise<void> {
  if (!rules.length) return;
  const url = `${xBase()}/2/tweets/search/stream/rules`;
  const res = await xFetch(url, { method: "POST", body: JSON.stringify({ add: rules }) });
  if (!res.ok) throw new Error(`X rules POST failed: HTTP ${res.status}: ${await res.text()}`);
}

export function startXFilteredStream(opts: {
  onEvent: (e: XStreamEvent) => void;
  reconnectMinSeconds: number;
  reconnectMaxSeconds: number;
}): () => void {
  let stopped = false;
  let backoff = opts.reconnectMinSeconds;

  const sleep = (s: number) => new Promise(r => setTimeout(r, s * 1000));
  const clamp = (x: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, x));

  async function connectOnce() {
    const url = new URL(`${xBase()}/2/tweets/search/stream`);
    url.searchParams.set("tweet.fields", "created_at,public_metrics,author_id,lang");

    const res = await xFetch(url.toString(), { method: "GET" });
    if (!res.ok) throw new Error(`X stream failed: HTTP ${res.status}: ${await res.text()}`);

    logger.info("X stream connected");
    backoff = opts.reconnectMinSeconds;

    const reader = res.body?.getReader();
    if (!reader) throw new Error("X stream: no reader");

    let buf = "";
    while (!stopped) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += new TextDecoder().decode(value);
      const parts = buf.split(/\r?\n/);
      buf = parts.pop() || "";
      for (const line of parts) {
        const trimmed = line.trim();
        if (!trimmed) continue; // keep-alive
        try {
          const msg = JSON.parse(trimmed);
          const data = msg?.data;
          if (data?.text) {
            opts.onEvent({
              id: data.id,
              text: data.text,
              created_at: data.created_at,
              author_id: data.author_id,
              public_metrics: data.public_metrics,
              matching_rules: msg.matching_rules,
            });
          }
        } catch {
          // skip
        }
      }
    }
  }

  (async () => {
    while (!stopped) {
      try {
        await connectOnce();
      } catch (err) {
        logger.warn({ err, backoff }, "X stream disconnected; reconnecting");
        await sleep(backoff);
        backoff = clamp(Math.round(backoff * 1.7), opts.reconnectMinSeconds, opts.reconnectMaxSeconds);
      }
    }
  })().catch(err => logger.error({ err }, "X stream loop crashed"));

  return () => { stopped = true; };
}
