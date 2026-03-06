#!/usr/bin/env node
/**
 * Ring Gates — Onchain inter-computer communication protocol for OK Computers.
 *
 * Named after the ring gates from The Expanse. OK Computers are isolated systems
 * (sandboxed iframes). The blockchain is ring space (shared medium). Ring Gates
 * are the protocol channels that let them communicate through it.
 *
 * Usage:
 *   const { RingGate } = require("./ring-gate");
 *   const rg = new RingGate(1399);
 *
 *   // Encode/decode individual messages
 *   const msg = RingGate.encodeMessage("D", "a7f3", 0, 10, 0x00, "SGVsbG8=");
 *   const parsed = RingGate.decodeMessage(msg);
 *
 *   // Chunk large data into transmissions
 *   const chunks = RingGate.chunk(htmlString, "a7f3");
 *   const assembled = RingGate.assemble(chunks[0], chunks.slice(1));
 *
 *   // Shard across multiple computers
 *   const plan = RingGate.planShards(chunks.slice(1), [1399, 22, 42]);
 *
 *   // Build Bankr transactions
 *   const txs = rg.buildTransmission("rg_1399_broadcast", htmlString);
 *   // Submit each tx via Bankr API
 */

const { ethers } = require("ethers");
const { OKComputer, CONTRACT_STORAGE, CHAIN_ID } = require("./okcomputer");
const { createHash } = require("crypto");
const zlib = require("zlib");

// --- Protocol Constants ---

const PROTOCOL_VERSION = "1";
const MAGIC_PREFIX = "RG";
const SEPARATOR = "|";
const HEADER_PARTS = 7; // RG|version|type|txid|seq|total|flags
const MAX_MESSAGE_LENGTH = 1024;

// Header: "RG|1|D|a7f3|0001|00d2|00|" = 25 chars
// Calculated: 2(RG) + 1(|) + 1(ver) + 1(|) + 1(type) + 1(|) + 4(txid) + 1(|) + 4(seq) + 1(|) + 4(total) + 1(|) + 2(flags) + 1(|) = 25
const HEADER_LENGTH = 25;
const MAX_PAYLOAD_LENGTH = MAX_MESSAGE_LENGTH - HEADER_LENGTH; // 999 chars

// Message types
const MSG_TYPES = {
  MANIFEST: "M",
  DATA: "D",
  ACK: "A",
  PING: "P",
  PONG: "O",
  ROUTE: "R",
  ERROR: "E",
};

// Flags (bitmask)
const FLAGS = {
  COMPRESSED: 0x01,
  ENCRYPTED: 0x02,
  URGENT: 0x04,
  FINAL: 0x08,
  TEXT: 0x20,
};

// --- Static Methods (Pure Protocol Logic) ---

class RingGate {
  /**
   * @param {number} tokenId - OK Computer token ID (e.g. 1399)
   * @param {string} [rpcUrl] - Base RPC URL
   */
  constructor(tokenId, rpcUrl) {
    this.tokenId = tokenId;
    this.ok = new OKComputer(tokenId, rpcUrl);
  }

  // ============================================================
  // STATIC: Encode / Decode
  // ============================================================

