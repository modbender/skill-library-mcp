// stdioモード: エージェントがJSONパイプで0x0を操作する
// stdin: 1行1コマンド(JSON)
// stdout: 1行1イベント(JSON) — パーサブルJSON保証
// stderr: ログのみ

import { createInterface } from 'readline'
import Hyperswarm from 'hyperswarm'
import { channelSecret } from '../core/channel.js'
import { createMessage, parseMessage } from '../core/message.js'
import * as identityStore from '../storage/identity.js'
import * as messagesStore from '../storage/messages.js'
import * as pinsStore from '../storage/pins.js'

function emit(obj) {
  process.stdout.write(JSON.stringify(obj) + '\n')
}

function log(msg) {
  process.stderr.write(msg + '\n')
}

export async function cmdPipe(theirNumber, pin) {
  const identity = identityStore.load()
  if (!identity) {
    emit({ type: 'error', code: 'NOT_INITIALIZED', message: 'run: 0x0 init' })
    process.exit(1)
  }

  const swarm = new Hyperswarm()
  const topic = channelSecret(theirNumber, pin)
  let activeConn = null

  log(`// connecting to ${theirNumber} via pin ${pin}...`)

  swarm.join(topic, { server: true, client: true })

  swarm.on('connection', (conn) => {
    activeConn = conn
    emit({ type: 'connected', peer: theirNumber, pin })

    conn.on('error', () => {})
    conn.on('data', (data) => {
      const msg = parseMessage(data)
      if (!msg || msg.type !== 'message') return

      const localPin = pinsStore.findByValue(pin)
      if (localPin) {
        messagesStore.append(localPin.value, {
          from: theirNumber, content: msg.content, isMine: false
        })
      }

      emit({
        type: 'message',
        from: theirNumber,
        content: msg.content,
        timestamp: Date.now()
      })
    })

    conn.on('close', () => {
      activeConn = null
      emit({ type: 'disconnected', peer: theirNumber })
    })
  })

  // stdin からコマンドを受け取る
  const rl = createInterface({ input: process.stdin })

  rl.on('line', (line) => {
    const trimmed = line.trim()
    if (!trimmed) return

    let cmd
    try { cmd = JSON.parse(trimmed) } catch {
      emit({ type: 'error', code: 'INVALID_JSON', message: 'stdin must be JSON' })
      return
    }

    switch (cmd.type) {
      case 'message': {
        if (!activeConn) {
          emit({ type: 'error', code: 'PEER_OFFLINE', message: 'not connected' })
          return
        }
        activeConn.write(createMessage(cmd.content))

        const localPin = pinsStore.findByValue(pin)
        if (localPin) {
          messagesStore.append(localPin.value, {
            from: identity.number, content: cmd.content, isMine: true
          })
        }

        emit({ type: 'sent', content: cmd.content, timestamp: Date.now() })
        break
      }

      case 'ping':
        emit({ type: 'pong', timestamp: Date.now() })
        break

      case 'disconnect':
        rl.close()
        break

      default:
        emit({ type: 'error', code: 'UNKNOWN_CMD', message: `unknown type: ${cmd.type}` })
    }
  })

  rl.on('close', async () => {
    await swarm.destroy()
    process.exit(0)
  })

  process.on('SIGINT', async () => {
    await swarm.destroy()
    process.exit(0)
  })
}
