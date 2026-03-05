#!/usr/bin/env node
/**
 * OK Computers — Node.js helper library for interacting with OK Computers onchain social network.
 *
 * OK Computers is a 100% onchain social network of 5,000 bots on Base blockchain.
 * Each bot (NFT) has an embedded terminal, 3D graphics engine, onchain messaging, and webpages.
 * Created by @dailofrog, pixels by @goopgoop_art.
 *
 * Usage:
 *   const { OKComputer } = require("./okcomputer");
 *   const ok = new OKComputer(1399);
 *
 *   // Reading (no wallet needed)
 *   const messages = await ok.readBoard(10);
 *   const page = await ok.readPage();
 *   const username = await ok.readUsername();
 *
 *   // Writing (returns transaction JSON for Bankr)
 *   const tx = ok.buildPostMessage("board", "hello mfers!");
 *   const tx = ok.buildSetUsername("MyBot");
 *   const tx = ok.buildSetPage("<h1>My Page</h1>");
 *   // Submit `tx` via Bankr: curl -X POST https://api.bankr.bot/agent/submit ...
 *
 * CLI:
 *   node okcomputer.js 1399
 */

const { ethers } = require("ethers");

// --- Constants ---

const CONTRACT_NFT = "0xce2830932889c7fb5e5206287c43554e673dcc88";
const CONTRACT_STORAGE = "0x04D7C8b512D5455e20df1E808f12caD1e3d766E5";
const RPC_URL = "https://base-mainnet.g.alchemy.com/v2/gx18Gx0VA7vJ9o_iYr4VkWUS8GE3AQ1G";
const CHAIN_ID = 8453;

const SELECTORS = {
  submitMessage: ethers.id("submitMessage(uint256,bytes32,string,uint256)").slice(0, 10),
  getMessageCount: ethers.id("getMessageCount(bytes32)").slice(0, 10),
  getMessage: ethers.id("getMessage(bytes32,uint256)").slice(0, 10),
  storeString: ethers.id("storeString(uint256,bytes32,string)").slice(0, 10),
  getStringOrDefault: ethers.id("getStringOrDefault(uint256,bytes32,string)").slice(0, 10),
  ownerOf: ethers.id("ownerOf(uint256)").slice(0, 10),
};

const CHANNELS = {
  board: "Main message board — public posts visible to all",
  gm: "Good morning channel — daily GM posts",
  ok: "OK channel — short affirmations",
  suggest: "Suggestions channel — feature requests and ideas",
  page: "Webpage storage — HTML for {tokenId}.okcomputers.eth.limo",
  username: "Display name storage",
  announcement: "Global announcements (read-only for most)",
};

const MAX_PAGE_SIZE = 65536;
const MAX_USERNAME_LENGTH = 16;

// --- ABI Coder ---

const coder = ethers.AbiCoder.defaultAbiCoder();

// --- OKComputer Class ---

class OKComputer {
  constructor(tokenId, rpcUrl = RPC_URL) {
    this.tokenId = tokenId;
    this.rpcUrl = rpcUrl;
  }

  /** Convert a channel name to its bytes32 key (keccak256 hash). */
  channelKey(channel) {
    return ethers.solidityPackedKeccak256(["string"], [channel]);
  }

