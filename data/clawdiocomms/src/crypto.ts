import sodium from 'libsodium-wrappers';

let ready = false;
export async function init(): Promise<void> {
  if (!ready) { await sodium.ready; ready = true; }
}

export interface KeyPair { publicKey: Uint8Array; secretKey: Uint8Array; }

export function generateKeyPair(): KeyPair {
  const kp = sodium.crypto_box_keypair();
  return { publicKey: kp.publicKey, secretKey: kp.privateKey };
}

/** HKDF-like extract-and-expand using BLAKE2b */
function hkdf(ck: Uint8Array, ikm: Uint8Array): [Uint8Array, Uint8Array] {
  const tempKey = sodium.crypto_generichash(64, ikm, ck);
  const out1 = sodium.crypto_generichash(32, new Uint8Array([0x01]), tempKey);
  const buf = new Uint8Array(33); buf.set(out1); buf[32] = 0x02;
  const out2 = sodium.crypto_generichash(32, buf, tempKey);
  return [out1, out2];
}

function dh(secret: Uint8Array, pub: Uint8Array): Uint8Array {
  return sodium.crypto_scalarmult(secret, pub);
}

/** Encrypt with XChaCha20-Poly1305 using a zero nonce (single use per key in Noise) */
function aead_encrypt(key: Uint8Array, nonce_counter: number, ad: Uint8Array, plaintext: Uint8Array): Uint8Array {
  const nonce = new Uint8Array(24);
  new DataView(nonce.buffer).setUint32(16, nonce_counter, true); // put counter in last 8 bytes area
  return sodium.crypto_aead_xchacha20poly1305_ietf_encrypt(plaintext, ad, null, nonce, key);
}

function aead_decrypt(key: Uint8Array, nonce_counter: number, ad: Uint8Array, ciphertext: Uint8Array): Uint8Array {
  const nonce = new Uint8Array(24);
  new DataView(nonce.buffer).setUint32(16, nonce_counter, true);
  return sodium.crypto_aead_xchacha20poly1305_ietf_decrypt(null, ciphertext, ad, nonce, key);
}

/**
 * Noise_XX handshake: -> e | <- e, ee, s, es | -> s, se
 * Forward secrecy + mutual authentication.
 */
export class NoiseXXHandshake {
  private ck: Uint8Array;     // chaining key
  private h: Uint8Array;      // handshake hash
  private k: Uint8Array | null = null; // cipher key (null = no encryption yet)
  private n = 0;              // nonce counter

  private localStatic: KeyPair;
  private localEphemeral!: KeyPair;
  private remoteStaticPub: Uint8Array | null = null;
  private remoteEphemeralPub: Uint8Array | null = null;

  constructor(staticKeyPair: KeyPair) {
    this.localStatic = staticKeyPair;
    const protocolName = sodium.from_string('Noise_XX_25519_ChaChaPoly_BLAKE2b');
    this.h = sodium.crypto_generichash(32, protocolName);
    this.ck = new Uint8Array(this.h);
  }

  private mixHash(data: Uint8Array): void {
    const buf = new Uint8Array(this.h.length + data.length);
    buf.set(this.h); buf.set(data, this.h.length);
    this.h = sodium.crypto_generichash(32, buf);
  }

  private mixKey(ikm: Uint8Array): void {
    const [ck, k] = hkdf(this.ck, ikm);
    this.ck = ck;
    this.k = k;
    this.n = 0;
  }

  private encryptAndHash(plaintext: Uint8Array): Uint8Array {
    if (!this.k) { this.mixHash(plaintext); return plaintext; }
    const ct = aead_encrypt(this.k, this.n++, this.h, plaintext);
    this.mixHash(ct);
    return ct;
  }

  private decryptAndHash(ciphertext: Uint8Array): Uint8Array {
    if (!this.k) { this.mixHash(ciphertext); return ciphertext; }
    const pt = aead_decrypt(this.k, this.n++, this.h, ciphertext);
    this.mixHash(ciphertext);
    return pt;
  }

  // --- Initiator ---

  /** Msg 1: -> e */
  writeMessage1(): Uint8Array {
    this.localEphemeral = generateKeyPair();
    this.mixHash(this.localEphemeral.publicKey);
    return this.localEphemeral.publicKey; // 32 bytes
  }

  /** Msg 2 received: <- e, ee, s, es */
  readMessage2(msg: Uint8Array): void {
    // e
    this.remoteEphemeralPub = msg.slice(0, 32);
    this.mixHash(this.remoteEphemeralPub);
    // ee
    this.mixKey(dh(this.localEphemeral.secretKey, this.remoteEphemeralPub));
    // s (encrypted)
    const encS = msg.slice(32);
    this.remoteStaticPub = this.decryptAndHash(encS);
    // es
    this.mixKey(dh(this.localEphemeral.secretKey, this.remoteStaticPub));
  }

  /** Msg 3: -> s, se */
  writeMessage3(): Uint8Array {
    const encS = this.encryptAndHash(this.localStatic.publicKey);
    // se
    this.mixKey(dh(this.localStatic.secretKey, this.remoteEphemeralPub!));
    return encS;
  }

