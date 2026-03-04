#!/usr/bin/env node
const { writeFileSync } = require("fs");
/**
 * browser.js — Lightweight CDP browser control for AI agents.
 *
 * Connects to the OpenClaw managed browser (or any Chrome with --remote-debugging-port)
 * and exposes minimal, indexed commands that burn almost no tokens.
 *
 * Usage:
 *   node browser.js <command> [args...]
 *
 * Commands:
 *   tabs                    List open tabs (index + title + url)
 *   open <url>              Navigate current tab (or first tab) to URL
 *   tab <index>             Switch active tab by index
 *   newtab [url]            Open a new tab (optionally with URL)
 *   close [index]           Close tab by index (default: current)
 *   elements [selector]     List interactive elements as numbered index
 *   click <index>           Click element by index
 *   type <index> <text>     Type text into element by index
 *   text [selector]         Extract visible text (compact)
 *   html [selector]         Get outerHTML of element (by CSS selector)
 *   eval <js>               Evaluate JS in page context
 *   screenshot [path]       Save screenshot to file
 *   wait <ms>               Wait for ms (useful in scripts)
 *   scroll <dir> [amount]   Scroll up/down/top/bottom
 *   url                     Print current URL
 *   back                    Go back
 *   forward                 Go forward
 *   refresh                 Reload page
 *
 * Env:
 *   CDP_URL   Override CDP endpoint (default: http://127.0.0.1:18800)
 */

const WebSocket = require("ws");

const CDP_URL = process.env.CDP_URL || "http://127.0.0.1:18800";

// ── Helpers ──

async function cdpFetch(path) {
  const res = await fetch(`${CDP_URL}${path}`);
  return res.json();
}

async function getTargets() {
  return cdpFetch("/json/list");
}

async function getWsUrl() {
  const ver = await cdpFetch("/json/version");
  return ver.webSocketDebuggerUrl?.replace(/^ws:\/\/[^/]+/, `ws://127.0.0.1:${new URL(CDP_URL).port}`);
}

// ── CDP WebSocket session ──

class CDPSession {
  constructor(ws) {
    this.ws = ws;
    this.id = 1;
    this.pending = new Map();
    ws.on("message", (data) => {
      const msg = JSON.parse(data.toString());
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(msg.error.message));
        else resolve(msg.result);
      }
    });
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = this.id++;
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  close() {
    this.ws.close();
  }
}

async function connectToTarget(targetId) {
  const port = new URL(CDP_URL).port;
  const wsUrl = `ws://127.0.0.1:${port}/devtools/page/${targetId}`;
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    ws.once("open", () => resolve(new CDPSession(ws)));
    ws.once("error", reject);
  });
}

async function connectToBrowser() {
  const wsUrl = await getWsUrl();
  if (!wsUrl) throw new Error("Cannot get browser WebSocket URL");
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    ws.once("open", () => resolve(new CDPSession(ws)));
    ws.once("error", reject);
  });
}

// Get the "current" page target (first visible page tab)
async function getCurrentTarget() {
  const targets = await getTargets();
  const pages = targets.filter(t => t.type === "page");
  if (pages.length === 0) throw new Error("No page tabs open");
  return pages[0];
}

async function getTargetByIndex(index) {
  const targets = await getTargets();
  const pages = targets.filter(t => t.type === "page");
  if (index < 0 || index >= pages.length) throw new Error(`Tab index ${index} out of range (0-${pages.length - 1})`);
  return pages[index];
}

// ── Commands ──

async function cmdTabs() {
  const targets = await getTargets();
  const pages = targets.filter(t => t.type === "page");
  if (pages.length === 0) return "No tabs open.";
  return pages.map((t, i) => `[${i}] ${t.title || "(untitled)"} — ${t.url}`).join("\n");
}

async function cmdOpen(url) {
  if (!url) return "Usage: open <url>";
  if (!url.startsWith("http")) url = "https://" + url;
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    await cdp.send("Page.navigate", { url });
    // Wait for load
    await cdp.send("Page.enable");
    await new Promise((resolve) => {
      const timeout = setTimeout(resolve, 10000);
      cdp.ws.on("message", (data) => {
        const msg = JSON.parse(data.toString());
        if (msg.method === "Page.loadEventFired") {
          clearTimeout(timeout);
          resolve();
        }
      });
    });
    return `Navigated to ${url}`;
  } finally {
    cdp.close();
  }
}

async function cmdTab(index) {
  const target = await getTargetByIndex(parseInt(index));
  const cdp = await connectToTarget(target.id);
  try {
    await cdp.send("Page.bringToFront");
    return `Switched to tab [${index}]: ${target.title} — ${target.url}`;
  } finally {
    cdp.close();
  }
}

async function cmdNewTab(url) {
  const browser = await connectToBrowser();
  try {
    const result = await browser.send("Target.createTarget", {
      url: url || "about:blank"
    });
    return `Opened new tab: ${result.targetId}`;
  } finally {
    browser.close();
  }
}

async function cmdClose(index) {
  const target = index !== undefined
    ? await getTargetByIndex(parseInt(index))
    : await getCurrentTarget();
  const browser = await connectToBrowser();
  try {
    await browser.send("Target.closeTarget", { targetId: target.id });
    return `Closed tab: ${target.title}`;
  } finally {
    browser.close();
  }
}

