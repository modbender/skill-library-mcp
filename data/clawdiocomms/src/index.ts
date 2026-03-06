import { EventEmitter } from 'events';
import * as fs from 'fs';
import * as path from 'path';
import { NoiseXXHandshake, TransportCipher, KeyPair, fingerprint, safetyNumber,
         toHex, fromHex, toBase64, fromBase64, init, generateKeyPair } from './crypto.js';
import { ClawdioOptions, AgentMessage, Peer, PeerStatus, ConnectionRequest,
         TrustLevel, TrustedPeerRecord, IdentityData, WireMessage, SendHandler } from './types.js';
export { AgentMessage, ClawdioOptions, PeerStatus, ConnectionRequest, TrustLevel,
         TrustedPeerRecord, IdentityData, SendHandler } from './types.js';

interface PendingHS { noise: NoiseXXHandshake; isInitiator: boolean; resolve?: (id: string) => void; }
interface PendingConsent { peer: Peer; queue: Array<{ payload: string; nonce: string; counter: string }>; }

const WORDS = ['apple','brave','coral','delta','eagle','flame','grape','haven','ivory','jewel',
  'karma','lemon','maple','night','ocean','pearl','quilt','river','storm','tiger',
  'ultra','vivid','waltz','xenon','yield','zephyr','amber','blaze','cedar','drift',
  'ember','frost','globe','haste','index','joker','kneel','lunar','marsh','noble',
  'orbit','prism','quest','reign','sonic','torch','umbra','vigor','wheat','xenial',
  'yacht','azure','birch','crane','dusk','elfin','flora','glyph','heron','isle',
  'jade','kite','lotus','mirth','nexus','onyx'];

export class Clawdio extends EventEmitter {
  private kp!: KeyPair;
  private peers = new Map<string, Peer>();
  private hs = new Map<string, PendingHS>();
  private consent = new Map<string, PendingConsent>();
  private trusted = new Map<string, TrustedPeerRecord>();
  private owner?: string;
  private idPath?: string;
  private autoAccept: boolean;
  private lastSeen = new Map<string, number>();
  private hbTimer: ReturnType<typeof setInterval> | null = null;
  private hbMs: number;
  private hbTimeout: number;
  private _send: SendHandler | null = null;

  constructor(private opts: ClawdioOptions = {}) {
    super();
    this.hbMs = opts.heartbeatMs ?? 5000;
    this.hbTimeout = opts.heartbeatTimeout ?? 15000;
    this.idPath = opts.identityPath;
    this.autoAccept = opts.autoAccept ?? false;
    this.owner = opts.owner;
  }

  static async create(opts?: ClawdioOptions): Promise<Clawdio> {
    const n = new Clawdio(opts); await n.init(); return n;
  }

  get publicKey(): string { return toHex(this.kp.publicKey); }
  get peerId(): string { return this.publicKey; }
  onSend(h: SendHandler): void { this._send = h; }
  onMessage(h: (msg: AgentMessage, from: string) => void): void { this.on('message', h); }
  setOwner(n: string): void { this.owner = n; this.save(); }
  getOwner(): string | undefined { return this.owner; }
  getPeerTrust(id: string): TrustLevel | null { return this.trusted.get(id)?.trust ?? null; }

  private async init(): Promise<void> {
    await init();
    if (this.idPath && fs.existsSync(this.idPath)) {
      const d: IdentityData = JSON.parse(fs.readFileSync(this.idPath, 'utf8'));
      this.kp = { publicKey: fromHex(d.publicKey), secretKey: fromHex(d.secretKey) };
      this.owner = d.owner ?? this.owner;
      for (const t of (d.trustedPeers ?? [])) this.trusted.set(t.id, t);
    } else { this.kp = generateKeyPair(); }
    this.hbTimer = setInterval(() => {
      const now = Date.now();
      for (const [id] of this.peers) {
        this.wire(id, { type: 'ping', payload: now.toString() });
        const l = this.lastSeen.get(id);
        if (l && now - l > this.hbTimeout) this.emit('peerDown', id);
      }
    }, this.hbMs);
    if (this.idPath) this.save();
  }

  receive(from: string, b64: string): void {
    try { this.handle(from, JSON.parse(Buffer.from(b64, 'base64').toString())); }
    catch (e) { this.emit('error', e); }
  }

  async connect(peerId: string): Promise<string> {
    const noise = new NoiseXXHandshake(this.kp);
    const msg1 = noise.writeMessage1();
    return new Promise((resolve, reject) => {
      const t = setTimeout(() => { this.hs.delete(peerId); reject(new Error('Handshake timeout')); }, 10000);
      this.hs.set(peerId, { noise, isInitiator: true, resolve: (id) => { clearTimeout(t); resolve(id); } });
      this.wire(peerId, { type: 'noise1', payload: toBase64(msg1) });
    });
  }

  async send(peerId: string, msg: AgentMessage | string): Promise<void> {
    const p = this.peers.get(peerId);
    if (!p) throw new Error(`Unknown peer: ${peerId}`);
    const payload = typeof msg === 'string' ? JSON.stringify({ task: msg }) : JSON.stringify(msg);
    const { ciphertext, nonce, counter } = p.cipher.encrypt(payload);
    this.wire(peerId, { type: 'message', payload: toBase64(ciphertext), nonce: toBase64(nonce), counter });
  }

  getVerificationCode(peerId: string): string {
    const p = this.peers.get(peerId);
    if (!p) throw new Error(`Unknown peer: ${peerId}`);
    const sorted = Buffer.compare(Buffer.from(this.kp.publicKey), Buffer.from(p.staticKey)) < 0
      ? new Uint8Array([...this.kp.publicKey, ...p.staticKey]) : new Uint8Array([...p.staticKey, ...this.kp.publicKey]);
    const hash = require('libsodium-wrappers').crypto_generichash(12, sorted);
    const w: string[] = [];
    for (let i = 0; i < 12; i += 2) w.push(WORDS[((hash[i] << 8) | hash[i + 1]) % WORDS.length]);
    return w.join(' ');
  }

