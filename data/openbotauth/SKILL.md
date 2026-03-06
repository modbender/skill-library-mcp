---
name: openbotauth
description: Cryptographic identity for AI agents. Register once, then sign HTTP
  requests (RFC 9421) anywhere. Optional browser integrations via per-request
  signing proxy.
---

# openbotauth

Cryptographic identity for AI agents. Register once, then sign HTTP requests (RFC 9421) anywhere. Optional browser integrations via per-request signing proxy.

## When to trigger

User wants to: browse websites with signed identity, authenticate a browser session, sign HTTP requests as a bot, set up OpenBotAuth headers, prove human-vs-bot session origin, manage agent keys, sign scraping sessions, register with OBA registry, set up enterprise SSO for agents.

## Tools

Bash

## Instructions

This skill is **self-contained** — no npm packages required. Core mode uses Node.js (v18+) + curl; proxy mode additionally needs openssl.

### Compatibility Modes

**Core Mode (portable, recommended):**
- Works with: Claude Code, Cursor, Codex CLI, Goose, any shell-capable agent
- Uses: Node.js crypto + curl for registration
- Token needed only briefly for `POST /agents`

**Browser Mode (optional, runtime-dependent):**
- For: agent-browser, OpenClaw Browser Relay, CUA tooling
- Bearer token must NOT live inside the browsing runtime
- Do registration in CLI mode first, then browse with signatures only

### Key Storage

Keys are stored at `~/.config/openbotauth/key.json` in **OBA's canonical format**:

```json
{
  "kid": "<thumbprint-based-id>",
  "x": "<base64url-raw-public-key>",
  "publicKeyPem": "-----BEGIN PUBLIC KEY-----\n...",
  "privateKeyPem": "-----BEGIN PRIVATE KEY-----\n...",
  "createdAt": "..."
}
```

The OBA token lives at `~/.config/openbotauth/token` (chmod 600).

Agent registration info (agent_id, JWKS URL) should be saved in agent memory/notes after Step 3.

### Token Handling Contract

**The bearer token is for registration only:**
- Use it ONLY for `POST /agents` (and key rotation)
- Delete `~/.config/openbotauth/token` after registration completes
- Never attach bearer tokens to browsing sessions

**Minimum scopes:** `agents:write` + `profile:read`
- Only add `keys:write` if you need `/keys` endpoint

**Never use global headers with OBA token:**
- agent-browser's `set headers` command applies headers globally
- Use origin-scoped headers only (via `open --headers`)

---

### Step 1: Check for existing identity

```bash
cat ~/.config/openbotauth/key.json 2>/dev/null && echo "---KEY EXISTS---" || echo "---NO KEY FOUND---"
```

**If a key exists:** read it to extract `kid`, `x`, and `privateKeyPem`. Check if the agent is already registered (look for agent_id in memory/notes). If registered, skip to Step 4 (signing).

**If no key exists:** proceed to Step 2.

---

### Step 2: Generate Ed25519 keypair (if no key exists)

Run this locally. Nothing leaves the machine.

```bash
node -e "
const crypto = require('node:crypto');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const { publicKey, privateKey } = crypto.generateKeyPairSync('ed25519');
const publicKeyPem = publicKey.export({ type: 'spki', format: 'pem' }).toString();
const privateKeyPem = privateKey.export({ type: 'pkcs8', format: 'pem' }).toString();

// Derive kid from JWK thumbprint (matches OBA's format)
const spki = publicKey.export({ type: 'spki', format: 'der' });
if (spki.length !== 44) throw new Error('Unexpected SPKI length: ' + spki.length);
const rawPub = spki.subarray(12, 44);
const x = rawPub.toString('base64url');
const thumbprint = JSON.stringify({ kty: 'OKP', crv: 'Ed25519', x });
const hash = crypto.createHash('sha256').update(thumbprint).digest();
const kid = hash.toString('base64url').slice(0, 16);

const dir = path.join(os.homedir(), '.config', 'openbotauth');
fs.mkdirSync(dir, { recursive: true, mode: 0o700 });
fs.writeFileSync(path.join(dir, 'key.json'), JSON.stringify({
  kid, x, publicKeyPem, privateKeyPem,
  createdAt: new Date().toISOString()
}, null, 2), { mode: 0o600 });

console.log('Key generated!');
console.log('kid:', kid);
console.log('x:', x);
"
```