// Generate the JS expression that indexes interactive elements
function ELEMENTS_JS(selector) {
  return `
    (() => {
      // ── Deep shadow DOM helpers ──
      function deepClearStamps(root) {
        root.querySelectorAll('[data-bjs-idx]').forEach(el => el.removeAttribute('data-bjs-idx'));
        root.querySelectorAll('*').forEach(el => {
          if (el.shadowRoot) deepClearStamps(el.shadowRoot);
        });
      }

      function deepQueryAll(root, selectors) {
        const results = [];
        try { results.push(...root.querySelectorAll(selectors)); } catch(e) {}
        const allEls = root.querySelectorAll('*');
        for (const el of allEls) {
          if (el.shadowRoot) {
            results.push(...deepQueryAll(el.shadowRoot, selectors));
          }
        }
        return results;
      }

      function deepQueryStamp(root, idx) {
        const found = root.querySelector('[data-bjs-idx="' + idx + '"]');
        if (found) return found;
        const allEls = root.querySelectorAll('*');
        for (const el of allEls) {
          if (el.shadowRoot) {
            const deep = deepQueryStamp(el.shadowRoot, idx);
            if (deep) return deep;
          }
        }
        return null;
      }

      // Expose deepQueryStamp globally for click/type/etc
      window.__bjsDeepQuery = (idx) => deepQueryStamp(document, idx);

      // Clear old stamps first (including inside shadow DOMs)
      deepClearStamps(document);

      const sel = ${JSON.stringify(selector)};
      const root = sel ? document.querySelector(sel) : document;
      if (!root) return JSON.stringify({ error: "Selector not found: " + sel });

      const interactive = deepQueryAll(root,
        'a[href], button, input, select, textarea, [role="button"], [role="link"], ' +
        '[role="tab"], [role="menuitem"], [role="checkbox"], [role="radio"], ' +
        '[role="textbox"], [onclick], [tabindex]:not([tabindex="-1"]), details > summary, ' +
        '[contenteditable="true"]'
      );

      // Detect topmost modal/dialog to scope de-duplication
      // Prefer role=dialog over role=presentation (presentation is often an empty overlay)
      const allDialogs = [...document.querySelectorAll('[role=dialog], [role=presentation], [aria-modal=true]')]
        .filter(d => d.offsetParent !== null || getComputedStyle(d).position === 'fixed');
      const realDialogs = allDialogs.filter(d => d.getAttribute('role') === 'dialog' || d.getAttribute('aria-modal') === 'true');
      const topDialog = (realDialogs.length > 0 ? realDialogs[realDialogs.length - 1] : allDialogs[allDialogs.length - 1]) || null;

      const seen = new Set();
      const results = [];

      // Sort: elements inside the top dialog come first (higher priority)
      const sorted = [...interactive].sort((a, b) => {
        const aInDialog = topDialog && topDialog.contains(a) ? 0 : 1;
        const bInDialog = topDialog && topDialog.contains(b) ? 0 : 1;
        return aInDialog - bInDialog;
      });

      for (const el of sorted) {
        if (el.offsetParent === null && el.tagName !== 'BODY' && getComputedStyle(el).position !== 'fixed') continue;

        const isDisabled = el.disabled || el.getAttribute('aria-disabled') === 'true';

        const tag = el.tagName.toLowerCase();
        const type = el.type || '';
        const role = el.getAttribute('role') || '';
        const text = (el.textContent || '').trim().slice(0, 80).replace(/\\s+/g, ' ');
        const ariaLabel = el.getAttribute('aria-label') || '';
        const placeholder = el.placeholder || '';
        const href = el.href || '';
        const name = el.name || '';
        const value = (tag === 'input' || tag === 'select' || tag === 'textarea')
          ? (el.value || '').slice(0, 40) : '';

        let label = '';
        if (tag === 'a') label = 'link';
        else if (tag === 'button' || role === 'button') label = 'button';
        else if (tag === 'input') label = type ? 'input:' + type : 'input';
        else if (tag === 'select') label = 'select';
        else if (tag === 'textarea') label = 'textarea';
        else if (role === 'textbox') label = 'textbox';
        else if (role) label = role;
        else label = tag;
        if (isDisabled) label += ':disabled';

        let desc = ariaLabel || text || placeholder || name || '';
        if (value && !desc.includes(value)) desc += desc ? ' [' + value + ']' : value;
        if (tag === 'a' && href && !href.startsWith('javascript:')) {
          const short = href.length > 60 ? href.slice(0, 57) + '...' : href;
          desc += desc ? ' → ' + short : short;
        }

        // De-dup key includes dialog scope — same label in modal vs page are different
        const scope = (topDialog && topDialog.contains(el)) ? 'modal' : 'page';
        const key = scope + '|' + label + '|' + desc;
        if (seen.has(key)) continue;
        seen.add(key);

        el.setAttribute('data-bjs-idx', results.length);
        results.push({ label, desc: desc.slice(0, 120) });
      }

      return JSON.stringify(results);
    })()
  `;
}

async function cmdElements(selector) {
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    await cdp.send("DOM.enable");
    await cdp.send("Runtime.enable");

    const { result } = await cdp.send("Runtime.evaluate", {
      expression: ELEMENTS_JS(selector || null),
      returnByValue: true
    });

    const elements = JSON.parse(result.value);
    if (elements.error) return elements.error;
    if (elements.length === 0) return "No interactive elements found.";

    return elements.map((e, i) =>
      `[${i}] (${e.label}) ${e.desc}`
    ).join("\n");
  } finally {
    cdp.close();
  }
}

// Ensure elements are indexed; returns true if re-indexed
async function ensureIndexed(cdp) {
  const { result } = await cdp.send("Runtime.evaluate", {
    expression: `!!(document.querySelector('[data-bjs-idx]') || (window.__bjsDeepQuery && window.__bjsDeepQuery(0)))`,
    returnByValue: true
  });
  if (!result.value) {
    // No stamps exist — auto-index
    await cdp.send("Runtime.evaluate", {
      expression: ELEMENTS_JS(null),
      returnByValue: true
    });
    return true;
  }
  return false;
}

