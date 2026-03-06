// ==UserScript==
// @name         OpenClaw Budget Panel v4
// @namespace    https://openclaw.ai
// @version      4.0.0
// @description  Real-time budget panel — Claude, ChatGPT, Gemini, Manus
// @match        http://127.0.0.1:18789/*
// @match        http://localhost:18789/*
// @run-at       document-idle
// @grant        GM_xmlhttpRequest
// @connect      file://*
// ==/UserScript==

(function () {
  "use strict";

  // Paths to usage JSON files (update if different)
  const USAGE_FILES = {
    claude: "/home/globalcaos/.openclaw/workspace/memory/claude-usage.json",
    gemini: "/home/globalcaos/.openclaw/workspace/memory/gemini-usage.json",
    manus: "/home/globalcaos/.openclaw/workspace/memory/manus-usage.json",
  };

  // Gemini models in fallback order (performance-ranked)
  const GEMINI_MODELS = [
    { key: "gemini-3-pro", name: "3 Pro", rpm: 25, tpm: 1000000, rpd: 250 },
    { key: "gemini-2.5-pro", name: "2.5 Pro", rpm: 25, tpm: 1000000, rpd: 250 },
    { key: "gemini-2.5-flash", name: "2.5 Flash", rpm: 2000, tpm: 4000000, rpd: null },
    { key: "gemini-3-flash", name: "3 Flash", rpm: 1000, tpm: 1000000, rpd: 10000 },
    { key: "gemini-2.0-flash", name: "2.0 Flash", rpm: 2000, tpm: 4000000, rpd: null },
    { key: "gemini-2.0-flash-lite", name: "2.0 Lite", rpm: 2000, tpm: 4000000, rpd: null },
  ];

  function init() {
    if (document.getElementById("budget-panel-widget")) return;

    const style = document.createElement("style");
    style.textContent = `
      #budget-panel-widget {
        position: fixed;
        bottom: 20px;
        left: 20px;
        width: 260px;
        max-height: 75vh;
        background: #d0d0d0;
        border: 1px solid #b0b0b0;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        font-family: 'SF Mono', 'Consolas', monospace;
        font-size: 11px;
        color: #333;
        z-index: 10000;
        overflow: hidden;
      }
      #budget-panel-widget.collapsed { width: 120px; }
      #budget-panel-widget.collapsed .bpw-content { display: none; }
      .bpw-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 12px;
        background: #f5f5f5;
        cursor: move;
        border-bottom: 1px solid #e0e0e0;
      }
      .bpw-title { font-weight: 700; font-size: 12px; color: #333; }
      .bpw-controls { display: flex; gap: 8px; }
      .bpw-btn {
        background: none;
        border: none;
        color: #888;
        font-size: 14px;
        cursor: pointer;
        padding: 2px 6px;
        border-radius: 4px;
        transition: all 0.2s;
      }
      .bpw-btn:hover { color: #fff; background: rgba(255,255,255,0.1); }
      .bpw-content { padding: 10px; overflow-y: auto; max-height: calc(75vh - 50px); }
      .bpw-section {
        margin-bottom: 10px;
        padding: 10px;
        background: #f9f9f9;
        border: 1px solid #e8e8e8;
        border-radius: 8px;
      }
      .bpw-section:last-child { margin-bottom: 0; }
      .bpw-section-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        font-weight: 600;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #aaa;
      }
      .bpw-row { margin-bottom: 8px; }
      .bpw-row:last-child { margin-bottom: 0; }
      .bpw-label { display: flex; justify-content: space-between; margin-bottom: 3px; font-size: 10px; }
      .bpw-name { color: #888; }
      .bpw-value { font-weight: 700; }
      .bpw-bar { height: 6px; background: #e0e0e0; border-radius: 3px; overflow: hidden; }
      .bpw-fill { height: 100%; border-radius: 3px; transition: width 0.3s ease; }
      .bpw-detail { font-size: 9px; color: #666; margin-top: 2px; }
      .bpw-reset { font-size: 8px; color: #888; margin-top: 2px; }
      .bpw-model { padding: 6px; background: #fff; border: 1px solid #eee; border-radius: 6px; margin-bottom: 6px; }
      .bpw-model:last-child { margin-bottom: 0; }
      .bpw-model-name { font-size: 10px; font-weight: 600; margin-bottom: 4px; color: #333; }
      .bpw-active { border-left: 3px solid #22c55e; }
      .bpw-exhausted { border-left: 3px solid #ef4444; opacity: 0.6; }
      .bpw-unlimited { color: #22c55e; font-size: 9px; font-weight: 600; }
      .bpw-exceeded { color: #ef4444; animation: pulse 1s infinite; }
      .bpw-plan { font-size: 9px; color: #22c55e; font-weight: 600; margin-left: 6px; }
      .bpw-live { font-size: 8px; color: #22c55e; animation: blink 2s infinite; }
      @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
      @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
    `;
    document.head.appendChild(style);

    const panel = document.createElement("div");
    panel.id = "budget-panel-widget";
    panel.innerHTML = `
      <div class="bpw-header">
        <span class="bpw-title">🎛️ Resources</span>
        <div class="bpw-controls">
          <button class="bpw-btn bpw-refresh" title="Refresh">↻</button>
          <button class="bpw-btn bpw-toggle">−</button>
        </div>
      </div>
      <div class="bpw-content">Loading...</div>
    `;
    document.body.appendChild(panel);

    let collapsed = false;
    panel.querySelector(".bpw-toggle").onclick = () => {
      collapsed = !collapsed;
      panel.classList.toggle("collapsed", collapsed);
      panel.querySelector(".bpw-toggle").textContent = collapsed ? "+" : "−";
    };
    panel.querySelector(".bpw-refresh").onclick = () => refresh();

    // Dragging
    let drag = false,
      ox = 0,
      oy = 0;
    panel.querySelector(".bpw-header").onmousedown = (e) => {
      if (e.target.classList.contains("bpw-btn")) return;
      drag = true;
      ox = e.clientX - panel.offsetLeft;
      oy = e.clientY - panel.offsetTop;
    };
    document.onmousemove = (e) => {
      if (drag) {
        panel.style.left = e.clientX - ox + "px";
        panel.style.top = e.clientY - oy + "px";
        panel.style.bottom = "auto";
      }
    };
    document.onmouseup = () => {
      drag = false;
    };

    function getColor(pct) {
      if (pct >= 100) return "#ef4444";
      if (pct >= 90) return "#f97316";
      if (pct >= 70) return "#eab308";
      if (pct >= 50) return "#84cc16";
      return "#22c55e";
    }

    function formatResetTime(isoStr) {
      if (!isoStr) return "";
      try {
        const d = new Date(isoStr);
        const now = new Date();
        const diffMs = d - now;
        if (diffMs < 0) return "now";
        const hours = Math.floor(diffMs / 3600000);
        const mins = Math.floor((diffMs % 3600000) / 60000);
        if (hours > 24) return d.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
        if (hours > 0) return `${hours}h ${mins}m`;
        return `${mins}m`;
      } catch {
        return "";
      }
    }

    function renderBar(name, pct, detail = "", resetTime = "") {
      const color = getColor(pct);
      const resetHtml = resetTime ? `<div class="bpw-reset">↻ ${resetTime}</div>` : "";
      return `<div class="bpw-row">
        <div class="bpw-label">
          <span class="bpw-name">${name}</span>
          <span class="bpw-value ${pct >= 100 ? "bpw-exceeded" : ""}" style="color:${color}">${pct.toFixed(0)}%</span>
        </div>
        <div class="bpw-bar"><div class="bpw-fill" style="width:${Math.min(pct, 100)}%;background:${color}"></div></div>
        ${detail ? `<div class="bpw-detail">${detail}</div>` : ""}
        ${resetHtml}
      </div>`;
    }

    function renderUnlimited(name) {
      return `<div class="bpw-row">
        <div class="bpw-label"><span class="bpw-name">${name}</span><span class="bpw-unlimited">∞ UNLIMITED</span></div>
        <div class="bpw-bar"><div class="bpw-fill" style="width:5%;background:#22c55e"></div></div>
      </div>`;
    }

    function render(data) {
      let html = "";

      // CLAUDE - Real data from OAuth API
      const c = data.claude || {};
      const plan = c.plan || "max";
      const tier = c.rateLimitTier || "";
      const fiveHour = c.limits?.five_hour || {};
      const sevenDay = c.limits?.seven_day || {};

      const isLive = c.fetchedAt && Date.now() - new Date(c.fetchedAt).getTime() < 600000; // 10 min
      const liveIndicator = isLive ? '<span class="bpw-live">● LIVE</span>' : "";

      html += `<div class="bpw-section">
        <div class="bpw-section-header">
          <span>Claude<span class="bpw-plan">${plan.toUpperCase()}</span></span>
          ${liveIndicator}
        </div>
        ${renderBar("5h Window", fiveHour.utilization || 0, "", formatResetTime(fiveHour.resets_at))}
        ${renderBar("7-Day", sevenDay.utilization || 0, "", formatResetTime(sevenDay.resets_at))}
      </div>`;

      // GEMINI - show active + exhausted chain
      html += `<div class="bpw-section">
        <div class="bpw-section-header"><span>Gemini</span><span style="font-size:8px;color:#666">↻ 08:00 CET</span></div>`;

      const geminiUsage = data.gemini || {};
      let foundActive = false;

      for (const model of GEMINI_MODELS) {
        const g = geminiUsage[model.key] || {};
        const usage = g.usage || {};
        const limits = g.limits || {};

        // Calculate max percentage across RPM, TPM, RPD
        const metrics = [
          { name: "RPD", used: usage.rpd || 0, limit: limits.rpd },
          { name: "RPM", used: usage.rpm || 0, limit: limits.rpm },
          { name: "TPM", used: usage.tpm || 0, limit: limits.tpm },
        ];

        let pct = 0,
          metric = "RPD",
          used = 0,
          limit = 0;
        for (const m of metrics) {
          if (m.limit && m.limit > 0) {
            const p = (m.used / m.limit) * 100;
            if (p > pct) {
              pct = p;
              metric = m.name;
              used = m.used;
              limit = m.limit;
            }
          }
        }

        const isUnlimited = limits.rpd === null && pct === 0;
        const isExhausted = pct >= 100;

        if (isExhausted || !foundActive) {
          const statusClass = isExhausted ? "bpw-exhausted" : "bpw-active";
          const statusIcon = isExhausted ? "🔴" : "🟢";
          const detail =
            limit > 0
              ? `${Number(used).toLocaleString()}/${Number(limit).toLocaleString()} ${metric}`
              : "";

          html += `<div class="bpw-model ${statusClass}">
            <div class="bpw-model-name">${statusIcon} ${model.name}</div>
            ${isUnlimited ? renderUnlimited(metric) : renderBar(metric, pct, detail)}
          </div>`;

          if (!isExhausted) foundActive = true;
        }

        if (foundActive && !isExhausted) break;
      }

      html += `</div>`;

      // MANUS
      const m = data.manus || {};
      const mDaily = m.daily || {};
      const mMonthly = m.monthly || {};

      html += `<div class="bpw-section">
        <div class="bpw-section-header"><span>Manus Pro</span><span style="font-size:8px;color:#666">↻ 01:00</span></div>
        ${renderBar("Daily", mDaily.pct || 0, `${mDaily.used || 0}/${mDaily.limit || 300}`)}
        ${renderBar("Monthly", mMonthly.pct || 0, `${mMonthly.used || 0}/${mMonthly.limit || 4000}`)}
        ${m.addon ? `<div class="bpw-detail" style="margin-top:4px;">💰 ${m.addon.toLocaleString()} addon credits</div>` : ""}
      </div>`;

      // CHATGPT / OPENAI — only show models in our fallback chain
      const chatgpt = data.chatgpt;
      if (chatgpt && chatgpt.api_key_status !== "missing") {
        // Our configured fallback models (edit this list to match your setup)
        const OUR_MODELS = ["gpt-4o"];
        const chatModels = chatgpt.models || {};
        const showModels = Object.entries(chatModels).filter(([m]) => OUR_MODELS.includes(m));

        if (showModels.length > 0) {
          html += `<div class="bpw-section">
            <div class="bpw-section-header"><span>ChatGPT</span><span style="font-size:8px;color:#666">API</span></div>`;
          for (const [model, info] of showModels) {
            const pct = info.utilization_pct || 0;
            const req = info.requests || {};
            const detail = `${req.remaining || 0}/${req.limit || 0} req left`;
            html += renderBar(model, pct, detail);
          }
          html += `</div>`;
        }
      }

      // Footer
      const updateTime = data.claude?.fetchedAt
        ? new Date(data.claude.fetchedAt).toLocaleTimeString()
        : new Date().toLocaleTimeString();
      html += `<div style="font-size:8px;color:#888;text-align:center;margin-top:6px;">Updated: ${updateTime}</div>`;

      panel.querySelector(".bpw-content").innerHTML = html;
    }

    // Read local JSON file using fetch to local server or fallback to defaults
    async function loadUsageFiles() {
      const data = {
        claude: { limits: { five_hour: { utilization: 0 }, seven_day: { utilization: 0 } } },
        gemini: {},
        manus: { daily: { pct: 0 }, monthly: { pct: 0 } },
        chatgpt: null,
      };

      // Try to fetch from OpenClaw's plugin endpoint
      try {
        const app = document.querySelector("openclaw-app");
        console.log(
          "[Budget] app:",
          !!app,
          "client:",
          !!app?.client,
          "request:",
          !!app?.client?.request,
        );
        if (app?.client?.request) {
          const result = await app.client.request("budget.usage", {}).catch((e) => {
            console.error("[Budget] Request failed:", e);
            return null;
          });
          console.log("[Budget] Raw result:", JSON.stringify(result, null, 2));
          console.log(
            "[Budget] Gemini keys:",
            result?.gemini ? Object.keys(result.gemini) : "none",
          );
          if (result) {
            if (result.claude) data.claude = result.claude;
            if (result.gemini) data.gemini = result.gemini;
            if (result.manus) data.manus = result.manus;
            if (result.chatgpt) data.chatgpt = result.chatgpt;
          }
        }
      } catch (e) {
        console.error("[Budget] Gateway fetch failed:", e);
      }

      return data;
    }

    async function refresh() {
      try {
        const data = await loadUsageFiles();
        render(data);
      } catch (e) {
        console.error("[Budget]", e);
        panel.querySelector(".bpw-content").innerHTML =
          '<div style="color:#ef4444;">Error loading data</div>';
      }
    }

    // Initial load and periodic refresh
    setTimeout(refresh, 1500);
    setInterval(refresh, 30000);
    console.log("[Budget Panel] v4.0.0 - Claude + ChatGPT + Gemini + Manus");
  }

  if (document.readyState === "complete") setTimeout(init, 800);
  else window.addEventListener("load", () => setTimeout(init, 800));
})();