Save the `kid` and `x` values — needed for registration.

---

### Step 3: Register with OpenBotAuth (if not yet registered)

This is a **one-time setup** that gives your agent a public JWKS endpoint for signature verification.

#### 3a. Get a token from the user

Ask the user:

> I need an OpenBotAuth token to register my cryptographic identity. Takes 30 seconds:
>
> 1. Go to **https://openbotauth.org/token**
> 2. Click "Login with GitHub"
> 3. Copy the token and paste it back to me
>
> The token looks like `oba_` followed by 64 hex characters.

When they provide it, save it:

```bash
node -e "
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const dir = path.join(os.homedir(), '.config', 'openbotauth');
fs.mkdirSync(dir, { recursive: true, mode: 0o700 });
const token = process.argv[1].trim();
fs.writeFileSync(path.join(dir, 'token'), token, { mode: 0o600 });
console.log('Token saved.');
" "THE_TOKEN_HERE"
```

#### 3b. Register the agent

```bash
node -e "
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');

const dir = path.join(os.homedir(), '.config', 'openbotauth');
const key = JSON.parse(fs.readFileSync(path.join(dir, 'key.json'), 'utf-8'));
const tokenPath = path.join(dir, 'token');
const token = fs.readFileSync(tokenPath, 'utf-8').trim();

const AGENT_NAME = process.argv[1] || 'my-agent';
const API = 'https://api.openbotauth.org';

fetch(API + '/agents', {
  method: 'POST',
  redirect: 'error',  // Never follow redirects with bearer token
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: AGENT_NAME,
    agent_type: 'agent',
    public_key: {
      kty: 'OKP',
      crv: 'Ed25519',
      kid: key.kid,
      x: key.x,
      use: 'sig',
      alg: 'EdDSA'
    }
  })
})
.then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
.then(async d => {
  console.log('Agent registered!');
  console.log('Agent ID:', d.id);

  // Fetch session to get username for JWKS URL
  const session = await fetch(API + '/auth/session', {
    redirect: 'error',  // Never follow redirects with bearer token
    headers: { 'Authorization': 'Bearer ' + token }
  }).then(r => { if (!r.ok) throw new Error('Session HTTP ' + r.status); return r.json(); });
  const username = session.profile?.username || session.user?.github_username;
  if (!username) throw new Error('Could not resolve username from /auth/session');
  const jwksUrl = API + '/jwks/' + username + '.json';

  // Write config.json for the signing proxy
  fs.writeFileSync(path.join(dir, 'config.json'), JSON.stringify({
    agent_id: d.id,
    username: username,
    jwksUrl: jwksUrl
  }, null, 2), { mode: 0o600 });
  console.log('Config written to ~/.config/openbotauth/config.json');

  // Delete token — no longer needed after registration
  fs.unlinkSync(tokenPath);
  console.log('Token deleted (no longer needed)');

  console.log('');
  console.log('JWKS URL:', jwksUrl);
  console.log('');
  console.log('Save this to memory:');
  console.log(JSON.stringify({
    openbotauth: {
      agent_id: d.id,
      kid: key.kid,
      username: username,
      jwks_url: jwksUrl
    }
  }, null, 2));
})
.catch(e => console.error('Registration failed:', e.message));
" "AGENT_NAME_HERE"
```

#### 3c. Verify registration

```bash
curl https://api.openbotauth.org/jwks/YOUR_USERNAME.json
```

You should see your public key in the `keys` array. This is the URL that verifiers will use to check your signatures.

**Save the agent_id, username, and JWKS URL to memory/notes** — you'll need the JWKS URL for the `Signature-Agent` header in every signed request.

### Token Safety Rules

