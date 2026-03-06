import fs from 'fs'
import path from 'path'
import os from 'os'
import { randomUUID } from 'crypto'
import { hashPin } from '../core/pin.js'

const BASE = path.join(os.homedir(), '.0x0', 'messages')

function dirForPin(pinValue) {
  return path.join(BASE, hashPin(pinValue))
}

// pubKeyHex 指定時は玄関PINサブスレッド、未指定は通常スレッド
function logFile(pinValue, pubKeyHex = null) {
  const base = dirForPin(pinValue)
  if (pubKeyHex) return path.join(base, pubKeyHex.slice(0, 16), 'log.jsonl')
  return path.join(base, 'log.jsonl')
}

export function append(pinValue, { from, content, isMine, type, filename, mimeType, pubKeyHex = null } = {}) {
  const file = logFile(pinValue, pubKeyHex)
  const dir = path.dirname(file)
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true })
  const safeFrom = String(from || '').replace(/[\n\r]/g, '').slice(0, 100)
  const safeContent = content != null ? String(content).slice(0, 65536) : undefined
  const record = {
    id: randomUUID(),
    from: safeFrom,
    timestamp: Date.now(),
    isMine
  }
  if (pubKeyHex) record.pubKeyHex = pubKeyHex
  if (safeContent !== undefined) record.content = safeContent
  if (type) record.type = String(type).slice(0, 20)
  if (filename) record.filename = String(filename).slice(0, 255)
  if (mimeType) record.mimeType = String(mimeType).slice(0, 100)
  fs.appendFileSync(file, JSON.stringify(record) + '\n')
}

export function list(pinValue, limit = 100, pubKeyHex = null) {
  const file = logFile(pinValue, pubKeyHex)
  if (!fs.existsSync(file)) return []
  return fs.readFileSync(file, 'utf8')
    .split('\n')
    .filter(Boolean)
    .map(line => { try { return JSON.parse(line) } catch { return null } })
    .filter(Boolean)
    .slice(-limit)
}

// 玄関PIN: サブスレッド一覧（接続者リスト）を返す
export function listLobbyThreads(pinValue) {
  const base = dirForPin(pinValue)
  if (!fs.existsSync(base)) return []
  return fs.readdirSync(base)
    .filter(name => fs.statSync(path.join(base, name)).isDirectory())
    .map(shortKey => {
      const msgs = list(pinValue, 1, shortKey)
      const latest = msgs[msgs.length - 1] || null
      return { pubKeyHex: shortKey, latest, count: list(pinValue, 1000, shortKey).length }
    })
}

export function getLatest(pinValue, pubKeyHex = null) {
  const msgs = list(pinValue, 1, pubKeyHex)
  return msgs[msgs.length - 1] || null
}

export function countUnread(pinValue, pubKeyHex = null) {
  return list(pinValue, 1000, pubKeyHex).filter(m => !m.isMine).length
}