async function cmdClick(index) {
  if (index === undefined) return "Usage: click <index>";
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    await ensureIndexed(cdp);
    // Click via JS events — more reliable than CDP Input.dispatchMouseEvent for SPAs (Angular, React, etc.)
    const { result } = await cdp.send("Runtime.evaluate", {
      expression: `
        (() => {
          const el = (window.__bjsDeepQuery && window.__bjsDeepQuery(${index})) || document.querySelector('[data-bjs-idx="${index}"]');
          if (!el) return JSON.stringify({ error: 'Element not found at index ${index}. Try: elements' });
          el.scrollIntoView({ block: 'center' });
          const rect = el.getBoundingClientRect();
          const cx = rect.x + rect.width / 2, cy = rect.y + rect.height / 2;
          const mOpts = { bubbles: true, cancelable: true, clientX: cx, clientY: cy, button: 0 };
          el.dispatchEvent(new MouseEvent('mousedown', mOpts));
          el.dispatchEvent(new MouseEvent('mouseup', mOpts));
          el.click();
          const label = (el.getAttribute('role') || el.tagName.toLowerCase());
          const desc = (el.getAttribute('aria-label') || el.textContent || '').trim().slice(0, 80);
          return JSON.stringify({ label, desc });
        })()
      `,
      returnByValue: true
    });

    const info = JSON.parse(result.value);
    if (info.error) return info.error;

    // Brief pause for state changes
    await new Promise(r => setTimeout(r, 150));

    // Check what changed
    let status = '';
    try {
      const { result: postResult } = await cdp.send("Runtime.evaluate", {
        expression: `
          (() => {
            const el = (window.__bjsDeepQuery && window.__bjsDeepQuery(${index})) || document.querySelector('[data-bjs-idx="${index}"]');
            const url = location.href;
            const dialogs = document.querySelectorAll('[role=dialog],[aria-modal=true]').length;
            let toggle = null;
            if (el) {
              const tag = el.tagName.toLowerCase();
              const type = (el.type || '').toLowerCase();
              if ((tag === 'input' && (type === 'checkbox' || type === 'radio')) || el.getAttribute('role') === 'checkbox' || el.getAttribute('role') === 'radio') {
                toggle = el.checked || el.getAttribute('aria-checked') === 'true' ? 'checked' : 'unchecked';
              }
            }
            return JSON.stringify({ url, dialogs, toggle });
          })()
        `,
        returnByValue: true
      });
      const post = JSON.parse(postResult.value);
      if (post.toggle !== null) {
        status = ` — now ${post.toggle}`;
      } else if (post.dialogs > 0) {
        status = ' — dialog opened';
      }
      // URL change detected by comparing with pre-click (simplified: check path)
    } catch (_) {
      status = ' — navigated away';
    }

    return `Clicked: (${info.label}) ${info.desc}${status}`;
  } finally {
    cdp.close();
  }
}

async function cmdType(index, text) {
  if (index === undefined || !text) return "Usage: type <index> <text>";
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    await ensureIndexed(cdp);

    // Get element info, verify it's typeable, get position for clicking
    const { result } = await cdp.send("Runtime.evaluate", {
      expression: `
        (() => {
          const el = (window.__bjsDeepQuery && window.__bjsDeepQuery(${index})) || document.querySelector('[data-bjs-idx="${index}"]');
          if (!el) return JSON.stringify({ error: 'Element [${index}] not found. Run elements to re-index.' });
          const tag = el.tagName.toLowerCase();
          const ce = el.isContentEditable;
          const role = el.getAttribute('role') || '';
          const type = el.type || '';
          const typeable = tag === 'input' || tag === 'textarea' || ce || role === 'textbox';
          if (!typeable) return JSON.stringify({ error: 'Element [${index}] is a ' + tag + ', not a text input. Run elements to re-index.' });
          el.scrollIntoView({ block: 'center' });
          const rect = el.getBoundingClientRect();
          return JSON.stringify({ ok: true, tag, ce, x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 });
        })()
      `,
      returnByValue: true
    });

    const info = JSON.parse(result.value);
    if (info.error) return info.error;

    // Focus element — try el.focus() first (quiet, won't trigger popups/contact cards)
    const { result: focusResult } = await cdp.send("Runtime.evaluate", {
      expression: `
        (() => {
          const el = (window.__bjsDeepQuery && window.__bjsDeepQuery(${index})) || document.querySelector('[data-bjs-idx="${index}"]');
          if (!el) return false;
          el.focus();
          return document.activeElement === el;
        })()
      `,
      returnByValue: true
    });
    const gotFocus = focusResult.value;

    if (!gotFocus) {
      // Fallback: mouse click for elements that need it (some SPAs)
      const clickOpts = { x: info.x, y: info.y, button: "left", clickCount: 1 };
      await cdp.send("Input.dispatchMouseEvent", { type: "mousePressed", ...clickOpts });
      await cdp.send("Input.dispatchMouseEvent", { type: "mouseReleased", ...clickOpts });
    }
    await new Promise(r => setTimeout(r, 100));

    // Clear existing content
    if (info.ce) {
      // For contenteditable: select all via JS, then delete
      await cdp.send("Runtime.evaluate", {
        expression: `
          (() => {
            const el = (window.__bjsDeepQuery && window.__bjsDeepQuery(${index})) || document.querySelector('[data-bjs-idx="${index}"]');
            if (el) {
              const range = document.createRange();
              range.selectNodeContents(el);
              const sel = window.getSelection();
              sel.removeAllRanges();
              sel.addRange(range);
            }
          })()
        `
      });
      await cdp.send("Input.dispatchKeyEvent", { type: "keyDown", key: "Backspace", code: "Backspace" });
      await cdp.send("Input.dispatchKeyEvent", { type: "keyUp", key: "Backspace", code: "Backspace" });
    } else {
      // For input/textarea: clear value
      await cdp.send("Runtime.evaluate", {
        expression: `
          (() => {
            const el = (window.__bjsDeepQuery && window.__bjsDeepQuery(${index})) || document.querySelector('[data-bjs-idx="${index}"]');
            if (el) el.value = '';
          })()
        `
      });
    }

    // Insert text via Input.insertText (works for both input and contenteditable)
    try {
      await cdp.send("Input.insertText", { text });
    } catch (_) {
      // Fallback: character-by-character key dispatch
      for (const char of text) {
        await cdp.send("Input.dispatchKeyEvent", { type: "keyDown", text: char, key: char, unmodifiedText: char });
        await cdp.send("Input.dispatchKeyEvent", { type: "keyUp", key: char });
      }
    }

    // Backup for input/textarea: also set .value directly for React/Vue state sync
    if (!info.ce) {
      await cdp.send("Runtime.evaluate", {
        expression: `
          (() => {
            const el = (window.__bjsDeepQuery && window.__bjsDeepQuery(${index})) || document.querySelector('[data-bjs-idx="${index}"]');
            if (el && !el.isContentEditable) {
              const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set
                || Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value')?.set;
              if (setter) setter.call(el, ${JSON.stringify(text)});
              else el.value = ${JSON.stringify(text)};
              el.dispatchEvent(new Event('input', { bubbles: true }));
              el.dispatchEvent(new Event('change', { bubbles: true }));
            }
          })()
        `
      });
    }

    // Auto-verify
    const tag = info.tag;
    const ce = info.ce ? ', contenteditable' : '';
    try {
      const { result: vResult } = await cdp.send("Runtime.evaluate", {
        expression: `
          (() => {
            const el = (window.__bjsDeepQuery && window.__bjsDeepQuery(${index})) || document.querySelector('[data-bjs-idx="${index}"]');
            if (!el) return JSON.stringify({ length: 0, focused: false });
            const isContentEditable = el.isContentEditable;
            const val = isContentEditable ? (el.innerText || '') : (el.value || '');
            return JSON.stringify({ length: val.length, focused: document.activeElement === el });
          })()
        `,
        returnByValue: true
      });
      const v = JSON.parse(vResult.value);
      if (v.length >= text.length * 0.9) {
        return `Typed ${v.length} chars into [${index}] (${tag}${ce}) — verified ✓`;
      } else if (v.length === 0 && !v.focused) {
        return `Typed into [${index}] (${tag}${ce}) — ⚠ element shows 0 chars and lost focus. Use focus ${index} to reclaim, then retry.`;
      } else if (v.length === 0) {
        return `Typed into [${index}] (${tag}${ce}) — ⚠ element shows 0 chars. Content may not have landed.`;
      } else {
        return `Typed into [${index}] (${tag}${ce}) — ⚠ expected ${text.length} chars, got ${v.length}`;
      }
    } catch (_) {
      return `Typed into [${index}] (${tag}${ce})`;
    }
  } finally {
    cdp.close();
  }
}

