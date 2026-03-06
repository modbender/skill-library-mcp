// メッセージフォーマット（モバイル版と共通）

export function createMessage(content) {
  return JSON.stringify({
    version: '1',
    type: 'message',
    content,
    timestamp: Date.now()
  })
}

export function createFileMessage(filename, mimeType, dataBase64) {
  return Buffer.from(JSON.stringify({
    version: '1',
    type: 'file',
    filename,
    mimeType,
    data: dataBase64,
    timestamp: Date.now(),
  }))
}

export function createPing() {
  return JSON.stringify({ version: '1', type: 'ping' })
}

// 玄関PIN → 専用PINへの移行通知（受け取り側には表示しない）
export function createPinMigrate(myNumber, newPin) {
  return JSON.stringify({
    version: '1',
    type: 'pin_migrate',
    newPin,
    newUri: `0x0://${myNumber}/${newPin}`,
    timestamp: Date.now()
  })
}

export function parseMessage(raw) {
  try {
    const msg = JSON.parse(raw.toString())
    if (!msg.version || !msg.type) return null
    return msg
  } catch {
    return null
  }
}
