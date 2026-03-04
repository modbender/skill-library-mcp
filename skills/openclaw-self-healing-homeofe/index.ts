import fs from "node:fs";
import path from "node:path";
import os from "node:os";

export function expandHome(p: string): string {
  if (!p) return p;
  if (p === "~") return os.homedir();
  if (p.startsWith("~/")) return path.join(os.homedir(), p.slice(2));
  return p;
}

export type State = {
  limited: Record<string, { lastHitAt: number; nextAvailableAt: number; reason?: string }>;
  pendingBackups?: Record<string, { createdAt: number; reason: string }>; // filePath -> meta
  whatsapp?: {
    lastSeenConnectedAt?: number;
    lastRestartAt?: number;
    disconnectStreak?: number;
  };
  cron?: {
    failCounts?: Record<string, number>; // job id -> consecutive failures
    lastIssueCreatedAt?: Record<string, number>; // job id -> timestamp
  };
  plugins?: {
    lastDisableAt?: Record<string, number>; // plugin id -> timestamp
  };
};

export function nowSec() {
  return Math.floor(Date.now() / 1000);
}

export function loadState(p: string): State {
  try {
    const raw = fs.readFileSync(p, "utf-8");
    const d = JSON.parse(raw);
    if (!d.limited) d.limited = {};
    if (!d.pendingBackups) d.pendingBackups = {};
    if (!d.whatsapp) d.whatsapp = {};
    if (!d.cron) d.cron = {};
    if (!d.cron.failCounts) d.cron.failCounts = {};
    if (!d.cron.lastIssueCreatedAt) d.cron.lastIssueCreatedAt = {};
    if (!d.plugins) d.plugins = {};
    if (!d.plugins.lastDisableAt) d.plugins.lastDisableAt = {};
    return d;
  } catch {
    return { limited: {}, pendingBackups: {}, whatsapp: {}, cron: { failCounts: {}, lastIssueCreatedAt: {} }, plugins: { lastDisableAt: {} } };
  }
}

export function saveState(p: string, s: State) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(s, null, 2));
}

export function isRateLimitLike(err?: string): boolean {
  if (!err) return false;
  const s = err.toLowerCase();
  return s.includes("rate limit") || s.includes("quota") || s.includes("429") || s.includes("resource_exhausted");
}

export function isAuthScopeLike(err?: string): boolean {
  if (!err) return false;
  const s = err.toLowerCase();
  return (
    s.includes("http 401") ||
    s.includes("insufficient permissions") ||
    s.includes("missing scopes") ||
    s.includes("api.responses.write") ||
    s.includes("unauthorized")
  );
}

export function pickFallback(modelOrder: string[], state: State): string {
  const t = nowSec();
  for (const m of modelOrder) {
    const lim = state.limited[m];
    if (!lim) return m;
    if (lim.nextAvailableAt <= t) return m;
  }
  return modelOrder[modelOrder.length - 1];
}

export function patchSessionModel(sessionsFile: string, sessionKey: string, model: string, logger: any): boolean {
  try {
    const raw = fs.readFileSync(sessionsFile, "utf-8");
    const data = JSON.parse(raw);
    if (!data[sessionKey]) return false;
    const prev = data[sessionKey].model;
    data[sessionKey].model = model;
    fs.writeFileSync(sessionsFile, JSON.stringify(data, null, 0));
    logger?.warn?.(`[self-heal] patched session model: ${sessionKey} ${prev} -> ${model}`);
    return true;
  } catch (e: any) {
    logger?.error?.(`[self-heal] failed to patch session model: ${e?.message ?? String(e)}`);
    return false;
  }
}

async function runCmd(api: any, cmd: string, timeoutMs = 15000): Promise<{ ok: boolean; stdout: string; stderr: string; code?: number }> {
  try {
    const res = await api.runtime.system.runCommandWithTimeout({
      command: ["bash", "-lc", cmd],
      timeoutMs,
    });
    return {
      ok: res.exitCode === 0,
      stdout: String(res.stdout ?? ""),
      stderr: String(res.stderr ?? ""),
      code: res.exitCode,
    };
  } catch (e: any) {
    return { ok: false, stdout: "", stderr: e?.message ?? String(e) };
  }
}