async function cmdFocus(index) {
  if (index === undefined) return "Usage: focus <index>";
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    await ensureIndexed(cdp);
    const { result } = await cdp.send("Runtime.evaluate", {
      expression: `
        (() => {
          const el = (window.__bjsDeepQuery && window.__bjsDeepQuery(${index})) || document.querySelector('[data-bjs-idx="${index}"]');
          if (!el) return JSON.stringify({ error: 'Element [${index}] not found. Run elements to re-index.' });
          el.scrollIntoView({ block: 'center' });
          el.focus();
          const tag = el.tagName.toLowerCase();
          const label = el.getAttribute('role') || tag;
          const desc = (el.getAttribute('aria-label') || el.textContent || '').trim().slice(0, 80);
          const active = document.activeElement === el || (el.shadowRoot && el.shadowRoot.activeElement === document.activeElement);
          return JSON.stringify({ label, desc, focused: active });
        })()
      `,
      returnByValue: true
    });
    const info = JSON.parse(result.value);
    if (info.error) return info.error;
    const status = info.focused ? "focused" : "focus sent (element may not accept focus)";
    const descPart = info.desc ? ` ${info.desc}` : "";
    return `Focused: (${info.label})${descPart} — ${status}`;
  } finally {
    cdp.close();
  }
}

async function cmdCheck(index) {
  if (index === undefined) return "Usage: check <index>";
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    await ensureIndexed(cdp);
    const { result } = await cdp.send("Runtime.evaluate", {
      expression: `
        (() => {
          const el = (window.__bjsDeepQuery && window.__bjsDeepQuery(${index})) || document.querySelector('[data-bjs-idx="${index}"]');
          if (!el) return JSON.stringify({ error: 'Element [${index}] not found. Run elements to re-index.' });
          const tag = el.tagName.toLowerCase();
          const ce = el.isContentEditable;
          const role = el.getAttribute('role') || '';
          let value = '';
          if (tag === 'input' || tag === 'textarea' || tag === 'select') {
            value = el.value || '';
          } else if (ce || role === 'textbox') {
            value = el.innerText || el.textContent || '';
          } else {
            value = el.innerText || el.textContent || '';
          }
          const label = role || tag;
          const desc = (el.getAttribute('aria-label') || el.placeholder || el.name || '').trim().slice(0, 60);
          const isFocused = document.activeElement === el;
          return JSON.stringify({ label, desc, value: value.slice(0, 2000), length: value.length, focused: isFocused });
        })()
      `,
      returnByValue: true
    });
    const info = JSON.parse(result.value);
    if (info.error) return info.error;
    const display = info.value.length > 100 ? info.value.slice(0, 100) + "..." : info.value;
    const focusStr = info.focused ? "focused" : "not focused";
    const descPart = info.desc ? ` ${info.desc}` : "";
    return `[${index}] (${info.label})${descPart} — value: "${display}" (${info.length} chars, ${focusStr})`;
  } finally {
    cdp.close();
  }
}

