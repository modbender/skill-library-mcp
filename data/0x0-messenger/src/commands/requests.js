import chalk from 'chalk'
import * as identityStore from '../storage/identity.js'
import * as pinsStore from '../storage/pins.js'
import * as messagesStore from '../storage/messages.js'

export async function cmdRequests() {
  const identity = identityStore.load()
  if (!identity) {
    console.log(chalk.gray('// not initialized. run: 0x0 init'))
    process.exit(1)
  }

  const lobbyPins = pinsStore.getActive().filter(p => p.type === 'lobby')

  if (lobbyPins.length === 0) {
    console.log(chalk.gray('// no public pins. create one with: 0x0 pin new --public'))
    return
  }

  let totalRequests = 0

  for (const pin of lobbyPins) {
    const threads = messagesStore.listLobbyThreads(pin.value)
    const label = pin.label ? `[${pin.label}]` : `[${pin.value}]`

    console.log(chalk.white(`${label} // ${threads.length} request(s)`))

    for (const t of threads) {
      const time = t.latest ? new Date(t.latest.timestamp).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' }) : ''
      const preview = t.latest?.content ? t.latest.content.slice(0, 50) : '(no message)'
      console.log(chalk.gray(`  ${t.pubKeyHex}… [${time}] ${preview}`))
      totalRequests++
    }

    if (threads.length === 0) {
      console.log(chalk.gray('  // no requests yet'))
    }
    console.log()
  }

  if (totalRequests > 0) {
    console.log(chalk.gray(`// to approve a request, reply to it:`))
    console.log(chalk.gray(`// 0x0 approve <shortKey> "<message>"`))
  }
}
