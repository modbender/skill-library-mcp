import fs from 'fs'
import path from 'path'
import os from 'os'
import { randomUUID } from 'crypto'
import { hashPin } from '../core/pin.js'

const FILE = path.join(os.homedir(), '.0x0', 'pins.json')

export function loadAll() {
  if (!fs.existsSync(FILE)) return []
  try {
    return JSON.parse(fs.readFileSync(FILE, 'utf8'))
  } catch {
    return []
  }
}

export function saveAll(pins) {
  fs.writeFileSync(FILE, JSON.stringify(pins, null, 2), { mode: 0o600 })
}

export function create({ value, label = '', expiry = 'none', expiresAt = null, type = 'direct' }) {
  const pins = loadAll()
  const pin = {
    id: randomUUID(),
    value,
    valueHash: hashPin(value),
    label,
    expiry,
    expiresAt,
    type,   // 'direct' | 'lobby'
    createdAt: Date.now(),
    isActive: true
  }
  pins.push(pin)
  saveAll(pins)
  return pin
}

export function findByValue(value) {
  return loadAll().find(p => p.value === value && p.isActive) || null
}

export function findById(id) {
  return loadAll().find(p => p.id === id) || null
}

export function update(id, changes) {
  const pins = loadAll()
  const idx = pins.findIndex(p => p.id === id)
  if (idx === -1) return null
  pins[idx] = { ...pins[idx], ...changes }
  saveAll(pins)
  return pins[idx]
}

export function rotate(id, newValue) {
  return update(id, { value: newValue, valueHash: hashPin(newValue) })
}

export function revoke(id) {
  return update(id, { isActive: false })
}

export function getActive() {
  const now = Date.now()
  return loadAll().filter(p => {
    if (!p.isActive) return false
    if (p.expiresAt && p.expiresAt < now) return false
    return true
  })
}
