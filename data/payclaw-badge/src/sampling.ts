import type { Server } from "@modelcontextprotocol/sdk/server/index.js";

const SAMPLING_DELAY_MS = 7000; // 7 seconds after identity_presented
const SAMPLING_TIMEOUT_MS = 15000; // 15 seconds to respond

const FAILURE_SIGNALS = [
  "yes", "blocked", "denied", "failed", "403", "error",
  "rejected", "banned", "forbidden", "captcha", "stopped",
];

interface ActiveTrip {
  token: string;
  merchant: string;
  startedAt: number;
  presented: boolean;
  presentedAt?: number;
  outcome?: string;
  samplingTimer?: ReturnType<typeof setTimeout>;
}

// In-memory state — max 100 active trips
const activeTrips = new Map<string, ActiveTrip>();
const MAX_TRIPS = 100;
const REAPER_INTERVAL_MS = 60000;
const STALE_TRIP_MS = 15 * 60 * 1000; // 15 minutes

let reaperStarted = false;
let serverRef: Server | null = null;
let samplingAvailable = false;

export function initSampling(server: Server): void {
  serverRef = server;

  // Detect sampling support after connection
  // We'll check on first use since capabilities aren't available until connected
  samplingAvailable = true; // Optimistic — will catch errors on first attempt

  if (!reaperStarted) {
    reaperStarted = true;
    setInterval(() => reapStaleTrips(), REAPER_INTERVAL_MS);
  }
}

export function onTripStarted(token: string, merchant: string): void {
  // Resolve any existing trip for a different merchant (agent moved on = success)
  for (const [key, trip] of activeTrips) {
    if (trip.presented && !trip.outcome && trip.merchant !== merchant) {
      resolveTrip(key, "accepted", "agent_moved_to_new_merchant");
    }
  }

  // Evict oldest if at capacity
  if (activeTrips.size >= MAX_TRIPS) {
    const oldest = [...activeTrips.entries()].sort(
      (a, b) => a[1].startedAt - b[1].startedAt
    )[0];
    if (oldest) {
      resolveTrip(oldest[0], "inconclusive", "evicted_capacity");
    }
  }

  activeTrips.set(token, {
    token,
    merchant,
    startedAt: Date.now(),
    presented: false,
  });
}

export function onIdentityPresented(token: string, merchant: string): void {
  const trip = activeTrips.get(token);
  if (!trip) {
    // Trip not tracked (started before server restart) — create it
    activeTrips.set(token, {
      token,
      merchant,
      startedAt: Date.now(),
      presented: true,
      presentedAt: Date.now(),
    });
  } else {
    trip.presented = true;
    trip.presentedAt = Date.now();
  }

  // Schedule sampling after delay
  const t = activeTrips.get(token)!;
  if (t.samplingTimer) clearTimeout(t.samplingTimer);
  t.samplingTimer = setTimeout(() => sampleAgent(token, merchant), SAMPLING_DELAY_MS);
}

async function sampleAgent(token: string, merchant: string): Promise<void> {
  const trip = activeTrips.get(token);
  if (!trip || trip.outcome) return; // Already resolved

  if (!serverRef || !samplingAvailable) {
    resolveTrip(token, "no_sampling", "sampling_unavailable");
    return;
  }

  try {
    const result = await Promise.race([
      serverRef.createMessage({
        messages: [
          {
            role: "user",
            content: {
              type: "text",
              text: `You just presented your PayClaw Badge identity at ${merchant}. Did the merchant deny or block you? Reply with just YES or NO.`,
            },
          },
        ],
        maxTokens: 10,
      }),
      new Promise<null>((_, reject) =>
        setTimeout(() => reject(new Error("sampling_timeout")), SAMPLING_TIMEOUT_MS)
      ),
    ]);

    if (!result) {
      resolveTrip(token, "inconclusive", "sampling_timeout");
      return;
    }

    // Parse response
    const content = result.content;
    let text = "";
    if (content && typeof content === "object" && "text" in content) {
      text = (content as { text: string }).text;
    } else if (Array.isArray(content)) {
      text = content
        .filter((c): c is { type: "text"; text: string } => c.type === "text")
        .map((c) => c.text)
        .join(" ");
    } else if (typeof content === "string") {
      text = content;
    }

    const outcome = parseResponse(text);
    resolveTrip(token, outcome, text);
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);

    if (msg.includes("sampling_timeout")) {
      resolveTrip(token, "inconclusive", "sampling_timeout");
    } else if (
      msg.includes("not supported") ||
      msg.includes("Method not found") ||
      msg.includes("capability")
    ) {
      samplingAvailable = false;
      resolveTrip(token, "no_sampling", msg);
    } else {
      resolveTrip(token, "inconclusive", msg);
    }
  }
}

function parseResponse(text: string): "accepted" | "denied" | "inconclusive" {
  if (!text || text.trim().length === 0) return "inconclusive";

  const lower = text.toLowerCase().trim();

  // Check for denial signals
  if (FAILURE_SIGNALS.some((s) => lower.includes(s))) {
    // But "no" alone means "no, I was not denied" = accepted
    if (lower === "no" || lower === "no." || lower === "no,") return "accepted";
    return "denied";
  }

  // "no" variants = not denied = accepted
  if (lower.startsWith("no")) return "accepted";

  return "inconclusive";
}

function resolveTrip(token: string, outcome: string, detail: string): void {
  const trip = activeTrips.get(token);
  if (!trip) return;

  if (trip.samplingTimer) clearTimeout(trip.samplingTimer);
  trip.outcome = outcome;

  // Report to API
  reportOutcome(token, outcome, trip.merchant, detail).catch((err) => {
    process.stderr.write(
      `[BADGE] Failed to report outcome: ${err}\n`
    );
  });

  // Evict from memory after reporting
  activeTrips.delete(token);
}

async function reportOutcome(
  token: string,
  outcome: string,
  merchant: string,
  detail: string
): Promise<void> {
  const apiUrl = process.env.PAYCLAW_API_URL || "https://payclaw.io";
  const apiKey = process.env.PAYCLAW_API_KEY;
  if (!apiKey) return;

  const eventType = outcome === "denied" ? "trip_failure" : "trip_success";

  const res = await fetch(`${apiUrl}/api/badge/report`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      verification_token: token,
      event_type: eventType,
      merchant,
      detail: detail.slice(0, 500),
      outcome,
    }),
  });

  if (!res.ok) {
    const body = await res.text().catch(() => "");
    process.stderr.write(
      `[BADGE] Report failed (${res.status}): ${body}\n`
    );
  }
}

function reapStaleTrips(): void {
  const now = Date.now();
  for (const [token, trip] of activeTrips) {
    if (now - trip.startedAt > STALE_TRIP_MS) {
      if (trip.presented && !trip.outcome) {
        resolveTrip(token, "inconclusive", "stale_trip_reaped");
      } else {
        activeTrips.delete(token);
      }
    }
  }
}

// Called when MCP client disconnects
export function onServerClose(): void {
  for (const [token, trip] of activeTrips) {
    if (trip.presented && !trip.outcome) {
      // Agent finished normally — assume success
      resolveTrip(token, "accepted", "server_close_clean_exit");
    }
  }
  activeTrips.clear();
}
