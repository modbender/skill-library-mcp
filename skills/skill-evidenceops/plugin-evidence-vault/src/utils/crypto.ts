import * as crypto from 'crypto';
import * as fs from 'fs/promises';
import { Readable } from 'stream';

export async function hashFile(filepath: string): Promise<string> {
  const fileBuffer = await fs.readFile(filepath);
  return hashBuffer(fileBuffer);
}

export async function hashBuffer(buffer: Buffer): Promise<string> {
  const hash = crypto.createHash('sha256');
  hash.update(buffer);
  return hash.digest('hex');
}

export async function hashStream(stream: Readable): Promise<string> {
  const hash = crypto.createHash('sha256');
  return new Promise((resolve, reject) => {
    stream.on('data', (chunk) => hash.update(chunk));
    stream.on('end', () => resolve(hash.digest('hex')));
    stream.on('error', reject);
  });
}

export function hashString(content: string): string {
  return crypto.createHash('sha256').update(content).digest('hex');
}

export function generateChainHash(
  previousHash: string | null,
  eventType: string,
  timestamp: string,
  data: string
): string {
  const payload = `${previousHash ?? 'genesis'}|${eventType}|${timestamp}|${data}`;
  return hashString(payload);
}

export function generateId(prefix: string = 'ev'): string {
  const timestamp = Date.now().toString(36);
  const random = crypto.randomBytes(8).toString('hex');
  return `${prefix}-${timestamp}-${random}`;
}
