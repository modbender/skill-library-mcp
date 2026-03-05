import { ws } from './ws.js'

// ===== State =====
interface PinEntry {
  id: string
  value: string
  label: string
  expiry: string
  expiresAt: number | null
  messageCount: number
  unread: number
  latest: { content: string; timestamp: number; isMine: boolean } | null
  type?: string
}

interface Contact {
  id: string
  theirNumber: string
  theirPin: string
  label: string
  createdAt: number
  messageCount: number
  unread: number
  latest: { content: string; timestamp: number; isMine: boolean } | null
}

interface Message {
  id?: string
  localId?: string
  content: string
  isMine: boolean
  timestamp: number
  from?: string
  status?: 'queued' | 'delivered'
}

interface State {
  number: string
  inbox: PinEntry[]
  contacts: Contact[]
  activePin: PinEntry | null
  activeContact: Contact | null
  messages: Record<string, Message[]>
  contactMessages: Record<string, Message[]>
  peerStatus: Record<string, 'connected' | 'disconnected' | 'connecting'>
  theme: 'dark' | 'light'
  screen: 'welcome' | 'chat' | 'newPin' | 'pinMenu' | 'connect' | 'agentExport' | 'requests' | 'requestChat'
  lobbyThreads: Record<string, { pubKeyHex: string; shortKey: string; latest: Message | null; count: number }[]>
  activeLobbyKey: string | null   // 選択中の接続者 pubKeyHex
  newPinValue: string
  newPinExpiry: string
  newPinCustomNum: string
  newPinCustomUnit: 'h' | 'd' | 'w'
  newPinIsLobby: boolean
}

const state: State = {
  number: '',
  inbox: [],
  contacts: [],
  activePin: null,
  activeContact: null,
  messages: {},
  contactMessages: {},
  peerStatus: {},
  theme: 'dark',
  screen: 'welcome',
  newPinValue: randomPin(),
  lobbyThreads: {},
  activeLobbyKey: null,
  newPinExpiry: 'none',
  newPinCustomNum: '6',
  newPinCustomUnit: 'h',
  newPinIsLobby: false
}

function randomPin() {
  return Math.floor(Math.random() * 65536).toString(16).padStart(4, '0')
}

// ===== Render =====
function render() {
  const app = document.getElementById('app')!
  app.innerHTML = buildApp()
  attachEvents()
}

function buildApp() {
  return `
    <div class="topbar">
      <span class="topbar-logo">0x0</span>
      <button class="theme-toggle" id="theme-toggle">
        // ${state.theme === 'dark' ? 'dark' : 'light'}
      </button>
    </div>
    <div class="main-area">
      ${buildSidebar()}
      <div class="panel ${state.screen !== 'welcome' ? 'active' : ''}">
        ${buildPanel()}
      </div>
    </div>
  `
}