| Do | Don't |
|----|-------|
| `curl -H "Authorization: Bearer ..." https://api.openbotauth.org/agents` | Set bearer token as global browser header |
| Delete token after registration | Keep token in browsing session |
| Use origin-scoped headers for signing | Use `set headers` with bearer tokens |
| Store token at `~/.config/openbotauth/token` (chmod 600) | Paste token into chat logs |

---

### Step 4: Sign a request

Generate RFC 9421 signed headers for a target URL. The output is a JSON object for `agent-browser open --headers` or `set headers --json` (OpenClaw).

**Required inputs:**
- `TARGET_URL` — the URL being browsed
- `METHOD` — HTTP method (GET, POST, etc.)
- `JWKS_URL` — your JWKS endpoint from Step 3 (the `Signature-Agent` value)

```bash
node -e "
const { createPrivateKey, sign, randomUUID } = require('crypto');
const { readFileSync } = require('fs');
const { join } = require('path');
const { homedir } = require('os');

const METHOD = (process.argv[1] || 'GET').toUpperCase();
const TARGET_URL = process.argv[2];
const JWKS_URL = process.argv[3] || '';

if (!TARGET_URL) { console.error('Usage: node sign.js METHOD URL JWKS_URL'); process.exit(1); }

const key = JSON.parse(readFileSync(join(homedir(), '.config', 'openbotauth', 'key.json'), 'utf-8'));
const url = new URL(TARGET_URL);
const created = Math.floor(Date.now() / 1000);
const expires = created + 300;
const nonce = randomUUID();

// RFC 9421 signature base
const lines = [
  '\"@method\": ' + METHOD,
  '\"@authority\": ' + url.host,
  '\"@path\": ' + url.pathname + url.search
];
const sigInput = '(\"@method\" \"@authority\" \"@path\");created=' + created + ';expires=' + expires + ';nonce=\"' + nonce + '\";keyid=\"' + key.kid + '\";alg=\"ed25519\"';
lines.push('\"@signature-params\": ' + sigInput);

const base = lines.join('\n');
const pk = createPrivateKey(key.privateKeyPem);
const sig = sign(null, Buffer.from(base), pk).toString('base64');

const headers = {
  'Signature': 'sig1=:' + sig + ':',
  'Signature-Input': 'sig1=' + sigInput
};
if (JWKS_URL) {
  headers['Signature-Agent'] = JWKS_URL;
}

console.log(JSON.stringify(headers));
" "METHOD" "TARGET_URL" "JWKS_URL"
```

Replace the arguments:
- `METHOD` — e.g., `GET`
- `TARGET_URL` — e.g., `https://example.com/page`
- `JWKS_URL` — e.g., `https://api.openbotauth.org/jwks/your-username.json`

**For strict verifiers:** If a site rejects signatures from this inline signer, use `@openbotauth/bot-cli` (recommended) or the `openbotauth-demos/packages/signing-ts` reference signer.

### Step 5: Apply headers to browser session

**For single signed navigation (demo / Radar proof):**
```bash
agent-browser open <url> --headers '<OUTPUT_FROM_STEP_4>'
```
This uses origin-scoped headers (safer than global).

**For real browsing (subresources/XHR):** Use the signing proxy (Step A-C below).

**OpenClaw browser:**
```
set headers --json '<OUTPUT_FROM_STEP_4>'
```

**With named session:**
```bash
agent-browser --session myagent open <url> --headers '<OUTPUT_FROM_STEP_4>'
```

**Important: re-sign before each navigation.** Because RFC 9421 signatures are bound to `@method`, `@authority`, and `@path`, you must regenerate headers (Step 4) before navigating to a different URL. For continuous browsing, use the proxy instead.

---

### Step 6: Show current identity

```bash
node -e "
const { readFileSync, existsSync } = require('fs');
const { join } = require('path');
const { homedir } = require('os');
const f = join(homedir(), '.config', 'openbotauth', 'key.json');
if (!existsSync(f)) { console.log('No identity found. Run Step 2 first.'); process.exit(0); }
const k = JSON.parse(readFileSync(f, 'utf-8'));
console.log('kid:        ' + k.kid);
console.log('Public (x): ' + k.x);
console.log('Created:    ' + k.createdAt);
"
```

