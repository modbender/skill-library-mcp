import chalk from 'chalk'
import * as identityStore from '../storage/identity.js'
import * as pinsStore from '../storage/pins.js'
import * as messagesStore from '../storage/messages.js'

function formatTime(ts) {
  const d = new Date(ts)
  const now = new Date()
  if (d.toDateString() === now.toDateString()) {
    return d.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })
  }
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (d.toDateString() === yesterday.toDateString()) return '昨日'
  return d.toLocaleDateString('ja-JP', { month: 'numeric', day: 'numeric' })
}

export async function cmdInbox({ json = false } = {}) {
  const identity = identityStore.load()
  if (!identity) {
    console.log(chalk.gray('// not initialized. run: 0x0 init'))
    process.exit(1)
  }

  const pins = pinsStore.getActive()

  if (json) {
    const result = pins.map(pin => {
      const msgs = messagesStore.list(pin.value)
      const latest = msgs[msgs.length - 1] || null
      return { pin: pin.value, label: pin.label, messageCount: msgs.length, latest }
    })
    console.log(JSON.stringify(result, null, 2))
    return
  }

  console.log(chalk.gray('// my_number'))
  console.log(chalk.white(identity.number))
  console.log()
  console.log(chalk.gray('// inbox'))
  console.log(chalk.gray('─'.repeat(52)))

  if (pins.length === 0) {
    console.log(chalk.gray('  (empty)  run: 0x0 pin new --label "someone"'))
    return
  }

  for (const pin of pins) {
    const msgs = messagesStore.list(pin.value)
    const latest = msgs[msgs.length - 1]
    const count = msgs.length

    const label = (pin.label || '').padEnd(14)
    const preview = latest
      ? latest.content.slice(0, 38) + (latest.content.length > 38 ? '…' : '')
      : chalk.gray('(no messages)')
    const time = latest ? formatTime(latest.timestamp) : ''
    const badge = count > 0 ? chalk.white(`(${count})`) : chalk.gray('(0)')

    console.log(
      `  ${chalk.hex('#aaaaaa')(pin.value.padEnd(6))}` +
      `  ${chalk.white(label)}` +
      `  ${badge.padEnd(5)}` +
      `  ${chalk.gray(preview.slice(0, 36))}` +
      (time ? `  ${chalk.gray(time)}` : '')
    )
  }
}
