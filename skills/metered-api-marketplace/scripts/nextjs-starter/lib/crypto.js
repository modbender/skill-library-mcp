import crypto from 'node:crypto';

export const nowMs = () => Date.now();
export const sha256Hex = (buf) => crypto.createHash('sha256').update(buf).digest('hex');
export const hmacHex = (secret, msg) => crypto.createHmac('sha256', secret).update(msg).digest('hex');

export function timingSafeHexEqual(aHex, bHex) {
  const a = Buffer.from(String(aHex), 'hex');
  const b = Buffer.from(String(bHex), 'hex');
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(a, b);
}

export const id = (prefix) => `${prefix}_${crypto.randomBytes(12).toString('hex')}`;
