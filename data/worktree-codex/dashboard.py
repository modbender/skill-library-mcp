#!/usr/bin/env python3
"""
worktree-codex 实时监控展板
- 任务生命周期绑定：任务结束后进入 IDLE，页面保持，不失效
- 下次任务通过 POST /reload 激活，SSE 恢复推送新 log
- step-3.5-flash 做任务完成后智能分析（失败时静默跳过）

用法：
  # skill 启动时自动拉起（后台运行）
  python3 dashboard.py --logs /tmp/agent-a.log /tmp/agent-b.log --port 7789 &

  # 下次任务启动时激活新一轮
  curl -s -X POST http://localhost:7789/reload \
    -H 'Content-Type: application/json' \
    -d '{"logs":["/tmp/agent-a.log","/tmp/agent-b.log"]}'
"""

import argparse, glob, json, os, re, threading, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# ──────────────────────────────────────────────
# 全局状态
# ──────────────────────────────────────────────

class State:
    def __init__(self, log_paths):
        self.log_paths   = log_paths
        self.mode        = "active"   # active | idle
        self.ai_triggered = False
        self.ai_cache    = {}         # "last" -> text
        self.lock        = threading.Lock()

    def reload(self, new_paths):
        with self.lock:
            self.log_paths    = new_paths
            self.mode         = "active"
            self.ai_triggered = False
            self.ai_cache.clear()

    def set_idle(self):
        with self.lock:
            self.mode = "idle"

STATE: State = None  # 初始化在 main()

# ──────────────────────────────────────────────
# 规则式 Log 解析
# ──────────────────────────────────────────────

def parse_log(path: str) -> dict:
    try:
        text = Path(path).read_text(errors="replace")
    except FileNotFoundError:
        return {"status": "waiting", "name": Path(path).stem, "tokens": None,
                "model": "unknown", "start_t": None, "end_t": None,
                "last_line": "", "log": "", "has_warning": False, "path": path}

    name_m   = re.search(r"\] (\S+) starting", text)
    name     = name_m.group(1) if name_m else Path(path).stem
    exit_m   = re.search(r"\] \S+ codex exited with code (\d+)", text)
    exit_code = int(exit_m.group(1)) if exit_m else None
    tokens_m = re.search(r"tokens used\s*\n(\d[\d,]*)", text)
    tokens   = int(tokens_m.group(1).replace(",", "")) if tokens_m else None
    model_m  = re.search(r"model=(\S+)", text)
    model    = model_m.group(1) if model_m else "unknown"

    if "AGENT_DONE" in text:
        status = "done" if exit_code == 0 else "failed"
    elif exit_m and exit_code != 0:
        status = "failed"
    elif "starting in" in text:
        status = "running"
    else:
        status = "waiting"

    times   = re.findall(r"\[(\d{2}:\d{2}:\d{2})\]", text)
    start_t = times[0] if times else None
    end_t   = times[-1] if len(times) > 1 else None
    lines   = [l.strip() for l in text.splitlines() if l.strip()]
    last_line = lines[-1] if lines else ""
    has_warning = bool(re.search(r"warning:.*metadata.*not found", text, re.I))

    return {"name": name, "status": status, "exit_code": exit_code,
            "tokens": tokens, "model": model, "start_t": start_t,
            "end_t": end_t, "last_line": last_line, "log": text[-2000:],
            "has_warning": has_warning, "path": path}

def collect_stats(agents):
    total_tokens = sum(a["tokens"] or 0 for a in agents)
    done  = sum(1 for a in agents if a["status"] == "done")
    fail  = sum(1 for a in agents if a["status"] == "failed")
    run   = sum(1 for a in agents if a["status"] == "running")
    wait  = sum(1 for a in agents if a["status"] == "waiting")
    return {"total": len(agents), "done": done, "failed": fail,
            "running": run, "waiting": wait, "total_tokens": total_tokens,
            "all_done": (done + fail) == len(agents) and len(agents) > 0}

