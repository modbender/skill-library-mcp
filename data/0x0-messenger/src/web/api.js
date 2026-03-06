import path from 'path'
import { randomUUID } from 'crypto'
import Hyperswarm from 'hyperswarm'
import { channelSecret } from '../core/channel.js'
import { createMessage, createFileMessage, createPinMigrate, parseMessage } from '../core/message.js'
import { generatePin } from '../core/pin.js'
import * as identityStore from '../storage/identity.js'
import * as pinsStore from '../storage/pins.js'
import * as messagesStore from '../storage/messages.js'
import * as contactsStore from '../storage/contacts.js'
import * as queueStore from '../storage/queue.js'

const WORKERS_URL = 'https://0x0-notification.tiidatech.workers.dev'
const NUMBER_RE = /^0x0-\d{3}-\d{4}-\d{4}$/
const PIN_RE = /^[0-9a-f]{4,16}$/

function validateLabel(v) {
  return typeof v === 'string' ? v.slice(0, 100) : ''
}
function validateNumber(v) {
  return typeof v === 'string' && NUMBER_RE.test(v) ? v : null
}
function validatePin(v) {
  return typeof v === 'string' && PIN_RE.test(v) ? v : null
}
function validateContent(v) {
  return typeof v === 'string' && v.length <= 65536 ? v : null
}
function validatePlatform(v) {
  return v === 'fcm' || v === 'apns' ? v : null
}
function validateFilename(v) {
  if (typeof v !== 'string') return 'file'
  return path.basename(v).slice(0, 255) || 'file'
}