  /**
   * Encode a Ring Gate message string (max 1024 chars).
   * @param {string} type - Message type code (D, M, P, etc.)
   * @param {string} txid - 4 hex char transmission ID
   * @param {number} seq - Sequence number (0-65535)
   * @param {number} total - Total chunks (0-65535)
   * @param {number} flags - Flag bitmask
   * @param {string} payload - Payload string (max 999 chars)
   * @returns {string} Encoded message
   */
  static encodeMessage(type, txid, seq, total, flags, payload) {
    if (!txid || txid.length !== 4) throw new Error("txid must be 4 hex chars");
    if (typeof seq !== "number" || seq < 0 || seq > 0xffff)
      throw new Error("seq must be 0-65535");
    if (typeof total !== "number" || total < 0 || total > 0xffff)
      throw new Error("total must be 0-65535");
    if (payload.length > MAX_PAYLOAD_LENGTH)
      throw new Error(`Payload exceeds ${MAX_PAYLOAD_LENGTH} chars (got ${payload.length})`);

    const seqHex = seq.toString(16).padStart(4, "0");
    const totalHex = total.toString(16).padStart(4, "0");
    const flagsHex = (flags & 0xff).toString(16).padStart(2, "0");

    const msg = `${MAGIC_PREFIX}${SEPARATOR}${PROTOCOL_VERSION}${SEPARATOR}${type}${SEPARATOR}${txid}${SEPARATOR}${seqHex}${SEPARATOR}${totalHex}${SEPARATOR}${flagsHex}${SEPARATOR}${payload}`;

    if (msg.length > MAX_MESSAGE_LENGTH) {
      throw new Error(`Encoded message exceeds ${MAX_MESSAGE_LENGTH} chars (got ${msg.length})`);
    }
    return msg;
  }

  /**
   * Decode a Ring Gate message string.
   * @param {string} text - Raw message text
   * @returns {object|null} Parsed message or null if not Ring Gate
   */
  static decodeMessage(text) {
    if (!RingGate.isRingGate(text)) return null;

    // Split only on first 7 separators (payload may contain separators)
    const parts = [];
    let idx = 0;
    for (let i = 0; i < HEADER_PARTS; i++) {
      const next = text.indexOf(SEPARATOR, idx);
      if (next === -1) return null;
      parts.push(text.slice(idx, next));
      idx = next + 1;
    }
    // Everything after the last separator is payload
    const payload = text.slice(idx);

    return {
      magic: parts[0],
      version: parts[1],
      type: parts[2],
      txid: parts[3],
      seq: parseInt(parts[4], 16),
      total: parseInt(parts[5], 16),
      flags: parseInt(parts[6], 16),
      payload,
      compressed: !!(parseInt(parts[6], 16) & FLAGS.COMPRESSED),
      encrypted: !!(parseInt(parts[6], 16) & FLAGS.ENCRYPTED),
      urgent: !!(parseInt(parts[6], 16) & FLAGS.URGENT),
      final: !!(parseInt(parts[6], 16) & FLAGS.FINAL),
      text: !!(parseInt(parts[6], 16) & FLAGS.TEXT),
    };
  }

  /**
   * Check if a string is a Ring Gate message.
   * @param {string} text
   * @returns {boolean}
   */
  static isRingGate(text) {
    return typeof text === "string" && text.startsWith(`${MAGIC_PREFIX}${SEPARATOR}`);
  }

  // ============================================================
  // STATIC: Hashing & Verification
  // ============================================================

  /**
   * SHA-256 hash of data, returned as hex string.
   * @param {string|Buffer} data
   * @returns {string} hex hash
   */
  static hash(data) {
    return createHash("sha256").update(data).digest("hex");
  }

  /**
   * Verify assembled data against a manifest's hash.
   * @param {object} manifest - Parsed manifest message
   * @param {string} assembled - Assembled data string
   * @returns {boolean}
   */
  static verify(manifest, assembled) {
    const meta = JSON.parse(manifest.payload);
    return meta.hash === RingGate.hash(assembled);
  }

  // ============================================================
  // STATIC: Chunk / Assemble
  // ============================================================

  /**
   * Generate a random 4-char hex transmission ID.
   * @returns {string}
   */
  static generateTxId() {
    return Math.floor(Math.random() * 0xffff).toString(16).padStart(4, "0");
  }

