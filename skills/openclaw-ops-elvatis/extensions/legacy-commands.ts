/**
 * openclaw-ops-elvatis Legacy Commands
 *
 * Commands originally defined inline in index.ts, extracted here to keep
 * the entry point thin and all command logic in extensions/.
 *
 * Commands: /cron, /privacy-scan, /release, /staging-smoke, /handoff, /limits
 */

import fs from "node:fs";
import path from "node:path";
import {
  safeExec,
  runCmd,
  latestFile,
  loadActiveCooldowns,
  formatCooldownLine,
  formatIsoCompact,
  listWorkspacePluginDirs,
} from "../src/utils.js";

export function registerLegacyCommands(
  api: any,
  workspace: string,
  cronDir: string,
  cronScripts: string,
  cronReports: string,
) {
  api.registerCommand({
    name: "cron",
    description: "Show cron dashboard (WhatsApp-friendly)",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => {
      const lines: string[] = [];
      lines.push("Cron dashboard");

      // CRONTAB
      const crontab = safeExec("crontab -l");
      const jobs = crontab
        ? crontab
            .split("\n")
            .map((l) => l.trim())
            .filter((l) => l && !l.startsWith("#"))
        : [];

      lines.push("");
      lines.push(`CRONTAB JOBS (${jobs.length})`);
      if (!jobs.length) {
        lines.push("- (none)");
      } else {
        for (const j of jobs.slice(0, 20)) lines.push(`- ${j}`);
        if (jobs.length > 20) lines.push("- ... (truncated)");
      }

      // SCRIPTS
      lines.push("");
      lines.push("SCRIPTS");
      try {
        const scripts = fs.readdirSync(cronScripts).filter((f) => f.endsWith(".sh")).sort();
        if (!scripts.length) {
          lines.push("- (none)");
        } else {
          for (const s of scripts) {
            const st = fs.statSync(path.join(cronScripts, s));
            const m = formatIsoCompact(st.mtimeMs);
            lines.push(`- ${s} (modified ${m} UTC)`);
          }
        }
      } catch {
        lines.push("- (cron/scripts missing)");
      }

      // REPORTS
      lines.push("");
      lines.push("REPORTS");
      const latestPrivacy = latestFile(cronReports, "github-privacy-scan_");
      if (latestPrivacy) {
        lines.push(`- latest privacy scan: ${latestPrivacy.replace(".txt", "")}`);
        lines.push(`  ${path.join(cronReports, latestPrivacy)}`);
      } else {
        lines.push("- (no privacy scan report yet)");
      }

      // SYSTEMD USER TIMERS (short)
      const timers = safeExec("systemctl --user list-timers --all --no-pager");
      if (timers) {
        const tlines = timers.split("\n").filter(Boolean);
        const head = tlines.slice(0, 1);
        const body = tlines.slice(1).filter((l) => !l.startsWith("-") && l.trim()).slice(0, 2);
        lines.push("");
        lines.push("SYSTEMD (USER) TIMERS (top 2)");
        lines.push("```text");
        for (const l of [...head, ...body]) lines.push(l);
        lines.push("```");
      }

      return { text: lines.join("\n") };
    },
  });

  api.registerCommand({
    name: "privacy-scan",
    description: "Run GitHub privacy scan (safe, report-only)",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => {
      const script = path.join(workspace, "ops", "github-privacy-scan.sh");
      if (!fs.existsSync(script)) {
        return { text: `privacy scan script not found: ${script}` };
      }

      const result = runCmd("bash", [script], 300_000);
      const report = latestFile(cronReports, "github-privacy-scan_");
      const tail = result.out.split("\n").slice(-30).join("\n");

      const lines: string[] = [];
      lines.push("Privacy scan finished.");
      if (report) lines.push(`Report: ${path.join(cronReports, report)}`);
      lines.push("");
      lines.push("```text");
      lines.push(tail.trim() || "(no output)");
      lines.push("```");

      return { text: lines.join("\n") };
    },
  });

  api.registerCommand({
    name: "release",
    description: "Show staging gateway + human GO checklist (QA gate)",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => {
      const p = path.join(workspace, "openclaw-ops-elvatis", "RELEASE.md");
      const lines: string[] = [];
      lines.push("Release / QA");
      lines.push("");
      if (fs.existsSync(p)) {
        const txt = fs.readFileSync(p, "utf-8").trim();
        const out = txt.split("\n").slice(0, 160).join("\n");
        lines.push(out);
        if (txt.split("\n").length > 160) lines.push("\n... (truncated)");
      } else {
        lines.push(`Missing: ${p}`);
      }
      return { text: lines.join("\n") };
    },
  });

  api.registerCommand({
    name: "staging-smoke",
    description: "Run staging smoke tests for all openclaw-* repos (install + restart + status)",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => {
      const reportsDir = path.join(workspace, "cron", "reports");
      fs.mkdirSync(reportsDir, { recursive: true });

      const stamp = new Date().toISOString().slice(0, 16).replace(/[:T]/g, "");
      const reportPath = path.join(reportsDir, `staging-smoke_${stamp}.txt`);

      const repoDirs = listWorkspacePluginDirs(workspace);

      const log: string[] = [];
      log.push(`staging-smoke ${new Date().toISOString()}`);
      log.push(`repos: ${repoDirs.length}`);
      log.push("");

      const outLines: string[] = [];
      outLines.push("Staging smoke");
      outLines.push("");
      outLines.push(`Repos: ${repoDirs.length}`);

      for (const repo of repoDirs) {
        const repoPath = path.join(workspace, repo);
        const rel = `~/.openclaw/workspace/${repo}`;

        const pluginId = repo;
        log.push(`== ${repo} ==`);
        const allow = runCmd(
          "openclaw",
          ["--profile", "staging", "config", "set", "plugins.allow", JSON.stringify([pluginId])],
          60_000,
        );
        log.push(`allowlist: exit ${allow.code}`);
        if (allow.out) log.push(allow.out);
        if (allow.code !== 0) {
          fs.writeFileSync(reportPath, log.join("\n") + "\n", "utf-8");
          return { text: `Staging smoke FAILED on ${repo} (set plugins.allow). Report: ${reportPath}` };
        }

        const step1 = runCmd("openclaw", ["--profile", "staging", "plugins", "install", "-l", repoPath], 300_000);
        log.push(`install: exit ${step1.code}`);
        if (step1.out) log.push(step1.out);
        if (step1.code !== 0) {
          log.push("");
          log.push(`FAIL: ${repo} install`);
          fs.writeFileSync(reportPath, log.join("\n") + "\n", "utf-8");
          return { text: `Staging smoke FAILED on ${repo} (install). Report: ${reportPath}` };
        }

        const step2 = runCmd("openclaw", ["--profile", "staging", "gateway", "restart"], 300_000);
        log.push(`restart: exit ${step2.code}`);
        if (step2.out) log.push(step2.out);
        if (step2.code !== 0) {
          log.push("");
          log.push(`FAIL: ${repo} gateway restart`);
          fs.writeFileSync(reportPath, log.join("\n") + "\n", "utf-8");
          return { text: `Staging smoke FAILED on ${repo} (gateway restart). Report: ${reportPath}` };
        }

        const step3 = runCmd("openclaw", ["--profile", "staging", "status"], 180_000);
        log.push(`status: exit ${step3.code}`);
        if (step3.out) log.push(step3.out);
        if (step3.code !== 0) {
          log.push("");
          log.push(`FAIL: ${repo} status`);
          fs.writeFileSync(reportPath, log.join("\n") + "\n", "utf-8");
          return { text: `Staging smoke FAILED on ${repo} (status). Report: ${reportPath}` };
        }

        outLines.push(`- OK: ${repo} (${rel})`);
        log.push("");
      }

      log.push("DONE");
      fs.writeFileSync(reportPath, log.join("\n") + "\n", "utf-8");

      outLines.push("");
      outLines.push(`Report: ${reportPath}`);
      return { text: outLines.join("\n") };
    },
  });

  api.registerCommand({
    name: "handoff",
    description: "Show latest handoff log entries for openclaw-ops-elvatis",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => {
      const p = path.join(workspace, "openclaw-ops-elvatis", ".ai", "handoff", "LOG.md");
      if (!fs.existsSync(p)) return { text: `Missing: ${p}` };
      const txt = fs.readFileSync(p, "utf-8");
      const tail = txt.split("\n").slice(-40).join("\n").trim();
      const lines: string[] = [];
      lines.push("openclaw-ops-elvatis handoff (tail)");
      lines.push("");
      lines.push("```text");
      lines.push(tail || "(empty)");
      lines.push("```");
      return { text: lines.join("\n") };
    },
  });

  api.registerCommand({
    name: "limits",
    description: "Show model/provider auth expiries and rate-limit cooldowns",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => {
      const out = safeExec("openclaw models status");
      if (!out) return { text: "Limits\n\n✗ Failed to run: openclaw models status" };

      const lines = out.split("\n");

      const pick = (prefix: string) => lines.find((l) => l.startsWith(prefix)) ?? "";
      const defaultModel = pick("Default");
      const fallbacks = pick("Fallbacks");

      const startIdx = lines.findIndex((l) => l.trim() === "OAuth/token status");
      const expiryLines: string[] = [];
      if (startIdx >= 0) {
        for (const l of lines.slice(startIdx + 1)) {
          if (l.trim() && !l.startsWith("-") && !l.startsWith(" ") && !l.startsWith("\t")) break;
          if (!l.trim()) continue;
          if (/^\s*-\s+/.test(l) || /^\s{2,}-\s+/.test(l)) expiryLines.push(l.trim().replace(/^-\s*/, ""));
        }
      }

      const msg: string[] = [];
      msg.push("Limits & Auth");

      msg.push("");
      msg.push("MODELS");
      if (defaultModel) msg.push(`- ${defaultModel}`);
      if (fallbacks) msg.push(`- ${fallbacks}`);
      if (!defaultModel && !fallbacks) msg.push("- (unable to read model config)");

      msg.push("");
      msg.push("AUTH EXPIRY");
      if (expiryLines.length) {
        const now = Date.now();
        for (const line of expiryLines.slice(0, 20)) {
          const daysMatch = line.match(/(\d+)d?\s*remaining/i);
          const dateMatch = line.match(/expires?:?\s*(\d{4}-\d{2}-\d{2})/i);
          let icon = "✓";
          let daysLeft: number | null = null;

          if (daysMatch) {
            daysLeft = parseInt(daysMatch[1]);
          } else if (dateMatch) {
            const expDate = new Date(dateMatch[1]).getTime();
            daysLeft = Math.floor((expDate - now) / 86_400_000);
          }

          if (daysLeft !== null) {
            if (daysLeft <= 0) icon = "✗";
            else if (daysLeft <= 7) icon = "⚠";
          }

          msg.push(`${icon} ${line}`);
        }
      } else {
        msg.push("- (no auth expiry data in CLI output)");
      }

      msg.push("");
      msg.push("COOLDOWNS");
      const active = loadActiveCooldowns(workspace).slice(0, 20);
      if (!active.length) {
        msg.push("✓ None active");
      } else {
        for (const a of active) {
          msg.push(`⚠ ${formatCooldownLine(a)}`);
          if (a.reason) msg.push(`  Reason: ${a.reason}`);
        }
      }

      msg.push("");
      msg.push("Best-effort data from local state and CLI. Per-model quotas not exposed by OpenClaw.");

      return { text: msg.join("\n") };
    },
  });
}
