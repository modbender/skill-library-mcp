import crypto from 'crypto'

// PIN: デフォルト6文字の16進数 (a3f9c2 など)、最小4・最大16
export function generatePin(len = 6) {
  const bytes = Math.ceil(len / 2)
  return crypto.randomBytes(bytes).toString('hex').slice(0, len)
}

export function hashPin(pin) {
  return crypto.createHash('sha256').update(pin).digest('hex')
}
