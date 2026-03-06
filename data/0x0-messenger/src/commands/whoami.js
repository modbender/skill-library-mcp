import chalk from 'chalk'
import * as identityStore from '../storage/identity.js'
import * as pinsStore from '../storage/pins.js'

export async function cmdWhoami() {
  const identity = identityStore.load()
  if (!identity) {
    console.log(chalk.gray('// not initialized. run: 0x0 init'))
    process.exit(1)
  }

  console.log(chalk.gray('// my_number'))
  console.log(chalk.white(identity.number))
  console.log()

  const pins = pinsStore.getActive()
  if (pins.length > 0) {
    console.log(chalk.gray('// active_pins'))
    for (const p of pins) {
      const label = p.label ? chalk.white(p.label) : chalk.gray('(no label)')
      console.log(`  ${chalk.hex('#aaaaaa')(p.value)}  ${label}`)
    }
  }
}