  // --- Responder ---

  /** Msg 1 received: -> e */
  readMessage1(msg: Uint8Array): void {
    this.remoteEphemeralPub = msg.slice(0, 32);
    this.mixHash(this.remoteEphemeralPub);
  }

  /** Msg 2: <- e, ee, s, es */
  writeMessage2(): Uint8Array {
    // e
    this.localEphemeral = generateKeyPair();
    this.mixHash(this.localEphemeral.publicKey);
    // ee
    this.mixKey(dh(this.localEphemeral.secretKey, this.remoteEphemeralPub!));
    // s
    const encS = this.encryptAndHash(this.localStatic.publicKey);
    // es
    this.mixKey(dh(this.localStatic.secretKey, this.remoteEphemeralPub!));
    // output: e_pub || encrypted_s
    const out = new Uint8Array(32 + encS.length);
    out.set(this.localEphemeral.publicKey);
    out.set(encS, 32);
    return out;
  }

  /** Msg 3 received: -> s, se */
  readMessage3(msg: Uint8Array): void {
    this.remoteStaticPub = this.decryptAndHash(msg);
    // se
    this.mixKey(dh(this.localEphemeral.secretKey, this.remoteStaticPub));
  }

  /** Split into transport keys. Call after handshake completes. */
  getTransportKeys(isInitiator: boolean): { sendKey: Uint8Array; recvKey: Uint8Array } {
    const [k1, k2] = hkdf(this.ck, new Uint8Array(0));
    return isInitiator ? { sendKey: k1, recvKey: k2 } : { sendKey: k2, recvKey: k1 };
  }

  getRemoteStaticKey(): Uint8Array {
    if (!this.remoteStaticPub) throw new Error('Handshake not complete');
    return this.remoteStaticPub;
  }
}

// --- Fingerprint verification ---

export function fingerprint(key1: Uint8Array, key2: Uint8Array): string {
  const sorted = Buffer.compare(Buffer.from(key1), Buffer.from(key2)) < 0
    ? new Uint8Array([...key1, ...key2]) : new Uint8Array([...key2, ...key1]);
  const hash = sodium.crypto_generichash(8, sorted);
  const emojis = ['🔑','🛡','🔒','🌟','⚡','🎯','🚀','🔥','💎','🌈','🎪','🎭','🦊','🐉','🌙','☀️','🌊','🏔','🎸','🎹','🎲','🏆','🌸','🍀','🔔','🎨','🧭','🦋','🐝','🌻','🍎','🎵'];
  return Array.from(hash).map(b => emojis[b % emojis.length]).join('');
}

export function safetyNumber(key1: Uint8Array, key2: Uint8Array): string {
  const sorted = Buffer.compare(Buffer.from(key1), Buffer.from(key2)) < 0
    ? new Uint8Array([...key1, ...key2]) : new Uint8Array([...key2, ...key1]);
  const hash = sodium.crypto_generichash(16, sorted);
  return sodium.to_hex(hash).match(/.{4}/g)!.join('-');
}

// --- Transport encryption with replay protection ---

export class TransportCipher {
  private sendCounter = 0n;
  private recvCounter = -1n;

  constructor(private sendKey: Uint8Array, private recvKey: Uint8Array) {}

  encrypt(plaintext: string): { ciphertext: Uint8Array; nonce: Uint8Array; counter: string } {
    const counter = this.sendCounter++;
    const ad = new Uint8Array(8);
    new DataView(ad.buffer).setBigUint64(0, counter);
    const nonce = sodium.randombytes_buf(sodium.crypto_aead_xchacha20poly1305_ietf_NPUBBYTES);
    const ciphertext = sodium.crypto_aead_xchacha20poly1305_ietf_encrypt(
      sodium.from_string(plaintext), ad, null, nonce, this.sendKey
    );
    return { ciphertext, nonce, counter: counter.toString() };
  }

  decrypt(ciphertext: Uint8Array, nonce: Uint8Array, counterStr: string): string {
    const counter = BigInt(counterStr);
    if (counter <= this.recvCounter) throw new Error(`Replay: counter ${counter} <= ${this.recvCounter}`);
    const ad = new Uint8Array(8);
    new DataView(ad.buffer).setBigUint64(0, counter);
    const pt = sodium.crypto_aead_xchacha20poly1305_ietf_decrypt(null, ciphertext, ad, nonce, this.recvKey);
    this.recvCounter = counter;
    return sodium.to_string(pt);
  }
}

// --- Encoding helpers ---
export function toHex(buf: Uint8Array): string { return sodium.to_hex(buf); }
export function fromHex(hex: string): Uint8Array { return sodium.from_hex(hex); }
export function toBase64(buf: Uint8Array): string { return sodium.to_base64(buf, sodium.base64_variants.ORIGINAL); }
export function fromBase64(b64: string): Uint8Array { return sodium.from_base64(b64, sodium.base64_variants.ORIGINAL); }