async function cmdPaste(index, args) {
  if (index === undefined) return "Usage: paste <index> <text>  OR  paste <index> --file <path>";
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    await ensureIndexed(cdp);

    // Resolve content from args or --file
    let content = '';
    const fileIdx = args.indexOf('--file');
    if (fileIdx !== -1 && args[fileIdx + 1]) {
      const fs = require('fs');
      const path = require('path');
      const fp = path.resolve(args[fileIdx + 1].replace(/^~/, process.env.HOME));
      if (!fs.existsSync(fp)) return `Error: File not found: ${fp}`;
      content = fs.readFileSync(fp, 'utf8');
    } else {
      content = args.join(' ');
    }
    if (!content) return "Error: provide text or --file <path>";

    // Step 1: Get element info
    const { result: typeResult } = await cdp.send("Runtime.evaluate", {
      expression: `
        (() => {
          const el = (window.__bjsDeepQuery && window.__bjsDeepQuery(${index})) || document.querySelector('[data-bjs-idx="${index}"]');
          if (!el) return JSON.stringify({ error: 'Element [${index}] not found. Run elements to re-index.' });
          const tag = el.tagName.toLowerCase();
          const ce = el.isContentEditable;
          const role = el.getAttribute('role') || '';
          const typeable = tag === 'input' || tag === 'textarea' || ce || role === 'textbox';
          if (!typeable) return JSON.stringify({ error: 'Element [${index}] is a ' + tag + ' — not a text input. Use keys for canvas apps.' });
          el.scrollIntoView({ block: 'center' });
          return JSON.stringify({ ok: true, tag, ce });
        })()
      `,
      returnByValue: true
    });
    const info = JSON.parse(typeResult.value);
    if (info.error) return info.error;

    // Step 2: Focus (no click events)
    await cdp.send("Runtime.evaluate", {
      expression: `
        (() => {
          const el = (window.__bjsDeepQuery && window.__bjsDeepQuery(${index})) || document.querySelector('[data-bjs-idx="${index}"]');
          if (el) { el.scrollIntoView({ block: 'center' }); el.focus(); }
        })()
      `
    });
    await new Promise(r => setTimeout(r, 100));

    // Step 3: Clear
    if (info.ce) {
      await cdp.send("Runtime.evaluate", {
        expression: `
          (() => {
            const el = (window.__bjsDeepQuery && window.__bjsDeepQuery(${index})) || document.querySelector('[data-bjs-idx="${index}"]');
            if (el) { const r = document.createRange(); r.selectNodeContents(el); const s = window.getSelection(); s.removeAllRanges(); s.addRange(r); }
          })()
        `
      });
      await cdp.send("Input.dispatchKeyEvent", { type: "keyDown", key: "Backspace", code: "Backspace" });
      await cdp.send("Input.dispatchKeyEvent", { type: "keyUp", key: "Backspace", code: "Backspace" });
    } else {
      await cdp.send("Runtime.evaluate", {
        expression: `
          (() => { const el = (window.__bjsDeepQuery && window.__bjsDeepQuery(${index})) || document.querySelector('[data-bjs-idx="${index}"]'); if (el) el.value = ''; })()
        `
      });
    }

    // Step 4: Insert via CDP
    try {
      await cdp.send("Input.insertText", { text: content });
    } catch (_) {}

    // Step 5: Verify
    const { result: checkResult } = await cdp.send("Runtime.evaluate", {
      expression: `
        (() => {
          const el = (window.__bjsDeepQuery && window.__bjsDeepQuery(${index})) || document.querySelector('[data-bjs-idx="${index}"]');
          if (!el) return JSON.stringify({ length: 0 });
          const ce = el.isContentEditable;
          const val = ce ? (el.innerText || '') : (el.value || '');
          return JSON.stringify({ length: val.length, focused: document.activeElement === el });
        })()
      `,
      returnByValue: true
    });
    const check = JSON.parse(checkResult.value);

    if (check.length >= content.length * 0.9) {
      const ce = info.ce ? ', contenteditable' : '';
      return `Pasted ${check.length} chars into [${index}] (${info.tag}${ce}) — verified ✓`;
    }

    // Step 6: JS fallback
    const escaped = JSON.stringify(content);
    await cdp.send("Runtime.evaluate", {
      expression: `
        (() => {
          const el = (window.__bjsDeepQuery && window.__bjsDeepQuery(${index})) || document.querySelector('[data-bjs-idx="${index}"]');
          if (!el) return;
          const ce = el.isContentEditable;
          if (ce) {
            el.focus();
            el.innerHTML = ${escaped}.replace(/\\n/g, '<br>');
            el.dispatchEvent(new Event('input', { bubbles: true }));
          } else {
            el.focus();
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set
              || Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value')?.set;
            if (setter) setter.call(el, ${escaped});
            else el.value = ${escaped};
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
          }
        })()
      `
    });

    // Step 7: Final verify
    const { result: finalResult } = await cdp.send("Runtime.evaluate", {
      expression: `
        (() => {
          const el = (window.__bjsDeepQuery && window.__bjsDeepQuery(${index})) || document.querySelector('[data-bjs-idx="${index}"]');
          if (!el) return JSON.stringify({ length: 0 });
          const ce = el.isContentEditable;
          const val = ce ? (el.innerText || '') : (el.value || '');
          return JSON.stringify({ length: val.length, focused: document.activeElement === el });
        })()
      `,
      returnByValue: true
    });
    const final = JSON.parse(finalResult.value);

    if (final.length >= content.length * 0.9) {
      const ce = info.ce ? ', contenteditable' : '';
      return `Pasted ${final.length} chars into [${index}] (${info.tag}${ce}) — verified ✓ (JS fallback)`;
    }

    const focusStr = final.focused ? 'focused' : 'NOT focused';
    return `Paste into [${index}] (${info.tag}) may have failed. Expected ~${content.length} chars, got ${final.length}. Element is ${focusStr}. Try: focus ${index}, then paste again.`;
  } finally {
    cdp.close();
  }
}

async function cmdText(selector) {
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    const { result } = await cdp.send("Runtime.evaluate", {
      expression: `
        (() => {
          const sel = ${JSON.stringify(selector || null)};
          const root = sel ? document.querySelector(sel) : document.body;
          if (!root) return 'Selector not found: ' + sel;

          const MAX = 8000;
          const chunks = [];
          let totalLen = 0;

          // Recursive text extraction that pierces shadow DOM
          function extractText(node) {
            if (totalLen >= MAX) return;
            if (node.nodeType === 3) { // TEXT_NODE
              const t = node.textContent.trim();
              if (t.length > 0) {
                const parent = node.parentElement;
                if (parent) {
                  const tag = parent.tagName;
                  if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'SVG'].includes(tag)) return;
                  if (parent.offsetParent === null && getComputedStyle(parent).position !== 'fixed') return;
                }
                chunks.push(t);
                totalLen += t.length;
              }
              return;
            }
            if (node.nodeType === 1) { // ELEMENT_NODE
              // Enter shadow root if present
              if (node.shadowRoot) {
                for (const child of node.shadowRoot.childNodes) extractText(child);
              }
              for (const child of node.childNodes) extractText(child);
            }
          }

          extractText(root);
          let text = chunks.join(' ').replace(/\\s+/g, ' ').trim();
          if (text.length > MAX) text = text.slice(0, MAX) + '... (truncated)';
          return text || '(empty page)';
        })()
      `,
      returnByValue: true
    });
    return result.value;
  } finally {
    cdp.close();
  }
}

async function cmdHtml(selector) {
  if (!selector) return "Usage: html <css-selector>";
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    const { result } = await cdp.send("Runtime.evaluate", {
      expression: `
        (() => {
          const el = document.querySelector(${JSON.stringify(selector)});
          if (!el) return 'Selector not found: ' + ${JSON.stringify(selector)};
          const html = el.outerHTML;
          return html.length > 10000 ? html.slice(0, 10000) + '... (truncated)' : html;
        })()
      `,
      returnByValue: true
    });
    return result.value;
  } finally {
    cdp.close();
  }
}

async function cmdEval(js) {
  if (!js) return "Usage: eval <javascript>";
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    const { result, exceptionDetails } = await cdp.send("Runtime.evaluate", {
      expression: js,
      returnByValue: true,
      awaitPromise: true
    });
    if (exceptionDetails) {
      return `Error: ${exceptionDetails.exception?.description || exceptionDetails.text}`;
    }
    if (result.value !== undefined) return typeof result.value === 'string' ? result.value : JSON.stringify(result.value, null, 2);
    if (result.description) return result.description;
    return result.type === 'undefined' ? '(undefined)' : JSON.stringify(result);
  } finally {
    cdp.close();
  }
}

