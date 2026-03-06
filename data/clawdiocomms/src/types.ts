import type { TransportCipher } from './crypto.js';

export interface ClawdioOptions {
  identityPath?: string;
  heartbeatMs?: number;
  heartbeatTimeout?: number;
  autoAccept?: boolean;
  owner?: string;
}

export interface AgentMessage {
  task?: string;
  result?: any;
  context?: any;
  status?: 'ok' | 'error';
  [key: string]: any;
}

export interface Peer {
  id: string;
  staticKey: Uint8Array;
  cipher: TransportCipher;
}

export interface WireMessage {
  type: 'noise1' | 'noise2' | 'noise3' | 'message' | 'ping' | 'pong';
  payload: string;
  nonce?: string;
  counter?: string;
}

export type PeerStatus = 'alive' | 'stale' | 'down';
export type TrustLevel = 'pending' | 'accepted' | 'human-verified';

export interface ConnectionRequest {
  id: string;
  fingerprint: string;
  safetyNumber: string;
}

export interface TrustedPeerRecord {
  id: string;
  trust: TrustLevel;
  addedAt: string;
  owner?: string;
}

export interface IdentityData {
  publicKey: string;
  secretKey: string;
  created: string;
  owner?: string;
  trustedPeers: TrustedPeerRecord[];
}

export type MessageHandler = (message: AgentMessage, fromPeerId: string) => void;
export type SendHandler = (peerId: string, base64Message: string) => void;