function buildSidebar() {
  const requestPins = state.inbox.filter(p => p.type === 'lobby')
  const inboxPins = state.inbox.filter(p => p.type !== 'lobby')
  const contacts = state.contacts
  return `
    <div class="sidebar">
      <div class="number-section">
        <div class="section-label">// my_number</div>
        <div class="my-number" id="my-number">${state.number || '...'}</div>
        <div class="number-actions">
          <button class="pill-btn" id="btn-copy">// COPY</button>
          <button class="pill-btn" id="btn-renew">// RENEW</button>
        </div>
      </div>
      ${requestPins.length > 0 ? `
      <div class="inbox-section">
        <div style="padding: 12px 20px 6px">
          <div class="section-label">// requests</div>
        </div>
        ${requestPins.map(pin => buildRequestsItem(pin)).join('')}
      </div>
      ` : ''}
      <div class="inbox-section">
        <div style="padding: 12px 20px 6px">
          <div class="section-label">// inbox</div>
        </div>
        ${inboxPins.map(pin => buildInboxItem(pin)).join('')}
      </div>
      <button class="new-pin-btn" id="btn-new-pin">+ // NEW_PIN</button>
      <div class="contacts-section">
        <div style="padding: 12px 20px 6px; display:flex; justify-content:space-between; align-items:center">
          <div class="section-label">// contacts</div>
          <button class="pill-btn" id="btn-connect">+ CONNECT</button>
        </div>
        ${contacts.length === 0
          ? `<div style="padding:8px 20px; font-size:11px; opacity:0.4">// no contacts yet</div>`
          : contacts.map(c => buildContactItem(c)).join('')}
      </div>
    </div>
  `
}

function buildRequestsItem(pin: PinEntry) {
  const isActive = state.activePin?.id === pin.id && (state.screen === 'requests' || state.screen === 'requestChat')
  const threads = state.lobbyThreads[pin.id] || []
  const pending = threads.length
  const totalUnread = threads.reduce((s, t) => s + t.count, 0)
  const preview = pending > 0
    ? `${pending} 件の差出人`
    : '(待機中)'

  return `
    <div class="inbox-item ${isActive ? 'active' : ''}" data-pin-id="${pin.id}">
      <div class="peer-dot"></div>
      <div class="inbox-pin">${escapeHtml(pin.value)}</div>
      <div class="inbox-info">
        <div class="inbox-label">${escapeHtml(pin.label || '(公開用)')}</div>
        <div class="inbox-preview">${escapeHtml(preview)}</div>
      </div>
      <div class="inbox-meta">
        <div class="inbox-badge" data-count="${totalUnread}">${totalUnread || ''}</div>
      </div>
    </div>
  `
}

function buildInboxItem(pin: PinEntry) {
  const isActive = state.activePin?.id === pin.id && state.screen === 'chat'
  const status = state.peerStatus[pin.id] || 'disconnected'
  const time = pin.latest ? formatTime(pin.latest.timestamp) : ''
  const preview = pin.latest
    ? pin.latest.content.slice(0, 35) + (pin.latest.content.length > 35 ? '…' : '')
    : '(no messages)'

  return `
    <div class="inbox-item ${isActive ? 'active' : ''}" data-pin-id="${pin.id}">
      <div class="peer-dot ${status === 'connected' ? 'connected' : ''}"></div>
      <div class="inbox-pin">${escapeHtml(pin.value)}</div>
      <div class="inbox-info">
        <div class="inbox-label">${escapeHtml(pin.label || '(no label)')}</div>
        <div class="inbox-preview">${escapeHtml(preview)}</div>
      </div>
      <div class="inbox-meta">
        <div class="inbox-time">${time}</div>
        <div class="inbox-badge" data-count="${pin.unread}">${pin.unread || ''}</div>
      </div>
    </div>
  `
}

function buildContactItem(c: Contact) {
  const isActive = state.activeContact?.id === c.id && state.screen === 'chat'
  const status = state.peerStatus[c.id] || 'disconnected'
  const time = c.latest ? formatTime(c.latest.timestamp) : ''
  const preview = c.latest
    ? c.latest.content.slice(0, 35) + (c.latest.content.length > 35 ? '…' : '')
    : '(no messages)'

  return `
    <div class="inbox-item ${isActive ? 'active' : ''}" data-contact-id="${c.id}">
      <div class="peer-dot ${status === 'connected' ? 'connected' : ''}"></div>
      <div class="inbox-pin">${escapeHtml(c.theirPin)}</div>
      <div class="inbox-info">
        <div class="inbox-label">${escapeHtml(c.label || c.theirNumber)}</div>
        <div class="inbox-preview">${escapeHtml(preview)}</div>
      </div>
      <div class="inbox-meta">
        <div class="inbox-time">${time}</div>
        <div class="inbox-badge" data-count="${c.unread}">${c.unread || ''}</div>
      </div>
    </div>
  `
}

function buildPanel() {
  switch (state.screen) {
    case 'welcome':      return buildWelcome()
    case 'chat':         return buildChat()
    case 'newPin':       return buildNewPin()
    case 'pinMenu':      return buildPinMenu()
    case 'connect':      return buildConnect()
    case 'agentExport':  return buildAgentExport()
    case 'requests':     return buildRequests()
    case 'requestChat':  return buildRequestChat()
  }
}

function buildWelcome() {
  return `
    <div class="welcome">
      <pre class="welcome-logo">
 ██████╗ ██╗  ██╗██████╗
██╔═══██╗╚██╗██╔╝██╔══██╗
██║   ██║ ╚███╔╝ ██║  ██║
██║   ██║ ██╔██╗ ██║  ██║
╚██████╔╝██╔╝ ██╗██████╔╝
 ╚═════╝ ╚═╝  ╚═╝╚═════╝</pre>
      <div class="welcome-hint">// select a pin from inbox to start chatting</div>
    </div>
  `
}

function buildChat() {
  const pin = state.activePin
  const contact = state.activeContact
  const msgs = pin
    ? (state.messages[pin.id] || [])
    : (contact ? (state.contactMessages[contact.id] || []) : [])
  const statusKey = pin ? pin.id : (contact?.id || '')
  const status = state.peerStatus[statusKey] || 'disconnected'

  const name = escapeHtml(pin
    ? (pin.label || pin.value)
    : (contact ? (contact.label || contact.theirNumber) : ''))
  const sub = pin
    ? `// pin: ${escapeHtml(pin.value)} &nbsp;·&nbsp; ${escapeHtml(status)}`
    : (contact ? `// ${escapeHtml(contact.theirNumber)} &nbsp;·&nbsp; pin: ${escapeHtml(contact.theirPin)} &nbsp;·&nbsp; ${escapeHtml(status)}` : '')

  return `
    <div style="display:flex;flex-direction:column;height:100%">
      <div class="chat-header">
        <div style="flex:1">
          <div class="chat-name">${name}</div>
          <div class="chat-pin-label">${sub}</div>
        </div>
        ${pin ? `<button class="chat-menu-btn" id="btn-pin-menu">⋯</button>` : `<button class="chat-menu-btn" id="btn-contact-remove" title="削除">✕</button>`}
      </div>
      <div class="messages-area" id="messages-area">
        ${msgs.map(m => buildMessage(m)).join('')}
      </div>
      <div class="chat-input-area">
        <textarea
          class="chat-input"
          id="chat-input"
          placeholder="メッセージ..."
          rows="1"
        ></textarea>
        <button class="send-btn" id="btn-send">▶</button>
      </div>
    </div>
  `
}

