import chalk from 'chalk'
import Hyperswarm from 'hyperswarm'
import { channelSecret } from '../core/channel.js'
import { parseMessage } from '../core/message.js'
import * as identityStore from '../storage/identity.js'
import * as pinsStore from '../storage/pins.js'
import * as messagesStore from '../storage/messages.js'
import * as contactsStore from '../storage/contacts.js'

export async function cmdListen({ pin: pinFilter } = {}) {
  const identity = identityStore.load()
  if (!identity) {
    console.log(chalk.gray('// not initialized. run: 0x0 init'))
    process.exit(1)
  }

  const pins = pinFilter
    ? [pinsStore.findByValue(pinFilter)].filter(Boolean)
    : pinsStore.getActive()

  if (pins.length === 0) {
    console.log(chalk.gray('// no active pins'))
    process.exit(0)
  }

  console.log(chalk.gray(`// listening on ${pins.length} pin(s)...`))
  console.log(chalk.gray('// ctrl+c to stop'))
  console.log()

  const swarms = []

  for (const pin of pins) {
    const swarm = new Hyperswarm()
    const topic = channelSecret(identity.number, pin.value)
    swarms.push(swarm)

    swarm.join(topic, { server: true, client: true })

    swarm.on('connection', (conn) => {
      conn.on('error', () => {})

      // 公開鍵で連絡先を自動識別・保存（送信者番号は不明なので 'unknown'）
      const pubKeyHex = conn.remotePublicKey?.toString('hex') ?? null
      if (pubKeyHex) {
        let c = contactsStore.findByPublicKey(pubKeyHex)
        if (!c) {
          c = contactsStore.create({ theirNumber: 'unknown', theirPin: pin.value, peerPublicKey: pubKeyHex })
        } else if (!c.peerPublicKey) {
          contactsStore.updatePublicKey(c.id, pubKeyHex)
        }
      }

      conn.on('data', (data) => {
        const msg = parseMessage(data)
        if (!msg || msg.type !== 'message') return

        const isLobby = pin.type === 'lobby'
        messagesStore.append(pin.value, {
          from: 'peer', content: msg.content, isMine: false,
          pubKeyHex: isLobby ? (pubKeyHex || null) : null
        })

        const time = new Date().toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })
        const label = pin.label ? `[${pin.label}]` : `[${pin.value}]`
        console.log(chalk.gray(`[${time}] ${label} `) + chalk.hex('#aaaaaa')(msg.content))
      })
    })
  }

  process.on('SIGINT', async () => {
    console.log()
    console.log(chalk.gray('// stopping...'))
    for (const swarm of swarms) await swarm.destroy()
    process.exit(0)
  })
}