  /**
   * Chunk data into a manifest + data messages.
   * @param {string} data - Raw data to transmit
   * @param {string} [txid] - Transmission ID (auto-generated if omitted)
   * @param {object} [options]
   * @param {string} [options.contentType] - MIME type (default "text/plain")
   * @param {boolean} [options.compress] - Deflate before base64 (default false)
   * @param {boolean} [options.textMode] - Send raw text, skip base64 (default false)
   * @returns {string[]} Array of encoded messages: [manifest, ...dataChunks]
   */
  static chunk(data, txid, options = {}) {
    txid = txid || RingGate.generateTxId();
    const { contentType = "text/plain", compress = false, textMode = false } = options;

    let flags = 0x00;
    let encoded;

    if (textMode) {
      // Raw text mode — no base64 encoding, payload is plain text
      flags |= FLAGS.TEXT;
      encoded = data;
    } else if (compress) {
      // Compress then base64
      flags |= FLAGS.COMPRESSED;
      const deflated = zlib.deflateSync(Buffer.from(data, "utf-8"));
      encoded = deflated.toString("base64");
    } else {
      // Standard base64
      encoded = Buffer.from(data, "utf-8").toString("base64");
    }

    // Split encoded data into payload-sized chunks
    const chunkSize = MAX_PAYLOAD_LENGTH;
    const dataChunks = [];
    for (let i = 0; i < encoded.length; i += chunkSize) {
      dataChunks.push(encoded.slice(i, i + chunkSize));
    }
    // Handle empty data — produce 1 empty chunk
    if (dataChunks.length === 0) dataChunks.push("");

    const totalChunks = dataChunks.length;
    const dataHash = RingGate.hash(data);

    // Build manifest
    const manifestPayload = JSON.stringify({
      type: contentType,
      size: Buffer.byteLength(data, "utf-8"),
      hash: dataHash,
      encoding: textMode ? "text" : "b64",
      chunks: totalChunks,
      compressed: compress,
    });
    const manifest = RingGate.encodeMessage(
      MSG_TYPES.MANIFEST, txid, 0, totalChunks, flags, manifestPayload
    );

    // Build data messages (seq starts at 1)
    const messages = [manifest];
    for (let i = 0; i < dataChunks.length; i++) {
      messages.push(
        RingGate.encodeMessage(MSG_TYPES.DATA, txid, i + 1, totalChunks, flags, dataChunks[i])
      );
    }

    return messages;
  }

  /**
   * Assemble data from a manifest and data chunks.
   * @param {string} manifestMsg - Raw manifest message string
   * @param {string[]} dataMessages - Raw data message strings (in any order)
   * @returns {string} Reassembled original data
   */
  static assemble(manifestMsg, dataMessages) {
    const manifest = RingGate.decodeMessage(manifestMsg);
    if (!manifest || manifest.type !== MSG_TYPES.MANIFEST) {
      throw new Error("First argument must be a MANIFEST message");
    }
    const meta = JSON.parse(manifest.payload);

    // Parse and sort data chunks by sequence number
    const chunks = dataMessages
      .map((msg) => RingGate.decodeMessage(msg))
      .filter((m) => m && m.type === MSG_TYPES.DATA && m.txid === manifest.txid)
      .sort((a, b) => a.seq - b.seq);

    if (chunks.length !== meta.chunks) {
      throw new Error(`Expected ${meta.chunks} chunks, got ${chunks.length}`);
    }

    // Reassemble encoded data
    const encoded = chunks.map((c) => c.payload).join("");

    // Decode
    let result;
    if (meta.encoding === "text") {
      result = encoded;
    } else if (meta.compressed) {
      const buf = Buffer.from(encoded, "base64");
      result = zlib.inflateSync(buf).toString("utf-8");
    } else {
      result = Buffer.from(encoded, "base64").toString("utf-8");
    }

    // Verify hash
    if (meta.hash && RingGate.hash(result) !== meta.hash) {
      throw new Error("Hash verification failed — data corrupted");
    }

    return result;
  }

  // ============================================================
  // STATIC: Multi-Computer Sharding
  // ============================================================