export function createApiHandler(ws) {
  const connections = new Map()        // pinId → { swarm, conn }
  const lobbyConnections = new Map()   // pinId → { swarm, conns: Map<pubKeyHex, conn> }
  const contactConnections = new Map() // contactId → { swarm, conn }
  const messageQueue = new Map()       // pinId → [{ id, content, timestamp }]

  function sendEvent(event, payload = {}) {
    if (ws.readyState !== ws.OPEN) return
    ws.send(JSON.stringify({ event, ...payload }))
  }

  // 起動時: ディスクキューを in-memory messageQueue に復元（TTL切れは自動除外）
  queueStore.purgeExpired()
  for (const item of queueStore.loadAll().filter(i => i.type === 'pin' && i.pinId)) {
    const pending = messageQueue.get(item.pinId) || []
    pending.push({ id: item.id, content: item.content, timestamp: item.timestamp })
    messageQueue.set(item.pinId, pending)
  }

  // 接続確立時に初期データを送信
  const identity = identityStore.load()
  if (identity) {
    sendEvent('init', { data: {
      number: identity.number,
      inbox: buildInbox(),
      contacts: buildContacts(),
      prefs: { theme: 'dark' }
    }})
  }

  ws.on('message', async (raw) => {
    let msg
    try { msg = JSON.parse(raw.toString()) } catch { return }
    await dispatch(msg)
  })

  ws.on('close', async () => {
    for (const { swarm } of connections.values()) {
      await swarm.destroy().catch(() => {})
    }
    for (const { swarm } of lobbyConnections.values()) {
      await swarm.destroy().catch(() => {})
    }
    for (const { swarm } of contactConnections.values()) {
      await swarm.destroy().catch(() => {})
    }
    connections.clear()
    lobbyConnections.clear()
    contactConnections.clear()
  })

  async function dispatch(msg) {
    const { cmd, pinId, content, label, expiry, key, value, type: pinType } = msg

    switch (cmd) {
      case 'inbox.list':
        sendEvent('inbox.list', { data: buildInbox() })
        break

      case 'messages.list': {
        const pin = pinsStore.findById(pinId)
        if (!pin) return
        if (pin.type === 'lobby') {
          const threads = messagesStore.listLobbyThreads(pin.value)
          sendEvent('lobby.threads', { pinId, data: threads })
          if (!lobbyConnections.has(pinId)) await openLobbyConnection(pin)
        } else {
          const msgs = messagesStore.list(pin.value)
          sendEvent('messages.list', { pinId, data: msgs })
          if (!connections.has(pinId)) await openConnection(pin)
        }
        break
      }

      case 'message.send': {
        const pin = pinsStore.findById(pinId)
        if (!pin) return
        const safeContent = validateContent(content)
        if (!safeContent) return
        const localId = msg.localId || randomUUID()
        const senderIdentity = identityStore.load()

        // 玄関PIN: pubKeyHex 指定で特定接続者に送信
        if (pin.type === 'lobby') {
          const { pubKeyHex } = msg
          if (!pubKeyHex) return
          const lobbyEntry = lobbyConnections.get(pinId)
          const conn = lobbyEntry?.conns?.get(pubKeyHex)
          if (!conn) return

          // 初回返信 → pin_migrate を自動送信
          const prevMine = messagesStore.list(pin.value, 1000, pubKeyHex.slice(0, 16)).filter(m => m.isMine)
          if (prevMine.length === 0) {
            const newPinValue = generatePin(pin.value.length)
            const newPin = pinsStore.create({ value: newPinValue, label: '', expiry: 'none', expiresAt: null, type: 'direct' })
            conn.write(createPinMigrate(senderIdentity.number, newPinValue))
            sendEvent('lobby.migrated', { pinId, pubKeyHex, newPinId: newPin.id, newPinValue })
            sendEvent('inbox.list', { data: buildInbox() })
          }

          conn.write(createMessage(safeContent))
          messagesStore.append(pin.value, { from: senderIdentity.number, content: safeContent, isMine: true, pubKeyHex: pubKeyHex.slice(0, 16) })
          sendEvent('message.sent', { pinId, localId, data: { content: safeContent, isMine: true, timestamp: Date.now(), status: 'delivered' } })
          break
        }

        // 通常PIN
        const entry = connections.get(pinId)
        if (!entry?.conn) {
          const pending = messageQueue.get(pinId) || []
          pending.push({ id: localId, content: safeContent, timestamp: Date.now() })
          messageQueue.set(pinId, pending)
          queueStore.append({ type: 'pin', pinId, content: safeContent, localId })
          sendEvent('message.queued', { pinId, localId })
          break
        }
        entry.conn.write(createMessage(safeContent))
        messagesStore.append(pin.value, { from: senderIdentity.number, content: safeContent, isMine: true })
        sendEvent('message.sent', { pinId, localId, data: { content: safeContent, isMine: true, timestamp: Date.now(), status: 'delivered' } })
        break
      }

      case 'pin.create': {
        const { expiry: exp = 'none', expiresAt = null } = parseExpiry(expiry)
        const len = value ? value.length : 6
        const pinValue = generatePin(len)
        const pin = pinsStore.create({ value: pinValue, label: validateLabel(label), expiry: exp, expiresAt, type: pinType === 'lobby' ? 'lobby' : 'direct' })
        sendEvent('pin.created', { data: pin })
        sendEvent('inbox.list', { data: buildInbox() })
        break
      }

      case 'pin.rotate': {
        const pin = pinsStore.findById(pinId)
        if (!pin) return
        pinsStore.rotate(pin.id, generatePin(pin.value.length))
        await destroyConnection(pinId)
        sendEvent('pin.rotated', { pinId, data: pinsStore.findById(pinId) })
        sendEvent('inbox.list', { data: buildInbox() })
        break
      }

      case 'pin.revoke': {
        const pin = pinsStore.findById(pinId)
        if (!pin) return
        pinsStore.revoke(pin.id)
        await destroyConnection(pinId)
        sendEvent('pin.revoked', { pinId })
        sendEvent('inbox.list', { data: buildInbox() })
        break
      }

      case 'number.renew': {
        const identity = identityStore.load()
        if (!identity) return
        const pins = pinsStore.getActive()
        for (const p of pins) pinsStore.revoke(p.id)
        for (const { swarm } of connections.values()) await swarm.destroy().catch(() => {})
        connections.clear()
        const { generateNumber } = await import('../core/identity.js')
        const newNumber = generateNumber()
        identityStore.save({ ...identity, number: newNumber, renewedAt: Date.now() })
        sendEvent('number.renewed', { data: { number: newNumber } })
        break
      }

      case 'prefs.set':
        // 将来: プリファレンス保存
        break

      case 'notify.register': {
        const { token, platform } = msg
        const safePlatform = validatePlatform(platform)
        if (!token || typeof token !== 'string' || token.length > 512 || !safePlatform) break
        const notifyIdentity = identityStore.load()
        if (!notifyIdentity) break
        await fetch(`${WORKERS_URL}/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ number: notifyIdentity.number, token, platform: safePlatform })
        }).catch(() => {})
        sendEvent('notify.registered', {})
        break
      }

      case 'notify.unregister': {
        const unregIdentity = identityStore.load()
        if (!unregIdentity) break
        await fetch(`${WORKERS_URL}/register`, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ number: unregIdentity.number })
        }).catch(() => {})
        sendEvent('notify.unregistered', {})
        break
      }

      case 'file.send': {
        const { mimeType, dataBase64 } = msg
        const safeFilename = validateFilename(msg.filename)
        const filePin = pinsStore.findById(pinId)
        if (!filePin) break
        const fileEntry = connections.get(pinId)
        if (!fileEntry?.conn) break
        fileEntry.conn.write(createFileMessage(safeFilename, mimeType, dataBase64))
        const fileIdentity = identityStore.load()
        messagesStore.append(filePin.value, {
          from: fileIdentity.number, type: 'file', filename: safeFilename, mimeType, isMine: true
        })
        sendEvent('file.sent', { pinId, data: { filename: safeFilename, mimeType, isMine: true, timestamp: Date.now() } })
        break
      }

      case 'chat.start': {
        const safeNumber = validateNumber(msg.theirNumber)
        const safePin = validatePin(msg.theirPin)
        if (!safeNumber || !safePin) return
        const contact = contactsStore.create({ theirNumber: safeNumber, theirPin: safePin, label: validateLabel(msg.label) })
        sendEvent('chat.started', { contactId: contact.id, data: contact })
        sendEvent('contacts.list', { data: buildContacts() })
        const cMsgs = messagesStore.list(contact.theirPin)
        sendEvent('contact.messages.list', { contactId: contact.id, data: cMsgs })
        if (!contactConnections.has(contact.id)) await openContactConnection(contact)
        break
      }

      case 'contact.message.send': {
        const { contactId } = msg
        const safeCContent = validateContent(msg.content)
        if (!safeCContent) return
        const contact = contactsStore.findById(contactId)
        if (!contact) return
        const cEntry = contactConnections.get(contactId)
        if (!cEntry?.conn) {
          queueStore.append({ type: 'contact', theirNumber: contact.theirNumber, pin: contact.theirPin, content: safeCContent })
          sendEvent('message.queued', { contactId })
          break
        }
        cEntry.conn.write(createMessage(safeCContent))
        const me = identityStore.load()
        messagesStore.append(contact.theirPin, { from: me.number, content: safeCContent, isMine: true })
        sendEvent('contact.message.sent', { contactId, data: { content: safeCContent, isMine: true, timestamp: Date.now() } })
        // 相手に通知を送る（バックグラウンド、失敗は無視）
        fetch(`${WORKERS_URL}/notify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ recipientNumber: contact.theirNumber })
        }).catch(() => {})
        break
      }

      case 'contacts.list':
        sendEvent('contacts.list', { data: buildContacts() })
        break

      case 'pin.label': {
        const { label: pinLabel } = msg
        const targetPin = pinsStore.findById(pinId)
        if (!targetPin) return
        pinsStore.update(pinId, { label: validateLabel(pinLabel) })
        sendEvent('inbox.list', { data: buildInbox() })
        break
      }

      case 'contact.label': {
        const { contactId, label: newLabel } = msg
        contactsStore.updateLabel(contactId, newLabel || '')
        sendEvent('contacts.list', { data: buildContacts() })
        break
      }

      case 'contact.remove': {
        const { contactId: removeId } = msg
        if (contactConnections.has(removeId)) {
          const { swarm } = contactConnections.get(removeId)
          await swarm.destroy().catch(() => {})
          contactConnections.delete(removeId)
        }
        contactsStore.remove(removeId)
        sendEvent('contact.removed', { contactId: removeId })
        sendEvent('contacts.list', { data: buildContacts() })
        break
      }
    }
  }

  async function openConnection(pin) {
    const identity = identityStore.load()
    if (!identity) return

    const swarm = new Hyperswarm()
    const topic = channelSecret(identity.number, pin.value)
    connections.set(pin.id, { swarm, conn: null })

    sendEvent('peer.status', { pinId: pin.id, status: 'connecting' })

    swarm.join(topic, { server: true, client: true })

    swarm.on('connection', (conn) => {
      const entry = connections.get(pin.id)
      if (entry) entry.conn = conn

      sendEvent('peer.status', { pinId: pin.id, status: 'connected' })
      flushMessageQueue(pin, conn)

      conn.on('data', (data) => {
        const msg = parseMessage(data)
        if (!msg) return

        if (msg.type === 'message') {
          messagesStore.append(pin.value, {
            from: 'peer', content: msg.content, isMine: false
          })
          sendEvent('message.received', {
            pinId: pin.id,
            data: { content: msg.content, isMine: false, timestamp: Date.now() }
          })
        } else if (msg.type === 'file') {
          messagesStore.append(pin.value, {
            from: 'peer', type: 'file', filename: msg.filename, mimeType: msg.mimeType, isMine: false
          })
          sendEvent('file.received', {
            pinId: pin.id,
            data: {
              filename: msg.filename,
              mimeType: msg.mimeType,
              dataBase64: msg.data,
              isMine: false,
              timestamp: Date.now()
            }
          })
        }
      })

      conn.on('close', () => {
        const entry = connections.get(pin.id)
        if (entry) entry.conn = null
        sendEvent('peer.status', { pinId: pin.id, status: 'disconnected' })
      })
    })
  }

  async function openLobbyConnection(pin) {
    const identity = identityStore.load()
    if (!identity) return

    const swarm = new Hyperswarm()
    const topic = channelSecret(identity.number, pin.value)
    const conns = new Map()
    lobbyConnections.set(pin.id, { swarm, conns })

    swarm.join(topic, { server: true, client: true })

    swarm.on('connection', (conn) => {
      conn.on('error', () => {})
      const pubKeyHex = conn.remotePublicKey?.toString('hex') ?? null
      if (!pubKeyHex) return
      conns.set(pubKeyHex, conn)

      sendEvent('lobby.connected', { pinId: pin.id, pubKeyHex })

      conn.on('data', (data) => {
        const msg = parseMessage(data)
        if (!msg) return

        if (msg.type === 'message') {
          const shortKey = pubKeyHex.slice(0, 16)
          messagesStore.append(pin.value, {
            from: 'peer', content: msg.content, isMine: false, pubKeyHex: shortKey
          })
          sendEvent('lobby.message', {
            pinId: pin.id, pubKeyHex, shortKey,
            data: { content: msg.content, isMine: false, timestamp: Date.now() }
          })
        } else if (msg.type === 'pin_migrate') {
          // 受け取り側: コンタクト情報を自動更新
          const contact = contactsStore.findByPublicKey(pubKeyHex)
          if (contact && msg.newPin) {
            contactsStore.updatePin(contact.id, msg.newPin)
            sendEvent('contacts.list', { data: buildContacts() })
          }
        }
      })

      conn.on('close', () => {
        conns.delete(pubKeyHex)
        sendEvent('lobby.disconnected', { pinId: pin.id, pubKeyHex })
      })
    })
  }

  async function destroyConnection(pinId) {
    if (!connections.has(pinId)) return
    const { swarm } = connections.get(pinId)
    await swarm.destroy().catch(() => {})
    connections.delete(pinId)
  }

  function flushMessageQueue(pin, conn) {
    const pending = messageQueue.get(pin.id)
    if (!pending || pending.length === 0) return
    const senderIdentity = identityStore.load()
    for (const queued of pending) {
      conn.write(createMessage(queued.content))
      if (senderIdentity) messagesStore.append(pin.value, { from: senderIdentity.number, content: queued.content, isMine: true })
      sendEvent('message.delivered', { pinId: pin.id, localId: queued.id })
      queueStore.remove(queued.id)
    }
    messageQueue.delete(pin.id)
  }

  function buildInbox() {
    const pins = pinsStore.getActive()
    return pins.map(pin => {
      const msgs = messagesStore.list(pin.value)
      const latest = msgs[msgs.length - 1] || null
      const unread = msgs.filter(m => !m.isMine).length
      return { ...pin, messageCount: msgs.length, unread, latest }
    })
  }

  function buildContacts() {
    return contactsStore.loadAll().map(c => {
      const msgs = messagesStore.list(c.theirPin)
      const latest = msgs[msgs.length - 1] || null
      const unread = msgs.filter(m => !m.isMine).length
      return { ...c, messageCount: msgs.length, unread, latest }
    })
  }

  async function openContactConnection(contact) {
    const swarm = new Hyperswarm()
    const topic = channelSecret(contact.theirNumber, contact.theirPin)
    contactConnections.set(contact.id, { swarm, conn: null })

    sendEvent('peer.status', { contactId: contact.id, status: 'connecting' })

    swarm.join(topic, { server: false, client: true })

    swarm.on('connection', (conn) => {
      const entry = contactConnections.get(contact.id)
      if (entry) entry.conn = conn

      sendEvent('peer.status', { contactId: contact.id, status: 'connected' })

      // コンタクトキューのフラッシュ
      const me = identityStore.load()
      const contactQueue = queueStore.loadAll()
        .filter(i => i.type === 'contact' && i.theirNumber === contact.theirNumber && i.pin === contact.theirPin)
      for (const item of contactQueue) {
        conn.write(createMessage(item.content))
        if (me) messagesStore.append(contact.theirPin, { from: me.number, content: item.content, isMine: true })
        sendEvent('contact.message.sent', { contactId: contact.id, data: { content: item.content, isMine: true, timestamp: Date.now() } })
        queueStore.remove(item.id)
      }

      conn.on('data', (data) => {
        const msg = parseMessage(data)
        if (!msg || msg.type !== 'message') return

        messagesStore.append(contact.theirPin, {
          from: contact.theirNumber, content: msg.content, isMine: false
        })

        sendEvent('contact.message.received', {
          contactId: contact.id,
          data: { content: msg.content, isMine: false, timestamp: Date.now() }
        })
      })

      conn.on('error', () => {})

      conn.on('close', () => {
        const entry = contactConnections.get(contact.id)
        if (entry) entry.conn = null
        sendEvent('peer.status', { contactId: contact.id, status: 'disconnected' })
      })
    })
  }
}

function parseExpiry(expires) {
  if (!expires || expires === 'none') return { expiry: 'none', expiresAt: null }
  const match = expires.match(/^(\d+)(h|d|w)$/)
  if (!match) return { expiry: expires, expiresAt: null }
  const num = parseInt(match[1])
  const unit = match[2]
  const ms = unit === 'h' ? num * 3_600_000
           : unit === 'd' ? num * 86_400_000
           : num * 7 * 86_400_000
  return { expiry: expires, expiresAt: Date.now() + ms }
}
