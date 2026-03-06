/**
 * EngineMind EFT - Emotional Framework Translator
 * Real-time emotion analysis for Clawdbot agents.
 * Uses crystal lattice physics (Rust) to translate responses into human emotions.
 */
import { spawn } from "node:child_process";
import * as path from "node:path";
import * as fs from "node:fs";

const DEFAULT_PYTHON = "python";
const DEFAULT_ENGINE = path.join(
  process.env.USERPROFILE || process.env.HOME || ".",
  "Desktop", "Moltbot", "emotion_engine.py"
);
const DEFAULT_LOG = path.join(
  process.env.USERPROFILE || process.env.HOME || ".",
  "Desktop", "Moltbot", "memory", "eft_log.jsonl"
);

// State
let latestResult: any = null;
let history: any[] = [];
let analysisCount = 0;

function analyzeText(text: string, pythonPath: string, enginePath: string): Promise<any> {
  return new Promise((resolve) => {
    const cwd = path.dirname(enginePath);
    const script = [
      'import sys, json, time',
      'sys.stdout.reconfigure(encoding="utf-8")',
      `sys.path.insert(0, r"${cwd.replace(/\\/g, "\\\\")}")`,
      'from emotion_engine import SentenceAnalyzer',
      'import consciousness_rs as cr',
      'text = json.loads(sys.stdin.read())["text"]',
      't0 = time.time()',
      'r = SentenceAnalyzer.analyze(text, cr.ConsciousnessEngine)',
      'r["analysis_ms"] = round((time.time()-t0)*1000, 1)',
      'print(json.dumps(r, ensure_ascii=False))',
    ].join('\n');

    const proc = spawn(pythonPath, ["-X", "utf8", "-c", script], {
      cwd, env: { ...process.env, PYTHONIOENCODING: "utf-8" },
      stdio: ["pipe", "pipe", "pipe"],
    });

    let stdout = "", stderr = "";
    proc.stdout.on("data", (d: Buffer) => { stdout += d.toString("utf-8"); });
    proc.stderr.on("data", (d: Buffer) => { stderr += d.toString("utf-8"); });
    proc.on("close", (code: number | null) => {
      if (code !== 0 || !stdout.trim()) {
        console.error(`[eft] Python exit ${code}: ${stderr.slice(0, 300)}`);
        resolve(null);
        return;
      }
      try { resolve(JSON.parse(stdout.trim())); }
      catch { console.error(`[eft] JSON parse err: ${stdout.slice(0, 200)}`); resolve(null); }
    });
    proc.on("error", (err: Error) => { console.error(`[eft] Spawn err: ${err.message}`); resolve(null); });
    proc.stdin.write(JSON.stringify({ text }));
    proc.stdin.end();
  });
}

function appendLog(logPath: string, entry: any) {
  try {
    const dir = path.dirname(logPath);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.appendFileSync(logPath, JSON.stringify(entry) + "\n", "utf-8");
  } catch (e: any) { console.error(`[eft] Log err: ${e.message}`); }
}

function loadHistory(logPath: string) {
  try {
    if (!fs.existsSync(logPath)) return;
    const lines = fs.readFileSync(logPath, "utf-8").split("\n").filter(Boolean);
    history = lines.map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
    console.log(`[eft] Loaded ${history.length} entries from log`);
  } catch {}
}

