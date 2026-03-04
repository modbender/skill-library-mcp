import chalk from 'chalk'
import { generatePin } from '../core/pin.js'
import * as pinsStore from '../storage/pins.js'
import * as identityStore from '../storage/identity.js'

function requireInit() {
  const identity = identityStore.load()
  if (!identity) {
    console.log(chalk.gray('// not initialized. run: 0x0 init'))
    process.exit(1)
  }
  return identity
}

function parseExpiry(expires, once) {
  if (once) return { expiry: 'once', expiresAt: null }
  if (!expires) return { expiry: 'none', expiresAt: null }

  const match = expires.match(/^(\d+)(h|d|w)$/)
  if (!match) return { expiry: expires, expiresAt: null }

  const num = parseInt(match[1])
  const unit = match[2]
  const ms = unit === 'h' ? num * 3_600_000
           : unit === 'd' ? num * 86_400_000
           : num * 7 * 86_400_000
  return { expiry: expires, expiresAt: Date.now() + ms }
}

export async function cmdPinNew({ label = '', expires, once, len = 6, lobby = false } = {}) {
  requireInit()

  const { expiry, expiresAt } = parseExpiry(expires, once)
  const value = generatePin(len)
  const pin = pinsStore.create({ value, label, expiry, expiresAt, type: lobby ? 'lobby' : 'direct' })

  console.log(chalk.gray('// new pin created'))
  console.log()
  console.log(chalk.gray('pin     ') + chalk.hex('#aaaaaa')(pin.value))
  if (label) console.log(chalk.gray('label   ') + chalk.white(label))
  if (expiry !== 'none') console.log(chalk.gray('expiry  ') + chalk.gray(expiry))
  if (expiresAt) console.log(chalk.gray('expires ') + chalk.gray(new Date(expiresAt).toLocaleString('ja-JP')))
}

export async function cmdPinList() {
  requireInit()

  const pins = pinsStore.getActive()
  if (pins.length === 0) {
    console.log(chalk.gray('// no active pins'))
    return
  }

  console.log(chalk.gray('// pins'))
  console.log()
  for (const pin of pins) {
    const label = pin.label ? chalk.white(pin.label) : chalk.gray('(no label)')
    const expiry = pin.expiry !== 'none' ? chalk.gray(` [${pin.expiry}]`) : ''
    console.log(`  ${chalk.hex('#aaaaaa')(pin.value.padEnd(6))}  ${label}${expiry}`)
  }
}

export async function cmdPinRotate(pinValue) {
  requireInit()

  const pin = pinsStore.findByValue(pinValue)
  if (!pin) {
    console.log(chalk.gray(`// pin ${pinValue} not found`))
    process.exit(1)
  }

  const newValue = generatePin(pin.value.length)
  pinsStore.rotate(pin.id, newValue)

  console.log(chalk.gray('// pin rotated'))
  console.log(chalk.gray('old  ') + chalk.gray(pinValue))
  console.log(chalk.gray('new  ') + chalk.hex('#aaaaaa')(newValue))
  console.log()
  console.log(chalk.gray('// share the new pin with your contact to continue'))
}

export async function cmdPinRevoke(pinValue) {
  requireInit()

  const pin = pinsStore.findByValue(pinValue)
  if (!pin) {
    console.log(chalk.gray(`// pin ${pinValue} not found`))
    process.exit(1)
  }

  pinsStore.revoke(pin.id)
  console.log(chalk.gray(`// pin ${pinValue} revoked`))
}

export async function cmdPinInfo(pinValue) {
  requireInit()

  const pin = pinsStore.findByValue(pinValue)
  if (!pin) {
    console.log(chalk.gray(`// pin ${pinValue} not found`))
    process.exit(1)
  }

  console.log(chalk.gray('// pin_info'))
  console.log()
  console.log(chalk.gray('value    ') + chalk.hex('#aaaaaa')(pin.value))
  console.log(chalk.gray('label    ') + chalk.white(pin.label || '(none)'))
  console.log(chalk.gray('expiry   ') + chalk.gray(pin.expiry))
  if (pin.expiresAt) {
    console.log(chalk.gray('expires  ') + chalk.gray(new Date(pin.expiresAt).toLocaleString('ja-JP')))
  }
  console.log(chalk.gray('created  ') + chalk.gray(new Date(pin.createdAt).toLocaleString('ja-JP')))
  console.log(chalk.gray('active   ') + chalk.gray(String(pin.isActive)))
}