function buildMessage(msg: Message) {
  const cls = msg.isMine ? 'mine' : 'theirs'
  const time = new Date(msg.timestamp).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })

  let statusHtml = ''
  if (msg.isMine) {
    if (msg.status === 'queued') {
      statusHtml = '<span class="msg-status-queued"> // waiting…</span>'
    } else if (msg.status === 'delivered') {
      statusHtml = '<span class="msg-status-delivered"> ✓</span>'
    }
  }

  return `
    <div class="msg ${cls}" data-local-id="${msg.localId || ''}">
      <div class="msg-bubble">${escapeHtml(msg.content)}</div>
      <div class="msg-time">${time}${statusHtml}</div>
    </div>
  `
}

function buildNewPin() {
  const expiryOpts = [
    { value: 'none', label: 'なし' },
    { value: '24h',  label: '24h' },
    { value: '1w',   label: '1週間' },
    { value: 'once', label: '1回のみ' },
    { value: 'custom', label: 'カスタム' },
  ]
  const isCustom = state.newPinExpiry === 'custom'
  return `
    <div class="newpin-panel">
      <div class="section-label">// new_pin</div>
      <div class="pin-display">
        <div class="pin-value" id="new-pin-display">${state.newPinValue}</div>
        <div class="pin-hint">相手に渡すPINです</div>
      </div>
      <div class="form-group">
        <div class="form-label">// label（任意）</div>
        <input class="form-input" id="pin-label-input" type="text" placeholder="例: フリマ用、田中さん...">
      </div>
      <div class="form-group">
        <div class="form-label">// expiry</div>
        <div class="expiry-grid">
          ${expiryOpts.map(o => `
            <button class="expiry-opt ${state.newPinExpiry === o.value ? 'selected' : ''}"
              data-expiry="${o.value}">${o.label}</button>
          `).join('')}
        </div>
        ${isCustom ? `
        <div class="expiry-custom">
          <input class="expiry-custom-num" id="expiry-custom-num" type="number" min="1" max="999"
            value="${state.newPinCustomNum}">
          <select class="expiry-custom-unit" id="expiry-custom-unit">
            <option value="h" ${state.newPinCustomUnit === 'h' ? 'selected' : ''}>時間</option>
            <option value="d" ${state.newPinCustomUnit === 'd' ? 'selected' : ''}>日</option>
            <option value="w" ${state.newPinCustomUnit === 'w' ? 'selected' : ''}>週間</option>
          </select>
        </div>
        ` : ''}
      </div>
      <div class="form-group">
        <div class="form-label">// type</div>
        <div class="expiry-grid" style="grid-template-columns: 1fr 1fr">
          <button class="expiry-opt ${!state.newPinIsLobby ? 'selected' : ''}" id="type-direct">通常</button>
          <button class="expiry-opt ${state.newPinIsLobby ? 'selected' : ''}" id="type-lobby">公開用</button>
        </div>
        ${state.newPinIsLobby ? `<div style="padding:6px 0; font-size:10px; color:var(--text-muted)">// 名刺・SNS公開用。メッセージは requests に届き、返信した時点で専用受信箱に昇格します</div>` : ''}
      </div>
      <button class="ghost-btn" id="btn-regen-pin">// GENERATE_NEW →</button>
      <button class="primary-btn" id="btn-save-pin">// SAVE_AND_USE →</button>
    </div>
  `
}

function buildConnect() {
  return `
    <div class="newpin-panel">
      <div class="section-label">// connect_to_peer</div>
      <div class="form-group">
        <div class="form-label">// their_number</div>
        <input class="form-input" id="connect-number" type="text" placeholder="0x0-NNN-NNNN-NNNN" autocomplete="off">
      </div>
      <div class="form-group">
        <div class="form-label">// pin</div>
        <input class="form-input" id="connect-pin" type="text" placeholder="a3f9" maxlength="16" autocomplete="off">
      </div>
      <div class="form-group">
        <div class="form-label">// label（任意）</div>
        <input class="form-input" id="connect-label" type="text" placeholder="例: 田中さん">
      </div>
      <button class="primary-btn" id="btn-do-connect">// CONNECT →</button>
    </div>
  `
}

function buildPinMenu() {
  const pin = state.activePin!
  return `
    <div class="menu-panel">
      <div class="menu-pin-header">
        <div class="menu-pin-name">${escapeHtml(pin.label || pin.value)}</div>
        <div class="menu-pin-sub">// pin: ${escapeHtml(pin.value)}</div>
      </div>
      <div class="menu-section-label">// pin_settings</div>
      <div class="menu-item" id="menu-rotate">
        <div>
          <div class="menu-item-label">PINを変更する</div>
          <div class="menu-item-sub">新しいPINを生成して渡し直す</div>
        </div>
        <div class="menu-item-arrow">›</div>
      </div>
      <div class="menu-item" id="menu-label">
        <div>
          <div class="menu-item-label">ラベルを編集</div>
          <div class="menu-item-sub">現在: ${escapeHtml(pin.label || '(なし)')}</div>
        </div>
        <div class="menu-item-arrow">›</div>
      </div>
      <div class="menu-section-label">// integrations</div>
      <div class="menu-item" id="menu-agent-export">
        <div>
          <div class="menu-item-label">エージェント接続</div>
          <div class="menu-item-sub">AIエージェント向けの接続設定を書き出す</div>
        </div>
        <div class="menu-item-arrow">›</div>
      </div>
      <div class="menu-section-label">// danger_zone</div>
      <div class="menu-item danger" id="menu-revoke">
        <div>
          <div class="menu-item-label">このPINを今すぐ無効化</div>
          <div class="menu-item-sub">相手からの受信が即時停止される</div>
        </div>
        <div class="menu-item-arrow">›</div>
      </div>
      <div style="padding: 16px 24px">
        <button class="ghost-btn" id="menu-back">← back</button>
      </div>
    </div>
  `
}

function buildRequests() {
  const pin = state.activePin!
  const threads = state.lobbyThreads[pin.id] || []
  return `
    <div class="menu-panel">
      <div class="menu-pin-header">
        <div class="menu-pin-name">// requests</div>
        <div class="menu-pin-sub">pin: ${escapeHtml(pin.value)} · ${threads.length} 件</div>
      </div>
      ${threads.length === 0
        ? `<div style="padding:16px 24px; font-size:11px; opacity:0.4">// no requests yet</div>`
        : threads.map(t => `
          <div class="menu-item request-thread-item" data-pubkey="${escapeHtml(t.pubKeyHex)}">
            <div>
              <div class="menu-item-label" style="font-family:var(--mono); font-size:11px">${escapeHtml(t.shortKey)}…</div>
              <div class="menu-item-sub">${t.latest ? escapeHtml(t.latest.content?.slice(0, 40) || '') : '(no messages)'}</div>
            </div>
            <div class="inbox-badge" data-count="${t.count}">${t.count || ''}</div>
          </div>
        `).join('')}
      <div style="padding: 16px 24px">
        <button class="ghost-btn" id="requests-back">← back</button>
      </div>
    </div>
  `
}

function buildRequestChat() {
  const pin = state.activePin!
  const pubKeyHex = state.activeLobbyKey!
  const shortKey = pubKeyHex.slice(0, 16)
  const msgs = (state.messages[pin.id + ':' + shortKey]) || []
  return `
    <div style="display:flex;flex-direction:column;height:100%">
      <div class="chat-header">
        <div style="flex:1">
          <div class="chat-name">${escapeHtml(shortKey)}…</div>
          <div class="chat-pin-label">// request · pin: ${escapeHtml(pin.value)}</div>
        </div>
        <button class="chat-menu-btn" id="requests-chat-back" title="戻る">✕</button>
      </div>
      <div class="messages-area" id="messages-area">
        ${msgs.map(m => `
          <div class="msg ${m.isMine ? 'mine' : 'theirs'}">
            <div class="msg-bubble">${escapeHtml(m.content || '')}</div>
          </div>
        `).join('')}
      </div>
      <div class="chat-input-area">
        <textarea class="chat-input" id="request-chat-input" placeholder="返信すると承認されます..." rows="1"></textarea>
        <button class="send-btn" id="request-send-btn">▶</button>
      </div>
    </div>
  `
}

function buildAgentExport() {
  const pin = state.activePin!
  const config = {
    provider: '0x0',
    number: state.number,
    pin: pin.value,
    command: `npx 0x0-cli pipe ${state.number} ${pin.value}`
  }
  const json = JSON.stringify(config, null, 2)

  return `
    <div class="menu-panel">
      <div class="menu-pin-header">
        <div class="menu-pin-name">// agent_connect</div>
        <div class="menu-pin-sub">pin: ${escapeHtml(pin.value)}${pin.label ? ' &nbsp;·&nbsp; ' + escapeHtml(pin.label) : ''}</div>
      </div>
      <div class="agent-export-body">
        <div class="agent-export-desc">
          AIエージェント（OpenClaw等）がこのPINで接続するための設定です。<br>
          以下の設定をエージェントのconfig（openclaw.json等）に貼り付けてください。
        </div>
        <div class="agent-config-block">
          <pre id="agent-config-pre">${escapeHtml(json)}</pre>
        </div>
        <div class="agent-export-actions">
          <button class="primary-btn" id="btn-copy-config">// COPY CONFIG →</button>
          <div class="agent-copy-hint" id="agent-copy-hint"></div>
        </div>
        <div class="agent-export-hint">
          <div>// how to use</div>
          <div style="margin-top:8px;opacity:0.6;font-size:0.78rem">
            1. エージェントが <code>command</code> を子プロセスとして起動する<br>
            2. stdin に JSON コマンドを送る<br>
            3. stdout から JSON イベントを受け取る<br>
            4. 詳細: <a href="https://0x0.contact/doc#openclaw" target="_blank" style="color:#888">0x0.contact/doc</a>
          </div>
        </div>
      </div>
      <div style="padding: 16px 24px">
        <button class="ghost-btn" id="agent-export-back">← back</button>
      </div>
    </div>
  `
}

// ===== Events =====
function attachEvents() {
  // Theme
  document.getElementById('theme-toggle')?.addEventListener('click', () => {
    state.theme = state.theme === 'dark' ? 'light' : 'dark'
    document.documentElement.classList.toggle('light', state.theme === 'light')
    render()
  })

  // Copy number
  document.getElementById('btn-copy')?.addEventListener('click', () => {
    navigator.clipboard.writeText(state.number).catch(() => {})
  })

  // Renew number
  document.getElementById('btn-renew')?.addEventListener('click', () => {
    if (confirm('番号を再発行しますか？全てのPINが無効になります。')) {
      ws.send('number.renew')
    }
  })

  // New PIN screen
  document.getElementById('btn-new-pin')?.addEventListener('click', () => {
    state.screen = 'newPin'
    state.newPinValue = randomPin()
    render()
  })

  // Connect screen
  document.getElementById('btn-connect')?.addEventListener('click', () => {
    state.screen = 'connect'
    state.activePin = null
    state.activeContact = null
    render()
  })

  // Inbox items
  document.querySelectorAll('.inbox-item[data-pin-id]').forEach(el => {
    el.addEventListener('click', () => {
      const pinId = (el as HTMLElement).dataset.pinId!
      const pin = state.inbox.find(p => p.id === pinId)
      if (!pin) return
      state.activePin = pin
      state.activeContact = null
      // 公開用PINはリクエスト一覧へ
      if (pin.type === 'lobby') {
        state.screen = 'requests'
        render()
        ws.send('messages.list', { pinId })
      } else {
        state.screen = 'chat'
        render()
        ws.send('messages.list', { pinId })
        scrollToBottom()
      }
    })
  })

  // Contact items
  document.querySelectorAll('.inbox-item[data-contact-id]').forEach(el => {
    el.addEventListener('click', () => {
      const contactId = (el as HTMLElement).dataset.contactId!
      const contact = state.contacts.find(c => c.id === contactId)
      if (!contact) return
      state.activeContact = contact
      state.activePin = null
      state.screen = 'chat'
      render()
      ws.send('chat.start', { theirNumber: contact.theirNumber, theirPin: contact.theirPin, label: contact.label })
      scrollToBottom()
    })
  })

  // PIN menu
  document.getElementById('btn-pin-menu')?.addEventListener('click', () => {
    state.screen = 'pinMenu'
    render()
  })

  // Contact remove
  document.getElementById('btn-contact-remove')?.addEventListener('click', () => {
    if (!state.activeContact) return
    if (confirm(`${state.activeContact.label || state.activeContact.theirNumber} を削除しますか？`)) {
      ws.send('contact.remove', { contactId: state.activeContact.id })
      state.activeContact = null
      state.screen = 'welcome'
      render()
    }
  })

  // Chat send
  const input = document.getElementById('chat-input') as HTMLTextAreaElement
  const sendFn = () => {
    const content = input?.value.trim()
    if (!content) return

    if (state.activePin) {
      const pinId = state.activePin.id
      const localId = crypto.randomUUID()

      if (!state.messages[pinId]) state.messages[pinId] = []
      state.messages[pinId].push({ localId, content, isMine: true, timestamp: Date.now(), status: 'queued' })

      ws.send('message.send', { pinId, content, localId })
      render()
      scrollToBottom()
    } else if (state.activeContact) {
      ws.send('contact.message.send', { contactId: state.activeContact.id, content })
    }

    input.value = ''
    input.style.height = 'auto'
  }

  document.getElementById('btn-send')?.addEventListener('click', sendFn)
  input?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendFn()
    }
  })
  input?.addEventListener('input', () => {
    if (input) {
      input.style.height = 'auto'
      input.style.height = Math.min(input.scrollHeight, 100) + 'px'
    }
  })

  // New PIN expiry
  document.querySelectorAll('.expiry-opt').forEach(btn => {
    btn.addEventListener('click', () => {
      state.newPinExpiry = (btn as HTMLElement).dataset.expiry || 'none'
      render()
    })
  })
  document.getElementById('expiry-custom-num')?.addEventListener('input', e => {
    state.newPinCustomNum = (e.target as HTMLInputElement).value
  })
  document.getElementById('expiry-custom-unit')?.addEventListener('change', e => {
    state.newPinCustomUnit = (e.target as HTMLSelectElement).value as 'h' | 'd' | 'w'
  })
  document.getElementById('type-direct')?.addEventListener('click', () => {
    state.newPinIsLobby = false; render()
  })
  document.getElementById('type-lobby')?.addEventListener('click', () => {
    state.newPinIsLobby = true; render()
  })

  // Regen PIN
  document.getElementById('btn-regen-pin')?.addEventListener('click', () => {
    state.newPinValue = randomPin()
    const el = document.getElementById('new-pin-display')
    if (el) glitch(el, state.newPinValue)
  })

  // Save PIN
  document.getElementById('btn-save-pin')?.addEventListener('click', () => {
    const label = (document.getElementById('pin-label-input') as HTMLInputElement)?.value.trim() || ''
    const num = (document.getElementById('expiry-custom-num') as HTMLInputElement)?.value || state.newPinCustomNum
    const unit = (document.getElementById('expiry-custom-unit') as HTMLSelectElement)?.value || state.newPinCustomUnit
    const expiry = state.newPinExpiry === 'custom'
      ? `${num}${unit}`
      : state.newPinExpiry
    ws.send('pin.create', { label, expiry, type: state.newPinIsLobby ? 'lobby' : 'direct' })
    state.screen = 'welcome'
    state.newPinExpiry = 'none'
    state.newPinIsLobby = false
    render()
  })

  // Connect form submit
  document.getElementById('btn-do-connect')?.addEventListener('click', () => {
    const theirNumber = (document.getElementById('connect-number') as HTMLInputElement)?.value.trim()
    const theirPin = (document.getElementById('connect-pin') as HTMLInputElement)?.value.trim()
    const label = (document.getElementById('connect-label') as HTMLInputElement)?.value.trim() || ''
    if (!theirNumber || !theirPin) return
    ws.send('chat.start', { theirNumber, theirPin, label })
  })

  // PIN menu actions
  document.getElementById('menu-rotate')?.addEventListener('click', () => {
    if (!state.activePin) return
    ws.send('pin.rotate', { pinId: state.activePin.id })
    state.screen = 'welcome'
    state.activePin = null
    render()
  })

  document.getElementById('menu-revoke')?.addEventListener('click', () => {
    if (!state.activePin) return
    ws.send('pin.revoke', { pinId: state.activePin.id })
    state.screen = 'welcome'
    state.activePin = null
    render()
  })

  document.getElementById('menu-back')?.addEventListener('click', () => {
    state.screen = 'chat'
    render()
  })

  document.getElementById('menu-agent-export')?.addEventListener('click', () => {
    state.screen = 'agentExport'
    render()
  })

  document.getElementById('agent-export-back')?.addEventListener('click', () => {
    state.screen = 'pinMenu'
    render()
  })

  document.getElementById('btn-copy-config')?.addEventListener('click', () => {
    const pre = document.getElementById('agent-config-pre')
    const hint = document.getElementById('agent-copy-hint')
    if (!pre) return
    navigator.clipboard.writeText(pre.textContent || '').then(() => {
      if (hint) { hint.textContent = '// copied!'; setTimeout(() => { if (hint) hint.textContent = '' }, 2000) }
    }).catch(() => {})
  })

  document.getElementById('menu-label')?.addEventListener('click', () => {
    const newLabel = prompt('新しいラベル:', state.activePin?.label || '')
    if (newLabel !== null && state.activePin) {
      ws.send('pin.label', { pinId: state.activePin.id, label: newLabel })
    }
  })

  // Requests: 差出人クリックで個別チャット
  document.querySelectorAll('.request-thread-item').forEach(el => {
    el.addEventListener('click', () => {
      const pubKeyHex = (el as HTMLElement).dataset.pubkey!
      if (!pubKeyHex || !state.activePin) return
      const shortKey = pubKeyHex.slice(0, 16)
      if (!state.messages[state.activePin.id + ':' + shortKey]) {
        state.messages[state.activePin.id + ':' + shortKey] = []
      }
      state.activeLobbyKey = pubKeyHex
      state.screen = 'requestChat'
      render()
      scrollToBottom()
    })
  })

  document.getElementById('requests-back')?.addEventListener('click', () => {
    state.screen = 'welcome'
    state.activePin = null
    render()
  })

  document.getElementById('requests-chat-back')?.addEventListener('click', () => {
    state.screen = 'requests'
    state.activeLobbyKey = null
    render()
  })

  // Request chat: メッセージ送信（返信 = 承認）
  const requestSendBtn = document.getElementById('request-send-btn')
  const requestChatInput = document.getElementById('request-chat-input') as HTMLTextAreaElement | null
  requestSendBtn?.addEventListener('click', () => sendRequestMessage())
  requestChatInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendRequestMessage() }
  })

  function sendRequestMessage() {
    const input = document.getElementById('request-chat-input') as HTMLTextAreaElement | null
    const content = input?.value.trim()
    if (!content || !state.activePin || !state.activeLobbyKey) return
    const pin = state.activePin
    const pubKeyHex = state.activeLobbyKey
    const shortKey = pubKeyHex.slice(0, 16)
    const localId = String(Date.now())
    const key = pin.id + ':' + shortKey
    const msgs = state.messages[key] || []
    msgs.push({ localId, content, isMine: true, timestamp: Date.now(), status: 'queued' })
    state.messages[key] = msgs
    ws.send('message.send', { pinId: pin.id, content, pubKeyHex, localId })
    if (input) { input.value = ''; input.style.height = 'auto' }
    render()
    scrollToBottom()
  }
}

// ===== WebSocket Events =====
ws.on('init', (msg: unknown) => {
  const m = msg as { data: { number: string; inbox: PinEntry[]; contacts: Contact[]; prefs: { theme: string } } }
  state.number = m.data.number
  state.inbox = m.data.inbox
  state.contacts = m.data.contacts || []
  if (m.data.prefs?.theme === 'light') {
    state.theme = 'light'
    document.documentElement.classList.add('light')
  }
  render()
  glitchNumber()
})

ws.on('inbox.list', (msg: unknown) => {
  const m = msg as { data: PinEntry[] }
  state.inbox = m.data
  if (state.activePin) {
    const updated = m.data.find(p => p.id === state.activePin!.id)
    if (updated) state.activePin = updated
  }
  render()
})

ws.on('contacts.list', (msg: unknown) => {
  const m = msg as { data: Contact[] }
  state.contacts = m.data
  if (state.activeContact) {
    const updated = m.data.find(c => c.id === state.activeContact!.id)
    if (updated) state.activeContact = updated
  }
  render()
})

ws.on('messages.list', (msg: unknown) => {
  const m = msg as { pinId: string; data: Message[] }
  state.messages[m.pinId] = m.data
  renderIfActivePin(m.pinId, true)
})

ws.on('chat.started', (msg: unknown) => {
  const m = msg as { contactId: string; data: Contact }
  const idx = state.contacts.findIndex(c => c.id === m.contactId)
  if (idx === -1) state.contacts.push(m.data)
  else state.contacts[idx] = { ...state.contacts[idx], ...m.data }
  state.activeContact = state.contacts.find(c => c.id === m.contactId) || m.data
  state.activePin = null
  state.screen = 'chat'
  render()
  scrollToBottom()
})

ws.on('contact.messages.list', (msg: unknown) => {
  const m = msg as { contactId: string; data: Message[] }
  state.contactMessages[m.contactId] = m.data
  renderIfActiveContact(m.contactId, true)
})

ws.on('message.received', (msg: unknown) => {
  const m = msg as { pinId: string; data: Message }
  if (!state.messages[m.pinId]) state.messages[m.pinId] = []
  state.messages[m.pinId].push(m.data)

  const pin = state.inbox.find(p => p.id === m.pinId)
  if (pin) {
    pin.unread++
    pin.latest = m.data
  }

  renderIfActivePin(m.pinId, true)
})

ws.on('contact.message.received', (msg: unknown) => {
  const m = msg as { contactId: string; data: Message }
  if (!state.contactMessages[m.contactId]) state.contactMessages[m.contactId] = []
  state.contactMessages[m.contactId].push(m.data)

  const contact = state.contacts.find(c => c.id === m.contactId)
  if (contact) {
    contact.unread++
    contact.latest = m.data
  }

  renderIfActiveContact(m.contactId, true)
})

ws.on('message.sent', (msg: unknown) => {
  const m = msg as { pinId: string; localId?: string; data: Message }

  if (m.localId) {
    updateMessageStatus(m.pinId, m.localId, 'delivered')
  } else {
    if (!state.messages[m.pinId]) state.messages[m.pinId] = []
    state.messages[m.pinId].push(m.data)
  }

  renderIfActivePin(m.pinId, true)
})

ws.on('message.queued', () => {
  // クライアント側で既に queued 表示済み
})

ws.on('message.delivered', (msg: unknown) => {
  const m = msg as { pinId: string; localId: string }
  updateMessageStatus(m.pinId, m.localId, 'delivered')
  renderIfActivePin(m.pinId, false)
})

ws.on('contact.message.sent', (msg: unknown) => {
  const m = msg as { contactId: string; data: Message }
  if (!state.contactMessages[m.contactId]) state.contactMessages[m.contactId] = []
  state.contactMessages[m.contactId].push(m.data)
  renderIfActiveContact(m.contactId, true)
})

ws.on('peer.status', (msg: unknown) => {
  const m = msg as { pinId?: string; contactId?: string; status: 'connected' | 'disconnected' | 'connecting' }
  const key = m.pinId || m.contactId || ''
  if (key) state.peerStatus[key] = m.status
  render()
})

ws.on('pin.created', () => { ws.send('inbox.list') })
ws.on('pin.rotated', () => { ws.send('inbox.list') })
ws.on('pin.revoked', () => { ws.send('inbox.list') })

ws.on('contact.removed', (msg: unknown) => {
  const m = msg as { contactId: string }
  state.contacts = state.contacts.filter(c => c.id !== m.contactId)
  delete state.contactMessages[m.contactId]
  delete state.peerStatus[m.contactId]
  render()
})

ws.on('lobby.threads', (msg: unknown) => {
  const m = msg as { pinId: string; data: { pubKeyHex: string; latest: Message | null; count: number }[] }
  state.lobbyThreads[m.pinId] = m.data.map(t => ({ ...t, shortKey: t.pubKeyHex.slice(0, 16) }))
  if (state.screen === 'requests' && state.activePin?.id === m.pinId) render()
})

ws.on('lobby.connected', (msg: unknown) => {
  const m = msg as { pinId: string; pubKeyHex: string }
  const threads = state.lobbyThreads[m.pinId] || []
  if (!threads.find(t => t.pubKeyHex === m.pubKeyHex)) {
    threads.push({ pubKeyHex: m.pubKeyHex, shortKey: m.pubKeyHex.slice(0, 16), latest: null, count: 0 })
    state.lobbyThreads[m.pinId] = threads
  }
  if (state.screen === 'requests' && state.activePin?.id === m.pinId) render()
  else render() // サイドバーのバッジを更新
})

ws.on('lobby.message', (msg: unknown) => {
  const m = msg as { pinId: string; pubKeyHex: string; shortKey: string; data: Message }
  const key = m.pinId + ':' + m.shortKey
  const msgs = state.messages[key] || []
  msgs.push({ ...m.data, id: String(Date.now()) })
  state.messages[key] = msgs
  const threads = state.lobbyThreads[m.pinId] || []
  const t = threads.find(t => t.pubKeyHex === m.pubKeyHex)
  if (t) { t.latest = m.data; t.count++ }
  if (state.screen === 'requestChat' && state.activePin?.id === m.pinId && state.activeLobbyKey === m.pubKeyHex) {
    render(); scrollToBottom()
  } else if (state.screen === 'requests' && state.activePin?.id === m.pinId) {
    render()
  } else {
    render() // サイドバーのバッジを更新
  }
})

ws.on('lobby.migrated', (msg: unknown) => {
  const m = msg as { pinId: string; newPinId: string; newPinValue: string }
  ws.send('inbox.list')
  // 返信（承認）完了 → inbox に新しい受信箱が生成された。requests 画面は戻す
  if (state.activePin?.id === m.pinId && (state.screen === 'requestChat' || state.screen === 'requests')) {
    state.screen = 'welcome'
    state.activePin = null
    state.activeLobbyKey = null
    render()
  }
})

ws.on('number.renewed', (msg: unknown) => {
  const m = msg as { data: { number: string } }
  state.number = m.data.number
  render()
  glitchNumber()
})

// ===== Helpers =====
function updateMessageStatus(pinId: string, localId: string, status: Message['status']) {
  const msgs = state.messages[pinId] || []
  const idx = msgs.findIndex(m => m.localId === localId)
  if (idx !== -1) {
    msgs[idx] = { ...msgs[idx], status }
    state.messages[pinId] = msgs
  }
}

function renderIfActivePin(pinId: string, scroll: boolean) {
  if (state.screen === 'chat' && state.activePin?.id === pinId) {
    render()
    if (scroll) scrollToBottom()
  } else {
    render()
  }
}

function renderIfActiveContact(contactId: string, scroll: boolean) {
  if (state.screen === 'chat' && state.activeContact?.id === contactId) {
    render()
    if (scroll) scrollToBottom()
  } else {
    render()
  }
}

function scrollToBottom() {
  setTimeout(() => {
    const area = document.getElementById('messages-area')
    if (area) area.scrollTop = area.scrollHeight
  }, 0)
}

function formatTime(ts: number) {
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

function escapeHtml(s: string) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#039;')
    .replace(/\n/g, '<br>')
}

function glitch(el: HTMLElement, final: string) {
  const chars = '0123456789abcdef'
  let count = 0
  const iv = setInterval(() => {
    let s = ''
    for (const c of final) {
      s += Math.random() < 0.3 ? chars[Math.floor(Math.random() * chars.length)] : c
    }
    el.textContent = s
    if (++count > 6) { clearInterval(iv); el.textContent = final }
  }, 70)
}

function glitchNumber() {
  const el = document.getElementById('my-number')
  if (el && state.number) glitch(el, state.number)
}

// ===== Boot =====
ws.connect()
render()
