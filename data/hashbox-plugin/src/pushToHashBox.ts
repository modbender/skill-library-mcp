import type {
  ArticlePayload,
  MetricItem,
  MetricPayload,
  AuditFinding,
  AuditPayload,
  HashBoxRequest,
} from "./types.js";
import { loadConfig } from "./setupHashBox.js";

const WEBHOOK_BASE_URL =
  "https://webhook-vcphors6kq-uc.a.run.app/webhook";

interface SendResult {
  status: number;
  message: string;
}

type PayloadData = string | MetricItem[] | AuditFinding[];

function validateChannel(name: string): void {
  if (!name || name.trim().length === 0) {
    throw new Error("channel.name must not be empty");
  }
}

function validatePayloadData(
  payloadType: HashBoxRequest["type"],
  contentOrData: PayloadData
): void {
  if (payloadType === "article") {
    if (typeof contentOrData !== "string" || contentOrData.length === 0) {
      throw new Error("payload.content must be a non-empty string");
    }
    return;
  }
  if (payloadType === "metric") {
    if (!Array.isArray(contentOrData) || contentOrData.length === 0) {
      throw new Error("payload.metrics must be a non-empty array");
    }
    return;
  }
  if (!Array.isArray(contentOrData) || contentOrData.length === 0) {
    throw new Error("payload.findings must be a non-empty array");
  }
}

function buildRequest(
  payloadType: HashBoxRequest["type"],
  channelName: string,
  channelIcon: string,
  title: string,
  contentOrData: PayloadData
): HashBoxRequest {
  validateChannel(channelName);
  validatePayloadData(payloadType, contentOrData);

  const channel = { name: channelName, icon: channelIcon };

  if (payloadType === "article") {
    const payload: ArticlePayload = {
      title,
      content: contentOrData as string,
    };
    return { type: "article", channel, payload };
  }
  if (payloadType === "metric") {
    const payload: MetricPayload = {
      title,
      metrics: contentOrData as MetricItem[],
    };
    return { type: "metric", channel, payload };
  }
  const payload: AuditPayload = {
    title,
    findings: contentOrData as AuditFinding[],
  };
  return { type: "audit", channel, payload };
}

export async function sendHashBoxNotification(
  payloadType: HashBoxRequest["type"],
  channelName: string,
  channelIcon: string,
  title: string,
  contentOrData: PayloadData
): Promise<SendResult> {
  const config = await loadConfig();
  if (!config) {
    throw new Error("HashBox config not found. Run configureHashBox first.");
  }
  const url = `${WEBHOOK_BASE_URL}?token=${config.token}`;
  const request = buildRequest(
    payloadType, channelName, channelIcon, title, contentOrData
  );
  const body = JSON.stringify(request);

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
    });

    return {
      status: response.status,
      message: response.ok
        ? "Notification sent successfully"
        : `Request failed with status ${response.status}`,
    };
  } catch (err: unknown) {
    const errorMessage =
      err instanceof Error ? err.message : "Unknown network error";
    return {
      status: 0,
      message: `Network error: ${errorMessage}`,
    };
  }
}