  /**
   * Plan how to distribute data chunks across multiple computers.
   * @param {string[]} dataMessages - Data chunk messages (NOT including manifest)
   * @param {number[]} computerIds - Token IDs of available computers
   * @returns {object[]} Shard plan: [{computer, channel, messages, range}, ...]
   */
  static planShards(dataMessages, computerIds) {
    if (!computerIds.length) throw new Error("Need at least one computer");

    const perShard = Math.ceil(dataMessages.length / computerIds.length);
    const shards = [];

    for (let i = 0; i < computerIds.length; i++) {
      const start = i * perShard;
      const end = Math.min(start + perShard, dataMessages.length);
      if (start >= dataMessages.length) break;

      // Extract txid from first message
      const parsed = RingGate.decodeMessage(dataMessages[start]);
      const txid = parsed ? parsed.txid : "0000";

      shards.push({
        computer: computerIds[i],
        channel: `rg_tx_${txid}_${i}`,
        messages: dataMessages.slice(start, end),
        range: [start + 1, end], // 1-based seq range (data chunks start at seq 1)
      });
    }

    return shards;
  }

  /**
   * Build a manifest payload that includes shard routing info.
   * @param {string} data - Original data
   * @param {string} txid - Transmission ID
   * @param {object[]} shardPlan - Output of planShards()
   * @param {object} [options]
   * @returns {string} Encoded manifest message with shard map
   */
  static buildShardedManifest(data, txid, shardPlan, options = {}) {
    const { contentType = "text/plain", compress = false, textMode = false } = options;

    let flags = 0x00;
    if (textMode) flags |= FLAGS.TEXT;
    if (compress) flags |= FLAGS.COMPRESSED;

    const totalChunks = shardPlan.reduce((sum, s) => sum + s.messages.length, 0);

    const manifestPayload = JSON.stringify({
      type: contentType,
      size: Buffer.byteLength(data, "utf-8"),
      hash: RingGate.hash(data),
      encoding: textMode ? "text" : "b64",
      chunks: totalChunks,
      compressed: compress,
      shards: shardPlan.map((s) => ({
        channel: s.channel,
        computer: s.computer,
        range: s.range,
      })),
    });

    return RingGate.encodeMessage(MSG_TYPES.MANIFEST, txid, 0, totalChunks, flags, manifestPayload);
  }

  // ============================================================
  // INSTANCE: Build Bankr Transactions
  // ============================================================

  /**
   * Build Bankr transaction array for a single-channel transmission.
   * @param {string} channel - Channel name (e.g. "rg_1399_broadcast")
   * @param {string} data - Data to transmit
   * @param {object} [options] - Options for chunk()
   * @returns {object[]} Array of Bankr-compatible transaction objects
   */
  buildTransmission(channel, data, options = {}) {
    const messages = RingGate.chunk(data, undefined, options);
    return messages.map((msg) => this.ok.buildPostMessage(channel, msg));
  }

  /**
   * Build Bankr transactions for one shard of a multi-computer transmission.
   * @param {object} shard - Single shard from planShards() output
   * @returns {object[]} Array of Bankr-compatible transaction objects
   */
  buildShard(shard) {
    const ok = new OKComputer(shard.computer, this.ok.rpcUrl);
    return shard.messages.map((msg) => ok.buildPostMessage(shard.channel, msg));
  }

  /**
   * Build all transactions for a sharded transmission (manifest + all shards).
   * @param {string} data - Data to transmit
   * @param {number[]} computerIds - Token IDs to shard across
   * @param {string} broadcastChannel - Channel for manifest (e.g. "rg_1399_broadcast")
   * @param {object} [options]
   * @returns {object} { manifestTx, shardTxs: [{computer, channel, txs}] }
   */
  buildShardedTransmission(data, computerIds, broadcastChannel, options = {}) {
    const txid = RingGate.generateTxId();
    const allMessages = RingGate.chunk(data, txid, options);
    const manifest = allMessages[0];
    const dataMessages = allMessages.slice(1);

    const shardPlan = RingGate.planShards(dataMessages, computerIds);

    // Rebuild manifest with shard info
    const shardedManifest = RingGate.buildShardedManifest(data, txid, shardPlan, options);
    const manifestTx = this.ok.buildPostMessage(broadcastChannel, shardedManifest);

    const shardTxs = shardPlan.map((shard) => ({
      computer: shard.computer,
      channel: shard.channel,
      txs: this.buildShard(shard),
    }));

    return { manifestTx, shardTxs, txid, shardPlan };
  }