async function cmdScreenshot(filePath) {
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    const { data } = await cdp.send("Page.captureScreenshot", { format: "png" });
    const outPath = filePath || `/tmp/browser_screenshot_${Date.now()}.png`;
    writeFileSync(outPath, Buffer.from(data, "base64"));
    return `Screenshot saved: ${outPath}`;
  } finally {
    cdp.close();
  }
}

async function cmdScroll(direction, amount) {
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    const px = parseInt(amount) || 600;
    let expr;
    switch (direction) {
      case "up": expr = `window.scrollBy(0, -${px})`; break;
      case "down": expr = `window.scrollBy(0, ${px})`; break;
      case "top": expr = `window.scrollTo(0, 0)`; break;
      case "bottom": expr = `window.scrollTo(0, document.body.scrollHeight)`; break;
      default: return "Usage: scroll <up|down|top|bottom> [pixels]";
    }
    await cdp.send("Runtime.evaluate", { expression: expr });
    return `Scrolled ${direction}${amount ? ` ${amount}px` : ''}`;
  } finally {
    cdp.close();
  }
}

async function cmdUrl() {
  const target = await getCurrentTarget();
  return target.url;
}

async function cmdBack() {
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    const { currentIndex, entries } = await cdp.send("Page.getNavigationHistory");
    if (currentIndex > 0) {
      await cdp.send("Page.navigateToHistoryEntry", { entryId: entries[currentIndex - 1].id });
      return `Back to: ${entries[currentIndex - 1].url}`;
    }
    return "Already at first page in history.";
  } finally {
    cdp.close();
  }
}

async function cmdForward() {
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    const { currentIndex, entries } = await cdp.send("Page.getNavigationHistory");
    if (currentIndex < entries.length - 1) {
      await cdp.send("Page.navigateToHistoryEntry", { entryId: entries[currentIndex + 1].id });
      return `Forward to: ${entries[currentIndex + 1].url}`;
    }
    return "Already at last page in history.";
  } finally {
    cdp.close();
  }
}

async function cmdRefresh() {
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    await cdp.send("Page.reload");
    return "Refreshed.";
  } finally {
    cdp.close();
  }
}

async function cmdUpload(filePath, selector) {
  if (!filePath) return "Usage: upload <file-path> [css-selector]\nDefault selector: input[type=file]";
  const { existsSync, realpathSync } = require("fs");
  const path = require("path");

  // Resolve to absolute path
  const absPath = path.resolve(filePath);
  if (!existsSync(absPath)) return `File not found: ${absPath}`;

  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    await cdp.send("DOM.enable");

    const cssSelector = selector || 'input[type="file"]';

    // Get the DOM node for the file input
    const { root } = await cdp.send("DOM.getDocument");
    const { nodeId } = await cdp.send("DOM.querySelector", {
      nodeId: root.nodeId,
      selector: cssSelector
    });

    if (!nodeId) return `No file input found matching: ${cssSelector}`;

    // Set the file on the input
    await cdp.send("DOM.setFileInputFiles", {
      files: [absPath],
      nodeId: nodeId
    });

    return `Uploaded: ${path.basename(absPath)} → ${cssSelector}`;
  } finally {
    cdp.close();
  }
}

async function cmdWait(ms) {
  const duration = parseInt(ms) || 1000;
  await new Promise(r => setTimeout(r, duration));
  return `Waited ${duration}ms`;
}

// ── Coordinate-based input (for cross-origin iframes, captchas, etc.) ──

async function cmdClickXY(x, y, opts = {}) {
  if (x === undefined || y === undefined) return "Usage: click-xy <x> <y> [--double] [--right]";
  const px = parseFloat(x), py = parseFloat(y);
  if (isNaN(px) || isNaN(py)) return "Error: x and y must be numbers";
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    const button = opts.right ? "right" : "left";
    const clickCount = opts.double ? 2 : 1;

    // Move mouse first (triggers hover states, reveals tooltips)
    await cdp.send("Input.dispatchMouseEvent", { type: "mouseMoved", x: px, y: py });
    await new Promise(r => setTimeout(r, 50));

    // Press + release
    await cdp.send("Input.dispatchMouseEvent", {
      type: "mousePressed", x: px, y: py, button, clickCount
    });
    await cdp.send("Input.dispatchMouseEvent", {
      type: "mouseReleased", x: px, y: py, button, clickCount
    });

    if (opts.double) {
      // Second click for double-click
      await cdp.send("Input.dispatchMouseEvent", {
        type: "mousePressed", x: px, y: py, button, clickCount: 2
      });
      await cdp.send("Input.dispatchMouseEvent", {
        type: "mouseReleased", x: px, y: py, button, clickCount: 2
      });
    }

    const label = opts.double ? "Double-clicked" : opts.right ? "Right-clicked" : "Clicked";
    return `${label} at (${px}, ${py})`;
  } finally {
    cdp.close();
  }
}

async function cmdHoverXY(x, y) {
  if (x === undefined || y === undefined) return "Usage: hover-xy <x> <y>";
  const px = parseFloat(x), py = parseFloat(y);
  if (isNaN(px) || isNaN(py)) return "Error: x and y must be numbers";
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    await cdp.send("Input.dispatchMouseEvent", { type: "mouseMoved", x: px, y: py });
    return `Hovered at (${px}, ${py})`;
  } finally {
    cdp.close();
  }
}

