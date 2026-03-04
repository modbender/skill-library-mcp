#!/usr/bin/env node
/**
 * Medina Station — Ring Gates Network Monitor & Assembler
 *
 * Named after Medina Station from The Expanse — the hub that sits at the center
 * of ring space, monitoring all traffic flowing between gates.
 *
 * This is the external observer. It watches OK Computer channels, detects Ring Gate
 * transmissions, assembles sharded data, and can deploy content to OK Computer pages.
 *
 * Usage:
 *   node medina.js scan                           Scan all known computers for Ring Gate traffic
 *   node medina.js status                         Network status overview
 *   node medina.js watch <channel> [interval]     Watch a channel for new messages
 *   node medina.js assemble <channel>             Assemble latest transmission from channel
 *   node medina.js assemble-sharded <channel>     Assemble sharded transmission
 *   node medina.js deploy <channel> <tokenId>     Assemble + deploy to OK Computer page
 *   node medina.js estimate <bytes>               Estimate transmission cost
 *   node medina.js read <channel> [count]         Read raw Ring Gate messages from channel
 */

const { OKComputer } = require("./okcomputer");
const {
  RingGate,
  MSG_TYPES,
  FLAGS,
  MAX_MESSAGE_LENGTH,
  MAX_PAYLOAD_LENGTH,
} = require("./ring-gate");

// --- Configuration ---

// Known fleet — potdealer's OK Computers
const FLEET = [1399]; // Add more token IDs as acquired

// Standard Ring Gate channel patterns to scan
const CHANNEL_PATTERNS = [
  "rg_{id}_broadcast",
  "rg_control_{id}",
];

// Polling interval for watch mode (ms)
const DEFAULT_WATCH_INTERVAL = 15000; // 15 seconds

// --- Medina Station Class ---

class MedinaStation {
  /**
   * @param {number[]} [knownComputers] - Token IDs of known OK Computers
   * @param {string} [rpcUrl] - Base RPC URL
   */
  constructor(knownComputers = FLEET, rpcUrl) {
    this.computers = knownComputers;
    this.ok = new OKComputer(knownComputers[0] || 1399, rpcUrl);
    this.rpcUrl = rpcUrl;
  }

  /**
   * Scan all known computers for Ring Gate activity.
   * Checks broadcast and control channels for each computer.
   * @returns {Promise<object>} Network scan results
   */
  async scanNetwork() {
    const results = {
      timestamp: new Date().toISOString(),
      computers: {},
      transmissions: [],
      totalMessages: 0,
    };

    for (const tokenId of this.computers) {
      const ok = new OKComputer(tokenId, this.rpcUrl);
      const computerResult = {
        tokenId,
        owner: null,
        username: null,
        channels: {},
      };

      try {
        computerResult.owner = await ok.getOwner();
        computerResult.username = await ok.readUsername() || "(not set)";
      } catch (e) {
        computerResult.error = e.message;
      }

      // Scan standard channels for this computer
      for (const pattern of CHANNEL_PATTERNS) {
        const channel = pattern.replace("{id}", tokenId);
        try {
          const count = await ok.getMessageCount(channel);
          if (count > 0) {
            computerResult.channels[channel] = { count };

            // Check for Ring Gate messages
            const messages = await ok.readChannel(channel, Math.min(count, 50));
            const rgMessages = messages.filter(
              (m) => m.text && RingGate.isRingGate(m.text)
            );

            computerResult.channels[channel].ringGateMessages = rgMessages.length;

            // Find manifests
            for (const msg of rgMessages) {
              const parsed = RingGate.decodeMessage(msg.text);
              if (parsed && parsed.type === MSG_TYPES.MANIFEST) {
                try {
                  const meta = JSON.parse(parsed.payload);
                  results.transmissions.push({
                    txid: parsed.txid,
                    channel,
                    computer: tokenId,
                    contentType: meta.type,
                    size: meta.size,
                    chunks: meta.chunks,
                    hash: meta.hash,
                    sharded: !!(meta.shards && meta.shards.length > 0),
                    shardCount: meta.shards ? meta.shards.length : 0,
                    timestamp: msg.timestamp,
                    time: msg.time,
                    sender: msg.sender,
                  });
                } catch {}
              }
            }

            results.totalMessages += rgMessages.length;
          }
        } catch {
          // Channel doesn't exist or can't be read — that's fine
        }
      }

      results.computers[tokenId] = computerResult;
    }

    return results;
  }

