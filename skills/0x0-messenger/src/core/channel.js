import crypto from 'crypto'

const APP_SALT = '0x0-v1-2026'

// チャンネルシークレット（Hyperswarm topic）
// 受信者の番号とPINからsha256で32バイトのトピックIDを生成
export function channelSecret(recipientNumber, pin) {
  const input = `0x0:${recipientNumber}:${pin}:${APP_SALT}`
  return crypto.createHash('sha256').update(input).digest()
}
