import chalk from 'chalk'
import ora from 'ora'
import Hyperswarm from 'hyperswarm'
import { channelSecret } from '../core/channel.js'
import { createMessage } from '../core/message.js'
import * as identityStore from '../storage/identity.js'
import * as messagesStore from '../storage/messages.js'
import * as pinsStore from '../storage/pins.js'
import * as queueStore from '../storage/queue.js'

const TTL = 10_000 // 10秒で接続タイムアウト

export async function cmdSend(theirNumber, pin, content) {
  const identity = identityStore.load()
  if (!identity) {
    console.log(chalk.gray('// not initialized. run: 0x0 init'))
    process.exit(1)
  }

  const spinner = ora({
    text: chalk.gray(`connecting to ${theirNumber}...`),
    color: 'white'
  }).start()

  const swarm = new Hyperswarm()
  const topic = channelSecret(theirNumber, pin)
  let sent = false

  swarm.join(topic, { server: false, client: true })

  swarm.on('connection', async (conn) => {
    spinner.stop()
    conn.on('error', () => {})

    conn.write(createMessage(content))

    // ローカルPINがあればメッセージを保存
    const localPin = pinsStore.findByValue(pin)
    if (localPin) {
      messagesStore.append(localPin.value, {
        from: identity.number,
        content,
        isMine: true
      })
    }

    console.log(chalk.gray('[sent]'))
    sent = true
    await swarm.destroy()
    process.exit(0)
  })

  setTimeout(async () => {
    if (!sent) {
      spinner.stop()
      queueStore.append({ type: 'contact', theirNumber, pin, content })
      console.log(chalk.gray('// peer offline. queued for delivery (TTL: 72h)'))
      console.log(chalk.gray('// 0x0 queue  — to see pending messages'))
      await swarm.destroy()
      process.exit(0)
    }
  }, TTL)
}
