import chalk from 'chalk'
import { generateNumber } from '../core/identity.js'
import { generatePin } from '../core/pin.js'
import * as identityStore from '../storage/identity.js'
import * as pinsStore from '../storage/pins.js'

export async function cmdInit() {
  const existing = identityStore.load()
  if (existing) {
    console.log(chalk.gray('// already initialized'))
    console.log()
    console.log(chalk.gray('your number  ') + chalk.white(existing.number))
    console.log(chalk.gray('// run: 0x0 pin list  to see your pins'))
    return
  }

  identityStore.ensureDir()
  const number = generateNumber()
  const pinValue = generatePin()

  identityStore.save({ number, createdAt: Date.now() })
  pinsStore.create({ value: pinValue, label: 'default' })

  console.log(chalk.gray('// generating your number...'))
  console.log()
  console.log(chalk.gray('your number  ') + chalk.white(number))
  console.log(chalk.gray('your pin     ') + chalk.hex('#aaaaaa')(pinValue))
  console.log()
  console.log(chalk.gray('// share your number and a pin with someone to start chatting'))
  console.log(chalk.gray('// example: 0x0 chat <their-number> <pin>'))
}
