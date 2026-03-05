import chalk from 'chalk'
import { generateNumber } from '../core/identity.js'
import * as identityStore from '../storage/identity.js'
import * as pinsStore from '../storage/pins.js'

export async function cmdRenew() {
  const identity = identityStore.load()
  if (!identity) {
    console.log(chalk.gray('// not initialized. run: 0x0 init'))
    process.exit(1)
  }

  // 全PINを無効化
  const pins = pinsStore.getActive()
  for (const pin of pins) {
    pinsStore.revoke(pin.id)
  }

  const newNumber = generateNumber()
  identityStore.save({ ...identity, number: newNumber, renewedAt: Date.now() })

  console.log(chalk.gray('// renewing number...'))
  console.log(chalk.gray(`// ${pins.length} pin(s) revoked`))
  console.log()
  console.log(chalk.gray('new number   ') + chalk.white(newNumber))
  console.log()
  console.log(chalk.gray('// all previous connections are now disconnected'))
}
