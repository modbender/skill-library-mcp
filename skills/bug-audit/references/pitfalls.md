# Pitfall Lookup Table

Real-world findings from auditing 200+ bugs across 30+ Node.js projects.

## High-Frequency Issues (by occurrence)

| Freq | Issue | Quick Fix |
|------|-------|-----------|
| ⭐⭐⭐ | fetch without .catch | Global search `fetch(`, add `.catch(function(){})` to each |
| ⭐⭐⭐ | destroy/splice inside forEach | Change to `.slice()` then iterate the copy |
| ⭐⭐⭐ | config.json values written but never read | `grep GAME_CONFIG` to verify each field has a reference |
| ⭐⭐⭐ | UTC vs Beijing time mixup | Use `getFullYear/getMonth/getDate`, not `toISOString` |
| ⭐⭐ | CORS origin:true reflection | Replace with whitelist array |
| ⭐⭐ | setInterval without clearInterval | Store ref, clear in matching teardown |
| ⭐⭐ | endBattle/gameOver fires multiple times | Add `_battleEnded` flag + reset in init |
| ⭐⭐ | Leaderboard N×M SQL per request | 60-second in-memory cache |
| ⭐ | Phaser canvas intercepts touch events | `pointer-events:none` + `input:{mouse:false,touch:false}` |
| ⭐ | CDN unavailable in China | Download library to server local path |
| ⭐ | Deploy overwrites SDK init code | Post-deploy check that SDK initialization still exists |
| ⭐ | JS float precision accumulation | `Math.floor()` on currency values |
| ⭐ | SQLite double quotes for strings | Use single quotes `''` (double quotes `""` = column identifiers) |
| ⭐ | Quest taskKey not whitelisted | Server-side whitelist; attacker fills progress with fake keys |
| ⭐ | Module load-time reads uninitialized config | Move config reads to runtime (inside functions, not top-level) |

## WeChat WebView Remote Debugging

WeChat WebView has no developer console. Three techniques, in order of preference:

### 1. sendBeacon Remote Logging (recommended)

```javascript
// Frontend: send logs to server
function remoteLog(msg) {
  navigator.sendBeacon('/api/debug-log', JSON.stringify({
    t: Date.now(), msg: String(msg)
  }));
}
window.onerror = function(msg, url, line) {
  remoteLog('ERR: ' + msg + ' at ' + url + ':' + line);
};
```

```javascript
// Server: store in memory, view via curl
var debugLogs = [];
app.post('/api/debug-log', function(req, res) {
  debugLogs.push(req.body);
  if (debugLogs.length > 200) debugLogs.shift();
  res.end();
});
app.get('/api/debug-log', function(req, res) {
  res.json(debugLogs.slice(-50));
});
```

View: `curl https://your-domain/api/debug-log | jq`

### 2. Inline Debug Panel

Add to `<head>` (before any other scripts):

```html
<script>
var _dbg = [];
window.onerror = function(m, u, l) {
  _dbg.push('[ERR] ' + m + ' L' + l);
  _renderDbg();
};
function _renderDbg() {
  var el = document.getElementById('_dbgPanel');
  if (!el) {
    el = document.createElement('div');
    el.id = '_dbgPanel';
    el.style.cssText = 'position:fixed;bottom:0;left:0;right:0;max-height:40vh;overflow:auto;background:#000;color:#0f0;font:12px monospace;z-index:99999;padding:8px;';
    document.body.appendChild(el);
  }
  el.innerHTML = _dbg.join('<br>');
  el.scrollTop = el.scrollHeight;
}
</script>
```

### 3. Cache Busting

WeChat caches JS aggressively. Always version your script tags:

```html
<script src="js/app.js?v=42"></script>
```

Increment `v=N` on every deploy. Also set server-side no-cache headers for `.js` and `.html` files during debugging.

## Modular Refactor Pitfalls

Common bugs introduced when splitting a single large file into modules:

1. **Variable initialization order** — Function A calls variable X, but X is assigned in Function B which loads later. Fix: reorder script tags or move initialization earlier.

2. **display toggle + immediate size read** — Setting `display:flex` then immediately reading `clientWidth` returns 0 (browser hasn't reflowed). Fix: wrap in `requestAnimationFrame`.

3. **CDN library replacement** — Switching from CDN to local copy may change API surface. Fix: `grep -c "FunctionName" library.min.js` to verify expected APIs exist.

4. **Global variable conflicts** — Two modules both declare `var config`. Fix: use unique names or namespace objects.

5. **Circular dependencies** — Module A reads from Module B at load time, but B hasn't loaded yet. Fix: defer reads to function call time.
