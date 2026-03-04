import { EventEmitter } from 'events';
import * as fs from 'fs';
import * as path from 'path';
import { Transport } from './transport.js';
import { NoiseXXHandshake, TransportCipher, KeyPair, fingerprint, safetyNumber,
         toHex, fromHex, toBase64, fromBase64, init, generateKeyPair } from './crypto.js';
import { encodeWire, decodeWire, parseConnectionString, buildConnectionString } from './protocol.js';
import { ClawdioOptions, AgentMessage, Peer, MessageHandler, PeerStatus, ConnectionRequest,
         TrustLevel, TrustedPeerRecord, IdentityData } from './types.js';
import type WebSocket from 'ws';

export { AgentMessage, ClawdioOptions, PeerStatus, ConnectionRequest, TrustLevel, TrustedPeerRecord, IdentityData } from './types.js';

interface PendingHandshake {
  noise: NoiseXXHandshake;
  isInitiator: boolean;
}

interface PendingConsent {
  peer: Peer;
  ws: WebSocket;
  messageQueue: Array<{ payload: string; nonce: string; counter: string }>;
}

// Word list for verification codes (BIP39 subset)
const VERIFY_WORDS = [
  'apple','brave','coral','delta','eagle','flame','grape','haven','ivory','jewel',
  'karma','lemon','maple','night','ocean','pearl','quilt','river','storm','tiger',
  'ultra','vivid','waltz','xenon','yield','zephyr','amber','blaze','cedar','drift',
  'ember','frost','globe','haste','index','joker','kneel','lunar','marsh','noble',
  'orbit','prism','quest','reign','sonic','torch','umbra','vigor','wheat','xenial',
  'yacht','azure','birch','crane','dusk','elfin','flora','glyph','heron','isle',
  'jade','kite','lotus','mirth','nexus','onyx',
];

export class Clawdio extends EventEmitter {
  private transport = new Transport();
  private keyPair!: KeyPair;
  private peers = new Map<string, Peer>();
  private pending = new Map<WebSocket, PendingHandshake>();
  private pendingConsent = new Map<string, PendingConsent>();
  private trustedPeers = new Map<string, TrustedPeerRecord>();
  private owner?: string;
  private port: number;
  private host: string;
  private identityPath?: string;
  private autoAccept: boolean;
  private peerLastSeen = new Map<string, number>();
  private heartbeatInterval: ReturnType<typeof setInterval> | null = null;
  private heartbeatMs: number;
  private heartbeatTimeout: number;

  constructor(private opts: ClawdioOptions = {}) {
    super();
    this.port = opts.port ?? 9090;
    this.host = opts.host ?? '0.0.0.0';
    this.heartbeatMs = opts.heartbeatMs ?? 5000;
    this.heartbeatTimeout = opts.heartbeatTimeout ?? 15000;
    this.identityPath = opts.identityPath;
    this.autoAccept = opts.autoAccept ?? false;
  }

  static async create(opts?: ClawdioOptions): Promise<Clawdio> {
    const node = new Clawdio(opts);
    await node.start();
    return node;
  }

  get publicKey(): string { return toHex(this.keyPair.publicKey); }
  get peerId(): string { return this.publicKey; }

  async start(): Promise<void> {
    await init();
    if (this.identityPath && fs.existsSync(this.identityPath)) {
      const data: IdentityData = JSON.parse(fs.readFileSync(this.identityPath, 'utf8'));
      this.keyPair = { publicKey: fromHex(data.publicKey), secretKey: fromHex(data.secretKey) };
      this.owner = data.owner;
      for (const tp of (data.trustedPeers ?? [])) {
        this.trustedPeers.set(tp.id, tp);
      }
    } else {
      this.keyPair = generateKeyPair();
    }
    await this.transport.listen(this.port, this.host);
    this.transport.on('data', (raw: string, ws: WebSocket) => this.handleData(raw, ws));
    this.startHeartbeat();
    if (this.identityPath) this.saveIdentity();
  }

