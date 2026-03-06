import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { writeFile, mkdtemp, rm } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { sendHashBoxNotification } from "../src/pushToHashBox.js";
import type { MetricItem, AuditFinding } from "../src/types.js";

let tempDir: string;

const EXPECTED_TOKEN = "HB-valid-token";
const EXPECTED_URL = `https://webhook-vcphors6kq-uc.a.run.app/webhook?token=${EXPECTED_TOKEN}`;

describe("sendHashBoxNotification", () => {
  beforeEach(async () => {
    tempDir = await mkdtemp(join(tmpdir(), "hashbox-push-"));
    vi.spyOn(process, "cwd").mockReturnValue(tempDir);
  });

  afterEach(async () => {
    vi.restoreAllMocks();
    await rm(tempDir, { recursive: true, force: true });
  });

  it("should POST article payload to correct URL with token as query param", async () => {
    const configPath = join(tempDir, "hashbox_config.json");
    await writeFile(configPath, JSON.stringify({ token: EXPECTED_TOKEN }), "utf-8");

    const mockResponse = { ok: true, status: 200 } as Response;
    const fetchMock = vi.fn().mockResolvedValue(mockResponse);
    vi.stubGlobal("fetch", fetchMock);

    const result = await sendHashBoxNotification(
      "article", "News", "📰", "Test Article", "This is a test body"
    );

    expect(result.status).toBe(200);
    expect(result.message).toBe("Notification sent successfully");

    expect(fetchMock).toHaveBeenCalledOnce();
    const [calledUrl, calledOptions] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(calledUrl).toBe(EXPECTED_URL);
    expect(calledOptions.method).toBe("POST");

    const sentBody = JSON.parse(calledOptions.body as string);
    expect(sentBody).toEqual({
      type: "article",
      channel: { name: "News", icon: "📰" },
      payload: { title: "Test Article", content: "This is a test body" },
    });
  });

  it("should POST metric payload with channel object", async () => {
    const configPath = join(tempDir, "hashbox_config.json");
    await writeFile(configPath, JSON.stringify({ token: EXPECTED_TOKEN }), "utf-8");

    const mockResponse = { ok: true, status: 200 } as Response;
    const fetchMock = vi.fn().mockResolvedValue(mockResponse);
    vi.stubGlobal("fetch", fetchMock);

    const metrics: MetricItem[] = [
      { label: "CPU", value: 85, unit: "%" },
    ];

    const result = await sendHashBoxNotification(
      "metric", "System Monitor", "📊", "Server Stats", metrics
    );

    expect(result.status).toBe(200);

    const sentBody = JSON.parse(
      (fetchMock.mock.calls[0] as [string, RequestInit])[1].body as string
    );
    expect(sentBody).toEqual({
      type: "metric",
      channel: { name: "System Monitor", icon: "📊" },
      payload: { title: "Server Stats", metrics },
    });
  });

  it("should POST audit payload with channel object and findings", async () => {
    const configPath = join(tempDir, "hashbox_config.json");
    await writeFile(configPath, JSON.stringify({ token: EXPECTED_TOKEN }), "utf-8");

    const mockResponse = { ok: true, status: 200 } as Response;
    const fetchMock = vi.fn().mockResolvedValue(mockResponse);
    vi.stubGlobal("fetch", fetchMock);

    const findings: AuditFinding[] = [
      { severity: "info", message: "email changed from a@b.com to c@d.com" },
    ];

    const result = await sendHashBoxNotification(
      "audit", "Audit Log", "🔍", "User Change", findings
    );

    expect(result.status).toBe(200);

    const sentBody = JSON.parse(
      (fetchMock.mock.calls[0] as [string, RequestInit])[1].body as string
    );
    expect(sentBody).toEqual({
      type: "audit",
      channel: { name: "Audit Log", icon: "🔍" },
      payload: { title: "User Change", findings },
    });
  });

  it("should throw when config file is missing", async () => {
    await expect(
      sendHashBoxNotification("article", "Ch", "📰", "Title", "Body")
    ).rejects.toThrow("HashBox config not found");
  });

  it("should handle network failure gracefully", async () => {
    const configPath = join(tempDir, "hashbox_config.json");
    await writeFile(configPath, JSON.stringify({ token: EXPECTED_TOKEN }), "utf-8");

    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("fetch failed")));

    const result = await sendHashBoxNotification(
      "article", "News", "📰", "Test", "Body"
    );
    expect(result.status).toBe(0);
    expect(result.message).toContain("Network error");
    expect(result.message).toContain("fetch failed");
  });

  it("should handle non-ok response status", async () => {
    const configPath = join(tempDir, "hashbox_config.json");
    await writeFile(configPath, JSON.stringify({ token: EXPECTED_TOKEN }), "utf-8");

    const mockResponse = { ok: false, status: 403 } as Response;
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(mockResponse));

    const result = await sendHashBoxNotification(
      "article", "News", "📰", "Test", "Body"
    );
    expect(result.status).toBe(403);
    expect(result.message).toBe("Request failed with status 403");
  });

  it("should throw when channel name is empty", async () => {
    const configPath = join(tempDir, "hashbox_config.json");
    await writeFile(configPath, JSON.stringify({ token: EXPECTED_TOKEN }), "utf-8");

    await expect(
      sendHashBoxNotification("article", "", "📰", "Title", "Body")
    ).rejects.toThrow("channel.name must not be empty");
  });

  it("should throw when channel name is only whitespace", async () => {
    const configPath = join(tempDir, "hashbox_config.json");
    await writeFile(configPath, JSON.stringify({ token: EXPECTED_TOKEN }), "utf-8");

    await expect(
      sendHashBoxNotification("article", "   ", "📰", "Title", "Body")
    ).rejects.toThrow("channel.name must not be empty");
  });

  it("should throw when article content is empty string", async () => {
    const configPath = join(tempDir, "hashbox_config.json");
    await writeFile(configPath, JSON.stringify({ token: EXPECTED_TOKEN }), "utf-8");

    await expect(
      sendHashBoxNotification("article", "News", "📰", "Title", "")
    ).rejects.toThrow("payload.content must be a non-empty string");
  });

  it("should throw when metric items array is empty", async () => {
    const configPath = join(tempDir, "hashbox_config.json");
    await writeFile(configPath, JSON.stringify({ token: EXPECTED_TOKEN }), "utf-8");

    const emptyMetrics: MetricItem[] = [];
    await expect(
      sendHashBoxNotification("metric", "Monitor", "📊", "Stats", emptyMetrics)
    ).rejects.toThrow("payload.metrics must be a non-empty array");
  });

  it("should throw when audit findings array is empty", async () => {
    const configPath = join(tempDir, "hashbox_config.json");
    await writeFile(configPath, JSON.stringify({ token: EXPECTED_TOKEN }), "utf-8");

    const emptyFindings: AuditFinding[] = [];
    await expect(
      sendHashBoxNotification("audit", "Audit", "🔍", "Check", emptyFindings)
    ).rejects.toThrow("payload.findings must be a non-empty array");
  });

  it("should not include token in the request body", async () => {
    const configPath = join(tempDir, "hashbox_config.json");
    await writeFile(configPath, JSON.stringify({ token: EXPECTED_TOKEN }), "utf-8");

    const mockResponse = { ok: true, status: 200 } as Response;
    const fetchMock = vi.fn().mockResolvedValue(mockResponse);
    vi.stubGlobal("fetch", fetchMock);

    await sendHashBoxNotification(
      "article", "News", "📰", "Test", "Body"
    );

    const sentBody = JSON.parse(
      (fetchMock.mock.calls[0] as [string, RequestInit])[1].body as string
    );
    expect(sentBody).not.toHaveProperty("token");
  });
});