export function safeJsonParse<T>(s: string): T | undefined {
  try {
    return JSON.parse(s) as T;
  } catch {
    return undefined;
  }
}

export default function register(api: any) {
  const cfg = (api.pluginConfig ?? {}) as any;
  if (cfg.enabled === false) return;

  const modelOrder: string[] = cfg.modelOrder?.length ? cfg.modelOrder : [
    "anthropic/claude-opus-4-6",
    "openai-codex/gpt-5.2",
    "google-gemini-cli/gemini-2.5-flash",
  ];
  const cooldownMinutes: number = cfg.cooldownMinutes ?? 300;
  const stateFile = expandHome(cfg.stateFile ?? "~/.openclaw/workspace/memory/self-heal-state.json");
  const sessionsFile = expandHome(cfg.sessionsFile ?? "~/.openclaw/agents/main/sessions/sessions.json");
  const configFile = expandHome(cfg.configFile ?? "~/.openclaw/openclaw.json");
  const configBackupsDir = expandHome(cfg.configBackupsDir ?? "~/.openclaw/backups/openclaw.json");

  const autoFix = cfg.autoFix ?? {};
  const patchPins: boolean = autoFix.patchSessionPins !== false;
  const disableFailingCrons: boolean = autoFix.disableFailingCrons === true;
  const disableFailingPlugins: boolean = autoFix.disableFailingPlugins === true;

  const whatsappRestartEnabled: boolean = cfg?.autoFix?.restartWhatsappOnDisconnect !== false;
  const whatsappDisconnectThreshold: number = cfg?.autoFix?.whatsappDisconnectThreshold ?? 2;
  const whatsappMinRestartIntervalSec: number = cfg?.autoFix?.whatsappMinRestartIntervalSec ?? 300;
  const cronFailThreshold: number = cfg?.autoFix?.cronFailThreshold ?? 3;
  const issueCooldownSec: number = cfg?.autoFix?.issueCooldownSec ?? 6 * 3600;
  const pluginDisableCooldownSec: number = cfg?.autoFix?.pluginDisableCooldownSec ?? 3600;

  api.logger?.info?.(`[self-heal] enabled. order=${modelOrder.join(" -> ")}`);

  // If the gateway booted and config is valid, remove any pending backups from previous runs.
  cleanupPendingBackups("startup").catch(() => undefined);

  function isConfigValid(): { ok: boolean; error?: string } {
    try {
      const raw = fs.readFileSync(configFile, "utf-8");
      JSON.parse(raw);
      return { ok: true };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? String(e) };
    }
  }

  function backupConfig(reason: string): string | undefined {
    try {
      fs.mkdirSync(configBackupsDir, { recursive: true });
      const ts = new Date().toISOString().replace(/[:.]/g, "-");
      const out = path.join(configBackupsDir, `openclaw.json.${ts}.bak`);
      fs.copyFileSync(configFile, out);

      // Mark as pending so we can delete it after we have evidence the gateway still boots.
      const st = loadState(stateFile);
      st.pendingBackups = st.pendingBackups || {};
      st.pendingBackups[out] = { createdAt: nowSec(), reason };
      saveState(stateFile, st);

      api.logger?.info?.(`[self-heal] backed up openclaw.json (${reason}) -> ${out} (pending cleanup)`);
      return out;
    } catch (e: any) {
      api.logger?.warn?.(`[self-heal] failed to backup openclaw.json: ${e?.message ?? String(e)}`);
      return undefined;
    }
  }

  async function cleanupPendingBackups(where: string) {
    const v = isConfigValid();
    if (!v.ok) {
      api.logger?.warn?.(`[self-heal] not cleaning backups (${where}): openclaw.json invalid: ${v.error}`);
      return;
    }

    // Best-effort: ensure gateway responds to a status call.
    const gw = await runCmd(api, "openclaw gateway status", 15000);
    if (!gw.ok) {
      api.logger?.warn?.(`[self-heal] not cleaning backups (${where}): gateway status check failed`);
      return;
    }

    const st = loadState(stateFile);
    const pending = st.pendingBackups || {};
    const paths = Object.keys(pending);
    if (paths.length === 0) return;

    let deleted = 0;
    for (const p of paths) {
      try {
        if (fs.existsSync(p)) {
          fs.unlinkSync(p);
          deleted++;
        }
      } catch {
        // keep it in pending if we couldn't delete
        continue;
      }
      delete pending[p];
    }

    st.pendingBackups = pending;
    saveState(stateFile, st);
    api.logger?.info?.(`[self-heal] cleaned ${deleted} pending openclaw.json backups (${where})`);
  }

  // Heal after an LLM failure.
  api.on("agent_end", (event: any, ctx: any) => {
    if (event?.success !== false) return;

    const err = event?.error as string | undefined;
    const rate = isRateLimitLike(err);
    const auth = isAuthScopeLike(err);
    if (!rate && !auth) return;

    const state = loadState(stateFile);
    const hitAt = nowSec();
    const extra = auth ? 12 * 60 : 0;
    const nextAvail = hitAt + (cooldownMinutes + extra) * 60;

    // Best effort: mark the pinned model as limited if we can read it.
    let pinnedModel: string | undefined;
    try {
      const data = JSON.parse(fs.readFileSync(sessionsFile, "utf-8"));
      pinnedModel = ctx?.sessionKey ? data?.[ctx.sessionKey]?.model : undefined;
    } catch {
      pinnedModel = undefined;
    }

    const key = pinnedModel || modelOrder[0];
    state.limited[key] = { lastHitAt: hitAt, nextAvailableAt: nextAvail, reason: err?.slice(0, 160) };
    saveState(stateFile, state);

    const fallback = pickFallback(modelOrder, state);

    if (patchPins && ctx?.sessionKey && fallback && fallback !== pinnedModel) {
      patchSessionModel(sessionsFile, ctx.sessionKey, fallback, api.logger);
    }
  });

  // If the system ever emits a raw rate-limit message, self-heal future turns.
  api.on("message_sent", (event: any, ctx: any) => {
    const content = String(event?.content ?? "");
    if (!content) return;
    if (!isRateLimitLike(content) && !isAuthScopeLike(content)) return;

    const state = loadState(stateFile);
    const hitAt = nowSec();
    state.limited[modelOrder[0]] = {
      lastHitAt: hitAt,
      nextAvailableAt: hitAt + cooldownMinutes * 60,
      reason: "outbound error observed",
    };
    saveState(stateFile, state);

    const fallback = pickFallback(modelOrder, state);
    if (patchPins && ctx?.sessionKey) {
      patchSessionModel(sessionsFile, ctx.sessionKey, fallback, api.logger);
    }
  });

  // Background monitor: WhatsApp disconnects, failing crons, failing plugins.
  api.registerService({
    id: "self-heal-monitor",
    start: async () => {
      let timer: NodeJS.Timeout | undefined;

      const tick = async () => {
        const state = loadState(stateFile);

        // --- WhatsApp disconnect self-heal ---
        if (whatsappRestartEnabled) {
          const st = await runCmd(api, "openclaw channels status --json", 15000);
          if (st.ok) {
            const parsed = safeJsonParse<any>(st.stdout);
            const wa = parsed?.channels?.whatsapp;
            const connected = wa?.status === "connected" || wa?.connected === true;

            if (connected) {
              state.whatsapp!.lastSeenConnectedAt = nowSec();
              state.whatsapp!.disconnectStreak = 0;
            } else {
              state.whatsapp!.disconnectStreak = (state.whatsapp!.disconnectStreak ?? 0) + 1;

              const lastRestartAt = state.whatsapp!.lastRestartAt ?? 0;
              const since = nowSec() - lastRestartAt;
              const shouldRestart =
                state.whatsapp!.disconnectStreak >= whatsappDisconnectThreshold &&
                since >= whatsappMinRestartIntervalSec;

              if (shouldRestart) {
                api.logger?.warn?.(
                  `[self-heal] WhatsApp appears disconnected (streak=${state.whatsapp!.disconnectStreak}). Restarting gateway.`
                );
                // Guardrail: never restart if openclaw.json is invalid
                const v = isConfigValid();
                if (!v.ok) {
                  api.logger?.error?.(`[self-heal] NOT restarting gateway: openclaw.json invalid: ${v.error}`);
                } else {
                  backupConfig("pre-gateway-restart");
                  await runCmd(api, "openclaw gateway restart", 60000);
                  // If we are still alive after restart, attempt cleanup.
                  await cleanupPendingBackups("post-gateway-restart");
                  state.whatsapp!.lastRestartAt = nowSec();
                  state.whatsapp!.disconnectStreak = 0;
                }
              }
            }
          }
        }

        // --- Cron failure self-heal ---
        if (disableFailingCrons) {
          const res = await runCmd(api, "openclaw cron list --json", 15000);
          if (res.ok) {
            const parsed = safeJsonParse<any>(res.stdout);
            const jobs: any[] = parsed?.jobs ?? [];
            for (const job of jobs) {
              const id = job.id;
              const name = job.name;
              const lastStatus = job?.state?.lastStatus;
              const lastError = String(job?.state?.lastError ?? "");

              const isFail = lastStatus === "error";
              const prev = state.cron!.failCounts![id] ?? 0;
              state.cron!.failCounts![id] = isFail ? prev + 1 : 0;

              if (isFail && state.cron!.failCounts![id] >= cronFailThreshold) {
                // Guardrail: do not touch crons if config is invalid
                const v = isConfigValid();
                if (!v.ok) {
                  api.logger?.error?.(`[self-heal] NOT disabling cron: openclaw.json invalid: ${v.error}`);
                } else {
                  // Disable the cron
                  api.logger?.warn?.(`[self-heal] Disabling failing cron ${name} (${id}).`);
                  backupConfig("pre-cron-disable");
                  await runCmd(api, `openclaw cron edit ${id} --disable`, 15000);
                  await cleanupPendingBackups("post-cron-disable");
                }

                // Create issue, but rate limit issue creation
                const lastIssueAt = state.cron!.lastIssueCreatedAt![id] ?? 0;
                if (nowSec() - lastIssueAt >= issueCooldownSec) {
                  const body = [
                    `Cron job failed repeatedly and was disabled by openclaw-self-healing.`,
                    ``,
                    `Name: ${name}`,
                    `ID: ${id}`,
                    `Consecutive failures: ${state.cron!.failCounts![id]}`,
                    `Last error:`,
                    "```",
                    lastError.slice(0, 1200),
                    "```",
                  ].join("\n");

                  // Issue goes to this repo by default
                  await runCmd(
                    api,
                    `gh issue create -R elvatis/openclaw-self-healing-elvatis --title "Cron disabled: ${name}" --body ${JSON.stringify(body)} --label security`,
                    20000
                  );
                  state.cron!.lastIssueCreatedAt![id] = nowSec();
                }

                state.cron!.failCounts![id] = 0;
              }
            }
          }
        }

        // --- Plugin error rollback (disable plugin) ---
        if (disableFailingPlugins) {
          const res = await runCmd(api, "openclaw plugins list", 15000);
          if (res.ok) {
            // Heuristic: look for lines containing 'error' or 'crash'
            const lines = res.stdout.split("\n");
            for (const ln of lines) {
              if (!ln.toLowerCase().includes("error")) continue;
              // No robust parsing available in plain output. Use a conservative approach:
              // if we see our own plugin listed with error, do not disable others.
            }
          }
          // TODO: when openclaw provides plugins list --json, parse and disable any status=error.
        }

        saveState(stateFile, state);
      };

      // tick every 60s
      timer = setInterval(() => {
        tick().catch((e) => api.logger?.error?.(`[self-heal] monitor tick failed: ${e?.message ?? String(e)}`));
      }, 60_000);

      // run once immediately
      tick().catch((e) => api.logger?.error?.(`[self-heal] monitor start tick failed: ${e?.message ?? String(e)}`));

      // store timer for stop
      (api as any).__selfHealTimer = timer;
    },
    stop: async () => {
      const t: NodeJS.Timeout | undefined = (api as any).__selfHealTimer;
      if (t) clearInterval(t);
    },
  });
}