  // --- Owner & Verification ---

  setOwner(name: string): void {
    this.owner = name;
    this.saveIdentity();
  }

  getOwner(): string | undefined { return this.owner; }

  /** Generate a 6-word verification code from both peers' static keys */
  getVerificationCode(peerId: string): string {
    const peer = this.peers.get(peerId);
    if (!peer) throw new Error(`Unknown peer: ${peerId}`);
    const key1 = this.keyPair.publicKey;
    const key2 = peer.staticKey;
    // Deterministic: sort keys, hash, pick 6 words
    const sorted = Buffer.compare(Buffer.from(key1), Buffer.from(key2)) < 0
      ? new Uint8Array([...key1, ...key2]) : new Uint8Array([...key2, ...key1]);
    // Use crypto_generichash via the safetyNumber approach
    const { crypto_generichash } = require('libsodium-wrappers');
    const hash = crypto_generichash(12, sorted); // 12 bytes = 6 words (2 bytes per word index)
    const words: string[] = [];
    for (let i = 0; i < 12; i += 2) {
      const idx = ((hash[i] << 8) | hash[i + 1]) % VERIFY_WORDS.length;
      words.push(VERIFY_WORDS[idx]);
    }
    return words.join(' ');
  }

  /** Mark peer as human-verified after in-person code exchange */
  verifyPeer(peerId: string): void {
    const rec = this.trustedPeers.get(peerId);
    if (!rec) throw new Error(`Peer not trusted: ${peerId}`);
    rec.trust = 'human-verified';
    this.saveIdentity();
  }

  /** Get trust level of a peer */
  getPeerTrust(peerId: string): TrustLevel | null {
    const rec = this.trustedPeers.get(peerId);
    return rec?.trust ?? null;
  }

  // --- Connection Consent ---

  /** Accept a pending peer connection */
  acceptPeer(peerId: string): void {
    const pc = this.pendingConsent.get(peerId);
    if (!pc) throw new Error(`No pending connection from: ${peerId}`);
    // Register as accepted trusted peer
    this.trustedPeers.set(peerId, {
      id: peerId, trust: 'accepted', addedAt: new Date().toISOString()
    });
    // Finalize the peer
    this.peers.set(peerId, pc.peer);
    this.peerLastSeen.set(peerId, Date.now());
    this.transport.registerSocket(peerId, pc.ws);
    this.pendingConsent.delete(peerId);
    this.saveIdentity();
    this.emit('peer', peerId);
    this.emit('_peerWs', peerId, pc.ws);
    // Drain queued messages
    for (const qm of pc.messageQueue) {
      this.handleEncryptedMessage(pc.peer, qm);
    }
  }

  /** Reject a pending peer connection */
  rejectPeer(peerId: string): void {
    const pc = this.pendingConsent.get(peerId);
    if (!pc) throw new Error(`No pending connection from: ${peerId}`);
    pc.ws.close();
    this.pendingConsent.delete(peerId);
    this.emit('peerRejected', peerId);
  }

