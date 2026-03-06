import fs from 'fs'
import path from 'path'
import os from 'os'

const DIR = path.join(os.homedir(), '.0x0')
const FILE = path.join(DIR, 'identity.json')

export function ensureDir() {
  if (!fs.existsSync(DIR)) {
    fs.mkdirSync(DIR, { recursive: true, mode: 0o700 })
  }
  const msgDir = path.join(DIR, 'messages')
  if (!fs.existsSync(msgDir)) {
    fs.mkdirSync(msgDir, { recursive: true })
  }
}

export function load() {
  if (!fs.existsSync(FILE)) return null
  try {
    return JSON.parse(fs.readFileSync(FILE, 'utf8'))
  } catch {
    return null
  }
}

export function save(data) {
  ensureDir()
  fs.writeFileSync(FILE, JSON.stringify(data, null, 2), { mode: 0o600 })
}