  /**
   * Watch a channel for new Ring Gate messages, calling back on new ones.
   * @param {string} channel - Channel to watch
   * @param {function} callback - Called with (message) on new Ring Gate messages
   * @param {number} [interval] - Poll interval in ms
   * @returns {object} Watcher handle with stop() method
   */
  watchChannel(channel, callback, interval = DEFAULT_WATCH_INTERVAL) {
    let lastCount = 0;
    let running = true;

    const poll = async () => {
      if (!running) return;
      try {
        const count = await this.ok.getMessageCount(channel);
        if (count > lastCount) {
          // Read new messages
          const newMessages = await this.ok.readChannel(channel, count - lastCount);
          for (const msg of newMessages) {
            if (msg.text && RingGate.isRingGate(msg.text)) {
              const parsed = RingGate.decodeMessage(msg.text);
              callback({
                raw: msg,
                parsed,
                channel,
              });
            }
          }
          lastCount = count;
        }
      } catch (e) {
        // First poll — initialize count
        if (lastCount === 0) {
          try {
            lastCount = await this.ok.getMessageCount(channel);
          } catch {}
        }
      }

      if (running) {
        setTimeout(poll, interval);
      }
    };

    // Initialize
    (async () => {
      try {
        lastCount = await this.ok.getMessageCount(channel);
      } catch {
        lastCount = 0;
      }
      console.log(`Watching ${channel} (${lastCount} existing messages, polling every ${interval / 1000}s)`);
      setTimeout(poll, interval);
    })();

    return {
      stop: () => {
        running = false;
      },
    };
  }

  /**
   * Assemble the latest transmission from a single channel.
   * @param {string} channel
   * @returns {Promise<object>} { data, manifest, chunks }
   */
  async assembleTransmission(channel) {
    const rg = new RingGate(this.computers[0] || 1399, this.rpcUrl);
    const allMessages = await this.ok.readAllMessages(channel);

    // Find Ring Gate messages
    const rgMessages = allMessages
      .filter((m) => m.text && RingGate.isRingGate(m.text))
      .map((m) => m.text);

    if (rgMessages.length === 0) {
      throw new Error(`No Ring Gate messages found in ${channel}`);
    }

    // Find the latest manifest
    let manifestMsg = null;
    let manifestParsed = null;
    for (let i = rgMessages.length - 1; i >= 0; i--) {
      const parsed = RingGate.decodeMessage(rgMessages[i]);
      if (parsed && parsed.type === MSG_TYPES.MANIFEST) {
        manifestMsg = rgMessages[i];
        manifestParsed = parsed;
        break;
      }
    }

    if (!manifestMsg) {
      throw new Error(`No manifest found in ${channel}`);
    }

    const meta = JSON.parse(manifestParsed.payload);

    // Collect data chunks
    const dataChunks = rgMessages.filter((msg) => {
      const p = RingGate.decodeMessage(msg);
      return p && p.type === MSG_TYPES.DATA && p.txid === manifestParsed.txid;
    });

    const data = RingGate.assemble(manifestMsg, dataChunks);

    return {
      data,
      txid: manifestParsed.txid,
      contentType: meta.type,
      size: meta.size,
      hash: meta.hash,
      chunks: dataChunks.length,
      verified: RingGate.hash(data) === meta.hash,
    };
  }

