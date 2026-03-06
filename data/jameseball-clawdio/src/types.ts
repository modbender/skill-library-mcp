import type { TransportCipher } from './crypto.js';

export interface ClawdioOptions {
  port?: number;
  host?: string;
  keyDir?: string;
  identityPath?: string;       // path to persistent identity/trust file
  heartbeatMs?: number;        // ping interval (default 5000)
  heartbeatTimeout?: number;   // peer considered down after this (default 15000)
  autoAccept?: boolean;        // auto-accept all connections (default false, for testing)
}

export interface AgentMessage {
  task?: string;
  result?: any;
  context?: any;
  status?: 'ok' | 'error';
  [key: string]: any;
}

export interface Peer {
  id: string;               // hex-encoded static public key
  staticKey: Uint8Array;
  cipher: TransportCipher;
  address: string;
  ws?: import('ws').WebSocket;
}

export interface WireMessage {
  type: 'noise1' | 'noise2' | 'noise3' | 'message' | 'ping' | 'pong';
  payload: string;          // base64
  nonce?: string;           // base64 nonce for messages
  counter?: string;         // monotonic counter for replay protection
}

export type PeerStatus = 'alive' | 'stale' | 'down';
export type TrustLevel = 'pending' | 'accepted' | 'human-verified';

export interface ConnectionRequest {
  id: string;               // hex public key
  fingerprint: string;      // emoji fingerprint
  safetyNumber: string;
  address: string;
}

export interface TrustedPeerRecord {
  id: string;
  trust: TrustLevel;
  addedAt: string;
  owner?: string;            // human owner name if known
}

export interface IdentityData {
  publicKey: string;
  secretKey: string;
  created: string;
  owner?: string;
  trustedPeers: TrustedPeerRecord[];
}

export type MessageHandler = (message: AgentMessage, fromPeerId: string) => void;