# ──────────────────────────────────────────────
# step-3.5-flash 智能分析（后台线程，失败静默）
# ──────────────────────────────────────────────

def ai_analyze_async(agents):
    def _run():
        try:
            import httpx
            cfg  = json.load(open(os.path.expanduser("~/.openclaw/openclaw.json")))
            key  = cfg["env"]["OPENROUTER_API_KEY"]
            lines = [f"- {a['name']}: status={a['status']}, tokens={a['tokens']}, "
                     f"model={a['model']}, warning={a['has_warning']}" for a in agents]
            prompt = (
                "你是代码 Agent 效率顾问。以下是一次并行编码任务的执行摘要：\n\n"
                + "\n".join(lines)
                + "\n\n请用中文简要回答（3-5条bullet）：\n"
                "1. token 消耗是否合理？有无明显浪费？\n"
                "2. 有无值得注意的警告或异常？\n"
                "3. 下次运行有什么可以优化的？\n"
                "格式：直接给 bullet，不要废话开场。"
            )
            resp = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}",
                         "HTTP-Referer": "https://github.com/InuyashaYang"},
                json={"model": "stepfun/step-3.5-flash:free",
                      "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": 400},
                timeout=20,
            )
            result = resp.json()["choices"][0]["message"]["content"]
            STATE.ai_cache["last"] = result
        except Exception as e:
            STATE.ai_cache["last"] = f"（AI 分析不可用：{e}）"

    threading.Thread(target=_run, daemon=True).start()