  /**
   * Assemble a sharded transmission from a manifest channel.
   * @param {string} manifestChannel
   * @returns {Promise<object>} { data, manifest, shards }
   */
  async assembleShardedTransmission(manifestChannel) {
    const allMessages = await this.ok.readAllMessages(manifestChannel);

    // Find latest sharded manifest
    let manifestMsg = null;
    let manifestParsed = null;
    let meta = null;

    for (let i = allMessages.length - 1; i >= 0; i--) {
      const msg = allMessages[i];
      if (!msg.text || !RingGate.isRingGate(msg.text)) continue;
      const parsed = RingGate.decodeMessage(msg.text);
      if (parsed && parsed.type === MSG_TYPES.MANIFEST) {
        try {
          const m = JSON.parse(parsed.payload);
          if (m.shards && m.shards.length > 0) {
            manifestMsg = msg.text;
            manifestParsed = parsed;
            meta = m;
            break;
          }
        } catch {}
      }
    }

    if (!manifestMsg || !meta) {
      throw new Error(`No sharded manifest found in ${manifestChannel}`);
    }

    // Read from all shard channels
    const allDataChunks = [];
    const shardResults = [];

    for (const shard of meta.shards) {
      const shardOk = new OKComputer(shard.computer, this.rpcUrl);
      try {
        const shardMessages = await shardOk.readAllMessages(shard.channel);
        const shardChunks = shardMessages
          .filter((m) => m.text && RingGate.isRingGate(m.text))
          .filter((m) => {
            const p = RingGate.decodeMessage(m.text);
            return p && p.type === MSG_TYPES.DATA && p.txid === manifestParsed.txid;
          })
          .map((m) => m.text);

        allDataChunks.push(...shardChunks);
        shardResults.push({
          computer: shard.computer,
          channel: shard.channel,
          expectedRange: shard.range,
          chunksFound: shardChunks.length,
          status: "ok",
        });
      } catch (e) {
        shardResults.push({
          computer: shard.computer,
          channel: shard.channel,
          expectedRange: shard.range,
          chunksFound: 0,
          status: "error",
          error: e.message,
        });
      }
    }

    const data = RingGate.assemble(manifestMsg, allDataChunks);

    return {
      data,
      txid: manifestParsed.txid,
      contentType: meta.type,
      size: meta.size,
      hash: meta.hash,
      totalChunks: meta.chunks,
      shards: shardResults,
      verified: RingGate.hash(data) === meta.hash,
    };
  }

  /**
   * Assemble a transmission and deploy it to an OK Computer's page.
   * @param {string} channel - Channel containing the transmission
   * @param {number} targetTokenId - Token ID to deploy page to
   * @param {boolean} [sharded] - Whether this is a sharded transmission
   * @returns {Promise<object>} { data, deployTx } — Bankr transaction JSON
   */
  async deployToPage(channel, targetTokenId, sharded = false) {
    const result = sharded
      ? await this.assembleShardedTransmission(channel)
      : await this.assembleTransmission(channel);

    if (!result.verified) {
      throw new Error("Hash verification failed — will not deploy corrupted data");
    }

    const targetOk = new OKComputer(targetTokenId, this.rpcUrl);
    const deployTx = targetOk.buildSetPage(result.data);

    return {
      ...result,
      targetTokenId,
      deployTx,
    };
  }

  /**
   * Get network status overview.
   * @returns {Promise<object>}
   */
  async getNetworkStatus() {
    const status = {
      timestamp: new Date().toISOString(),
      fleet: [],
      networkStats: null,
    };

    for (const tokenId of this.computers) {
      const ok = new OKComputer(tokenId, this.rpcUrl);
      try {
        const owner = await ok.getOwner();
        const username = await ok.readUsername() || "(not set)";
        status.fleet.push({ tokenId, owner, username, status: "online" });
      } catch (e) {
        status.fleet.push({ tokenId, status: "error", error: e.message });
      }
    }

    try {
      const ok = new OKComputer(this.computers[0] || 1399, this.rpcUrl);
      status.networkStats = await ok.getNetworkStats();
    } catch {}

    return status;
  }
}

