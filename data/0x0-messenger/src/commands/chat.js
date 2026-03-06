import readline from 'readline'
import chalk from 'chalk'
import ora from 'ora'
import Hyperswarm from 'hyperswarm'
import { channelSecret } from '../core/channel.js'
import { createMessage, parseMessage } from '../core/message.js'
import { generatePin } from '../core/pin.js'
import * as identityStore from '../storage/identity.js'
import * as pinsStore from '../storage/pins.js'
import * as messagesStore from '../storage/messages.js'
import * as contactsStore from '../storage/contacts.js'

export async function cmdChat(theirNumber, pin) {
  const identity = identityStore.load()
  if (!identity) {
    console.log(chalk.gray('// not initialized. run: 0x0 init'))
    process.exit(1)
  }

  const localPin = pinsStore.findByValue(pin)
  const swarm = new Hyperswarm()
  const topic = channelSecret(theirNumber, pin)
  let activeConn = null
  let rl = null

  const spinner = ora({
    text: chalk.gray(`connecting to ${theirNumber}...`),
    color: 'white'
  }).start()

  swarm.join(topic, { server: true, client: true })

  swarm.on('connection', (conn) => {
    if (activeConn) return // 既に接続済みなら無視
    activeConn = conn

    // 公開鍵で連絡先を自動識別・保存
    const pubKeyHex = conn.remotePublicKey?.toString('hex') ?? null
    if (pubKeyHex) {
      let c = contactsStore.findByPublicKey(pubKeyHex)
      if (!c) {
        c = contactsStore.create({ theirNumber, theirPin: pin, peerPublicKey: pubKeyHex })
      } else if (!c.peerPublicKey) {
        contactsStore.updatePublicKey(c.id, pubKeyHex)
      }
    }

    spinner.stop()
    printHeader(pin)

    conn.on('error', () => {})
    conn.on('data', (data) => {
      const msg = parseMessage(data)
      if (!msg || msg.type !== 'message') return

      const time = new Date().toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })
      // readline の入力行をクリアして上書き表示
      if (rl) process.stdout.write('\r\x1b[K')
      console.log(
        chalk.gray(`[${time}]`) + ' ' +
        chalk.hex('#888888')(theirNumber.slice(0, 16) + '…: ') +
        chalk.hex('#aaaaaa')(msg.content)
      )
      if (rl) rl.prompt(true)

      if (localPin) {
        messagesStore.append(localPin.value, {
          from: theirNumber, content: msg.content, isMine: false
        })
      }
    })

    conn.on('close', () => {
      console.log()
      console.log(chalk.gray('[peer disconnected]'))
      activeConn = null
    })

    if (!rl) rl = startRepl()
  })

  // 3秒後もつながっていなければ待機状態でREPLを開始
  setTimeout(() => {
    if (!activeConn) {
      spinner.stop()
      console.log(chalk.gray('[waiting for peer...]'))
      printHeader(pin)
      if (!rl) rl = startRepl()
    }
  }, 3000)

  function printHeader(p) {
    console.log()
    console.log(chalk.gray(`// pin: ${p} | type :help for commands`))
    console.log()
  }

  function startRepl() {
    const r = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: chalk.gray('> ')
    })

    r.prompt()

    r.on('line', async (line) => {
      const input = line.trim()
      if (!input) { r.prompt(); return }

      if (input.startsWith(':')) {
        await handleCommand(input.slice(1).trim(), r)
        r.prompt()
        return
      }

      if (!activeConn) {
        console.log(chalk.gray('// not connected yet'))
        r.prompt()
        return
      }

      activeConn.write(createMessage(input))

      const time = new Date().toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })
      process.stdout.write('\x1b[1A\x1b[K')
      console.log(chalk.gray(`[${time}]`) + chalk.gray(' you: ') + chalk.white(input))

      if (localPin) {
        messagesStore.append(localPin.value, {
          from: identity.number, content: input, isMine: true
        })
      }

      r.prompt()
    })

    r.on('close', async () => {
      console.log(chalk.gray('[disconnected]'))
      await swarm.destroy()
      process.exit(0)
    })

    return r
  }

  async function handleCommand(cmd, r) {
    switch (cmd) {
      case 'help':
        console.log(chalk.gray(':pin rotate  — change pin and get new one'))
        console.log(chalk.gray(':pin info    — show current pin info'))
        console.log(chalk.gray(':history     — show message history'))
        console.log(chalk.gray(':clear       — clear screen'))
        console.log(chalk.gray(':quit / :q   — disconnect and exit'))
        break

      case 'pin rotate':
        if (localPin) {
          const newValue = generatePin()
          pinsStore.rotate(localPin.id, newValue)
          console.log(chalk.gray('rotating pin...'))
          console.log(chalk.gray('new pin: ') + chalk.hex('#aaaaaa')(newValue))
          console.log(chalk.gray('// share the new pin with your contact to continue'))
        } else {
          console.log(chalk.gray('// pin not found in your list'))
        }
        break

      case 'pin info':
        console.log(chalk.gray(`pin: ${pin}`))
        if (localPin) console.log(chalk.gray(`label: ${localPin.label || '(none)'}`))
        break

      case 'history':
        if (localPin) {
          const msgs = messagesStore.list(localPin.value)
          if (msgs.length === 0) {
            console.log(chalk.gray('(no history)'))
          } else {
            for (const msg of msgs) {
              const t = new Date(msg.timestamp).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })
              const prefix = msg.isMine
                ? chalk.gray(`[${t}] you: `)
                : chalk.gray(`[${t}] them: `)
              console.log(prefix + chalk.white(msg.content))
            }
          }
        }
        break

      case 'clear':
        process.stdout.write('\x1b[2J\x1b[0f')
        break

      case 'quit':
      case 'q':
        r.close()
        break

      default:
        console.log(chalk.gray(`// unknown command: :${cmd}`))
    }
  }
}