  // ============================================================
  // INSTANCE: Read Transmissions from Chain
  // ============================================================

  /**
   * Read and assemble a transmission from a single channel.
   * @param {string} channel - Channel to read from
   * @returns {Promise<string>} Assembled data
   */
  async readTransmission(channel) {
    const allMessages = await this.ok.readAllMessages(channel);

    // Find Ring Gate messages
    const rgMessages = allMessages
      .filter((m) => m.text && RingGate.isRingGate(m.text))
      .map((m) => m.text);

    if (rgMessages.length === 0) throw new Error("No Ring Gate messages found in channel");

    // Find the latest manifest
    let manifestMsg = null;
    for (let i = rgMessages.length - 1; i >= 0; i--) {
      const parsed = RingGate.decodeMessage(rgMessages[i]);
      if (parsed && parsed.type === MSG_TYPES.MANIFEST) {
        manifestMsg = rgMessages[i];
        break;
      }
    }
    if (!manifestMsg) throw new Error("No manifest found in channel");

    const manifest = RingGate.decodeMessage(manifestMsg);

    // Collect data chunks matching this transmission
    const dataChunks = rgMessages.filter((msg) => {
      const p = RingGate.decodeMessage(msg);
      return p && p.type === MSG_TYPES.DATA && p.txid === manifest.txid;
    });

    return RingGate.assemble(manifestMsg, dataChunks);
  }

  /**
   * Read and assemble a sharded transmission from multiple channels.
   * @param {string} manifestChannel - Channel containing the manifest
   * @returns {Promise<string>} Assembled data
   */
  async readShardedTransmission(manifestChannel) {
    const allMessages = await this.ok.readAllMessages(manifestChannel);

    // Find the latest manifest with shard info
    let manifestMsg = null;
    let manifestMeta = null;
    for (let i = allMessages.length - 1; i >= 0; i--) {
      const msg = allMessages[i];
      if (!msg.text || !RingGate.isRingGate(msg.text)) continue;
      const parsed = RingGate.decodeMessage(msg.text);
      if (parsed && parsed.type === MSG_TYPES.MANIFEST) {
        try {
          const meta = JSON.parse(parsed.payload);
          if (meta.shards && meta.shards.length > 0) {
            manifestMsg = msg.text;
            manifestMeta = meta;
            break;
          }
        } catch {}
      }
    }

    if (!manifestMsg || !manifestMeta) {
      throw new Error("No sharded manifest found");
    }

    // Read data chunks from all shard channels
    const allDataChunks = [];
    for (const shard of manifestMeta.shards) {
      const shardOk = new OKComputer(shard.computer, this.ok.rpcUrl);
      const shardMessages = await shardOk.readAllMessages(shard.channel);
      for (const m of shardMessages) {
        if (m.text && RingGate.isRingGate(m.text)) {
          const parsed = RingGate.decodeMessage(m.text);
          if (parsed && parsed.type === MSG_TYPES.DATA) {
            allDataChunks.push(m.text);
          }
        }
      }
    }

    return RingGate.assemble(manifestMsg, allDataChunks);
  }

  // ============================================================
  // INSTANCE: Utility
  // ============================================================

  /**
   * Scan a channel for Ring Gate transmissions and return summaries.
   * @param {string} channel
   * @returns {Promise<object[]>} Array of transmission summaries
   */
  async scanChannel(channel) {
    const allMessages = await this.ok.readAllMessages(channel);
    const manifests = [];

    for (const msg of allMessages) {
      if (!msg.text || !RingGate.isRingGate(msg.text)) continue;
      const parsed = RingGate.decodeMessage(msg.text);
      if (parsed && parsed.type === MSG_TYPES.MANIFEST) {
        try {
          const meta = JSON.parse(parsed.payload);
          manifests.push({
            txid: parsed.txid,
            contentType: meta.type,
            size: meta.size,
            chunks: meta.chunks,
            hash: meta.hash,
            sharded: !!(meta.shards && meta.shards.length > 0),
            shardCount: meta.shards ? meta.shards.length : 0,
            timestamp: msg.timestamp,
            time: msg.time,
            sender: msg.sender,
            tokenId: msg.tokenId,
          });
        } catch {}
      }
    }

    return manifests;
  }
}

