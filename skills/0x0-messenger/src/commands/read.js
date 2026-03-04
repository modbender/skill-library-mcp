import chalk from 'chalk'
import * as identityStore from '../storage/identity.js'
import * as pinsStore from '../storage/pins.js'
import * as messagesStore from '../storage/messages.js'

function printMessages(msgs) {
  if (msgs.length === 0) {
    console.log(chalk.gray('  (no messages)'))
    return
  }
  for (const msg of msgs) {
    const time = new Date(msg.timestamp).toLocaleTimeString('ja-JP', {
      hour: '2-digit', minute: '2-digit'
    })
    if (msg.isMine) {
      console.log(chalk.gray(`[${time}]`) + chalk.gray(' you: ') + chalk.white(msg.content))
    } else {
      const from = msg.from ? msg.from.slice(0, 14) + '…' : 'them'
      console.log(chalk.gray(`[${time}]`) + chalk.gray(` ${from}: `) + chalk.hex('#aaaaaa')(msg.content))
    }
  }
}

export async function cmdRead(pinValue, { json = false } = {}) {
  const identity = identityStore.load()
  if (!identity) {
    console.log(chalk.gray('// not initialized. run: 0x0 init'))
    process.exit(1)
  }

  const pin = pinsStore.findByValue(pinValue)
  if (!pin) {
    console.log(chalk.gray(`// pin ${pinValue} not found or inactive`))
    process.exit(1)
  }

  const msgs = messagesStore.list(pin.value)

  if (json) {
    console.log(JSON.stringify(msgs, null, 2))
    return
  }

  const label = pin.label ? `  label: ${pin.label}` : ''
  console.log(chalk.gray(`// pin: ${pin.value}${label}`))
  console.log(chalk.gray('─'.repeat(50)))
  printMessages(msgs)
}
