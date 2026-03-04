import chalk from 'chalk'
import qrcode from 'qrcode-terminal'
import { buildUri } from '../core/uri.js'
import * as identityStore from '../storage/identity.js'
import * as pinsStore from '../storage/pins.js'

function log(msg) {
  console.log(chalk.gray(msg))
}

export function cmdQr(pin) {
  const identity = identityStore.load()
  if (!identity) {
    log('// not initialized. run: 0x0 init')
    return
  }

  const pinEntry = pinsStore.findByValue(pin)
  if (!pinEntry) {
    log(`// pin not found: ${pin}`)
    return
  }

  const uri = buildUri(identity.number, pin)

  console.log()
  log(`// ${uri}`)
  console.log()

  qrcode.generate(uri, { small: true })

  const label = pinEntry.label ? `  · label: ${pinEntry.label}` : ''
  console.log()
  log(`// scan to connect${label}`)
}
