import chalk from 'chalk'
import ora from 'ora'
import Hyperswarm from 'hyperswarm'
import { channelSecret } from '../core/channel.js'
import { createMessage, createPinMigrate } from '../core/message.js'
import { generatePin } from '../core/pin.js'
import * as identityStore from '../storage/identity.js'
import * as pinsStore from '../storage/pins.js'
import * as messagesStore from '../storage/messages.js'

const TTL = 30_000 // 30秒で接続タイムアウト

export async function cmdApprove(shortKey, message) {
  const identity = identityStore.load()
  if (!identity) {
    console.log(chalk.gray('// not initialized. run: 0x0 init'))
    process.exit(1)
  }

  // shortKey にマッチするスレッドを持つ lobby PIN を探す
  const lobbyPins = pinsStore.getActive().filter(p => p.type === 'lobby')
  let targetPin = null

  for (const pin of lobbyPins) {
    const threads = messagesStore.listLobbyThreads(pin.value)
    if (threads.find(t => t.pubKeyHex.startsWith(shortKey))) {
      targetPin = pin
      break
    }
  }

  if (!targetPin) {
    console.log(chalk.gray(`// request not found: ${shortKey}`))
    console.log(chalk.gray('// run "0x0 requests" to see pending requests'))
    process.exit(1)
  }

  const spinner = ora({
    text: chalk.gray(`waiting for peer ${shortKey}…`),
    color: 'white'
  }).start()

  const swarm = new Hyperswarm()
  const topic = channelSecret(identity.number, targetPin.value)
  let approved = false

  swarm.join(topic, { server: true, client: true })

  swarm.on('connection', async (conn) => {
    conn.on('error', () => {})
    const pubKeyHex = conn.remotePublicKey?.toString('hex') ?? null
    if (!pubKeyHex || !pubKeyHex.startsWith(shortKey)) return

    spinner.stop()

    // 専用 PIN を生成して pin_migrate を送信
    const newPinValue = generatePin(targetPin.value.length)
    const newPin = pinsStore.create({ value: newPinValue, label: '', expiry: 'none', expiresAt: null, type: 'direct' })
    conn.write(createPinMigrate(identity.number, newPinValue))

    // 承認メッセージを送信
    conn.write(createMessage(message))

    const shortPub = pubKeyHex.slice(0, 16)
    messagesStore.append(targetPin.value, {
      from: identity.number, content: message, isMine: true, pubKeyHex: shortPub
    })

    console.log(chalk.gray(`// approved: ${shortPub}…`))
    console.log(chalk.gray(`// new direct pin created: ${newPinValue}`))
    console.log(chalk.gray(`// message sent: ${message}`))

    approved = true
    await swarm.destroy()
    process.exit(0)
  })

  setTimeout(async () => {
    if (!approved) {
      spinner.stop()
      console.log(chalk.gray('// peer offline. try again when they come online.'))
      await swarm.destroy()
      process.exit(0)
    }
  }, TTL)
}
