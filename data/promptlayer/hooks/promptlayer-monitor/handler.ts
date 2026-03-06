/**
 * PromptLayer Monitor Hook
 * Logs every outbound agent message to PromptLayer for observability.
 * 
 * message:sent context fields:
 *   to, content, success, error, channelId, accountId, conversationId, messageId
 */

type HookHandler = (event: {
  type: string;
  action: string;
  sessionKey: string;
  timestamp: Date;
  messages: string[];
  context: Record<string, any>;
}) => Promise<void>;

const API_URL = "https://api.promptlayer.com";

const handler: HookHandler = async (event) => {
  console.log(`[promptlayer-monitor] Event: ${event.type}:${event.action}`);
  
  if (event.type !== "message" || event.action !== "sent") return;
  
  console.log(`[promptlayer-monitor] message:sent fired! success=${event.context?.success} content=${(event.context?.content || "").slice(0, 50)}`);
  
  if (!event.context?.success) return;

  const apiKey = process.env.PROMPTLAYER_API_KEY;
  if (!apiKey) {
    console.error("[promptlayer-monitor] No PROMPTLAYER_API_KEY set!");
    return;
  }

  const ctx = event.context;
  const content = ctx.content || "";
  const channelId = ctx.channelId || "unknown";
  const to = ctx.to || "unknown";
  const conversationId = ctx.conversationId || "";
  const messageId = ctx.messageId || "";
  const sessionKey = event.sessionKey || "unknown";

  // Classify session type
  let sessionType = "main";
  if (sessionKey.includes("cron") || sessionKey.includes("isolated")) sessionType = "cron";
  else if (sessionKey.includes("subagent") || sessionKey.includes("spawn")) sessionType = "subagent";

  const now = event.timestamp?.toISOString() || new Date().toISOString();

  // Run inline (not fire-and-forget) so we can see errors
  try {
      const logRes = await fetch(`${API_URL}/log-request`, {
        method: "POST",
        headers: {
          "X-API-KEY": apiKey,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          provider: "anthropic",
          model: "claude-opus-4-6",
          input: {
            type: "chat",
            messages: [{
              role: "user",
              content: [{ type: "text", text: "(agent turn)" }],
            }],
          },
          output: {
            type: "chat",
            messages: [{
              role: "assistant",
              content: [{ type: "text", text: content.slice(0, 4000) }],
            }],
          },
          request_start_time: now,
          request_end_time: now,
          tags: [sessionType, channelId],
          metadata: {
            session_key: sessionKey,
            session_type: sessionType,
            channel: channelId,
            to: to,
            conversation_id: conversationId,
            message_id: messageId,
          },
        }),
      });

    if (!logRes.ok) {
      console.error(`[promptlayer-monitor] Log failed: ${logRes.status} ${await logRes.text()}`);
    } else {
      console.log(`[promptlayer-monitor] ✅ Logged to PromptLayer`);
    }
  } catch (err) {
    console.error(`[promptlayer-monitor] Error:`, err);
  }
};

export default handler;