  verifyPeer(id: string): void {
    const r = this.trusted.get(id);
    if (!r) throw new Error(`Peer not trusted: ${id}`);
    r.trust = 'human-verified'; this.save();
  }

  acceptPeer(id: string): void {
    const c = this.consent.get(id);
    if (!c) throw new Error(`No pending connection from: ${id}`);
    this.trusted.set(id, { id, trust: 'accepted', addedAt: new Date().toISOString() });
    this.peers.set(id, c.peer); this.lastSeen.set(id, Date.now());
    this.consent.delete(id); this.save(); this.emit('peer', id);
    for (const q of c.queue) this.decryptMsg(c.peer, q);
  }

  rejectPeer(id: string): void {
    if (!this.consent.has(id)) throw new Error(`No pending connection from: ${id}`);
    this.consent.delete(id); this.emit('peerRejected', id);
  }

  getFingerprint(id: string): string {
    const p = this.peers.get(id); if (!p) throw new Error(`Unknown peer: ${id}`);
    return fingerprint(this.kp.publicKey, p.staticKey);
  }
  getSafetyNumber(id: string): string {
    const p = this.peers.get(id); if (!p) throw new Error(`Unknown peer: ${id}`);
    return safetyNumber(this.kp.publicKey, p.staticKey);
  }
  getPeerStatus(id: string): PeerStatus {
    const l = this.lastSeen.get(id); if (!l) return 'down';
    const e = Date.now() - l;
    return e <= this.hbMs * 2 ? 'alive' : e <= this.hbTimeout ? 'stale' : 'down';
  }

  async stop(): Promise<void> {
    if (this.hbTimer) { clearInterval(this.hbTimer); this.hbTimer = null; }
    this.peers.clear(); this.hs.clear(); this.consent.clear(); this.lastSeen.clear();
  }

  // --- internals ---
  private wire(id: string, w: WireMessage): void {
    const b = Buffer.from(JSON.stringify(w)).toString('base64');
    if (this._send) this._send(id, b); else this.emit('_send', id, b);
  }

  private handle(from: string, w: WireMessage): void {
    if (w.type === 'ping') { this.wire(from, { type: 'pong', payload: w.payload }); this.lastSeen.set(from, Date.now()); }
    else if (w.type === 'pong') { this.lastSeen.set(from, Date.now()); }
    else if (w.type === 'noise1') {
      const noise = new NoiseXXHandshake(this.kp);
      noise.readMessage1(fromBase64(w.payload));
      this.hs.set(from, { noise, isInitiator: false });
      this.wire(from, { type: 'noise2', payload: toBase64(noise.writeMessage2()) });
    } else if (w.type === 'noise2') {
      const h = this.hs.get(from); if (!h) return;
      h.noise.readMessage2(fromBase64(w.payload));
      this.wire(from, { type: 'noise3', payload: toBase64(h.noise.writeMessage3()) });
      this.finish(from, h);
    } else if (w.type === 'noise3') {
      const h = this.hs.get(from); if (!h) return;
      h.noise.readMessage3(fromBase64(w.payload));
      this.finish(from, h);
    } else if (w.type === 'message') {
      const c = this.consent.get(from);
      if (c) { if (w.nonce && w.counter) c.queue.push({ payload: w.payload, nonce: w.nonce, counter: w.counter }); return; }
      const p = this.peers.get(from);
      if (!p || !w.nonce || !w.counter) { this.emit('error', new Error('Bad message')); return; }
      this.decryptMsg(p, { payload: w.payload, nonce: w.nonce, counter: w.counter });
    }
  }

  private finish(from: string, h: PendingHS): void {
    this.hs.delete(from);
    const rs = h.noise.getRemoteStaticKey();
    const { sendKey, recvKey } = h.noise.getTransportKeys(h.isInitiator);
    const id = toHex(rs);
    const peer: Peer = { id, staticKey: rs, cipher: new TransportCipher(sendKey, recvKey) };
    if (this.trusted.has(id) || h.isInitiator || this.autoAccept) {
      this.peers.set(id, peer); this.lastSeen.set(id, Date.now());
      if (!this.trusted.has(id)) { this.trusted.set(id, { id, trust: 'accepted', addedAt: new Date().toISOString() }); this.save(); }
      this.emit('peer', id); if (h.resolve) h.resolve(id);
    } else {
      this.consent.set(id, { peer, queue: [] });
      this.emit('connectionRequest', { id, fingerprint: fingerprint(this.kp.publicKey, rs), safetyNumber: safetyNumber(this.kp.publicKey, rs) } as ConnectionRequest);
      if (h.resolve) h.resolve(id);
    }
  }

  private decryptMsg(p: Peer, w: { payload: string; nonce: string; counter: string }): void {
    this.emit('message', JSON.parse(p.cipher.decrypt(fromBase64(w.payload), fromBase64(w.nonce), w.counter)), p.id);
  }

  private save(): void {
    if (!this.idPath) return;
    const d = path.dirname(this.idPath);
    if (d && !fs.existsSync(d)) fs.mkdirSync(d, { recursive: true });
    fs.writeFileSync(this.idPath, JSON.stringify({
      publicKey: toHex(this.kp.publicKey), secretKey: toHex(this.kp.secretKey),
      created: new Date().toISOString(), owner: this.owner,
      trustedPeers: Array.from(this.trusted.values()),
    }, null, 2));
  }
}

export default Clawdio;
