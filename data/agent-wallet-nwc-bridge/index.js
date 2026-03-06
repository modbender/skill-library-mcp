#!/usr/bin/env node
/**
 * agent-wallet-nwc-bridge — minimal NIP-47 (Nostr Wallet Connect) bridge for @moneydevkit/agent-wallet
 *
 * Commands:
 *   node index.js init --relay wss://relay.damus.io
 *   node index.js new-connection --name stacker --budget-sats 2000
 *   node index.js run
 *
 * State is stored in ./state.json (contains wallet service secret key).
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { SimplePool, finalizeEvent, generateSecretKey, getPublicKey, nip44, nip04 } = require('nostr-tools');
const { spawnSync } = require('child_process');

const DEFAULT_STATE_PATH = path.join(__dirname, 'state.json');

function getStatePath() {
  const idx = process.argv.indexOf('--state');
  if (idx !== -1 && process.argv[idx + 1]) return process.argv[idx + 1];
  if (process.env.NWC_STATE && process.env.NWC_STATE.trim()) return process.env.NWC_STATE.trim();
  return DEFAULT_STATE_PATH;
}

const STATE_PATH = getStatePath();

function die(msg) {
  console.error(msg);
  process.exit(1);
}

function loadState() {
  if (!fs.existsSync(STATE_PATH)) return null;
  return JSON.parse(fs.readFileSync(STATE_PATH, 'utf8'));
}

function saveState(state) {
  fs.writeFileSync(STATE_PATH, JSON.stringify(state, null, 2));
}

function randHex(bytes) {
  return crypto.randomBytes(bytes).toString('hex');
}

function toHex(u8) {
  return Buffer.from(u8).toString('hex');
}

function fromHex(hex) {
  return Uint8Array.from(Buffer.from(hex, 'hex'));
}

function now() {
  return Math.floor(Date.now() / 1000);
}

function runAgentWallet(args) {
  const res = spawnSync('npx', ['-y', '@moneydevkit/agent-wallet', ...args], {
    encoding: 'utf8',
    maxBuffer: 5 * 1024 * 1024,
  });
  if (res.status !== 0) {
    throw new Error((res.stderr || '').trim() || `agent-wallet failed (${res.status})`);
  }
  const out = (res.stdout || '').trim();
  if (!out) return null;
  return JSON.parse(out);
}

function satsBalance() {
  const j = runAgentWallet(['balance']);
  return Number(j.balance_sats);
}

async function main() {
  const [,, cmd, ...rest] = process.argv;
  if (!cmd || ['-h', '--help', 'help'].includes(cmd)) {
    console.log(`Usage:
  node index.js init --relay <wss://...> [--relay <wss://...> ...] [--state <path>]
  node index.js new-connection --name <label> [--budget-sats <n>] [--state <path>]
  node index.js run [--state <path>]

Env overrides:
  NWC_STATE=<path>        (state file path)
  NWC_RELAYS=wss://a,wss://b   (overrides relays from state)

State file: ${STATE_PATH}
`);
    process.exit(0);
  }

  if (cmd === 'init') {
    const relays = [];
    for (let i = 0; i < rest.length; i++) {
      if (rest[i] === '--relay') {
        relays.push(rest[i + 1]);
        i++;
      }
    }
    if (relays.length === 0) {
      const envRelays = (process.env.NWC_RELAYS || '').split(',').map(s => s.trim()).filter(Boolean);
      relays.push(...envRelays);
    }
    if (relays.length === 0) die('init requires at least one --relay wss://... (or set NWC_RELAYS)');

    const sk = generateSecretKey();
    const pk = getPublicKey(sk);

    const state = {
      version: 1,
      created_at: new Date().toISOString(),
      wallet_service: {
        sk_hex: toHex(sk),
        pk,
      },
      relays,
      // connections keyed by client pubkey
      connections: {}
    };

    // Sanity: ensure agent-wallet daemon is reachable
    try {
      satsBalance();
    } catch (e) {
      die(`agent-wallet not ready: ${e.message}`);
    }

    saveState(state);
    console.log(JSON.stringify({ ok: true, wallet_service_pubkey: pk, relays }, null, 2));
    return;
  }

  const state = loadState();
  if (!state) die('Missing state.json. Run: node index.js init --relay wss://...');

  if (cmd === 'new-connection') {
    let name = null;
    let budgetSats = null;
    for (let i = 0; i < rest.length; i++) {
      if (rest[i] === '--name') { name = rest[i + 1]; i++; }
      else if (rest[i] === '--budget-sats') { budgetSats = Number(rest[i + 1]); i++; }
    }
    if (!name) die('new-connection requires --name');

    // In NWC URI, `secret` is the *client* secret key. We'll generate it and store its pubkey as connection id.
    const clientSecret = fromHex(randHex(32));
    const clientPub = getPublicKey(clientSecret);

    // Optional per-connection method allowlist.
    // Stacker.News NWC flow uses separate steps for send vs receive; it expects different permissions.
    // Heuristic: if name contains "recv"/"receive" -> disallow spending (no pay_invoice).
    // if name contains "send" -> allow spending only.
    let allow_methods = null;
    const lname = name.toLowerCase();
    if (lname.includes('recv') || lname.includes('receive')) {
      // Receiver connection must NOT allow any spending methods (SN validates this).
      allow_methods = ['make_invoice', 'get_balance', 'get_info'];
    } else if (lname.includes('send')) {
      // Sender connection must allow spending.
      // SN send validation checks only `pay_invoice`.
      allow_methods = ['pay_invoice', 'get_balance', 'get_info'];
    }

    state.connections[clientPub] = {
      name,
      created_at: new Date().toISOString(),
      budget_sats: Number.isFinite(budgetSats) ? budgetSats : null,
      spent_sats: 0,
      allow_methods,
    };
    saveState(state);

    const qs = new URLSearchParams();
    const envRelays = (process.env.NWC_RELAYS || '').split(',').map(s => s.trim()).filter(Boolean);
    const connRelays = envRelays.length ? envRelays : state.relays;
    for (const r of connRelays) qs.append('relay', r);
    // De-facto standard (e.g. getAlby/js-sdk) also includes the client pubkey in the URI.
    // Stacker.News appears to depend on this for validation / keyHash.
    qs.set('pubkey', clientPub);
    qs.set('secret', toHex(clientSecret));
    const uri = `nostr+walletconnect://${state.wallet_service.pk}?${qs.toString()}`;

    console.log(JSON.stringify({ ok: true, name, client_pubkey: clientPub, uri }, null, 2));
    return;
  }

  if (cmd !== 'run') die(`Unknown command: ${cmd}`);

  const pool = new SimplePool();
  const relays = (process.env.NWC_RELAYS || '').split(',').map(s => s.trim()).filter(Boolean);
  const effectiveRelays = relays.length ? relays : state.relays;
  const wsSk = fromHex(state.wallet_service.sk_hex);
  const wsPk = state.wallet_service.pk;

  console.log(`agent-wallet-nwc-bridge running as wallet service pubkey: ${wsPk}`);
  console.log(`relays: ${effectiveRelays.join(', ')}`);

  // Publish info event (replaceable)
  // We claim support for: pay_invoice, make_invoice, get_balance, get_info
  const infoEvent = finalizeEvent({
    kind: 13194,
    created_at: now(),
    tags: [
      ['encryption', 'nip04 nip44_v2'],
      ['notifications', 'payment_sent payment_received'],
    ],
    content: 'pay_invoice make_invoice get_balance get_info',
    pubkey: wsPk,
  }, wsSk);

  await pool.publish(effectiveRelays, infoEvent);

  // Subscribe for requests addressed to us
  const sub = pool.subscribeMany(effectiveRelays, { kinds: [23194], '#p': [wsPk] }, {
    onevent: async (ev) => {
      try {
        console.log(`[nwc] request event id=${ev.id} from=${ev.pubkey} tags=${(ev.tags||[]).map(t=>t[0]).join(',')}`);
        // Determine requested encryption
        const encTag = (ev.tags || []).find(t => t[0] === 'encryption');
        const enc = encTag ? encTag[1] : 'nip04';

        // In NWC, the requester is the *client pubkey*.
        // Response must be encrypted to that client pubkey.
        const clientPub = ev.pubkey;
        if (!state.connections[clientPub]) {
          if ((process.env.NWC_AUTO_REGISTER || '').toLowerCase() === '1' || (process.env.NWC_AUTO_REGISTER || '').toLowerCase() === 'true') {
            const defaultBudget = Number(process.env.NWC_DEFAULT_BUDGET_SATS || 0) || null;
            state.connections[clientPub] = {
              name: process.env.NWC_AUTO_REGISTER_NAME || 'auto',
              created_at: new Date().toISOString(),
              budget_sats: defaultBudget,
              spent_sats: 0,
            };
            saveState(state);
            console.log(`[nwc] auto-registered client pubkey: ${clientPub} (budget_sats=${defaultBudget})`);
          } else {
            await sendError(ev, clientPub, enc, 'UNAUTHORIZED', 'Unknown client pubkey / no connection', 'get_info');
            return;
          }
        }

        let decrypted;
        let payload;
        if (enc.startsWith('nip44')) {
          decrypted = nip44.decrypt(ev.content, wsSk, clientPub);
        } else {
          decrypted = await nip04.decrypt(wsSk, clientPub, ev.content);
        }
        console.log(`[nwc] decrypted (enc=${enc}) len=${decrypted?.length || 0}`);
        payload = JSON.parse(decrypted);

        const { method, params } = payload;
        console.log(`[nwc] payload=${JSON.stringify(payload)}`);
        console.log(`[nwc] method=${method}`);
        const conn = state.connections[clientPub];

        if (method === 'get_balance') {
          const balance = satsBalance();
          await sendResult(ev, clientPub, enc, 'get_balance', { balance });
          return;
        }

        if (method === 'get_info') {
          // NIP-47 get_info response: different libs/clients use different field names.
          // Provide both `methods` (per spec) and `supported` (some libs expect this).
          const defaultMethods = ['pay_invoice', 'make_invoice', 'get_balance', 'get_info'];
          const methods = Array.isArray(conn.allow_methods) && conn.allow_methods.length ? conn.allow_methods : defaultMethods;
          console.log(`[nwc] get_info methods=${methods.join(',')}`);
          await sendResult(ev, clientPub, enc, 'get_info', {
            alias: 'agent-wallet',
            color: '#FF4500',
            pubkey: wsPk,
            network: 'mainnet',
            methods,
            supported: methods,
          });
          return;
        }

        if (method === 'make_invoice') {
          const amount = Number(params?.amount);
          const description = (params?.description || '').toString();
          if (!Number.isFinite(amount) || amount <= 0) {
            await sendError(ev, clientPub, enc, 'OTHER', 'make_invoice requires params.amount (msats) > 0', 'make_invoice');
            return;
          }
          const sats = Math.ceil(amount / 1000);
          const j = runAgentWallet(['receive', String(sats), '--description', description || 'NWC invoice']);
          await sendResult(ev, clientPub, enc, 'make_invoice', { invoice: j.invoice, payment_hash: j.payment_hash });
          return;
        }

        if (method === 'pay_invoice') {
          const invoice = (params?.invoice || '').toString().trim();
          if (!invoice) {
            await sendError(ev, clientPub, enc, 'OTHER', 'pay_invoice requires params.invoice', 'pay_invoice');
            return;
          }

          // Basic quota enforcement (best-effort): we cannot know final fees; agent-wallet will enforce balance.
          if (conn.budget_sats != null && conn.spent_sats >= conn.budget_sats) {
            await sendError(ev, clientPub, enc, 'QUOTA_EXCEEDED', `Budget exceeded (${conn.spent_sats}/${conn.budget_sats} sats)`, 'pay_invoice');
            return;
          }

          const j = runAgentWallet(['send', invoice]);
          // Try to record amount if agent-wallet returns it (not guaranteed)
          const amt = Number(j.amountSats || j.amount_sats || 0);
          if (amt > 0) conn.spent_sats += amt;
          state.connections[clientPub] = conn;
          saveState(state);

          await sendResult(ev, clientPub, enc, 'pay_invoice', { preimage: j.preimage || null, payment_hash: j.payment_hash || j.paymentHash || null });
          return;
        }

        await sendError(ev, clientPub, enc, 'NOT_IMPLEMENTED', `Method not implemented: ${method}`, method || 'unknown');
      } catch (e) {
        console.error('[nwc] handler error:', e && (e.stack || e.message || e));
        try {
          const clientPub = ev.pubkey;
          const encTag = (ev.tags || []).find(t => t[0] === 'encryption');
          const enc = encTag ? encTag[1] : 'nip04';
          await sendError(ev, clientPub, enc, 'INTERNAL', (e && e.message) ? e.message : String(e), 'unknown');
        } catch (e2) {
          console.error('[nwc] failed to send error response:', e2 && (e2.stack || e2.message || e2));
        }
      }
    }
  });

  async function sendResult(reqEvent, clientPub, enc, resultType, result) {
    const payload = { result_type: resultType, error: null, result };
    await sendResponse(reqEvent, clientPub, enc, payload);
  }

  async function sendError(reqEvent, clientPub, enc, code, message, resultType) {
    const payload = { result_type: resultType, error: { code, message }, result: null };
    console.log(`[nwc] sendError to=${clientPub} code=${code} msg=${message} result_type=${resultType}`);
    await sendResponse(reqEvent, clientPub, enc, payload);
  }

  async function sendResponse(reqEvent, clientPub, enc, payloadObj) {
    let content;
    if (enc && enc.startsWith('nip44')) {
      content = nip44.encrypt(JSON.stringify(payloadObj), wsSk, clientPub);
    } else {
      content = await nip04.encrypt(wsSk, clientPub, JSON.stringify(payloadObj));
    }

    // Per NIP-47, responses (kind 23195) should be addressed to the requester (client) pubkey.
    // Keep tags minimal: one `p` (client) + one `e` (request id). Extra `p` tags can confuse clients.
    // NOTE: Some real-world implementations (e.g. getAlby/js-sdk) send NIP-47 responses with ONLY an `e` tag.
    // Although the spec suggests a `p` tag, Stacker.News seems to reject our responses when `p` is present.
    // So we mimic the de-facto behavior for compatibility.
    const tags = [
      ['e', reqEvent.id],
      ...(enc && enc.startsWith('nip44') ? [['encryption', enc]] : []),
    ];

    const resp = finalizeEvent({
      kind: 23195,
      created_at: now(),
      tags,
      content,
      pubkey: wsPk,
    }, wsSk);

    await pool.publish(effectiveRelays, resp);
    console.log(`[nwc] responded to=${clientPub} kind=23195 e=${reqEvent.id}`);
  }

  process.on('SIGINT', () => {
    try { sub.close(); } catch (_) {}
    try { pool.close(effectiveRelays); } catch (_) {}
    process.exit(0);
  });

  // Keep alive
  setInterval(() => {}, 1 << 30);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