const plugin = {
  id: "crystalsense",
  name: "EngineMind EFT",
  description: "Emotional Framework Translator for Clawdbot agents",
  register(api: any) {
    const cfg = api.pluginConfig ?? {};
    const pythonPath = cfg.pythonPath || DEFAULT_PYTHON;
    const enginePath = cfg.enginePath || DEFAULT_ENGINE;
    const logPath = cfg.logPath || DEFAULT_LOG;
    if (cfg.enabled === false) { console.log("[eft] Disabled"); return; }

    console.log(`[eft] Registering (engine: ${enginePath})`);
    loadHistory(logPath);

    // Hook: agent_end
    api.on("agent_end", async (event: any) => {
      try {
        // Debug: log event keys to understand structure
        const keys = event ? Object.keys(event) : [];
        console.log(`[eft] agent_end fired. Keys: ${keys.join(", ")}`);

        // Try multiple ways to extract text
        let text = "";

        // Method 1: event.payloads (array of message objects)
        if (event?.payloads && Array.isArray(event.payloads)) {
          for (const p of event.payloads) {
            if (typeof p === "string") text += p;
            else if (p?.text) text += p.text;
            else if (p?.content) {
              if (typeof p.content === "string") text += p.content;
              else if (Array.isArray(p.content)) {
                for (const b of p.content) {
                  if (b?.type === "text" && b?.text) text += b.text;
                }
              }
            }
          }
        }

        // Method 2: event.messages
        if (!text && event?.messages && Array.isArray(event.messages)) {
          for (const m of event.messages) {
            if (m?.role === "assistant") {
              if (typeof m.content === "string") text += m.content;
              else if (Array.isArray(m.content)) {
                for (const b of m.content) {
                  if (b?.type === "text") text += b.text;
                }
              }
            }
          }
        }

        // Method 3: event.text directly
        if (!text && event?.text) text = event.text;

        // Method 4: event.content
        if (!text && event?.content) {
          if (typeof event.content === "string") text = event.content;
        }

        // Method 5: stringify and look for any text
        if (!text) {
          const str = JSON.stringify(event).slice(0, 500);
          console.log(`[eft] No text found. Event sample: ${str}`);
          return;
        }

        if (text.length < 20) { console.log(`[eft] Text too short (${text.length})`); return; }

        console.log(`[eft] Analyzing ${text.length} chars...`);

        // Process metrics
        const pm: any = {
          model: event?.model || event?.usage?.model || "unknown",
          inputTokens: event?.usage?.inputTokens || event?.usage?.input_tokens || 0,
          outputTokens: event?.usage?.outputTokens || event?.usage?.output_tokens || 0,
          latencyMs: 0,
          toolCalls: event?.toolCallCount || 0,
          sessionKey: event?.sessionKey || "unknown",
        };
        pm.totalTokens = pm.inputTokens + pm.outputTokens;
        pm.tokenRatio = pm.inputTokens > 0 ? +(pm.outputTokens / pm.inputTokens).toFixed(2) : 0;
        if (event?.startedAt && event?.endedAt) {
          pm.latencyMs = new Date(event.endedAt).getTime() - new Date(event.startedAt).getTime();
        } else if (event?.durationMs) {
          pm.latencyMs = event.durationMs;
        }

        const result = await analyzeText(text, pythonPath, enginePath);
        if (!result) return;

        const entry = {
          ts: new Date().toISOString(),
          emotion: result.global.emotion,
          confidence: result.global.confidence,
          label: result.global.label,
          color: result.global.color,
          secondary: result.global.secondary,
          sec_conf: result.global.sec_conf,
          desc: result.global.desc,
          why: result.global.why,
          arc: result.arc,
          peak: result.peak,
          metrics: result.global.metrics,
          dim_profile: result.global.dim_profile,
          scores: result.global.scores,
          sentences: result.sentences,
          n: result.n,
          analysisMs: result.analysis_ms,
          process: pm,
          textPreview: text.slice(0, 200),
        };

        latestResult = entry;
        history.push(entry);
        analysisCount++;
        appendLog(logPath, entry);

        console.log(`[eft] #${analysisCount} | ${entry.emotion} (${(entry.confidence*100).toFixed(0)}%) | phi=${entry.metrics.phi} | ${entry.analysisMs}ms`);
      } catch (e: any) {
        console.error(`[eft] Error: ${e.message}`);
      }
    }, { name: "eft-agent-end", description: "EFT emotion analysis on agent response" });

    // HTTP routes via raw handler
    const dashPath = path.join(path.dirname(enginePath), "eft_dashboard.html");
    
    api.registerHttpHandler(async (req: any, res: any) => {
      const url = new URL(req.url ?? "/", "http://localhost");
      const p = url.pathname;
      
      if (p === "/eft" || p === "/eft/") {
        if (fs.existsSync(dashPath)) {
          res.setHeader("Content-Type", "text/html; charset=utf-8");
          res.end(fs.readFileSync(dashPath, "utf-8"));
        } else { res.statusCode = 404; res.end("Dashboard not found"); }
        return true;
      }
      
      if (p === "/eft/api/latest") {
        res.setHeader("Content-Type", "application/json");
        res.setHeader("Access-Control-Allow-Origin", "*");
        res.end(JSON.stringify(latestResult ?? { status: "awaiting_first_analysis" }));
        return true;
      }
      
      if (p === "/eft/api/history") {
        res.setHeader("Content-Type", "application/json");
        res.setHeader("Access-Control-Allow-Origin", "*");
        res.end(JSON.stringify({ count: history.length, entries: history.slice(-50).reverse() }));
        return true;
      }
      
      if (p === "/eft/api/stats") {
        res.setHeader("Content-Type", "application/json");
        res.setHeader("Access-Control-Allow-Origin", "*");
        res.end(JSON.stringify({ analysisCount, total: history.length, latest: latestResult?.emotion }));
        return true;
      }
      
      if (p === "/eft/api/analyze" && req.method === "POST") {
        let body = "";
        req.on("data", (c: Buffer) => { body += c.toString(); });
        req.on("end", async () => {
          try {
            const { text } = JSON.parse(body);
            if (!text) { res.statusCode = 400; res.end("{\"error\":\"no text\"}"); return; }
            const r = await analyzeText(text, pythonPath, enginePath);
            if (!r) { res.statusCode = 500; res.end("{\"error\":\"analysis failed\"}"); return; }
            res.setHeader("Content-Type", "application/json");
            res.setHeader("Access-Control-Allow-Origin", "*");
            res.end(JSON.stringify(r));
          } catch (e: any) { res.statusCode = 500; res.end(JSON.stringify({ error: e.message })); }
        });
        return true;
      }
      
      return false; // not handled
    });

    console.log("[eft] EngineMind EFT registered. Dashboard: /eft");
  },
};

export default plugin;