---

### Enterprise SSO Binding — Roadmap

> **Status:** Not yet implemented. This describes the planned direction.

For organizations using Okta, WorkOS, or Descope: OBA will support binding agent keys to enterprise subjects issued by your IdP. OBA is **not replacing your IdP directory** — it attaches verifiable agent keys and audit trails to identities you already manage.

**Planned flow:**
1. Authenticate via your IdP (SAML/OIDC)
2. Bind an agent public key to that enterprise subject
3. Signatures from that agent carry the enterprise identity anchor

This complements (not competes with) IdP-native agent features — you get portable keys + web verification surface.

---

### Signed Headers Reference

Every signed request produces these RFC 9421-compliant headers:

| Header | Purpose |
|--------|---------|
| `Signature` | `sig1=:<base64-ed25519-signature>:` |
| `Signature-Input` | Covered components `(@method @authority @path)`, `created`, `expires`, `nonce`, `keyid`, `alg` |
| `Signature-Agent` | JWKS URL for public key resolution (from OBA Registry) |

The `Signature-Input` encodes everything a verifier needs: which components were signed, when, by whom (keyid), and when it expires.

### OpenClaw Session Binding

When running inside OpenClaw, you can include the session key in the nonce or as a custom parameter to bind the signature to the originating chat:

```
agent:main:main                              # Main chat session
agent:main:discord:channel:123456789         # Discord channel
agent:main:subagent:<uuid>                   # Spawned sub-agent
```

This lets publishers trace whether a request came from the main agent or a sub-agent.

---

### Sub-Agent Identity (Tier 2 — TBD)

Sub-agent key derivation (HKDF from parent key) is planned but not yet implemented in a cryptographically sound way. For now, sub-agents should:

1. Generate their own independent keypair (Step 2)
2. Register separately with OBA (Step 3)
3. Optionally, the parent agent can publish a signed attestation linking the sub-agent's kid to its own

A proper delegation/attestation protocol is being designed.

---

### Per-Request Signing via Proxy (Recommended for Real Browsing)

RFC 9421 signatures are **per-request** — they are bound to the specific method, authority, and path. Setting headers once (Steps 4-5) only works for the initial page load. Sub-resources, XHRs, and redirects will carry stale signatures and get blocked.

**Solution: Start a local signing proxy.** It intercepts every HTTP/HTTPS request and adds a fresh signature automatically. No external packages needed — uses only Node.js built-ins and openssl.

#### Step A: Write the proxy to a temp file

