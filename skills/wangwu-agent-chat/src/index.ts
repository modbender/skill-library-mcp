/**
 * AgentChat - Nostr-based Agent messaging CLI
 * 
 * MVP Features:
 * - Login with npub/nsec
 * - Send direct messages
 * - Receive messages
 * - File support (small files via Nostr events)
 */

import { SimplePool, nip04, Kind, finalizeEvent, getEventHash } from "nostr-tools";
import { readFileSync, writeFileSync, existsSync } from "fs";
import { homedir } from "os";
import { join } from "path";

// ============================================================================
// Types
// ============================================================================

interface Config {
  npub: string;
  nsec: string;
  relays: string[];
}

interface Message {
  type: "message";
  from: string;
  to: string;
  content: string;
  content_type: "text/plain" | "application/json";
  timestamp: number;
}

// ============================================================================
// Config
// ============================================================================

const CONFIG_PATH = join(homedir(), ".agent-chat", "config.json");

function loadConfig(): Config {
  if (existsSync(CONFIG_PATH)) {
    return JSON.parse(readFileSync(CONFIG_PATH, "utf-8"));
  }
  throw new Error("Config not found. Run: agent-chat login <nsec>");
}

function saveConfig(config: Config): void {
  const dir = join(homedir(), ".agent-chat");
  import("fs").then(fs => {
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
  });
}

// ============================================================================
// Nostr Client
// ============================================================================

class AgentChatClient {
  private pool: SimplePool;
  private relays: string[];
  private keys: { pubkey: string; privkey: Uint8Array };

  constructor(npub: string, npriv: string, relays: string[] = []) {
    this.pool = new SimplePool();
    this.relays = relays.length > 0 ? relays : ["wss://relay.damus.io", "wss://nos.lol"];
    this.keys = {
      pubkey: npub,
      privkey: typeof npriv === 'string' ? new Uint8Array(Buffer.from(npriv, 'hex')) : npriv,
    };
  }

  // Send a direct message
  async send(to: string, content: string, contentType: "text/plain" | "application/json" = "text/plain"): Promise<string> {
    const plaintext = JSON.stringify({ to, content, content_type: contentType });
    const encrypted = await nip04.encrypt(this.keys.privkey, to, plaintext);
    
    const event = finalizeEvent({
      kind: 4 as Kind, // Encrypted DM
      created_at: Math.floor(Date.now() / 1000),
      tags: [["p", to]],
      content: encrypted,
      pubkey: this.keys.pubkey,
    }, this.keys.privkey);

    const pubs = this.pool.publish(this.relays, event);
    await Promise.all(pubs);
    
    return event.id;
  }

  // Subscribe to DMs
  async *messages() {
    const subscription = this.pool.subscribeMany(this.relays, [
      {
        kinds: [4],
        "#p": [this.keys.pubkey],
        limit: 50,
      },
    ]);

    for await (const msg of subscription) {
      try {
        const decrypted = await nip04.decrypt(this.keys.privkey, msg.pubkey, msg.content);
        const payload = JSON.parse(decrypted);
        yield {
          id: msg.id,
          from: msg.pubkey,
          ...payload,
          timestamp: msg.created_at * 1000,
        };
      } catch (e) {
        // Skip unparseable messages
      }
    }
  }

  // Close connections
  close(): void {
    this.pool.close(this.relays);
  }
}

// ============================================================================
// CLI Commands
// ============================================================================

async function login(nsec: string): Promise<void> {
  // Decode nsec to get private key bytes
  const { getPublicKey, nip19 } = await import("nostr-tools");
  
  let privateKey: Uint8Array;
  if (nsec.startsWith('nsec')) {
    const decoded = nip19.decode(nsec);
    privateKey = decoded.data as Uint8Array;
  } else {
    // Assume hex string
    privateKey = new Uint8Array(Buffer.from(nsec, 'hex'));
  }
  
  const npub = getPublicKey(privateKey);
  
  const config: Config = {
    npub,
    nsec,
    relays: [],
  };
  
  saveConfig(config);
  console.log(`✅ Logged in as: ${npub}`);
}

async function send(toNpub: string, content: string): Promise<void> {
  const config = loadConfig();
  const client = new AgentChatClient(config.npub, config.nsec, config.relays);
  
  const id = await client.send(toNpub, content);
  console.log(`✅ Message sent! ID: ${id}`);
  
  client.close();
}

async function receive(limit = 10): Promise<void> {
  const config = loadConfig();
  const client = new AgentChatClient(config.npub, config.nsec, config.relays);
  
  console.log("📥 Listening for messages...");
  
  let count = 0;
  for await (const msg of client.messages()) {
    console.log(`\n[${new Date(msg.timestamp).toLocaleString()}]`);
    console.log(`From: ${msg.from}`);
    console.log(`Content: ${msg.content}`);
    count++;
    if (count >= limit) break;
  }
  
  client.close();
}

function status(): void {
  try {
    const config = loadConfig();
    console.log(`🟢 Logged in: ${config.npub}`);
    console.log(`Relays: ${config.relays.length > 0 ? config.relays.join(", ") : "default"}`);
  } catch {
    console.log("🔴 Not logged in. Run: agent-chat login <nsec>");
  }
}

// ============================================================================
// Main
// ============================================================================

const args = process.argv.slice(2);
const command = args[0];

switch (command) {
  case "login":
    if (!args[1]) {
      console.error("Usage: agent-chat login <nsec>");
      process.exit(1);
    }
    login(args[1]);
    break;
    
  case "send":
    if (!args[1] || !args[2]) {
      console.error("Usage: agent-chat send <npub> <message>");
      process.exit(1);
    }
    send(args[1], args[2]);
    break;
    
  case "receive":
    receive(parseInt(args[1]) || 10);
    break;
    
  case "status":
    status();
    break;
    
  default:
    console.log(`
AgentChat CLI - Nostr-based Agent messaging

Usage:
  agent-chat login <nsec>     # Login with private key
  agent-chat send <npub> <msg> # Send message
  agent-chat receive [count]   # Receive messages
  agent-chat status            # Show status
    `);
}