// --- CLI ---

if (require.main === module) {
  const args = process.argv.slice(2);
  const cmd = args[0];

  const medina = new MedinaStation();

  if (!cmd) {
    console.log("Medina Station — Ring Gates Network Monitor\n");
    console.log("Usage:");
    console.log("  node medina.js scan                             Scan fleet for Ring Gate traffic");
    console.log("  node medina.js status                           Network status overview");
    console.log("  node medina.js watch <channel> [interval_sec]   Watch channel for new messages");
    console.log("  node medina.js assemble <channel>               Assemble transmission from channel");
    console.log("  node medina.js assemble-sharded <channel>       Assemble sharded transmission");
    console.log("  node medina.js deploy <channel> <tokenId>       Assemble + build deploy transaction");
    console.log("  node medina.js estimate <bytes>                 Estimate transmission cost");
    console.log("  node medina.js read <channel> [count]           Read Ring Gate messages from channel");
    console.log("\nFleet: " + FLEET.join(", "));
    process.exit(0);
  }

  (async () => {
    try {
      if (cmd === "scan") {
        console.log("=== MEDINA STATION — NETWORK SCAN ===\n");
        console.log("Scanning fleet...\n");
        const results = await medina.scanNetwork();

        for (const [tokenId, computer] of Object.entries(results.computers)) {
          console.log(`OKCPU #${tokenId} — ${computer.username}`);
          if (computer.owner) console.log(`  Owner: ${computer.owner}`);
          if (Object.keys(computer.channels).length > 0) {
            for (const [ch, info] of Object.entries(computer.channels)) {
              console.log(`  ${ch}: ${info.count} msgs (${info.ringGateMessages || 0} Ring Gate)`);
            }
          } else {
            console.log("  No Ring Gate channels detected");
          }
          console.log();
        }

        if (results.transmissions.length > 0) {
          console.log("--- TRANSMISSIONS ---\n");
          for (const tx of results.transmissions) {
            console.log(`  [${tx.txid}] ${tx.contentType} — ${tx.size} bytes, ${tx.chunks} chunks`);
            console.log(`    Channel: ${tx.channel} | Hash: ${tx.hash.slice(0, 16)}...`);
            console.log(`    Sharded: ${tx.sharded ? `Yes (${tx.shardCount} shards)` : "No"}`);
            console.log(`    Time: ${tx.time}`);
            console.log();
          }
        } else {
          console.log("No transmissions detected.\n");
        }

        console.log(`Total Ring Gate messages: ${results.totalMessages}`);
      } else if (cmd === "status") {
        console.log("=== MEDINA STATION — NETWORK STATUS ===\n");
        const status = await medina.getNetworkStatus();

        console.log("Fleet:");
        for (const node of status.fleet) {
          if (node.status === "online") {
            console.log(`  OKCPU #${node.tokenId} — ${node.username} (${node.owner.slice(0, 10)}...)`);
          } else {
            console.log(`  OKCPU #${node.tokenId} — ${node.status}: ${node.error}`);
          }
        }

        if (status.networkStats) {
          console.log("\nOK Computers Network:");
          for (const [ch, count] of Object.entries(status.networkStats)) {
            console.log(`  #${ch}: ${count} messages`);
          }
        }
      } else if (cmd === "watch") {
        const channel = args[1];
        const interval = (parseInt(args[2]) || 15) * 1000;

        if (!channel) {
          console.error("Usage: node medina.js watch <channel> [interval_sec]");
          process.exit(1);
        }

        console.log("=== MEDINA STATION — WATCH MODE ===\n");

        medina.watchChannel(
          channel,
          ({ raw, parsed }) => {
            const time = new Date().toISOString().slice(11, 19);
            const typeNames = Object.fromEntries(
              Object.entries(MSG_TYPES).map(([k, v]) => [v, k])
            );
            const typeName = typeNames[parsed.type] || parsed.type;

            console.log(
              `[${time}] ${typeName} txid=${parsed.txid} seq=${parsed.seq}/${parsed.total} ` +
              `flags=0x${parsed.flags.toString(16).padStart(2, "0")} ` +
              `payload=${parsed.payload.length} chars`
            );

            if (parsed.type === MSG_TYPES.MANIFEST) {
              try {
                const meta = JSON.parse(parsed.payload);
                console.log(
                  `         Manifest: ${meta.type}, ${meta.size} bytes, ${meta.chunks} chunks` +
                  (meta.shards ? `, ${meta.shards.length} shards` : "")
                );
              } catch {}
            }
          },
          interval
        );

        // Keep running until Ctrl+C
        process.on("SIGINT", () => {
          console.log("\nWatch stopped.");
          process.exit(0);
        });
      } else if (cmd === "assemble") {
        const channel = args[1];
        if (!channel) {
          console.error("Usage: node medina.js assemble <channel>");
          process.exit(1);
        }

        console.log(`=== MEDINA STATION — ASSEMBLE ===\n`);
        console.log(`Reading from ${channel}...\n`);

        const result = await medina.assembleTransmission(channel);
        console.log(`Transmission ID: ${result.txid}`);
        console.log(`Content type:    ${result.contentType}`);
        console.log(`Size:            ${result.size} bytes`);
        console.log(`Chunks:          ${result.chunks}`);
        console.log(`Hash:            ${result.hash}`);
        console.log(`Verified:        ${result.verified ? "YES" : "FAILED"}`);
        console.log(`\n--- DATA PREVIEW (first 500 chars) ---\n`);
        console.log(result.data.slice(0, 500));
        if (result.data.length > 500) console.log(`\n... (${result.data.length - 500} more chars)`);
      } else if (cmd === "assemble-sharded") {
        const channel = args[1];
        if (!channel) {
          console.error("Usage: node medina.js assemble-sharded <channel>");
          process.exit(1);
        }

        console.log(`=== MEDINA STATION — ASSEMBLE SHARDED ===\n`);
        console.log(`Reading manifest from ${channel}...\n`);

        const result = await medina.assembleShardedTransmission(channel);
        console.log(`Transmission ID: ${result.txid}`);
        console.log(`Content type:    ${result.contentType}`);
        console.log(`Size:            ${result.size} bytes`);
        console.log(`Total chunks:    ${result.totalChunks}`);
        console.log(`Hash:            ${result.hash}`);
        console.log(`Verified:        ${result.verified ? "YES" : "FAILED"}`);
        console.log(`\nShards:`);
        for (const shard of result.shards) {
          console.log(
            `  OKCPU #${shard.computer} — ${shard.channel}: ` +
            `${shard.chunksFound} chunks (${shard.status})`
          );
        }
        console.log(`\n--- DATA PREVIEW (first 500 chars) ---\n`);
        console.log(result.data.slice(0, 500));
        if (result.data.length > 500) console.log(`\n... (${result.data.length - 500} more chars)`);
      } else if (cmd === "deploy") {
        const channel = args[1];
        const tokenId = parseInt(args[2]);
        const sharded = args[3] === "--sharded";

        if (!channel || !tokenId) {
          console.error("Usage: node medina.js deploy <channel> <tokenId> [--sharded]");
          process.exit(1);
        }

        console.log(`=== MEDINA STATION — DEPLOY ===\n`);
        console.log(`Assembling from ${channel}...`);
        console.log(`Target: OKCPU #${tokenId}\n`);

        const result = await medina.deployToPage(channel, tokenId, sharded);
        console.log(`Transmission ID: ${result.txid}`);
        console.log(`Content type:    ${result.contentType}`);
        console.log(`Size:            ${result.size} bytes`);
        console.log(`Verified:        ${result.verified ? "YES" : "FAILED"}`);
        console.log(`\nBankr transaction JSON:`);
        console.log(JSON.stringify(result.deployTx, null, 2));
        console.log(`\nSubmit via: curl -X POST https://api.bankr.bot/agent/submit -H "X-API-Key: $BANKR_API_KEY" -H "Content-Type: application/json" -d '${JSON.stringify({ transaction: result.deployTx })}'`);
      } else if (cmd === "estimate") {
        const size = parseInt(args[1]) || 1024;
        const computers = parseInt(args[2]) || 1;

        const b64Size = Math.ceil(size * (4 / 3));
        const totalMessages = Math.ceil(b64Size / MAX_PAYLOAD_LENGTH) + 1;
        const messagesPerComputer = Math.ceil((totalMessages - 1) / computers) + 1;
        const gasCost = totalMessages * 0.000005;
        const ethPrice = 3000;

        console.log("=== MEDINA STATION — TRANSMISSION ESTIMATE ===\n");
        console.log(`Data size:           ${size} bytes (${(size / 1024).toFixed(1)} KB)`);
        console.log(`Base64 size:         ${b64Size} chars`);
        console.log(`Total messages:      ${totalMessages} (${totalMessages - 1} data + 1 manifest)`);
        console.log(`Computers:           ${computers}`);
        console.log(`Messages/computer:   ~${messagesPerComputer}`);
        console.log(`Est. gas cost:       ~${gasCost.toFixed(6)} ETH (~$${(gasCost * ethPrice).toFixed(4)})`);
        console.log(`\nExamples:`);
        console.log(`  64KB (1 page):     ~${Math.ceil(65536 * 4 / 3 / MAX_PAYLOAD_LENGTH) + 1} messages`);
        console.log(`  200KB:             ~${Math.ceil(204800 * 4 / 3 / MAX_PAYLOAD_LENGTH) + 1} messages`);
        console.log(`  1MB:               ~${Math.ceil(1048576 * 4 / 3 / MAX_PAYLOAD_LENGTH) + 1} messages`);
      } else if (cmd === "read") {
        const channel = args[1];
        const count = parseInt(args[2]) || 20;

        if (!channel) {
          console.error("Usage: node medina.js read <channel> [count]");
          process.exit(1);
        }

        console.log(`=== MEDINA STATION — READ CHANNEL ===\n`);
        console.log(`Channel: ${channel} (last ${count})\n`);

        const messages = await medina.ok.readChannel(channel, count);
        const typeNames = Object.fromEntries(
          Object.entries(MSG_TYPES).map(([k, v]) => [v, k])
        );

        for (const msg of messages) {
          if (msg.error) {
            console.log(`  [#${msg.index}] Error: ${msg.error}`);
            continue;
          }

          if (msg.text && RingGate.isRingGate(msg.text)) {
            const parsed = RingGate.decodeMessage(msg.text);
            const typeName = typeNames[parsed.type] || parsed.type;
            console.log(
              `  [#${msg.index}] RG ${typeName} txid=${parsed.txid} ` +
              `seq=${parsed.seq}/${parsed.total} payload=${parsed.payload.length} chars`
            );

            if (parsed.type === MSG_TYPES.MANIFEST) {
              try {
                const meta = JSON.parse(parsed.payload);
                console.log(
                  `           ${meta.type} | ${meta.size} bytes | ${meta.chunks} chunks | hash=${meta.hash.slice(0, 12)}...`
                );
              } catch {}
            }
          } else {
            console.log(`  [#${msg.index}] (non-RG) ${(msg.text || "").slice(0, 80)}`);
          }
        }
      } else {
        console.error(`Unknown command: ${cmd}`);
        process.exit(1);
      }
    } catch (e) {
      console.error(`Error: ${e.message}`);
      process.exit(1);
    }
  })();
}

// --- Exports ---

module.exports = { MedinaStation, FLEET };