```bash
cat > /tmp/openbotauth-proxy.mjs << 'PROXY_EOF'
import { createServer as createHttpServer, request as httpRequest } from "node:http";
import { request as httpsRequest } from "node:https";
import { createServer as createTlsServer } from "node:tls";
import { connect, isIP } from "node:net";
import { createPrivateKey, sign as cryptoSign, randomUUID, createHash } from "node:crypto";
import { readFileSync, writeFileSync, existsSync, mkdirSync, unlinkSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";
import { execFileSync } from "node:child_process";

const OBA_DIR = join(homedir(), ".config", "openbotauth");
const KEY_FILE = join(OBA_DIR, "key.json");
const CONFIG_FILE = join(OBA_DIR, "config.json");
const CA_DIR = join(OBA_DIR, "ca");
const CA_KEY = join(CA_DIR, "ca.key");
const CA_CRT = join(CA_DIR, "ca.crt");

// Load credentials
if (!existsSync(KEY_FILE)) { console.error("No key found. Run keygen first."); process.exit(1); }
const obaKey = JSON.parse(readFileSync(KEY_FILE, "utf-8"));
let jwksUrl = null;
if (existsSync(CONFIG_FILE)) { const c = JSON.parse(readFileSync(CONFIG_FILE, "utf-8")); jwksUrl = c.jwksUrl || null; }

// Strict hostname validation (blocks shell injection & path traversal)
const HOSTNAME_RE = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
function isValidHostname(h) {
  return typeof h === "string" && h.length > 0 && h.length <= 253 && (HOSTNAME_RE.test(h) || isIP(h) > 0);
}

// Ensure CA exists
mkdirSync(CA_DIR, { recursive: true, mode: 0o700 });
if (!existsSync(CA_KEY) || !existsSync(CA_CRT)) {
  console.log("Generating proxy CA certificate (one-time)...");
  execFileSync("openssl", ["req", "-x509", "-new", "-nodes", "-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:prime256v1", "-keyout", CA_KEY, "-out", CA_CRT, "-days", "3650", "-subj", "/CN=OpenBotAuth Proxy CA/O=OpenBotAuth"], { stdio: "pipe" });
  execFileSync("chmod", ["600", CA_KEY], { stdio: "pipe" });
}

// Per-domain cert cache
const certCache = new Map();
function getDomainCert(hostname) {
  if (!isValidHostname(hostname)) throw new Error("Invalid hostname: " + hostname.slice(0, 50));
  if (certCache.has(hostname)) return certCache.get(hostname);
  // Use hash for filenames to prevent path traversal
  const hHash = createHash("sha256").update(hostname).digest("hex").slice(0, 16);
  const tk = join(CA_DIR, `_t_${hHash}.key`), tc = join(CA_DIR, `_t_${hHash}.csr`);
  const to = join(CA_DIR, `_t_${hHash}.crt`), te = join(CA_DIR, `_t_${hHash}.ext`);
  try {
    execFileSync("openssl", ["ecparam", "-genkey", "-name", "prime256v1", "-noout", "-out", tk], { stdio: "pipe" });
    execFileSync("openssl", ["req", "-new", "-key", tk, "-out", tc, "-subj", `/CN=${hostname}`], { stdio: "pipe" });
    writeFileSync(te, `subjectAltName=DNS:${hostname}\nbasicConstraints=CA:FALSE\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth`);
    execFileSync("openssl", ["x509", "-req", "-sha256", "-in", tc, "-CA", CA_CRT, "-CAkey", CA_KEY, "-CAcreateserial", "-out", to, "-days", "365", "-extfile", te], { stdio: "pipe" });
    const r = { key: readFileSync(tk, "utf-8"), cert: readFileSync(to, "utf-8") };
    certCache.set(hostname, r);
    return r;
  } finally { for (const f of [tk, tc, to, te]) try { unlinkSync(f); } catch {} }
}

// RFC 9421 signing
function signReq(method, authority, path) {
  const created = Math.floor(Date.now() / 1000), expires = created + 300, nonce = randomUUID();
  const lines = [`"@method": ${method.toUpperCase()}`, `"@authority": ${authority}`, `"@path": ${path}`];
  const sigInput = `("@method" "@authority" "@path");created=${created};expires=${expires};nonce="${nonce}";keyid="${obaKey.kid}";alg="ed25519"`;
  lines.push(`"@signature-params": ${sigInput}`);
  const sig = cryptoSign(null, Buffer.from(lines.join("\n")), createPrivateKey(obaKey.privateKeyPem)).toString("base64");
  const h = { signature: `sig1=:${sig}:`, "signature-input": `sig1=${sigInput}` };
  if (jwksUrl) h["signature-agent"] = jwksUrl;
  return h;
}

const verbose = process.argv.includes("--verbose") || process.argv.includes("-v");
const port = parseInt(process.argv.find((a,i) => process.argv[i-1] === "--port")) || 8421;
let rc = 0;
function log(id, msg) { if (verbose) console.log(`[${id}] ${msg}`); }

const server = createHttpServer((cReq, cRes) => {
  const id = ++rc, url = new URL(cReq.url), auth = url.host, p = url.pathname + url.search;
  const sig = signReq(cReq.method, auth, p);
  log(id, `HTTP ${cReq.method} ${auth}${p} → signed`);
  const h = { ...cReq.headers }; delete h["proxy-connection"]; delete h["proxy-authorization"];
  Object.assign(h, sig); h.host = auth;
  const fn = url.protocol === "https:" ? httpsRequest : httpRequest;
  const pr = fn({ hostname: url.hostname, port: url.port || (url.protocol === "https:" ? 443 : 80), path: p, method: cReq.method, headers: h }, (r) => { cRes.writeHead(r.statusCode, r.headers); r.pipe(cRes); });
  pr.on("error", (e) => { log(id, `Error: ${e.message}`); cRes.writeHead(502); cRes.end("Proxy error"); });
  cReq.pipe(pr);
});

server.on("connect", (req, cSock, head) => {
  const id = ++rc, [host, ps] = req.url.split(":"), tp = parseInt(ps) || 443;
  // Validate host and port before processing
  if (!isValidHostname(host) || tp < 1 || tp > 65535) {
    log(id, `CONNECT rejected: invalid ${host}:${tp}`);
    cSock.write("HTTP/1.1 400 Bad Request\r\n\r\n"); cSock.end(); return;
  }
  log(id, `CONNECT ${host}:${tp} → MITM`);
  cSock.write("HTTP/1.1 200 Connection Established\r\nProxy-Agent: openbotauth-proxy\r\n\r\n");
  const dc = getDomainCert(host);
  const tls = createTlsServer({ key: dc.key, cert: dc.cert }, (ts) => {
    let data = Buffer.alloc(0);
    ts.on("data", (chunk) => {
      data = Buffer.concat([data, chunk]);
      const he = data.indexOf("\r\n\r\n");
      if (he === -1) return;
      const hs = data.subarray(0, he).toString(), body = data.subarray(he + 4);
      const ls = hs.split("\r\n"), [method, path] = ls[0].split(" ");
      const rh = {};
      for (let i = 1; i < ls.length; i++) { const c = ls[i].indexOf(":"); if (c > 0) rh[ls[i].substring(0, c).trim().toLowerCase()] = ls[i].substring(c + 1).trim(); }
      const cl = parseInt(rh["content-length"]) || 0, fp = path || "/";
      const sig = signReq(method, host + (tp !== 443 ? `:${tp}` : ""), fp);
      log(id, `HTTPS ${method} ${host}${fp} → signed`);
      Object.assign(rh, sig);
      const pr = httpsRequest({ hostname: host, port: tp, path: fp, method, headers: rh, rejectUnauthorized: true }, (r) => {
        let resp = `HTTP/1.1 ${r.statusCode} ${r.statusMessage}\r\n`;
        const rw = r.rawHeaders; for (let i = 0; i < rw.length; i += 2) resp += `${rw[i]}: ${rw[i+1]}\r\n`;
        resp += "\r\n"; ts.write(resp); r.pipe(ts);
      });
      pr.on("error", (e) => { log(id, `Error: ${e.message}`); ts.end("HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n"); });
      if (body.length > 0) pr.write(body);
      if (cl <= body.length) { pr.end(); } else {
        let recv = body.length;
        const bh = (d) => { recv += d.length; pr.write(d); if (recv >= cl) { pr.end(); ts.removeListener("data", bh); } };
        ts.on("data", bh);
      }
    });
  });
  tls.listen(0, "127.0.0.1", () => {
    const lc = connect(tls.address().port, "127.0.0.1", () => { lc.write(head); lc.pipe(cSock); cSock.pipe(lc); });
    lc.on("error", () => cSock.end()); cSock.on("error", () => lc.end());
    cSock.on("close", () => { tls.close(); lc.end(); });
  });
});

server.listen(port, "127.0.0.1", () => {
  console.log(`openbotauth signing proxy on http://127.0.0.1:${port}`);
  console.log(`  kid: ${obaKey.kid}`);
  if (jwksUrl) console.log(`  Signature-Agent: ${jwksUrl}`);
  console.log("Every request gets a fresh RFC 9421 signature.");
});
PROXY_EOF
echo "Proxy written to /tmp/openbotauth-proxy.mjs"
```

#### Step B: Start the proxy

```bash
node /tmp/openbotauth-proxy.mjs --verbose
```

This starts the signing proxy on `127.0.0.1:8421`. Every HTTP and HTTPS request flowing through it gets a fresh RFC 9421 Ed25519 signature.

#### Step C: Browse through the proxy

In another terminal (or from agent-browser):

```bash
# For demos (ignore cert warnings):
agent-browser --proxy http://127.0.0.1:8421 --ignore-https-errors open https://example.com

