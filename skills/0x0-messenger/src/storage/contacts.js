import fs from 'fs'
import path from 'path'
import os from 'os'
import { randomUUID } from 'crypto'

const FILE = path.join(os.homedir(), '.0x0', 'contacts.json')

export function loadAll() {
  if (!fs.existsSync(FILE)) return []
  try { return JSON.parse(fs.readFileSync(FILE, 'utf8')) } catch { return [] }
}

function saveAll(contacts) {
  fs.writeFileSync(FILE, JSON.stringify(contacts, null, 2), { mode: 0o600 })
}

export function create({ theirNumber, theirPin, label = '', peerPublicKey = null }) {
  const contacts = loadAll()
  const existing = contacts.find(c => c.theirNumber === theirNumber && c.theirPin === theirPin)
  if (existing) {
    if (peerPublicKey && !existing.peerPublicKey) {
      existing.peerPublicKey = peerPublicKey
      saveAll(contacts)
    }
    return existing
  }
  const contact = {
    id: randomUUID(),
    theirNumber,
    theirPin,
    label,
    peerPublicKey,
    createdAt: Date.now()
  }
  contacts.push(contact)
  saveAll(contacts)
  return contact
}

function matchId(contact, id) {
  return contact.id === id || contact.id.startsWith(id)
}

export function findById(id) {
  return loadAll().find(c => matchId(c, id)) || null
}

export function findByPublicKey(hexStr) {
  return loadAll().find(c => c.peerPublicKey === hexStr) || null
}

function update(id, changes) {
  const contacts = loadAll()
  const idx = contacts.findIndex(c => matchId(c, id))
  if (idx === -1) return null
  Object.assign(contacts[idx], changes)
  saveAll(contacts)
  return contacts[idx]
}

export function updateLabel(id, label) {
  return update(id, { label })
}

export function updatePublicKey(id, hexStr) {
  return update(id, { peerPublicKey: hexStr })
}

export function updatePin(id, theirPin) {
  return update(id, { theirPin })
}

export function remove(id) {
  const contacts = loadAll().filter(c => !matchId(c, id))
  saveAll(contacts)
}
