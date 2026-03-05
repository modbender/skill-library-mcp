import fs from 'fs'
import path from 'path'
import os from 'os'
import { randomUUID } from 'crypto'

const FILE = path.join(os.homedir(), '.0x0', 'queue.jsonl')
const TTL = 72 * 3_600_000 // 72時間

function ensureDir() {
  const dir = path.dirname(FILE)
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true })
}

// type: 'pin'     → 自分の受信箱PIN経由（pinId, content, localId）
// type: 'contact' → 相手のPINに直接送る（theirNumber, pin, content）
export function append({ type, pinId = null, theirNumber = null, pin = null, content, localId = null }) {
  ensureDir()
  const item = {
    id: localId || randomUUID(),
    type,
    pinId,
    theirNumber,
    pin,
    content,
    timestamp: Date.now(),
    expiresAt: Date.now() + TTL
  }
  fs.appendFileSync(FILE, JSON.stringify(item) + '\n')
  return item
}

export function loadAll() {
  if (!fs.existsSync(FILE)) return []
  const now = Date.now()
  return fs.readFileSync(FILE, 'utf8')
    .split('\n').filter(Boolean)
    .map(line => { try { return JSON.parse(line) } catch { return null } })
    .filter(Boolean)
    .filter(item => item.expiresAt > now)
}

export function remove(id) {
  const remaining = loadAll().filter(i => i.id !== id)
  saveAll(remaining)
}

export function purgeExpired() {
  saveAll(loadAll()) // loadAll already filters expired
}

function saveAll(items) {
  ensureDir()
  fs.writeFileSync(
    FILE,
    items.length ? items.map(i => JSON.stringify(i)).join('\n') + '\n' : '',
    { mode: 0o600 }
  )
}