# For production: install ~/.config/openbotauth/ca/ca.crt as trusted CA
```

**TLS Note:** The proxy MITMs HTTPS by generating per-domain certs signed by a local CA. Either:
- Use `--ignore-https-errors` for demos/testing
- Install `~/.config/openbotauth/ca/ca.crt` as a trusted CA for clean operation

The proxy:
- Signs **every** outgoing request with a fresh RFC 9421 signature
- Handles both HTTP and HTTPS (generates a local CA for HTTPS MITM)
- Includes the `Signature-Agent` header (JWKS URL) on every request
- Runs on `127.0.0.1:8421` by default (configurable with `--port`)
- Requires openssl (pre-installed on macOS/Linux) for HTTPS certificate generation

**Security warning:** `~/.config/openbotauth/ca/ca.key` is a local MITM root key. Treat it as sensitive as a private key — if stolen, an attacker can intercept traffic on that machine.

**Limitations:**
- HTTP/2, WebSockets, and multiplexed connections are not reliably supported
- Best for demos and basic browsing; not a production-grade proxy
- **IP-based hostnames:** If the CONNECT target is an IP address, consider rejecting it or use `subjectAltName=IP:<ip>` instead of `DNS:` (current code uses DNS, which strict clients may reject)

**When to use Steps 4-5 instead:** Simple single-page-load scenarios where you control every navigation and can re-sign before each one.

---

### Important Notes

- Private keys live at `~/.config/openbotauth/key.json` with 0600 permissions — never expose them
- The OBA token at `~/.config/openbotauth/token` is also sensitive — never log or share it
- `Signature-Agent` must point to a publicly reachable JWKS URL for verification to work
- All crypto uses Node.js built-in `crypto` module — no npm dependencies required
- **Security:** Never send private keys or OBA tokens to any domain other than `api.openbotauth.org`
- **Token lifecycle:** Delete `~/.config/openbotauth/token` after registration. You won't need it for signing.
- **Browser sessions:** After registration, only signatures travel over the wire. The token stays local and should be deleted.
- **Global headers warning:** Never use `set headers` with bearer tokens in agent-browser. Use `open --headers` for origin-scoped injection.

---

### File Layout

```
~/.config/openbotauth/
├── key.json       # kid, x, publicKeyPem, privateKeyPem (chmod 600)
├── key.pub.json   # Public JWK for sharing (chmod 644)
├── config.json    # Agent ID, JWKS URL, registration info
├── token          # oba_xxx bearer token (chmod 600)
└── ca/            # Proxy CA certificate (auto-generated)
    ├── ca.key     # CA private key
    └── ca.crt     # CA certificate
```

### Runtime Compatibility

| Runtime | Support | Notes |
|---------|---------|-------|
| Claude Code / Cursor / Codex | ✅ Full | Recommended path - CLI registration |
| agent-browser | ✅ Full | Use scoped headers, not global |
| OpenClaw Browser Relay | ✅ After registration | Register via CLI first |
| CUA / Browser Control | ⚠️ Caution | Treat control plane as hostile |
| skills.sh | ✅ Full | curl-based registration is safe |

**For browser runtimes:** Complete registration in CLI mode. The signing proxy only needs the private key (local) and JWKS URL (public). No bearer token needed during browsing.

### Official Packages

For production integrations, prefer the official packages:
- `@openbotauth/verifier-client` — verify signatures
- `@openbotauth/registry-signer` — key generation and JWK utilities
- `@openbotauth/bot-cli` — CLI for signing requests
- `@openbotauth/proxy` — signing proxy

For strict RFC 9421 signing, use the reference signer from `openbotauth-demos` (`packages/signing-ts`).

### Links

- **Website:** https://openbotauth.org
- **API:** https://api.openbotauth.org
- **Spec:** https://github.com/OpenBotAuth/openbotauth
- **IETF:** Web Bot Auth Architecture draft
