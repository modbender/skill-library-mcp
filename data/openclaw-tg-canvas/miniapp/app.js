// OpenClaw Canvas Mini App
// Vanilla JS client for Telegram WebApp

(() => {
  const tg = window.Telegram?.WebApp;
  // Apply Telegram theme (light/dark)
  try {
    const theme = tg?.colorScheme || (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
  } catch (_) {}

  const contentEl = document.querySelector('.content-inner');
  const connDot = document.getElementById('connDot');
  const connText = document.getElementById('connText');
  const lastUpdatedEl = document.getElementById('lastUpdated');
  const openControlBtn = document.getElementById('openControlBtn');
  const openTerminalBtn = document.getElementById('openTerminalBtn');
  const closeTerminalBtn = document.getElementById('closeTerminalBtn');
  let openingControl = false;

  let jwt = null;
  let ws = null;
  let reconnectTimer = null;
  let lastUpdatedTs = null;
  let relativeTimer = null;

  // ---------- UI Helpers ----------
  function setStatus(state) {
    connDot.classList.remove('connected', 'connecting');
    if (state === 'connected') {
      connDot.classList.add('connected');
      connText.textContent = 'Connected';
    } else if (state === 'connecting' || state === 'reconnecting') {
      connDot.classList.add('connecting');
      connText.textContent = state === 'reconnecting' ? 'Reconnecting…' : 'Connecting…';
    } else {
      connText.textContent = 'Offline';
    }
  }

  function setControlButtonLoading(isLoading) {
    if (!openControlBtn) return;
    if (isLoading) {
      openControlBtn.disabled = true;
      openControlBtn.dataset.prevText = openControlBtn.textContent || 'Control';
      openControlBtn.textContent = 'Opening…';
      openControlBtn.style.opacity = '0.75';
      openControlBtn.style.cursor = 'wait';
    } else {
      openControlBtn.disabled = false;
      openControlBtn.textContent = openControlBtn.dataset.prevText || 'Control';
      openControlBtn.style.opacity = '';
      openControlBtn.style.cursor = '';
    }
  }

  function showCenter(message, withSpinner = false, buttonText = null, buttonHandler = null, useCard = true) {
    contentEl.innerHTML = '';
    const wrap = document.createElement('div');
    wrap.className = 'center fade-in';

    let holder = wrap;
    if (useCard) {
      const card = document.createElement('div');
      card.className = 'empty-card';
      wrap.appendChild(card);
      holder = card;
    }

    if (withSpinner) {
      const spinner = document.createElement('div');
      spinner.className = 'spinner';
      holder.appendChild(spinner);
    }

    const text = document.createElement('div');
    text.textContent = message;
    holder.appendChild(text);

    if (buttonText && buttonHandler) {
      const btn = document.createElement('button');
      btn.className = 'button';
      btn.textContent = buttonText;
      btn.addEventListener('click', buttonHandler);
      holder.appendChild(btn);
    }

    contentEl.appendChild(wrap);
  }

  function formatRelative(ts) {
    if (!ts) return '—';
    const delta = Math.max(0, Date.now() - ts);
    const sec = Math.floor(delta / 1000);
    if (sec < 5) return 'just now';
    if (sec < 60) return `${sec}s ago`;
    const min = Math.floor(sec / 60);
    if (min < 60) return `${min}m ago`;
    const hr = Math.floor(min / 60);
    if (hr < 24) return `${hr}h ago`;
    const days = Math.floor(hr / 24);
    return `${days}d ago`;
  }

  function updateLastUpdated(ts) {
    lastUpdatedTs = ts || Date.now();
    lastUpdatedEl.textContent = `Last updated ${formatRelative(lastUpdatedTs)}`;
    clearInterval(relativeTimer);
    relativeTimer = setInterval(() => {
      lastUpdatedEl.textContent = `Last updated ${formatRelative(lastUpdatedTs)}`;
    }, 30000);
  }

  // ---------- Markdown Renderer (minimal) ----------
  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function renderMarkdown(md) {
    // Simple, safe markdown conversion
    const lines = md.split('\n');
    let html = '';
    let inCodeBlock = false;
    let listType = null; // 'ul' | 'ol'

    const closeList = () => {
      if (listType) {
        html += `</${listType}>`;
        listType = null;
      }
    };

    for (let i = 0; i < lines.length; i++) {
      let line = lines[i];

      // Code block (```) toggle
      if (line.trim().startsWith('```')) {
        if (!inCodeBlock) {
          closeList();
          inCodeBlock = true;
          html += '<pre><code>';
        } else {
          inCodeBlock = false;
          html += '</code></pre>';
        }
        continue;
      }

      if (inCodeBlock) {
        html += `${escapeHtml(line)}\n`;
        continue;
      }

      // Headings
      if (/^###\s+/.test(line)) {
        closeList();
        html += `<h3>${escapeHtml(line.replace(/^###\s+/, ''))}</h3>`;
        continue;
      }
      if (/^##\s+/.test(line)) {
        closeList();
        html += `<h2>${escapeHtml(line.replace(/^##\s+/, ''))}</h2>`;
        continue;
      }
      if (/^#\s+/.test(line)) {
        closeList();
        html += `<h1>${escapeHtml(line.replace(/^#\s+/, ''))}</h1>`;
        continue;
      }

      // Lists
      const ulMatch = /^-\s+/.test(line);
      const olMatch = /^\d+\.\s+/.test(line);
      if (ulMatch || olMatch) {
        const type = ulMatch ? 'ul' : 'ol';
        if (listType && listType !== type) closeList();
        if (!listType) {
          listType = type;
          html += `<${listType}>`;
        }
        const itemText = line.replace(ulMatch ? /^-\s+/ : /^\d+\.\s+/, '');
        html += `<li>${inlineMarkdown(escapeHtml(itemText))}</li>`;
        continue;
      } else {
        closeList();
      }

      // Paragraphs / blank
      if (line.trim() === '') {
        html += '<br />';
      } else {
        html += `<p>${inlineMarkdown(escapeHtml(line))}</p>`;
      }
    }

    closeList();
    return html;
  }

  function inlineMarkdown(text) {
    // bold **text**
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // italic *text*
    text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');
    // inline code `code`
    text = text.replace(/`(.+?)`/g, '<code>$1</code>');
    return text;
  }

  // ---------- Rendering ----------
  function renderA2UI(container, a2uiPayload) {
    // Optional A2UI runtime hook. If present, use it. Otherwise show JSON.
    const runtime = window.OpenClawA2UI || window.A2UI || null;
    if (runtime && typeof runtime.render === 'function') {
      try {
        runtime.render(container, a2uiPayload);
        return;
      } catch (_) {
        // fall through to JSON
      }
    }
    const pre = document.createElement('pre');
    pre.textContent = JSON.stringify(a2uiPayload, null, 2);
    container.appendChild(pre);
  }

  // ---------- Terminal ----------
  let termInstance = null;
  let termWs = null;
  let termResizeObserver = null;

  function destroyTerminal() {
    if (termResizeObserver) { try { termResizeObserver.disconnect(); } catch (_) {} termResizeObserver = null; }
    if (termWs) { try { termWs.close(); } catch (_) {} termWs = null; }
    if (termInstance) { try { termInstance.dispose(); } catch (_) {} termInstance = null; }
    const pane = document.getElementById('terminal-pane');
    pane.style.display = 'none';
    // Remove dynamically built toolbar so it's fresh on next open
    pane.querySelector('.term-toolbar')?.remove();
    document.getElementById('terminal-container').innerHTML = '';
    // Canvas content and topbar are unaffected — they stay visible underneath
  }

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      if (document.querySelector(`script[src="${src}"]`)) { resolve(); return; }
      const s = document.createElement('script');
      s.src = src;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  async function connectTerminal() {
    const pane = document.getElementById('terminal-pane');
    const containerEl = document.getElementById('terminal-container');
    containerEl.innerHTML = '';

    // Lazy-load xterm.js and FitAddon from CDN
    try {
      await loadScript('https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.js');
      await loadScript('https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.js');
    } catch (e) {
      containerEl.innerHTML = '<div style="color:#ff7b72;padding:16px">Failed to load terminal library.</div>';
      return;
    }

    // Compute font size: target ~72 cols on the current device.
    // 72 cols fits most terminal output; floor at 10px (20 physical px on retina).
    // charWidthRatio ≈ 0.6 for typical monospace fonts in xterm.js.
    const _paneW = (pane.offsetWidth || window.innerWidth) - 8;
    const _fontSize = Math.max(10, Math.min(14, Math.round(_paneW / 72 / 0.6)));

    // Init xterm
    const term = new Terminal({
      cursorBlink: true,
      fontSize: _fontSize,
      fontFamily: '"Cascadia Code", "Fira Code", "JetBrains Mono", Menlo, Monaco, "Courier New", monospace',
      theme: {
        background: '#0d1117',
        foreground: '#c9d1d9',
        cursor: '#58a6ff',
        selectionBackground: '#264f78',
        black: '#000000', red: '#ff7b72', green: '#3fb950', yellow: '#d29922',
        blue: '#58a6ff', magenta: '#bc8cff', cyan: '#39c5cf', white: '#b1bac4',
        brightBlack: '#6e7681', brightRed: '#ffa198', brightGreen: '#56d364',
        brightYellow: '#e3b341', brightBlue: '#79c0ff', brightMagenta: '#d2a8ff',
        brightCyan: '#56d4dd', brightWhite: '#ffffff',
      },
      allowTransparency: false,
      scrollback: 1000,
    });

    const fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);
    term.open(containerEl);

    // Fit after paint
    requestAnimationFrame(() => {
      fitAddon.fit();
      term.focus();
    });

    termInstance = term;

    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${proto}//${location.host}/ws/terminal?token=${encodeURIComponent(jwt)}`;
    const tws = new WebSocket(wsUrl);
    termWs = tws;

    // ---- Sticky modifiers ----
    let ctrlActive = false;
    let altActive = false;

    function setModifier(mod, on) {
      if (mod === 'ctrl') ctrlActive = on;
      if (mod === 'alt') altActive = on;
      const btn = pane.querySelector(`.tbkey[data-mod="${mod}"]`);
      if (btn) btn.classList.toggle('active', on);
    }

    function sendRaw(data) {
      if (tws.readyState === WebSocket.OPEN) {
        tws.send(JSON.stringify({ type: 'data', data }));
      }
    }

    tws.onopen = () => {
      const dims = fitAddon.proposeDimensions();
      if (dims) tws.send(JSON.stringify({ type: 'resize', cols: dims.cols, rows: dims.rows }));
    };

    tws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'data') term.write(msg.data);
        else if (msg.type === 'exit') {
          term.writeln(`\r\n\x1b[33m[Process exited with code ${msg.code}]\x1b[0m`);
        }
      } catch (_) {}
    };

    tws.onclose = () => {
      if (termInstance) termInstance.writeln('\r\n\x1b[31m[Connection closed]\x1b[0m');
    };

    // Keyboard input → WS (apply sticky modifiers)
    term.onData((data) => {
      let out = data;
      if (ctrlActive && data.length === 1) {
        out = String.fromCharCode(data.charCodeAt(0) & 0x1f);
        setModifier('ctrl', false);
      } else if (altActive && data.length === 1) {
        out = '\x1b' + data;
        setModifier('alt', false);
      }
      sendRaw(out);
    });

    // ---- Mobile toolbar ----
    const TOOLBAR_KEYS = [
      { label: 'Ctrl', mod: 'ctrl' },
      { label: 'Alt',  mod: 'alt'  },
      { label: 'Esc',  seq: '\x1b' },
      { label: 'Tab',  seq: '\t'   },
      { label: '↑',    seq: '\x1b[A', arrow: true },
      { label: '↓',    seq: '\x1b[B', arrow: true },
      { label: '←',    seq: '\x1b[D', arrow: true },
      { label: '→',    seq: '\x1b[C', arrow: true },
    ];

    const toolbar = document.createElement('div');
    toolbar.className = 'term-toolbar';

    TOOLBAR_KEYS.forEach(({ label, mod, seq, arrow }) => {
      const btn = document.createElement('button');
      btn.className = 'tbkey' + (arrow ? ' tbkey-arrow' : '') + (mod ? ' tbkey-mod' : '');
      if (mod) btn.dataset.mod = mod;
      btn.textContent = label;
      btn.addEventListener('pointerdown', (e) => {
        e.preventDefault(); // don't steal focus from xterm
        if (mod) {
          const current = mod === 'ctrl' ? ctrlActive : altActive;
          // toggle off the other modifier
          if (mod === 'ctrl' && altActive) setModifier('alt', false);
          if (mod === 'alt' && ctrlActive) setModifier('ctrl', false);
          setModifier(mod, !current);
        } else {
          sendRaw(seq);
          term.focus();
        }
      });
      toolbar.appendChild(btn);
    });

    pane.appendChild(toolbar);

    // Resize: observe pane, fit, send new dims to server
    termResizeObserver = new ResizeObserver(() => {
      try {
        fitAddon.fit();
        const dims = fitAddon.proposeDimensions();
        if (dims && tws.readyState === WebSocket.OPEN) {
          tws.send(JSON.stringify({ type: 'resize', cols: dims.cols, rows: dims.rows }));
        }
      } catch (_) {}
    });
    termResizeObserver.observe(pane);
  }

  // ---------- Rendering ----------
  function renderPayload(payload) {
    if (!payload || payload.type === 'clear') {
      destroyTerminal();
      showCenter('Waiting for content…');
      return;
    }

    const { format, content } = payload;
    contentEl.innerHTML = '';

    const container = document.createElement('div');
    container.className = 'fade-in';

    if (format === 'html') {
      // Trusted HTML from server (agent only)
      container.innerHTML = content || '';
      // Execute inline scripts (Telegram WebView doesn't run scripts from innerHTML)
      container.querySelectorAll('script').forEach((oldScript) => {
        const s = document.createElement('script');
        if (oldScript.src) s.src = oldScript.src;
        s.type = oldScript.type || 'text/javascript';
        s.text = oldScript.textContent || '';
        oldScript.replaceWith(s);
      });
    } else if (format === 'markdown') {
      container.innerHTML = renderMarkdown(content || '');
    } else if (format === 'a2ui') {
      renderA2UI(container, content || {});
    } else {
      // text
      const pre = document.createElement('pre');
      pre.textContent = content || '';
      container.appendChild(pre);
    }

    contentEl.appendChild(container);
    updateLastUpdated(Date.now());
  }

  // ---------- Auth + Networking ----------
  async function authenticate() {
    const initData = tg?.initData || '';
    try {
      const res = await fetch('/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ initData }),
      });

      if (!res.ok) throw new Error('auth_failed');
      const data = await res.json();
      if (!data?.token) throw new Error('no_token');
      jwt = data.token;

      if (openTerminalBtn) {
        openTerminalBtn.onclick = () => {
          document.getElementById('terminal-pane').style.display = 'flex';
          connectTerminal();
        };
      }

      if (closeTerminalBtn) {
        closeTerminalBtn.onclick = () => {
          destroyTerminal();
        };
      }

      if (openControlBtn) {
        openControlBtn.onclick = () => {
          if (openingControl) return;
          openingControl = true;
          setControlButtonLoading(true);
          setStatus('connecting');
          connText.textContent = 'Opening control…';

          // Open control inline in the same Mini App WebView.
          setTimeout(() => {
            const url = `/oc/?token=${encodeURIComponent(jwt)}`;
            window.location.assign(url);
          }, 80);
        };
      }

      return true;
    } catch (e) {
      return false;
    }
  }

  async function fetchState() {
    try {
      const res = await fetch(`/state?token=${encodeURIComponent(jwt)}`);
      if (!res.ok) return null;
      return await res.json();
    } catch (e) {
      return null;
    }
  }

  function connectWS() {
    if (!jwt) return;

    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${proto}//${location.host}/ws?token=${encodeURIComponent(jwt)}`;

    setStatus('connecting');
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setStatus('connected');
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'ping') return;
        if (msg.type === 'clear') {
          renderPayload({ type: 'clear' });
          return;
        }
        if (msg.type === 'canvas') {
          renderPayload(msg);
        }
      } catch (e) {
        // ignore malformed message
      }
    };

    ws.onerror = () => {
      setStatus('reconnecting');
      showCenter('Connection lost. Reconnecting…', true);
    };

    ws.onclose = () => {
      setStatus('reconnecting');
      showCenter('Connection lost. Reconnecting…', true);
      scheduleReconnect();
    };
  }

  function scheduleReconnect() {
    clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(() => {
      connectWS();
    }, 3000);
  }

  // ---------- Boot ----------
  async function boot() {
    setStatus('connecting');
    showCenter('Connecting…', true, null, null, false);

    const authed = await authenticate();
    if (!authed) {
      setStatus('disconnected');
      showCenter('Access denied', false, 'Close', () => tg?.close?.());
      return;
    }

    // Fetch current state before WS connect
    const state = await fetchState();
    if (state) renderPayload(state);
    else showCenter('Waiting for content…');

    connectWS();
  }

  boot();
})();