async function cmdDragXY(x1, y1, x2, y2) {
  if (x1 === undefined || y1 === undefined || x2 === undefined || y2 === undefined)
    return "Usage: drag-xy <fromX> <fromY> <toX> <toY>";
  const sx = parseFloat(x1), sy = parseFloat(y1), ex = parseFloat(x2), ey = parseFloat(y2);
  if ([sx, sy, ex, ey].some(isNaN)) return "Error: all coordinates must be numbers";
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    // Move to start position
    await cdp.send("Input.dispatchMouseEvent", { type: "mouseMoved", x: sx, y: sy });
    await new Promise(r => setTimeout(r, 50));
    // Press at start
    await cdp.send("Input.dispatchMouseEvent", {
      type: "mousePressed", x: sx, y: sy, button: "left", clickCount: 1
    });
    await new Promise(r => setTimeout(r, 50));
    // Move to end (intermediate steps for smooth drag)
    const steps = 10;
    for (let i = 1; i <= steps; i++) {
      const mx = sx + (ex - sx) * (i / steps);
      const my = sy + (ey - sy) * (i / steps);
      await cdp.send("Input.dispatchMouseEvent", { type: "mouseMoved", x: mx, y: my, button: "left" });
      await new Promise(r => setTimeout(r, 20));
    }
    // Release at end
    await cdp.send("Input.dispatchMouseEvent", {
      type: "mouseReleased", x: ex, y: ey, button: "left", clickCount: 1
    });
    return `Dragged from (${sx}, ${sy}) to (${ex}, ${ey})`;
  } finally {
    cdp.close();
  }
}

async function cmdIframeRect(selector) {
  if (!selector) return "Usage: iframe-rect <css-selector>\nReturns bounding box of an iframe for use with click-xy";
  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  try {
    const { result, exceptionDetails } = await cdp.send("Runtime.evaluate", {
      expression: `
        (() => {
          const el = document.querySelector(${JSON.stringify(selector)});
          if (!el) return JSON.stringify({ error: "Selector not found: " + ${JSON.stringify(selector)} });
          el.scrollIntoView({ block: 'center' });
          const r = el.getBoundingClientRect();
          return JSON.stringify({ x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height), cx: Math.round(r.x + r.width/2), cy: Math.round(r.y + r.height/2) });
        })()
      `,
      returnByValue: true
    });
    if (exceptionDetails) return `Error: ${exceptionDetails.text}`;
    const info = JSON.parse(result.value);
    if (info.error) return info.error;
    return `x=${info.x} y=${info.y} w=${info.width} h=${info.height} center=(${info.cx}, ${info.cy})`;
  } finally {
    cdp.close();
  }
}

// ── Raw keyboard input (for canvas-based apps: Google Sheets, Docs, Figma, etc.) ──

// Key name → { key, code, keyCode }
const SPECIAL_KEYS = {
  enter:     { key: "Enter",     code: "Enter",      keyCode: 13 },
  tab:       { key: "Tab",       code: "Tab",        keyCode: 9  },
  escape:    { key: "Escape",    code: "Escape",     keyCode: 27 },
  backspace: { key: "Backspace", code: "Backspace",  keyCode: 8  },
  delete:    { key: "Delete",    code: "Delete",     keyCode: 46 },
  arrowup:   { key: "ArrowUp",   code: "ArrowUp",    keyCode: 38 },
  arrowdown: { key: "ArrowDown", code: "ArrowDown",  keyCode: 40 },
  arrowleft: { key: "ArrowLeft", code: "ArrowLeft",  keyCode: 37 },
  arrowright:{ key: "ArrowRight",code: "ArrowRight", keyCode: 39 },
  home:      { key: "Home",      code: "Home",       keyCode: 36 },
  end:       { key: "End",       code: "End",        keyCode: 35 },
  pageup:    { key: "PageUp",    code: "PageUp",     keyCode: 33 },
  pagedown:  { key: "PageDown",  code: "PageDown",   keyCode: 34 },
  space:     { key: " ",         code: "Space",      keyCode: 32 },
  f1:  { key: "F1",  code: "F1",  keyCode: 112 },
  f2:  { key: "F2",  code: "F2",  keyCode: 113 },
  f3:  { key: "F3",  code: "F3",  keyCode: 114 },
  f4:  { key: "F4",  code: "F4",  keyCode: 115 },
  f5:  { key: "F5",  code: "F5",  keyCode: 116 },
  f6:  { key: "F6",  code: "F6",  keyCode: 117 },
  f7:  { key: "F7",  code: "F7",  keyCode: 118 },
  f8:  { key: "F8",  code: "F8",  keyCode: 119 },
  f9:  { key: "F9",  code: "F9",  keyCode: 120 },
  f10: { key: "F10", code: "F10", keyCode: 121 },
  f11: { key: "F11", code: "F11", keyCode: 122 },
  f12: { key: "F12", code: "F12", keyCode: 123 },
};

const MODIFIER_FLAGS = {
  alt: 1,
  ctrl: 2,
  control: 2,
  meta: 4,
  cmd: 4,
  command: 4,
  shift: 8,
};

function parseKeyCombo(combo) {
  // e.g. "cmd+b", "ctrl+shift+a", "cmd+a"
  const parts = combo.toLowerCase().split("+");
  let modifiers = 0;
  let keyPart = null;
  for (const p of parts) {
    if (MODIFIER_FLAGS[p] !== undefined) {
      modifiers |= MODIFIER_FLAGS[p];
    } else {
      keyPart = p;
    }
  }
  if (!keyPart) return null;

  // Check if it's a special key
  const special = SPECIAL_KEYS[keyPart];
  if (special) {
    return { ...special, modifiers };
  }

  // Single character
  const upper = (modifiers & 8) ? keyPart.toUpperCase() : keyPart; // shift
  const code = `Key${keyPart.toUpperCase()}`;
  return { key: upper, code, keyCode: keyPart.toUpperCase().charCodeAt(0), modifiers };
}