// --- Exports ---

module.exports = {
  RingGate,
  MSG_TYPES,
  FLAGS,
  PROTOCOL_VERSION,
  MAGIC_PREFIX,
  MAX_MESSAGE_LENGTH,
  MAX_PAYLOAD_LENGTH,
  HEADER_LENGTH,
};

// --- CLI ---

if (require.main === module) {
  const args = process.argv.slice(2);
  const cmd = args[0];

  if (!cmd) {
    console.log("Ring Gates — OK Computer Communication Protocol\n");
    console.log("Usage:");
    console.log("  node ring-gate.js info                   Show protocol info");
    console.log("  node ring-gate.js chunk <file>           Chunk a file into messages");
    console.log("  node ring-gate.js estimate <size>        Estimate messages for N bytes");
    console.log("  node ring-gate.js encode <text>          Encode a single test message");
    process.exit(0);
  }

  if (cmd === "info") {
    console.log("=== RING GATES PROTOCOL ===\n");
    console.log(`Version:         ${PROTOCOL_VERSION}`);
    console.log(`Max message:     ${MAX_MESSAGE_LENGTH} chars`);
    console.log(`Header:          ${HEADER_LENGTH} chars`);
    console.log(`Max payload:     ${MAX_PAYLOAD_LENGTH} chars`);
    console.log(`B64 data/msg:    ~${Math.floor(MAX_PAYLOAD_LENGTH * 0.75)} bytes`);
    console.log(`Gas per msg:     ~0.000005 ETH`);
    console.log(`\nMessage types:   ${Object.entries(MSG_TYPES).map(([k, v]) => `${v}=${k}`).join(", ")}`);
    console.log(`Flags:           ${Object.entries(FLAGS).map(([k, v]) => `0x${v.toString(16).padStart(2, "0")}=${k}`).join(", ")}`);
  } else if (cmd === "estimate") {
    const size = parseInt(args[1]) || 1024;
    const b64Size = Math.ceil(size * (4 / 3));
    const messages = Math.ceil(b64Size / MAX_PAYLOAD_LENGTH) + 1; // +1 for manifest
    const gasCost = messages * 0.000005;
    console.log(`=== TRANSMISSION ESTIMATE ===\n`);
    console.log(`Data size:       ${size} bytes`);
    console.log(`Base64 size:     ${b64Size} chars`);
    console.log(`Messages:        ${messages} (${messages - 1} data + 1 manifest)`);
    console.log(`Est. gas cost:   ~${gasCost.toFixed(6)} ETH`);
    console.log(`Est. USD cost:   ~$${(gasCost * 3000).toFixed(4)}`);
  } else if (cmd === "chunk") {
    const fs = require("fs");
    const file = args[1];
    if (!file) {
      console.error("Usage: node ring-gate.js chunk <file>");
      process.exit(1);
    }
    const data = fs.readFileSync(file, "utf-8");
    const messages = RingGate.chunk(data, undefined, { contentType: "text/html" });
    console.log(`Chunked ${data.length} chars into ${messages.length} messages:\n`);
    for (const msg of messages) {
      const parsed = RingGate.decodeMessage(msg);
      console.log(`  [${parsed.type}] seq=${parsed.seq}/${parsed.total} flags=0x${parsed.flags.toString(16).padStart(2, "0")} payload=${parsed.payload.length} chars`);
    }
    console.log(`\nTotal message chars: ${messages.reduce((s, m) => s + m.length, 0)}`);
  } else if (cmd === "encode") {
    const text = args.slice(1).join(" ") || "hello ring gates";
    const messages = RingGate.chunk(text, undefined, { textMode: true });
    console.log("Encoded message:\n");
    console.log(messages[0]);
    if (messages.length > 1) console.log(messages[1]);
    console.log(`\nTotal: ${messages.length} messages`);
  }
}
