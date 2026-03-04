import type { ResolvedOneBotAccount, OneBotApiResponse, OneBotMessageSegment } from "./types.js";

export interface OutboundContext {
  to: string;
  text: string;
  accountId?: string | null;
  replyToId?: string | null;
  account: ResolvedOneBotAccount;
}

export interface OutboundResult {
  channel: string;
  messageId?: string;
  timestamp?: string | number;
  error?: string;
}

/**
 * Parse target address.
 * Formats:
 *   - private:<user_id>  -> private message
 *   - group:<group_id>   -> group message
 *   - onebot:private:<user_id>  -> with prefix
 *   - onebot:group:<group_id>   -> with prefix
 *   - raw number         -> defaults to private
 */
function parseTarget(to: string): { type: "private" | "group"; id: number } {
  let normalized = to.replace(/^onebot:/i, "");

  if (normalized.startsWith("private:")) {
    return { type: "private", id: Number(normalized.slice(8)) };
  }
  if (normalized.startsWith("group:")) {
    return { type: "group", id: Number(normalized.slice(6)) };
  }
  // Default to private
  return { type: "private", id: Number(normalized) };
}

/**
 * Call OneBot 11 HTTP API.
 */
async function callApi(
  account: ResolvedOneBotAccount,
  endpoint: string,
  body: Record<string, unknown>,
): Promise<OneBotApiResponse> {
  const url = `${account.httpUrl}/${endpoint}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (account.accessToken) {
    headers["Authorization"] = `Bearer ${account.accessToken}`;
  }

  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`OneBot API error: ${response.status} ${response.statusText}`);
  }

  return (await response.json()) as OneBotApiResponse;
}

/**
 * Build a CQ message array from text, with optional media segments.
 */
function buildMessage(text: string): OneBotMessageSegment[] {
  const segments: OneBotMessageSegment[] = [];

  if (text.trim()) {
    segments.push({ type: "text", data: { text } });
  }

  return segments;
}

/**
 * Send a text message via OneBot 11 HTTP API.
 */
export async function sendText(ctx: OutboundContext): Promise<OutboundResult> {
  const { to, text, account } = ctx;

  if (!account.httpUrl) {
    return { channel: "onebot", error: "OneBot not configured (missing httpUrl)" };
  }

  try {
    const target = parseTarget(to);
    const message = buildMessage(text);

    let result: OneBotApiResponse;

    if (target.type === "private") {
      result = await callApi(account, "send_private_msg", {
        user_id: target.id,
        message,
      });
    } else {
      result = await callApi(account, "send_group_msg", {
        group_id: target.id,
        message,
      });
    }

    if (result.retcode !== 0) {
      return {
        channel: "onebot",
        error: `OneBot API returned error: ${result.retcode} ${result.message ?? result.wording ?? ""}`,
      };
    }

    const data = result.data as { message_id?: number } | null;
    return {
      channel: "onebot",
      messageId: data?.message_id != null ? String(data.message_id) : undefined,
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return { channel: "onebot", error: message };
  }
}

/**
 * Send an image via OneBot 11 HTTP API.
 */
export async function sendImage(
  account: ResolvedOneBotAccount,
  targetType: "private" | "group",
  targetId: number,
  filePath: string,
): Promise<OneBotApiResponse> {
  const message: OneBotMessageSegment[] = [
    { type: "image", data: { file: filePath.startsWith("file://") ? filePath : `file://${filePath}` } },
  ];

  const endpoint = targetType === "private" ? "send_private_msg" : "send_group_msg";
  const idField = targetType === "private" ? "user_id" : "group_id";

  return callApi(account, endpoint, { [idField]: targetId, message });
}

/**
 * Send a voice/record via OneBot 11 HTTP API.
 */
export async function sendRecord(
  account: ResolvedOneBotAccount,
  targetType: "private" | "group",
  targetId: number,
  filePath: string,
): Promise<OneBotApiResponse> {
  const message: OneBotMessageSegment[] = [
    { type: "record", data: { file: filePath.startsWith("file://") ? filePath : `file://${filePath}` } },
  ];

  const endpoint = targetType === "private" ? "send_private_msg" : "send_group_msg";
  const idField = targetType === "private" ? "user_id" : "group_id";

  return callApi(account, endpoint, { [idField]: targetId, message });
}

/**
 * Upload a file via OneBot 11 HTTP API.
 */
export async function uploadFile(
  account: ResolvedOneBotAccount,
  targetType: "private" | "group",
  targetId: number,
  filePath: string,
  fileName: string,
): Promise<OneBotApiResponse> {
  const endpoint = targetType === "private" ? "upload_private_file" : "upload_group_file";
  const idField = targetType === "private" ? "user_id" : "group_id";

  return callApi(account, endpoint, {
    [idField]: targetId,
    file: filePath,
    name: fileName,
  });
}