async function cmdKeys(rawArgs) {
  if (!rawArgs || rawArgs.length === 0) {
    return `Usage: keys <text> [--enter] [--tab] [--escape]
       keys --combo <key-combo>     e.g. --combo cmd+b

Sends raw CDP keyboard events (bypasses DOM, works on canvas apps like Google Sheets, Docs, Figma).

Flags:  --enter  --tab  --escape  --backspace  --delete
        --up  --down  --left  --right
        --combo <combo>  (e.g. cmd+a, ctrl+shift+end, cmd+b)
        --delay <ms>  (per-character delay, default 10)

Can chain: keys "hello" --tab "world" --enter`;
  }

  const target = await getCurrentTarget();
  const cdp = await connectToTarget(target.id);
  const sleep = ms => new Promise(r => setTimeout(r, ms));

  try {
    let delay = 10;
    const actions = []; // { type: "text", value } | { type: "key", ... } | { type: "combo", ... }

    // Parse args into an action sequence
    for (let i = 0; i < rawArgs.length; i++) {
      const arg = rawArgs[i];

      if (arg === "--delay" && rawArgs[i + 1]) {
        delay = parseInt(rawArgs[++i]) || 10;
        continue;
      }

      if (arg === "--combo" && rawArgs[i + 1]) {
        const combo = parseKeyCombo(rawArgs[++i]);
        if (combo) actions.push({ type: "combo", ...combo });
        continue;
      }

      // Special key flags
      const flagMap = {
        "--enter": "enter", "--tab": "tab", "--escape": "escape", "--esc": "escape",
        "--backspace": "backspace", "--delete": "delete",
        "--up": "arrowup", "--down": "arrowdown", "--left": "arrowleft", "--right": "arrowright",
        "--home": "home", "--end": "end", "--pageup": "pageup", "--pagedown": "pagedown",
        "--space": "space",
      };

      if (flagMap[arg.toLowerCase()]) {
        const sk = SPECIAL_KEYS[flagMap[arg.toLowerCase()]];
        actions.push({ type: "key", ...sk, modifiers: 0 });
        continue;
      }

      // Plain text to type
      if (!arg.startsWith("--")) {
        actions.push({ type: "text", value: arg });
      }
    }

    if (actions.length === 0) return "Nothing to type. Provide text or key flags.";

    let typed = 0, keys = 0;

    for (const action of actions) {
      if (action.type === "text") {
        for (const char of action.value) {
          await cdp.send("Input.dispatchKeyEvent", { type: "keyDown", text: char });
          await cdp.send("Input.dispatchKeyEvent", { type: "keyUp" });
          await sleep(delay);
        }
        typed += action.value.length;
      } else if (action.type === "key" || action.type === "combo") {
        await cdp.send("Input.dispatchKeyEvent", {
          type: "rawKeyDown",
          key: action.key,
          code: action.code,
          windowsVirtualKeyCode: action.keyCode,
          nativeVirtualKeyCode: action.keyCode,
          modifiers: action.modifiers || 0,
        });
        await sleep(10);
        await cdp.send("Input.dispatchKeyEvent", {
          type: "keyUp",
          key: action.key,
          code: action.code,
          windowsVirtualKeyCode: action.keyCode,
          nativeVirtualKeyCode: action.keyCode,
          modifiers: action.modifiers || 0,
        });
        keys++;
        await sleep(30);
      }
    }

    const parts = [];
    if (typed > 0) parts.push(`${typed} chars`);
    if (keys > 0) parts.push(`${keys} key(s)`);
    return `Sent: ${parts.join(" + ")}`;
  } finally {
    cdp.close();
  }
}

// ── Main ──

const COMMANDS = {
  tabs: () => cmdTabs(),
  open: (args) => cmdOpen(args[0]),
  tab: (args) => cmdTab(args[0]),
  newtab: (args) => cmdNewTab(args[0]),
  close: (args) => cmdClose(args[0]),
  elements: (args) => cmdElements(args[0]),
  click: (args) => cmdClick(args[0]),
  "click-xy": (args) => {
    const opts = { double: args.includes("--double"), right: args.includes("--right") };
    const coords = args.filter(a => !a.startsWith("--"));
    return cmdClickXY(coords[0], coords[1], opts);
  },
  "hover-xy": (args) => cmdHoverXY(args[0], args[1]),
  "drag-xy": (args) => cmdDragXY(args[0], args[1], args[2], args[3]),
  "iframe-rect": (args) => cmdIframeRect(args.join(" ")),
  keys: (args) => cmdKeys(args),
  type: (args) => cmdType(args[0], args.slice(1).join(" ")),
  text: (args) => cmdText(args[0]),
  html: (args) => cmdHtml(args[0]),
  eval: (args) => cmdEval(args.join(" ")),
  screenshot: (args) => cmdScreenshot(args[0]),
  focus: (args) => cmdFocus(parseInt(args[0])),
  check: (args) => cmdCheck(parseInt(args[0])),
  paste: (args) => cmdPaste(parseInt(args[0]), args.slice(1)),
  scroll: (args) => cmdScroll(args[0], args[1]),
  url: () => cmdUrl(),
  back: () => cmdBack(),
  forward: () => cmdForward(),
  refresh: () => cmdRefresh(),
  upload: (args) => cmdUpload(args[0], args[1]),
  wait: (args) => cmdWait(args[0]),
};

async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0]?.toLowerCase();

  if (cmd === "--version" || cmd === "-V" || cmd === "version") {
    console.log("tappi 3.0.0 (bjs)");
    return;
  }

  if (!cmd || cmd === "help" || cmd === "--help") {
    console.log(`browser.js — Lightweight CDP browser control

Commands:
  tabs                    List open tabs
  open <url>              Navigate to URL
  tab <index>             Switch to tab by index
  newtab [url]            Open new tab
  close [index]           Close tab
  elements [selector]     List interactive elements (indexed)
  click <index>           Click element by index
  type <index> <text>     Type into element
  focus <index>           Focus element (no click events, reclaim focus)
  check <index>           Read element value (verify after type)
  paste <index> <text>    Paste content with auto-verify + fallback
  paste <index> --file <path>  Paste from file
  text [selector]         Extract page text
  html <selector>         Get element HTML
  eval <js>               Run JavaScript
  screenshot [path]       Save screenshot
  scroll <up|down|top|bottom> [px]
  url                     Current URL
  back / forward / refresh
  upload <path> [selector] Upload file to input
  wait <ms>

Raw keyboard input (canvas apps: Google Sheets, Docs, Figma):
  keys <text> [--enter] [--tab] ...        Type via CDP keyboard events
  keys --combo <combo>                     Key combo (e.g. cmd+b, ctrl+a)

Coordinate commands (for iframes, captchas, overlays):
  click-xy <x> <y> [--double] [--right]   Click at page coordinates
  hover-xy <x> <y>                         Hover at page coordinates
  drag-xy <x1> <y1> <x2> <y2>             Drag between coordinates
  iframe-rect <css-selector>               Get iframe bounding box

Env: CDP_URL (default: http://127.0.0.1:18800)`);
    return;
  }

  const handler = COMMANDS[cmd];
  if (!handler) {
    console.error(`Unknown command: ${cmd}\nRun "browser.js help" for usage.`);
    process.exit(1);
  }

  try {
    const result = await handler(args.slice(1));
    if (result) console.log(result);
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

main();