  // --- Core ---

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      const now = Date.now();
      for (const [id, peer] of this.peers) {
        const ws = peer.ws ?? this.transport.getSocket(id);
        if (ws) this.transport.send(ws, encodeWire({ type: 'ping', payload: now.toString() }));
        const last = this.peerLastSeen.get(id);
        if (last && now - last > this.heartbeatTimeout) {
          this.emit('peerDown', id);
        }
      }
    }, this.heartbeatMs);
  }

  getPeerStatus(peerId: string): PeerStatus {
    const last = this.peerLastSeen.get(peerId);
    if (!last) return 'down';
    const elapsed = Date.now() - last;
    if (elapsed <= this.heartbeatMs * 2) return 'alive';
    if (elapsed <= this.heartbeatTimeout) return 'stale';
    return 'down';
  }

  getConnectionString(externalHost?: string): string {
    return buildConnectionString(this.publicKey, externalHost ?? '127.0.0.1', this.port);
  }

  /** Initiate Noise XX handshake */
  async exchangeKeys(connStr: string): Promise<string> {
    const { address } = parseConnectionString(connStr);
    const ws = await this.transport.connect(address);
    const noise = new NoiseXXHandshake(this.keyPair);
    const msg1 = noise.writeMessage1();
    this.pending.set(ws, { noise, isInitiator: true });
    this.transport.send(ws, encodeWire({ type: 'noise1', payload: toBase64(msg1) }));

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error('Handshake timeout')), 10000);
      const onPeer = (id: string, peerWs: WebSocket) => {
        if (peerWs === ws) { clearTimeout(timeout); this.removeListener('_peerWs', onPeer); resolve(id); }
      };
      this.on('_peerWs', onPeer);
    });
  }

  async send(peerId: string, message: AgentMessage | string): Promise<void> {
    const peer = this.peers.get(peerId);
    if (!peer) throw new Error(`Unknown peer: ${peerId}`);
    const payload = typeof message === 'string' ? JSON.stringify({ task: message }) : JSON.stringify(message);
    const { ciphertext, nonce, counter } = peer.cipher.encrypt(payload);
    const ws = peer.ws ?? this.transport.getSocket(peerId);
    if (!ws) throw new Error(`No connection to peer: ${peerId}`);
    this.transport.send(ws, encodeWire({
      type: 'message', payload: toBase64(ciphertext), nonce: toBase64(nonce), counter
    }));
  }

  onMessage(handler: MessageHandler): void { this.on('message', handler); }

  getFingerprint(peerId: string): string {
    const peer = this.peers.get(peerId);
    if (!peer) throw new Error(`Unknown peer: ${peerId}`);
    return fingerprint(this.keyPair.publicKey, peer.staticKey);
  }

  getSafetyNumber(peerId: string): string {
    const peer = this.peers.get(peerId);
    if (!peer) throw new Error(`Unknown peer: ${peerId}`);
    return safetyNumber(this.keyPair.publicKey, peer.staticKey);
  }

  private handleData(raw: string, ws: WebSocket): void {
    try {
      const wire = decodeWire(raw);
      if (wire.type === 'ping') {
        this.transport.send(ws, encodeWire({ type: 'pong', payload: wire.payload }));
        this.touchPeer(ws);
      } else if (wire.type === 'pong') {
        this.touchPeer(ws);
      } else if (wire.type === 'noise1') this.handleNoise1(ws, fromBase64(wire.payload));
      else if (wire.type === 'noise2') this.handleNoise2(ws, fromBase64(wire.payload));
      else if (wire.type === 'noise3') this.handleNoise3(ws, fromBase64(wire.payload));
      else if (wire.type === 'message') this.handleMessage(ws, wire);
    } catch (e) { this.emit('error', e); }
  }

  /** Responder: receives → e, sends ← e, ee, s, es */
  private handleNoise1(ws: WebSocket, msg1: Uint8Array): void {
    const noise = new NoiseXXHandshake(this.keyPair);
    noise.readMessage1(msg1);
    const msg2 = noise.writeMessage2();
    this.pending.set(ws, { noise, isInitiator: false });
    this.transport.send(ws, encodeWire({ type: 'noise2', payload: toBase64(msg2) }));
  }

  /** Initiator: receives ← e, ee, s, es; sends → s, se */
  private handleNoise2(ws: WebSocket, msg2: Uint8Array): void {
    const hs = this.pending.get(ws);
    if (!hs) throw new Error('No pending handshake');
    hs.noise.readMessage2(msg2);
    const msg3 = hs.noise.writeMessage3();
    this.transport.send(ws, encodeWire({ type: 'noise3', payload: toBase64(msg3) }));
    this.finishHandshake(ws, hs);
  }

  /** Responder: receives → s, se */
  private handleNoise3(ws: WebSocket, msg3: Uint8Array): void {
    const hs = this.pending.get(ws);
    if (!hs) throw new Error('No pending handshake');
    hs.noise.readMessage3(msg3);
    this.finishHandshake(ws, hs);
  }

  private touchPeer(ws: WebSocket): void {
    const peer = [...this.peers.values()].find(p => p.ws === ws || this.transport.getSocket(p.id) === ws);
    if (peer) this.peerLastSeen.set(peer.id, Date.now());
  }

  private finishHandshake(ws: WebSocket, hs: PendingHandshake): void {
    this.pending.delete(ws);
    const remoteStatic = hs.noise.getRemoteStaticKey();
    const { sendKey, recvKey } = hs.noise.getTransportKeys(hs.isInitiator);
    const id = toHex(remoteStatic);
    const peer: Peer = {
      id, staticKey: remoteStatic,
      cipher: new TransportCipher(sendKey, recvKey),
      address: '', ws
    };

    // Check if this peer is already trusted or if autoAccept is on
    const isTrusted = this.trustedPeers.has(id);
    const isInitiator = hs.isInitiator;

    if (isTrusted || isInitiator || this.autoAccept) {
      // Auto-accept: trusted peers, outbound connections, or autoAccept mode
      this.peers.set(id, peer);
      this.peerLastSeen.set(id, Date.now());
      this.transport.registerSocket(id, ws);
      if (!isTrusted) {
        this.trustedPeers.set(id, {
          id, trust: 'accepted', addedAt: new Date().toISOString()
        });
        this.saveIdentity();
      }
      this.emit('peer', id);
      this.emit('_peerWs', id, ws);
    } else {
      // Unknown inbound peer — require consent
      this.pendingConsent.set(id, { peer, ws, messageQueue: [] });
      const fp = fingerprint(this.keyPair.publicKey, remoteStatic);
      const sn = safetyNumber(this.keyPair.publicKey, remoteStatic);
      const req: ConnectionRequest = { id, fingerprint: fp, safetyNumber: sn, address: '' };
      this.emit('connectionRequest', req);
    }
  }

  private handleMessage(ws: WebSocket, wire: { payload: string; nonce?: string; counter?: string }): void {
    // Check if message is from a peer in pending consent
    const pendingEntry = [...this.pendingConsent.entries()].find(([_, pc]) => pc.ws === ws);
    if (pendingEntry) {
      // Queue the message
      if (wire.nonce && wire.counter) {
        pendingEntry[1].messageQueue.push({ payload: wire.payload, nonce: wire.nonce, counter: wire.counter });
      }
      return;
    }

    const peer = [...this.peers.values()].find(p => p.ws === ws || this.transport.getSocket(p.id) === ws);
    if (!peer) { this.emit('error', new Error('Message from unknown peer')); return; }
    if (!wire.nonce || !wire.counter) { this.emit('error', new Error('Missing nonce/counter')); return; }
    this.handleEncryptedMessage(peer, { payload: wire.payload, nonce: wire.nonce, counter: wire.counter });
  }

  private handleEncryptedMessage(peer: Peer, wire: { payload: string; nonce: string; counter: string }): void {
    const plaintext = peer.cipher.decrypt(fromBase64(wire.payload), fromBase64(wire.nonce), wire.counter);
    const msg: AgentMessage = JSON.parse(plaintext);
    this.emit('message', msg, peer.id);
  }

  private saveIdentity(): void {
    if (!this.identityPath) return;
    const data: IdentityData = {
      publicKey: toHex(this.keyPair.publicKey),
      secretKey: toHex(this.keyPair.secretKey),
      created: new Date().toISOString(),
      owner: this.owner,
      trustedPeers: Array.from(this.trustedPeers.values()),
    };
    const dir = path.dirname(this.identityPath);
    if (dir && !fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(this.identityPath, JSON.stringify(data, null, 2));
  }

  async stop(): Promise<void> {
    if (this.heartbeatInterval) { clearInterval(this.heartbeatInterval); this.heartbeatInterval = null; }
    await this.transport.close();
    this.peers.clear();
    this.pending.clear();
    this.pendingConsent.clear();
    this.peerLastSeen.clear();
  }
}

export default Clawdio;