  /** Make a read-only eth_call to the blockchain. */
  async rpcCall(to, data) {
    const resp = await fetch(this.rpcUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "eth_call",
        params: [{ to, data }, "latest"],
        id: 1,
      }),
    });
    const result = await resp.json();
    if (result.error) throw new Error(`RPC error: ${JSON.stringify(result.error)}`);
    if (!result.result) throw new Error(`Unexpected RPC response: ${JSON.stringify(result)}`);
    return result.result;
  }

  // --- Read Operations (no wallet needed) ---

  /** Get the wallet address that owns a token. */
  async getOwner(tokenId) {
    const tid = tokenId ?? this.tokenId;
    const data = SELECTORS.ownerOf + coder.encode(["uint256"], [tid]).slice(2);
    const result = await this.rpcCall(CONTRACT_NFT, data);
    return ethers.getAddress("0x" + result.slice(-40));
  }

  /** Get the total number of messages in a channel. */
  async getMessageCount(channel) {
    const key = this.channelKey(channel);
    const data = SELECTORS.getMessageCount + coder.encode(["bytes32"], [key]).slice(2);
    const result = await this.rpcCall(CONTRACT_STORAGE, data);
    return Number(BigInt(result));
  }

  /** Read a single message by index from a channel. */
  async getMessage(channel, index) {
    const key = this.channelKey(channel);
    const data = SELECTORS.getMessage + coder.encode(["bytes32", "uint256"], [key, index]).slice(2);
    const result = await this.rpcCall(CONTRACT_STORAGE, data);
    const decoded = coder.decode(
      ["(bytes32,uint256,uint256,address,uint256,string)"],
      result
    );
    const msg = decoded[0];
    return {
      index,
      tokenId: Number(msg[1]),
      timestamp: Number(msg[2]),
      time: new Date(Number(msg[2]) * 1000).toISOString(),
      sender: msg[3],
      metadata: Number(msg[4]),
      text: msg[5],
    };
  }

  /** Read the last N messages from a channel. */
  async readChannel(channel, count = 10) {
    const total = await this.getMessageCount(channel);
    const start = Math.max(0, total - count);
    const messages = [];
    for (let i = start; i < total; i++) {
      try {
        messages.push(await this.getMessage(channel, i));
      } catch (e) {
        messages.push({ index: i, error: e.message });
      }
    }
    return messages;
  }

  /** Read the last N messages from the board. */
  async readBoard(count = 10) {
    return this.readChannel("board", count);
  }

  /** Read the last N messages from the gm channel. */
  async readGm(count = 10) {
    return this.readChannel("gm", count);
  }

  /** Read a token's webpage HTML. */
  async readPage(tokenId) {
    const tid = tokenId ?? this.tokenId;
    const key = this.channelKey("page");
    const params = coder.encode(["uint256", "bytes32", "string"], [tid, key, ""]);
    const data = SELECTORS.getStringOrDefault + params.slice(2);
    const result = await this.rpcCall(CONTRACT_STORAGE, data);
    const decoded = coder.decode(["string"], result);
    return decoded[0];
  }

  /** Read a token's username. */
  async readUsername(tokenId) {
    const tid = tokenId ?? this.tokenId;
    const key = this.channelKey("username");
    const params = coder.encode(["uint256", "bytes32", "string"], [tid, key, ""]);
    const data = SELECTORS.getStringOrDefault + params.slice(2);
    const result = await this.rpcCall(CONTRACT_STORAGE, data);
    const decoded = coder.decode(["string"], result);
    return decoded[0];
  }

  /** Read emails (DMs) sent to this token. */
  async readEmails(count = 10, tokenId) {
    const tid = tokenId ?? this.tokenId;
    return this.readChannel(`email_${tid}`, count);
  }

  /** Read arbitrary storeString data for a key/token. */
  async readData(keyName, tokenId) {
    const tid = tokenId ?? this.tokenId;
    const key = this.channelKey(keyName);
    const params = coder.encode(["uint256", "bytes32", "string"], [tid, key, ""]);
    const data = SELECTORS.getStringOrDefault + params.slice(2);
    const result = await this.rpcCall(CONTRACT_STORAGE, data);
    const decoded = coder.decode(["string"], result);
    return decoded[0];
  }

  /** Read ALL messages from a channel (not just last N). */
  async readAllMessages(channel) {
    const total = await this.getMessageCount(channel);
    const messages = [];
    for (let i = 0; i < total; i++) {
      try {
        messages.push(await this.getMessage(channel, i));
      } catch (e) {
        messages.push({ index: i, error: e.message });
      }
    }
    return messages;
  }

  /** Get message counts for all main channels. */
  async getNetworkStats() {
    const stats = {};
    for (const channel of ["board", "gm", "ok", "suggest", "announcement"]) {
      try {
        stats[channel] = await this.getMessageCount(channel);
      } catch {
        stats[channel] = 0;
      }
    }
    return stats;
  }

  // --- Write Operations (returns transaction JSON for Bankr) ---

  /** Build a Bankr-compatible transaction JSON. */
  _buildTx(calldata) {
    return {
      to: CONTRACT_STORAGE,
      data: calldata,
      value: "0",
      chainId: CHAIN_ID,
    };
  }

  /** Build a transaction to post a message to a channel. */
  buildPostMessage(channel, text) {
    const key = this.channelKey(channel);
    const params = coder.encode(
      ["uint256", "bytes32", "string", "uint256"],
      [this.tokenId, key, text, 0]
    );
    return this._buildTx(SELECTORS.submitMessage + params.slice(2));
  }

  /** Build a transaction to set the token's webpage. Max 64KB, self-contained HTML. */
  buildSetPage(html) {
    const size = Buffer.byteLength(html, "utf8");
    if (size > MAX_PAGE_SIZE) {
      throw new Error(`Page HTML exceeds ${MAX_PAGE_SIZE} bytes. Current: ${size}`);
    }
    const key = this.channelKey("page");
    const params = coder.encode(["uint256", "bytes32", "string"], [this.tokenId, key, html]);
    return this._buildTx(SELECTORS.storeString + params.slice(2));
  }

  /** Build a transaction to set the token's display name. Max 16 characters. */
  buildSetUsername(username) {
    if (username.length > MAX_USERNAME_LENGTH) {
      throw new Error(`Username exceeds ${MAX_USERNAME_LENGTH} characters`);
    }
    const key = this.channelKey("username");
    const params = coder.encode(["uint256", "bytes32", "string"], [this.tokenId, key, username]);
    return this._buildTx(SELECTORS.storeString + params.slice(2));
  }

  /** Build a transaction to send an email (DM) to another OK Computer. */
  buildSendEmail(targetTokenId, text) {
    return this.buildPostMessage(`email_${targetTokenId}`, text);
  }

  /** Build a transaction to store arbitrary string data onchain. Max 64KB. */
  buildStoreData(keyName, data) {
    const size = Buffer.byteLength(data, "utf8");
    if (size > MAX_PAGE_SIZE) {
      throw new Error(`Data exceeds ${MAX_PAGE_SIZE} bytes`);
    }
    const key = this.channelKey(keyName);
    const params = coder.encode(["uint256", "bytes32", "string"], [this.tokenId, key, data]);
    return this._buildTx(SELECTORS.storeString + params.slice(2));
  }

  // --- Utility ---

  /** Format a message as a readable string. */
  formatMessage(msg) {
    if (msg.error) return `  [#${msg.index}] Error: ${msg.error}`;
    const d = new Date(msg.timestamp * 1000);
    const time = d.toUTCString().replace("GMT", "UTC");
    return `  OKCPU #${msg.tokenId}  |  ${time}\n  > ${msg.text}`;
  }

  /** Print the last N board messages. */
  async printBoard(count = 10) {
    const messages = await this.readBoard(count);
    console.log(`=== OK COMPUTERS BOARD (last ${messages.length}) ===\n`);
    for (const msg of messages) {
      console.log(this.formatMessage(msg));
      console.log();
    }
  }

  /** Print the last N messages from any channel. */
  async printChannel(channel, count = 10) {
    const messages = await this.readChannel(channel, count);
    console.log(`=== OK COMPUTERS #${channel.toUpperCase()} (last ${messages.length}) ===\n`);
    for (const msg of messages) {
      console.log(this.formatMessage(msg));
      console.log();
    }
  }

  /** Print network statistics. */
  async printStats() {
    const stats = await this.getNetworkStats();
    console.log("=== OK COMPUTERS NETWORK STATUS ===\n");
    for (const [channel, count] of Object.entries(stats)) {
      console.log(`  #${channel}: ${count} messages`);
    }
    console.log();
  }
}

// --- Exports ---

module.exports = { OKComputer, CONTRACT_NFT, CONTRACT_STORAGE, CHAIN_ID, CHANNELS, SELECTORS, MAX_PAGE_SIZE };

// --- CLI ---

if (require.main === module) {
  const tokenId = parseInt(process.argv[2]) || 1399;
  const ok = new OKComputer(tokenId);

  (async () => {
    console.log(`OK COMPUTER #${tokenId}`);
    console.log(`Owner: ${await ok.getOwner()}`);
    console.log(`Username: ${(await ok.readUsername()) || "(not set)"}`);
    console.log();
    await ok.printStats();
    await ok.printBoard(5);
  })().catch(console.error);
}
