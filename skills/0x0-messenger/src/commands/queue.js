import chalk from 'chalk'
import * as queueStore from '../storage/queue.js'

export function cmdQueue() {
  queueStore.purgeExpired()
  const items = queueStore.loadAll()

  if (items.length === 0) {
    console.log(chalk.gray('// no pending messages'))
    return
  }

  console.log(chalk.gray(`// ${items.length} pending message(s)\n`))

  for (const item of items) {
    const time = new Date(item.timestamp).toLocaleString('ja-JP')
    const ttlHours = Math.max(0, Math.floor((item.expiresAt - Date.now()) / 3_600_000))
    const dest = item.type === 'contact'
      ? `${item.theirNumber} / ${item.pin}`
      : `pin:${item.pinId?.slice(0, 8)}…`

    console.log(chalk.white(`  → ${dest}`))
    console.log(chalk.gray(`     ${item.content.slice(0, 60)}${item.content.length > 60 ? '…' : ''}`))
    console.log(chalk.gray(`     ${time}  // TTL: ${ttlHours}h remaining`))
    console.log()
  }
}
