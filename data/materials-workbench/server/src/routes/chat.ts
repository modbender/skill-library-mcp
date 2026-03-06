import { Router, type Request, type Response } from "express";
import { chat, type ChatMessage, type StreamEvent } from "materials-agents";
import { openai, getMaxTokens } from "../config.js";
import {
  uploadDataUrlToPicui,
  needsPicuiUpload,
} from "../picui.js";

const router = Router();

interface ChatRequestBody {
  messages: Array<{
    role: "user" | "assistant";
    content?: string;
    image?: string;
  }>;
  /** Current canvas JSON so every AI call (orchestrator, canvas) has context. */
  currentRenderData?: unknown;
}

router.post("/", async (req: Request, res: Response) => {
  const apiKey = openai.apiKey;
  if (!apiKey) {
    res.status(500).json({ error: "OPENAI_API_KEY is not set" });
    return;
  }
  const body = req.body as ChatRequestBody;
  const messages = body?.messages;
  if (!Array.isArray(messages)) {
    res.status(400).json({ error: "messages array is required" });
    return;
  }

  // Upload base64/data URL images to PICUI on the server; keep http(s) URLs as-is
  const normalized: ChatMessage[] = await Promise.all(
    messages.map(async (m) => {
      let image = m.image;
      if (image && needsPicuiUpload(image)) {
        try {
          image = await uploadDataUrlToPicui(image);
        } catch (err) {
          const msg = err instanceof Error ? err.message : "Image upload failed";
          throw new Error(msg);
        }
      }
      return {
        role: m.role,
        content: m.content,
        image,
      };
    }),
  );
  const currentRenderData = body?.currentRenderData;

  // ── SSE streaming response ──
  res.writeHead(200, {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    Connection: "keep-alive",
    "X-Accel-Buffering": "no",
  });
  res.flushHeaders();

  const sendEvent = (event: StreamEvent) => {
    res.write(`data: ${JSON.stringify(event)}\n\n`);
    // Flush immediately so the client receives each token without buffering delay.
    if (typeof (res as any).flush === "function") {
      (res as any).flush();
    }
  };

  try {
    await chat(apiKey, normalized, currentRenderData, sendEvent, {
      baseURL: openai.baseURL,
      model: openai.model,
      getMaxTokens: (agent) => getMaxTokens(agent),
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Chat failed";
    // Error event is already emitted by chat(), but send one more to be safe
    sendEvent({ type: "error", message });
  } finally {
    res.end();
  }
});

export default router;
