import { config } from "dotenv";
config();

const CDP_URL = "http://127.0.0.1:9222/json";

const getTarget = async () => {
  const res = await fetch(CDP_URL);
  const pages = (await res.json()) as Array<{ url: string; webSocketDebuggerUrl: string }>;
  const page = pages.find((p) => p.url.includes("square")) ?? pages[0];
  if (!page) throw new Error("No browser page found");
  return page;
};

type CdpResult = {
  id: number;
  result?: { result?: { value?: { status: number; body: string } } };
  error?: { message: string };
};

const connectCdp = async (wsUrl: string) => {
  const ws = new WebSocket(wsUrl);
  let msgId = 1;

  await new Promise<void>((resolve) => ws.addEventListener("open", () => resolve()));

  const send = (method: string, params: Record<string, unknown> = {}): Promise<CdpResult> =>
    new Promise((resolve, reject) => {
      const id = msgId++;
      const timeout = setTimeout(() => reject(new Error("CDP timeout")), 15000);
      const handler = (evt: MessageEvent) => {
        const data = JSON.parse(String(evt.data)) as CdpResult;
        if (data.id === id) {
          clearTimeout(timeout);
          ws.removeEventListener("message", handler);
          resolve(data);
        }
      };
      ws.addEventListener("message", handler);
      ws.send(JSON.stringify({ id, method, params }));
    });

  return { ws, send };
};

const testEndpoint = async (
  send: ReturnType<typeof connectCdp> extends Promise<infer T> ? T extends { send: infer S } ? S : never : never,
  method: string,
  path: string,
  body?: Record<string, unknown>
) => {
  const bodyStr = body ? JSON.stringify(body) : "undefined";
  const expression = `
    fetch("${path}", {
      method: "${method}",
      headers: { "content-type": "application/json", "clienttype": "web" },
      credentials: "include",
      body: ${method === "GET" ? "undefined" : bodyStr}
    }).then(async r => {
      const t = await r.text();
      return { status: r.status, body: t.slice(0, 400) };
    })
  `;

  const result = await send("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });

  return result.result?.result?.value;
};

const main = async () => {
  const target = await getTarget();
  process.stdout.write(`Target: ${target.url}\n`);

  const { ws, send } = await connectCdp(target.webSocketDebuggerUrl);

  const endpoints: Array<[string, string, Record<string, unknown>?]> = [
    // Content creation
    ["POST", "/bapi/composite/v1/private/pgc/content/create", { content: "test" }],
    ["POST", "/bapi/composite/v2/private/pgc/content/create", { content: "test" }],
    ["POST", "/bapi/composite/v1/private/pgc/content/publish", { content: "test" }],
    ["POST", "/bapi/composite/v1/private/pgc/post/create", { content: "test" }],
    ["POST", "/bapi/composite/v1/private/pgc/post/publish", { content: "test" }],
    ["POST", "/bapi/composite/v1/private/pgc/content/short/create", { content: "test" }],
    ["POST", "/bapi/composite/v2/private/pgc/content/short/create", { content: "test" }],
    ["POST", "/bapi/composite/v1/private/pgc/content/article/create", { content: "test" }],
    ["POST", "/bapi/composite/v2/private/pgc/content/article/create", { content: "test" }],
    ["POST", "/bapi/composite/v1/private/pgc/content/short/publish", { content: "test" }],
    ["POST", "/bapi/composite/v2/private/pgc/content/short/publish", { content: "test" }],
    // Image upload
    ["POST", "/bapi/composite/v1/private/pgc/content/image/upload"],
    ["POST", "/bapi/composite/v1/private/pgc/upload/image"],
    ["POST", "/bapi/composite/v1/private/pgc/media/upload"],
    ["POST", "/bapi/composite/v2/private/pgc/media/upload"],
    // Content detail / status
    ["POST", "/bapi/composite/v1/public/pgc/content/detail", { contentId: "1" }],
    ["POST", "/bapi/composite/v1/private/pgc/content/detail", { contentId: "1" }],
    ["POST", "/bapi/composite/v2/public/pgc/content/detail", { contentId: "1" }],
    // Draft
    ["POST", "/bapi/composite/v1/private/pgc/content/draft/save", { content: "test" }],
    ["POST", "/bapi/composite/v2/private/pgc/content/draft/save", { content: "test" }],
    // Poll
    ["POST", "/bapi/composite/v1/private/pgc/content/vote/create"],
    ["POST", "/bapi/composite/v1/private/pgc/vote/create"],
  ];

  for (const [method, path, body] of endpoints) {
    try {
      const r = await testEndpoint(send, method, path, body);
      if (!r || r.status === 404) continue;
      process.stdout.write(`${r.status} ${method} ${path}\n`);
      process.stdout.write(`  -> ${r.body}\n\n`);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "unknown";
      process.stdout.write(`ERR ${path}: ${msg}\n`);
    }
  }

  ws.close();
  process.stdout.write("done\n");
};

main().catch((e) => {
  process.stderr.write(`Fatal: ${e instanceof Error ? e.message : "unknown"}\n`);
  process.exitCode = 1;
});