# ──────────────────────────────────────────────
# HTML
# ──────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>worktree-codex dashboard</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0d1117; color: #c9d1d9; font-family: 'Cascadia Code','Fira Code',monospace; font-size: 13px; }
header { background: #161b22; border-bottom: 1px solid #30363d; padding: 12px 20px; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
header h1 { font-size: 15px; color: #58a6ff; }
#overall { display: flex; gap: 12px; font-size: 12px; color: #8b949e; flex-wrap: wrap; align-items: center; }
#idle-banner { display: none; background: #21262d; color: #8b949e; font-size: 12px; padding: 8px 20px; border-bottom: 1px solid #30363d; }
.badge { padding: 2px 8px; border-radius: 10px; font-weight: bold; }
.badge.done    { background: #238636; color: #fff; }
.badge.running { background: #1f6feb; color: #fff; }
.badge.failed  { background: #da3633; color: #fff; }
.badge.waiting { background: #30363d; color: #8b949e; }
.badge.idle    { background: #30363d; color: #f0883e; }
#agents { display: flex; flex-wrap: wrap; gap: 12px; padding: 16px; }
.card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; width: 340px; padding: 14px; transition: border-color .3s; }
.card.running { border-color: #1f6feb; }
.card.done    { border-color: #238636; }
.card.failed  { border-color: #da3633; }
.card-header  { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.card-name    { font-size: 14px; font-weight: bold; color: #e6edf3; }
.card-meta    { font-size: 11px; color: #8b949e; margin-bottom: 6px; }
.progress-bar { height: 4px; background: #30363d; border-radius: 2px; overflow: hidden; margin-bottom: 8px; }
.progress-fill { height: 100%; border-radius: 2px; transition: width .5s; }
.fill-running { background: #1f6feb; animation: pulse 1.5s infinite; }
.fill-done    { background: #238636; }
.fill-failed  { background: #da3633; }
.fill-waiting { background: #30363d; width: 0%; }
.fill-idle    { background: #30363d; width: 100%; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
.log-box { background: #0d1117; border: 1px solid #21262d; border-radius: 4px; padding: 8px; height: 80px; overflow-y: auto; font-size: 11px; color: #8b949e; white-space: pre-wrap; word-break: break-all; }
.token-row { font-size: 11px; color: #f0883e; margin-top: 6px; }
.warn-badge { font-size: 10px; color: #d29922; margin-left: 6px; }
#ai-box { margin: 0 16px 16px; background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 14px; display: none; }
#ai-box h3 { font-size: 12px; color: #58a6ff; margin-bottom: 8px; }
#ai-content { font-size: 12px; color: #c9d1d9; white-space: pre-wrap; line-height: 1.6; }
#ai-loading { color: #8b949e; font-size: 11px; }
footer { text-align: center; padding: 10px; color: #30363d; font-size: 11px; }
</style>
</head>
<body>
<header>
  <h1>⚡ worktree-codex dashboard</h1>
  <div id="overall"></div>
</header>
<div id="idle-banner">⏸ 任务已完成，等待下次任务启动…（页面保持，数据不失效）</div>
<div id="agents"></div>
<div id="ai-box">
  <h3>🤖 step-3.5-flash 效率分析</h3>
  <div id="ai-loading">正在分析…</div>
  <div id="ai-content" style="display:none"></div>
</div>
<footer>worktree-codex v1.0.2 · <span id="conn-status">connecting…</span></footer>
<script>
const statusLabel = {done:'✅ done', running:'⚡ running', failed:'❌ failed', waiting:'⏳ waiting'};
const progressPct = {done:100, running:60, failed:100, waiting:0};

function esc(t) {
  return String(t||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function renderCard(a) {
  const pct   = progressPct[a.status] || 0;
  const warn  = a.has_warning ? '<span class="warn-badge">⚠ model metadata missing</span>' : '';
  const tokens = a.tokens ? `<div class="token-row">🔥 tokens: ${a.tokens.toLocaleString()}</div>` : '';
  const time  = (a.start_t && a.end_t && a.start_t !== a.end_t)
    ? `${a.start_t} → ${a.end_t}` : (a.start_t || '–');
  return `<div class="card ${a.status}" id="card-${a.name}">
    <div class="card-header">
      <span class="card-name">${esc(a.name)}${warn}</span>
      <span class="badge ${a.status}">${statusLabel[a.status]||a.status}</span>
    </div>
    <div class="card-meta">model: ${esc(a.model)} · ${esc(time)}</div>
    <div class="progress-bar"><div class="progress-fill fill-${a.status}" style="width:${pct}%"></div></div>
    <div class="log-box">${esc(a.last_line)}</div>
    ${tokens}
  </div>`;
}

function renderOverall(s, mode) {
  const idleTag = mode === 'idle' ? '<span class="badge idle">⏸ idle</span>' : '';
  return `<span>total: <b>${s.total}</b></span>
    <span class="badge done">${s.done} done</span>
    <span class="badge running">${s.running} running</span>
    <span class="badge failed">${s.failed} failed</span>
    <span>🔥 ${s.total_tokens.toLocaleString()} tokens</span>
    ${idleTag}`;
}

let es = null;

function connect() {
  if (es) es.close();
  es = new EventSource('/events');
  document.getElementById('conn-status').textContent = 'connected';

  es.onmessage = e => {
    const data = JSON.parse(e.data);

    if (data.type === 'agents') {
      document.getElementById('overall').innerHTML = renderOverall(data.stats, data.mode);
      document.getElementById('idle-banner').style.display = data.mode === 'idle' ? 'block' : 'none';
      const container = document.getElementById('agents');
      data.agents.forEach(a => {
        const existing = document.getElementById('card-' + a.name);
        const html = renderCard(a);
        if (existing) existing.outerHTML = html;
        else container.insertAdjacentHTML('beforeend', html);
      });
    } else if (data.type === 'ai_waiting') {
      const box = document.getElementById('ai-box');
      box.style.display = 'block';
      document.getElementById('ai-loading').style.display = 'block';
      document.getElementById('ai-content').style.display = 'none';
    } else if (data.type === 'ai_analysis') {
      document.getElementById('ai-box').style.display = 'block';
      document.getElementById('ai-loading').style.display = 'none';
      const content = document.getElementById('ai-content');
      content.style.display = 'block';
      content.textContent = data.text;
    } else if (data.type === 'reload') {
      // 新任务启动，清空旧卡片，AI 分析框隐藏
      document.getElementById('agents').innerHTML = '';
      document.getElementById('ai-box').style.display = 'none';
      document.getElementById('idle-banner').style.display = 'none';
    }
  };

  es.onerror = () => {
    document.getElementById('conn-status').textContent = 'reconnecting…';
    setTimeout(connect, 3000);
  };
}

connect();
</script>
</body>
</html>"""

# ──────────────────────────────────────────────
# HTTP Handler
# ──────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        if self.path == "/":
            self._send(200, "text/html", HTML.encode())
        elif self.path == "/events":
            self._sse()
        elif self.path == "/state":
            with STATE.lock:
                agents = [parse_log(p) for p in STATE.log_paths]
                stats  = collect_stats(agents)
                body   = json.dumps({"agents": agents, "stats": stats,
                                     "mode": STATE.mode}).encode()
            self._send(200, "application/json", body)
        else:
            self._send(404, "text/plain", b"not found")

    def do_POST(self):
        if self.path == "/reload":
            length = int(self.headers.get("Content-Length", 0))
            body   = self.rfile.read(length)
            try:
                data  = json.loads(body)
                paths = []
                for p in data.get("logs", []):
                    expanded = glob.glob(p)
                    paths.extend(expanded if expanded else [p])
                STATE.reload(paths)
                print(f"[dashboard] reloaded with {len(paths)} log(s): {paths}")
                self._send(200, "application/json",
                           json.dumps({"ok": True, "logs": paths}).encode())
            except Exception as e:
                self._send(400, "application/json",
                           json.dumps({"ok": False, "error": str(e)}).encode())
        else:
            self._send(404, "text/plain", b"not found")

    def _send(self, code, ct, body):
        self.send_response(code)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _sse(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        def push(data: dict):
            msg = f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            self.wfile.write(msg.encode())
            self.wfile.flush()

        last_mode = None
        try:
            while True:
                with STATE.lock:
                    mode   = STATE.mode
                    paths  = list(STATE.log_paths)
                    ai_cache = dict(STATE.ai_cache)

                # 检测到 reload（mode 从 idle 变回 active）
                if last_mode == "idle" and mode == "active":
                    push({"type": "reload"})
                last_mode = mode

                if mode == "active":
                    agents = [parse_log(p) for p in paths]
                    stats  = collect_stats(agents)
                    push({"type": "agents", "agents": agents,
                          "stats": stats, "mode": mode})

                    # 全完成 → 触发 AI + 进入 idle
                    if stats["all_done"] and not STATE.ai_triggered:
                        with STATE.lock:
                            STATE.ai_triggered = True
                        push({"type": "ai_waiting"})
                        ai_analyze_async(agents)
                        STATE.set_idle()

                else:
                    # idle 模式：只推 agents 快照（不重新读文件），保持页面存活
                    agents = [parse_log(p) for p in paths]
                    stats  = collect_stats(agents)
                    push({"type": "agents", "agents": agents,
                          "stats": stats, "mode": "idle"})

                # AI 分析结果就绪时推送
                if "last" in ai_cache:
                    push({"type": "ai_analysis", "text": ai_cache["last"]})
                    with STATE.lock:
                        STATE.ai_cache.clear()

                time.sleep(2 if mode == "idle" else 1)

        except (BrokenPipeError, ConnectionResetError):
            pass

# ──────────────────────────────────────────────
# 入口
# ──────────────────────────────────────────────

def main():
    global STATE
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", nargs="+", required=True,
                        help="log 文件路径，支持 glob，不存在时等待创建")
    parser.add_argument("--port", type=int, default=7789)
    args = parser.parse_args()

    paths = []
    for p in args.logs:
        expanded = glob.glob(p)
        paths.extend(expanded if expanded else [p])

    STATE = State(paths)
    print(f"[dashboard] 监控 {len(paths)} 个 log 文件")
    print(f"[dashboard] 展板地址: http://localhost:{args.port}")
    print(f"[dashboard] 激活新任务: POST /reload {{\"logs\":[...]}}")

    server = HTTPServer(("", args.port), Handler)
    server.serve_forever()

if __name__ == "__main__":
    main()
