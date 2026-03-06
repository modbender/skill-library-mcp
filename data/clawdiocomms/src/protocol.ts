import { WireMessage } from './types.js';

export function encodeWire(msg: WireMessage): string { return JSON.stringify(msg); }

export function decodeWire(data: string): WireMessage {
  const parsed = JSON.parse(data);
  if (!parsed.type || !parsed.payload) throw new Error('Invalid wire message');
  return parsed as WireMessage;
}

export function parseConnectionString(connStr: string): { publicKey: string; address: string } {
  const match = connStr.match(/^clawdio:\/\/([a-f0-9]+)@(.+)$/i);
  if (!match) throw new Error(`Invalid connection string: ${connStr}`);
  return { publicKey: match[1], address: match[2] };
}

export function buildConnectionString(publicKeyHex: string, host: string, port: number): string {
  return `clawdio://${publicKeyHex}@${host}:${port}`;
}
