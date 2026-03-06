(async () => {
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));

  if (!location.href.includes('/i/grok')) {
    console.log('Open https://x.com/i/grok first.');
    return;
  }

  const INDEX_PASSES = 8;
  const SCROLL_MAX = 340;
  const STABLE_TARGET = 24;
  const CHECKPOINT_KEY = 'xgrok_capture_checkpoint_v1';
  const CHECKPOINT_EVERY = 25;

  const captured = new Map(); // restId -> {requestUrl, source, data}
  const seenUrls = new Set();
  let cooldownUntilMs = 0;
  let rateLimitHits = 0;

  const loadCheckpoint = () => {
    try {
      const raw = localStorage.getItem(CHECKPOINT_KEY);
      if (!raw) return null;
      const cp = JSON.parse(raw);
      if (!cp || !Array.isArray(cp.captured)) return null;
      return cp;
    } catch {
      return null;
    }
  };

  const saveCheckpoint = (targets, currentIndex, pass) => {
    try {
      const cp = {
        version: 1,
        savedAt: new Date().toISOString(),
        pass,
        currentIndex,
        targets,
        captured: [...captured.values()].map(x => ({ restId: x.restId, requestUrl: x.requestUrl, source: x.source, data: x.data })),
        rateLimitHits,
      };
      localStorage.setItem(CHECKPOINT_KEY, JSON.stringify(cp));
    } catch {}
  };

  const clearCheckpoint = () => {
    try { localStorage.removeItem(CHECKPOINT_KEY); } catch {}
  };

  const parseRestIdFromUrl = (u) => {
    try {
      const url = new URL(u, location.origin);
      const vars = url.searchParams.get('variables');
      if (vars) {
        const obj = JSON.parse(decodeURIComponent(vars));
        if (obj?.restId) return String(obj.restId);
      }
    } catch {}
    const m = String(u).match(/restId%22%3A%22(\d+)/);
    return m ? m[1] : null;
  };

  const maybeStore = (reqUrl, data, source) => {
    const url = String(reqUrl || '');
    if (!url.includes('/GrokConversationItemsByRestId')) return;
    const restId = parseRestIdFromUrl(url) || data?.data?.grok_conversation_by_rest_id?.rest_id || null;
    if (!restId) return;
    if (!captured.has(restId)) {
      captured.set(restId, { restId, requestUrl: url, source, data });
      console.log('[capture]', restId, source);
    }
  };

  const setCooldownFromResponse = (res) => {
    const reset = res.headers?.get?.('x-rate-limit-reset');
    const now = Date.now();
    let until = now + 15 * 60 * 1000; // fallback 15 min
    if (reset && /^\d+$/.test(reset)) {
      const ts = Number(reset) * 1000;
      if (ts > now) until = ts + 5000; // +5s jitter
    }
    cooldownUntilMs = Math.max(cooldownUntilMs, until);
    rateLimitHits += 1;
    console.log(`[rate-limit] 429 hit. Cooling down until ${new Date(cooldownUntilMs).toISOString()}`);
  };

  // --- intercept fetch
  const origFetch = window.fetch.bind(window);
  window.fetch = async (...args) => {
    const reqUrl = String(args[0]?.url || args[0] || '');
    const res = await origFetch(...args);
    try {
      if (reqUrl.includes('/GrokConversationItemsByRestId')) {
        if (res.status === 429) {
          setCooldownFromResponse(res);
          return res;
        }
        if (!seenUrls.has(reqUrl)) {
          seenUrls.add(reqUrl);
          const j = await res.clone().json();
          maybeStore(reqUrl, j, 'fetch');
        }
      }
    } catch {}
    return res;
  };

  // --- intercept XHR
  const XO = XMLHttpRequest.prototype.open;
  const XS = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function(method, url, ...rest) {
    this.__u = url;
    return XO.call(this, method, url, ...rest);
  };
  XMLHttpRequest.prototype.send = function(...args) {
    this.addEventListener('load', function() {
      try {
        const u = String(this.__u || '');
        if (!u.includes('/GrokConversationItemsByRestId')) return;
        if (this.status === 429) {
          const reset = this.getResponseHeader('x-rate-limit-reset');
          const now = Date.now();
          let until = now + 15 * 60 * 1000;
          if (reset && /^\d+$/.test(reset)) {
            const ts = Number(reset) * 1000;
            if (ts > now) until = ts + 5000;
          }
          cooldownUntilMs = Math.max(cooldownUntilMs, until);
          rateLimitHits += 1;
          console.log(`[rate-limit] 429 hit (xhr). Cooling down until ${new Date(cooldownUntilMs).toISOString()}`);
          return;
        }
        if (seenUrls.has(u)) return;
        seenUrls.add(u);
        const j = JSON.parse(this.responseText);
        maybeStore(u, j, 'xhr');
      } catch {}
    });
    return XS.apply(this, args);
  };

  const openHistory = () => {
    const b = [...document.querySelectorAll('button')].find(x =>
      /chat history/i.test(x.getAttribute('aria-label') || '') ||
      /history/i.test((x.textContent || '').trim())
    );
    if (b) b.click();
  };

  const getScroller = () => {
    const scrollers = [...document.querySelectorAll('div')].filter(d => d.scrollHeight > d.clientHeight + 250);
    scrollers.sort((a,b)=> (b.clientHeight*b.clientWidth) - (a.clientHeight*a.clientWidth));
    return scrollers[0] || document.scrollingElement || document.body;
  };

  const collectIndex = () => {
    const map = new Map();
    for (const a of document.querySelectorAll('a[href*="/i/grok?conversation="]')) {
      const href = a.getAttribute('href') || '';
      const m = href.match(/conversation=(\d+)/);
      if (!m) continue;
      const id = m[1];
      const title = (a.textContent || '').trim().replace(/\s+/g, ' ');
      const url = href.startsWith('http') ? href : `https://x.com${href}`;
      if (!map.has(id) || title.length > (map.get(id).title || '').length) {
        map.set(id, { id, title, URL: url });
      }
    }
    return [...map.values()].sort((a,b)=>String(b.id).localeCompare(String(a.id)));
  };

  // -------- PHASE 1: v8-style multi-pass union indexing --------
  const union = new Map();
  const passStats = [];

  const checkpoint = loadCheckpoint();
  if (checkpoint) {
    for (const c of (checkpoint.captured || [])) {
      if (c?.restId) captured.set(String(c.restId), c);
    }
    rateLimitHits = checkpoint.rateLimitHits || rateLimitHits;
    console.log(`[checkpoint] restored captured=${captured.size}`);
  }

  let targets;
  if (checkpoint?.targets?.length) {
    targets = checkpoint.targets;
    console.log(`[checkpoint] reusing target list: ${targets.length}`);
  } else {
    for (let pass = 1; pass <= INDEX_PASSES; pass++) {
      openHistory();
      await sleep(1400);

      let prev = -1;
      let stable = 0;

      for (let i = 0; i < SCROLL_MAX && stable < STABLE_TARGET; i++) {
        const s = getScroller();
        s.scrollTop = s.scrollHeight;
        await sleep(280);

        const nowList = collectIndex();
        nowList.forEach(c => union.set(c.id, c));

        const now = union.size;
        if (now === prev) stable++; else stable = 0;
        prev = now;

        if (i % 50 === 0) await sleep(700);
      }

      passStats.push({ pass, union_count: union.size });
      console.log(`index pass ${pass}/${INDEX_PASSES}: union=${union.size}`);

      // panel toggle to force redraw/reload behavior
      openHistory(); await sleep(700);
      openHistory(); await sleep(900);
    }

    targets = [...union.values()].sort((a,b)=>String(b.id).localeCompare(String(a.id)));
    console.log('Final indexed targets:', targets.length);
  }

  const closeBlockingDialog = () => {
    const closeBtn = [...document.querySelectorAll('button')].find(b => {
      const txt = ((b.textContent || '') + ' ' + (b.getAttribute('aria-label') || '')).toLowerCase();
      return /close/.test(txt);
    });
    const hasDialog = !!document.querySelector('[role="dialog"]');
    if (hasDialog && closeBtn) {
      closeBtn.click();
      return true;
    }
    return false;
  };

  const waitForCaptureOrTimeout = async (restId, timeoutMs = 9000) => {
    const started = Date.now();
    while (Date.now() - started < timeoutMs) {
      if (captured.has(restId)) return true;
      closeBlockingDialog();
      await sleep(250);
    }
    return captured.has(restId);
  };

  // -------- PHASE 2: click-through capture with retry passes --------
  const startPass = checkpoint?.pass && checkpoint.pass >= 1 && checkpoint.pass <= 3 ? checkpoint.pass : 1;
  const startIndex = Number.isInteger(checkpoint?.currentIndex) ? checkpoint.currentIndex : 0;

  for (let pass = startPass; pass <= 3; pass++) {
    console.log(`capture pass ${pass}/3`);

    for (let i = (pass === startPass ? startIndex : 0); i < targets.length; i++) {
      const t = targets[i];
      if (captured.has(t.id)) continue;

      closeBlockingDialog();

      // honor cooldown after 429s
      if (Date.now() < cooldownUntilMs) {
        const waitMs = cooldownUntilMs - Date.now();
        console.log(`[rate-limit] waiting ${Math.ceil(waitMs/1000)}s before continuing...`);
        await sleep(waitMs);
      }

      // Prefer direct SPA navigation to avoid getting stuck in history-panel open/scroll loops.
      try {
        const u = new URL(t.URL);
        history.pushState({}, '', `${u.pathname}${u.search}`);
        window.dispatchEvent(new PopStateEvent('popstate'));
      } catch {
        // fallback to history link click only if direct nav fails
        openHistory();
        await sleep(500);

        let link = [...document.querySelectorAll('a[href*="/i/grok?conversation="]')]
          .find(a => (a.getAttribute('href') || '').includes(t.id));

        if (!link) {
          for (let j = 0; j < 40; j++) {
            const s = getScroller();
            s.scrollTop = s.scrollHeight;
            await sleep(160);
          }
          link = [...document.querySelectorAll('a[href*="/i/grok?conversation="]')]
            .find(a => (a.getAttribute('href') || '').includes(t.id));
        }

        if (!link) continue;
        try { link.click(); } catch { continue; }
      }

      const ok = await waitForCaptureOrTimeout(t.id, 9000);
      if (!ok) {
        // not captured in time; continue, later passes may still capture it
        console.log(`timeout ${t.id} (will retry in next pass)`);
      }

      if ((i + 1) % 50 === 0) {
        console.log(`processed ${i + 1}/${targets.length}, captured=${captured.size}, 429_hits=${rateLimitHits}`);
      }

      if ((i + 1) % CHECKPOINT_EVERY === 0) {
        saveCheckpoint(targets, i, pass);
        console.log(`[checkpoint] saved at pass=${pass}, index=${i}, captured=${captured.size}`);
      }

      // pacing to reduce burst rate
      await sleep(350);
    }
  }

  // -------- PHASE 3: normalize from captured endpoint payload --------
  const conversations = [];

  for (const t of targets) {
    const cap = captured.get(t.id);
    if (!cap) {
      conversations.push({ id: t.id, title: t.title, URL: t.URL, error: 'not_captured' });
      continue;
    }

    const items = cap?.data?.data?.grok_conversation_items_by_rest_id?.items || [];

    const normalizedItems = items.map(it => ({
      chat_item_id: it.chat_item_id,
      sender_type: it.sender_type,
      created_at_ms: it.created_at_ms,
      message: it.message || '',
      thinking_trace: it.thinking_trace || '',
      deepsearch_headers: it.deepsearch_headers || [],
      cited_web_results: it.cited_web_results || [],
      web_results: it.web_results || [],
      is_partial: !!it.is_partial,
      grok_mode: it.grok_mode || null,
    }));

    conversations.push({
      id: t.id,
      title: t.title,
      URL: t.URL,
      source_request_url: cap.requestUrl,
      item_count: normalizedItems.length,
      items: normalizedItems,
    });
  }

  const out = {
    summary: {
      exported_at: new Date().toISOString(),
      index_passes: INDEX_PASSES,
      capture_passes: 3,
      indexed_total: targets.length,
      captured_conversations: captured.size,
      missing_conversations: targets.length - captured.size,
      rate_limit_hits: rateLimitHits,
      resumed_from_checkpoint: !!checkpoint,
      index_pass_stats: passStats,
    },
    conversations,
  };

  // final checkpoint save before download
  saveCheckpoint(targets, targets.length - 1, 3);

  const blob = new Blob([JSON.stringify(out, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `grok-conversation-history-${Date.now()}.json`;
  a.click();

  // completed successfully; clear resume state
  clearCheckpoint();

  console.log('DONE', out.summary);
})();
