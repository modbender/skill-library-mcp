// No external imports — Node 24 strips type annotations at runtime.
// Reads blocklist from env var SNITCH_BLOCKLIST (comma-separated) or falls back to defaults.

const DEFAULT_BLOCKLIST = ["clawhub", "clawdhub"];

function resolveBlocklist(): string[] {
  const env = (process as unknown as { env: Record<string, string> }).env.SNITCH_BLOCKLIST?.trim();
  if (env) return env.split(",").map((s: string) => s.trim()).filter(Boolean);
  return DEFAULT_BLOCKLIST;
}

function buildPatterns(blocklist: string[]): RegExp[] {
  return blocklist.map(
    (term: string) =>
      new RegExp(`\\b${term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`, "i"),
  );
}

const BLOCKLIST = resolveBlocklist();
const PATTERNS = buildPatterns(BLOCKLIST);

const handler = async (event: {
  type: string;
  action: string;
  context: Record<string, unknown>;
  messages: string[];
}) => {
  if (event.type !== "message" || event.action !== "received") return;
  const content: string = (event.context?.content as string) ?? "";
  const channelId: string = (event.context?.channelId as string) ?? "";
  if (!channelId) return; // system events have no channelId — avoid feedback loop
  if (!PATTERNS.some((re: RegExp) => re.test(content))) return;

  const from = (event.context?.from as string) ?? "unknown";
  console.warn(
    `[openclaw-snitch] POLICY VIOLATION: blocked term in message from=${from} channel=${channelId}`,
  );

  event.messages.push(
    `🚨 **Security policy violation**: This message references a blocked term (${BLOCKLIST.join(", ")}). ` +
      `These tools are blocked by system policy. The attempt has been logged.`,
  );
};

export default handler;
