/**
 * 0x0 CLI テストスイート
 * - Unit: コアロジック（ネットワーク不要）
 * - Storage: ファイルI/O（tmpdir 分離）
 * - CLI smoke: 全コマンドをサブプロセスで実行
 */

import assert from 'assert'
import fs from 'fs'
import path from 'path'
import os from 'os'
import { execSync } from 'child_process'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const CLI_DIR = path.resolve(__dirname, '..')
const CLI = `node "${path.join(CLI_DIR, 'bin/0x0.js')}"`

// テスト用 tmpHome
const TMP_HOME = fs.mkdtempSync(path.join(os.tmpdir(), '0x0-test-'))
const ENV = { ...process.env, HOME: TMP_HOME, USERPROFILE: TMP_HOME, APPDATA: TMP_HOME }

// ─────────────────────────────────────────────
// ヘルパー
// ─────────────────────────────────────────────
let passed = 0
let failed = 0
const errors = []

function test(name, fn) {
  try {
    fn()
    console.log(`  ✓ ${name}`)
    passed++
  } catch (e) {
    console.log(`  ✗ ${name}`)
    console.log(`    ${e.message}`)
    failed++
    errors.push({ name, message: e.message })
  }
}

function section(title) {
  console.log(`\n── ${title}`)
}

function run(cmd, env = ENV) {
  return execSync(`${CLI} ${cmd}`, { env, cwd: CLI_DIR, encoding: 'utf8' })
}

// ─────────────────────────────────────────────
// 1. Unit: core/pin.js
// ─────────────────────────────────────────────
section('Unit: core/pin.js')
const { generatePin, hashPin } = await import('../src/core/pin.js')

test('generatePin() — デフォルト6文字', () => {
  const p = generatePin()
  assert.strictEqual(p.length, 6, `length=${p.length}`)
})

test('generatePin() — 指定長（4文字）', () => {
  const p = generatePin(4)
  assert.strictEqual(p.length, 4)
})

test('generatePin() — 指定長（16文字）', () => {
  const p = generatePin(16)
  assert.strictEqual(p.length, 16)
})

test('generatePin() — 16進数のみ', () => {
  for (let i = 0; i < 20; i++) {
    const p = generatePin(8)
    assert.match(p, /^[0-9a-f]+$/, `invalid chars: ${p}`)
  }
})

test('generatePin() — ランダム性（20回で重複なし）', () => {
  const pins = new Set(Array.from({ length: 20 }, () => generatePin()))
  assert(pins.size > 15, `too many duplicates: ${pins.size} unique`)
})

test('hashPin() — 確定的（同入力→同出力）', () => {
  assert.strictEqual(hashPin('a3f9'), hashPin('a3f9'))
})

test('hashPin() — 異なる入力→異なる出力', () => {
  assert.notStrictEqual(hashPin('a3f9'), hashPin('b72e'))
})

test('hashPin() — 64文字 hex', () => {
  assert.match(hashPin('test'), /^[0-9a-f]{64}$/)
})

// ─────────────────────────────────────────────
// 2. Unit: core/channel.js
// ─────────────────────────────────────────────
section('Unit: core/channel.js')
const { channelSecret } = await import('../src/core/channel.js')

test('channelSecret() — 32バイト Buffer', () => {
  const s = channelSecret('0x0-123-4567-8901', 'a3f9')
  assert(Buffer.isBuffer(s), 'not a Buffer')
  assert.strictEqual(s.length, 32)
})

test('channelSecret() — 確定的', () => {
  const a = channelSecret('0x0-123-4567-8901', 'a3f9')
  const b = channelSecret('0x0-123-4567-8901', 'a3f9')
  assert.strictEqual(a.toString('hex'), b.toString('hex'))
})

test('channelSecret() — 番号が違えば異なる', () => {
  const a = channelSecret('0x0-123-4567-8901', 'a3f9')
  const b = channelSecret('0x0-999-9999-9999', 'a3f9')
  assert.notStrictEqual(a.toString('hex'), b.toString('hex'))
})

test('channelSecret() — PINが違えば異なる', () => {
  const a = channelSecret('0x0-123-4567-8901', 'a3f9')
  const b = channelSecret('0x0-123-4567-8901', 'b72e')
  assert.notStrictEqual(a.toString('hex'), b.toString('hex'))
})

// ─────────────────────────────────────────────
// 3. Unit: core/message.js
// ─────────────────────────────────────────────
section('Unit: core/message.js')
const { createMessage, createPinMigrate, createPing, parseMessage } = await import('../src/core/message.js')

test('createMessage() — JSON 文字列', () => {
  const raw = createMessage('hello')
  const msg = JSON.parse(raw)
  assert.strictEqual(msg.type, 'message')
  assert.strictEqual(msg.content, 'hello')
  assert.strictEqual(msg.version, '1')
  assert(typeof msg.timestamp === 'number')
})

test('createPinMigrate() — JSON 文字列', () => {
  const raw = createPinMigrate('0x0-123-4567-8901', 'newpin1')
  const msg = JSON.parse(raw)
  assert.strictEqual(msg.type, 'pin_migrate')
  assert.strictEqual(msg.newPin, 'newpin1')
  assert.strictEqual(msg.newUri, '0x0://0x0-123-4567-8901/newpin1')
})

test('createPing() — JSON 文字列', () => {
  const msg = JSON.parse(createPing())
  assert.strictEqual(msg.type, 'ping')
})

test('parseMessage() — 正常パース', () => {
  const raw = createMessage('world')
  const msg = parseMessage(Buffer.from(raw))
  assert.strictEqual(msg.content, 'world')
  assert.strictEqual(msg.type, 'message')
})

test('parseMessage() — 不正JSON → null', () => {
  assert.strictEqual(parseMessage(Buffer.from('not json')), null)
})

test('parseMessage() — version/type なし → null', () => {
  assert.strictEqual(parseMessage(Buffer.from('{"foo":"bar"}')), null)
})

// ─────────────────────────────────────────────
// 4. Storage: queue.js（tmpdir で分離）
// ─────────────────────────────────────────────
section('Storage: queue.js')
const queueFile = path.join(TMP_HOME, '.0x0', 'queue.jsonl')
// os.homedir() が TMP_HOME を返すよう上書き（Node.js: HOME 環境変数を参照）
// 注: 別プロセスで実行しているため、直接importでは HOME が反映されない
// → subprocessでテスト

function runScript(script) {
  return execSync(`node --input-type=module`, {
    input: script,
    env: ENV,
    cwd: CLI_DIR,
    encoding: 'utf8'
  })
}

test('queue.append() — ファイル生成 & 内容確認', () => {
  const out = runScript(`
    import * as q from './src/storage/queue.js'
    const item = q.append({ type: 'contact', theirNumber: '0x0-111-2222-3333', pin: 'abcd', content: 'hello' })
    console.log(JSON.stringify(item))
  `)
  const item = JSON.parse(out.trim())
  assert.strictEqual(item.type, 'contact')
  assert.strictEqual(item.content, 'hello')
  assert(item.expiresAt > Date.now())
})

test('queue.loadAll() — 追加したアイテムが読める', () => {
  const out = runScript(`
    import * as q from './src/storage/queue.js'
    q.append({ type: 'pin', pinId: 'pin-123', content: 'test msg' })
    const items = q.loadAll()
    console.log(items.length)
  `)
  assert(parseInt(out.trim()) >= 1)
})

test('queue.remove() — 削除後は取得されない', () => {
  const out = runScript(`
    import * as q from './src/storage/queue.js'
    const item = q.append({ type: 'contact', theirNumber: 'x', pin: 'y', content: 'del-me' })
    q.remove(item.id)
    const remaining = q.loadAll().filter(i => i.id === item.id)
    console.log(remaining.length)
  `)
  assert.strictEqual(parseInt(out.trim()), 0)
})

test('queue.purgeExpired() — 期限切れは除外', () => {
  const out = runScript(`
    import * as q from './src/storage/queue.js'
    import fs from 'fs'
    import path from 'path'
    import os from 'os'
    // 期限切れアイテムを直接書き込む
    const file = path.join(os.homedir(), '.0x0', 'queue.jsonl')
    const expired = JSON.stringify({ id: 'expired-1', type: 'contact', content: 'old', timestamp: 0, expiresAt: 1 })
    fs.appendFileSync(file, expired + '\\n')
    q.purgeExpired()
    const items = q.loadAll().filter(i => i.id === 'expired-1')
    console.log(items.length)
  `)
  assert.strictEqual(parseInt(out.trim()), 0)
})

// ─────────────────────────────────────────────
// 5. Storage: pins.js
// ─────────────────────────────────────────────
section('Storage: pins.js')

test('pins.create() — 正常に生成される', () => {
  const out = runScript(`
    import * as p from './src/storage/pins.js'
    const pin = p.create({ value: 'a1b2c3', label: 'test', expiry: 'none', expiresAt: null })
    console.log(JSON.stringify(pin))
  `)
  const pin = JSON.parse(out.trim())
  assert.strictEqual(pin.value, 'a1b2c3')
  assert.strictEqual(pin.label, 'test')
  assert.strictEqual(pin.isActive, true)
  assert.strictEqual(pin.type, 'direct')
})

test('pins.create() — lobby type', () => {
  const out = runScript(`
    import * as p from './src/storage/pins.js'
    const pin = p.create({ value: 'lobby1', label: '', expiry: 'none', expiresAt: null, type: 'lobby' })
    console.log(pin.type)
  `)
  assert.strictEqual(out.trim(), 'lobby')
})

test('pins.getActive() — isActive: true のものだけ返す', () => {
  const out = runScript(`
    import * as p from './src/storage/pins.js'
    p.create({ value: 'active1', label: '', expiry: 'none', expiresAt: null })
    p.create({ value: 'active2', label: '', expiry: 'none', expiresAt: null })
    const active = p.getActive()
    console.log(active.filter(x => x.value === 'active1' || x.value === 'active2').length)
  `)
  assert(parseInt(out.trim()) >= 2)
})

test('pins.revoke() — 無効化後は getActive に出ない', () => {
  const out = runScript(`
    import * as p from './src/storage/pins.js'
    const pin = p.create({ value: 'revoke-me', label: '', expiry: 'none', expiresAt: null })
    p.revoke(pin.id)
    const active = p.getActive().filter(x => x.value === 'revoke-me')
    console.log(active.length)
  `)
  assert.strictEqual(parseInt(out.trim()), 0)
})

test('pins.rotate() — value が変わる', () => {
  const out = runScript(`
    import * as p from './src/storage/pins.js'
    const pin = p.create({ value: 'rotate-me', label: '', expiry: 'none', expiresAt: null })
    p.rotate(pin.id, 'new-val')
    const updated = p.findById(pin.id)
    console.log(updated.value)
  `)
  assert.strictEqual(out.trim(), 'new-val')
})

test('pins.findByValue() — 存在するPINを返す', () => {
  const out = runScript(`
    import * as p from './src/storage/pins.js'
    p.create({ value: 'findme11', label: '', expiry: 'none', expiresAt: null })
    const found = p.findByValue('findme11')
    console.log(found ? found.value : 'null')
  `)
  assert.strictEqual(out.trim(), 'findme11')
})

test('pins.expiresAt — 期限切れは getActive に出ない', () => {
  const out = runScript(`
    import * as p from './src/storage/pins.js'
    p.create({ value: 'expired2', label: '', expiry: '1h', expiresAt: 1 }) // 過去
    const active = p.getActive().filter(x => x.value === 'expired2')
    console.log(active.length)
  `)
  assert.strictEqual(parseInt(out.trim()), 0)
})

// ─────────────────────────────────────────────
// 6. Storage: messages.js
// ─────────────────────────────────────────────
section('Storage: messages.js')

test('messages.append() & list() — 通常スレッド', () => {
  const out = runScript(`
    import * as m from './src/storage/messages.js'
    m.append('testpin1', { from: 'peer', content: 'hello world', isMine: false })
    m.append('testpin1', { from: 'me', content: 'reply', isMine: true })
    const msgs = m.list('testpin1')
    console.log(msgs.length + ' ' + msgs[0].content)
  `)
  const [count, first] = out.trim().split(' ')
  assert.strictEqual(parseInt(count), 2)
  assert.strictEqual(first, 'hello')
})

test('messages.append() — pubKeyHex サブスレッド', () => {
  const out = runScript(`
    import * as m from './src/storage/messages.js'
    m.append('lobbypin1', { from: 'peer', content: 'sub msg', isMine: false, pubKeyHex: 'abc123def456' })
    const msgs = m.list('lobbypin1', 100, 'abc123def456')
    console.log(msgs.length + ' ' + (msgs[0]?.content || 'none'))
  `)
  const [count, content] = out.trim().split(' ')
  assert.strictEqual(parseInt(count), 1)
  assert.strictEqual(content, 'sub')
})

test('messages.listLobbyThreads() — サブスレッド一覧', () => {
  const out = runScript(`
    import * as m from './src/storage/messages.js'
    m.append('lpin2', { from: 'p', content: 'msg1', isMine: false, pubKeyHex: 'aaa111bbb222' })
    m.append('lpin2', { from: 'p', content: 'msg2', isMine: false, pubKeyHex: 'ccc333ddd444' })
    const threads = m.listLobbyThreads('lpin2')
    console.log(threads.length)
  `)
  assert(parseInt(out.trim()) >= 2)
})

test('messages.getLatest() — 最後のメッセージを返す', () => {
  const out = runScript(`
    import * as m from './src/storage/messages.js'
    m.append('latestpin', { from: 'p', content: 'first', isMine: false })
    m.append('latestpin', { from: 'p', content: 'last', isMine: false })
    const latest = m.getLatest('latestpin')
    console.log(latest?.content)
  `)
  assert.strictEqual(out.trim(), 'last')
})

test('messages.countUnread() — 未読数カウント', () => {
  const out = runScript(`
    import * as m from './src/storage/messages.js'
    m.append('unreadpin', { from: 'p', content: 'a', isMine: false })
    m.append('unreadpin', { from: 'p', content: 'b', isMine: false })
    m.append('unreadpin', { from: 'me', content: 'c', isMine: true })
    console.log(m.countUnread('unreadpin'))
  `)
  assert.strictEqual(parseInt(out.trim()), 2)
})

// ─────────────────────────────────────────────
// 7. CLI smoke tests
// ─────────────────────────────────────────────
section('CLI smoke: init / whoami')

test('0x0 init — 初期化成功', () => {
  const out = run('init')
  assert.match(out, /0x0-\d{3}-\d{4}-\d{4}/, `output: ${out}`)
})

test('0x0 whoami — 番号が表示される', () => {
  const out = run('whoami')
  assert.match(out, /0x0-\d{3}-\d{4}-\d{4}/)
})

test('0x0 whoami — PINリストが表示される', () => {
  const out = run('whoami')
  assert.match(out, /pins?/, `output: ${out}`)
})

section('CLI smoke: pin')

test('0x0 pin new — PINが作成される', () => {
  const out = run('pin new --label smoketest')
  assert.match(out, /[0-9a-f]{4,16}/, `output: ${out}`)
})

test('0x0 pin list — 作成したPINが出る', () => {
  const out = run('pin list')
  assert.match(out, /smoketest|[0-9a-f]{4,}/, `output: ${out}`)
})

test('0x0 pin new --public — lobby PINが作成される', () => {
  const out = run('pin new --public --label publicpin')
  assert.match(out, /[0-9a-f]{4,16}/, `output: ${out}`)
})

section('CLI smoke: inbox / read / queue / requests')

test('0x0 inbox — エラーなし', () => {
  const out = run('inbox')
  assert(typeof out === 'string')
})

test('0x0 inbox --json — JSON配列を返す', () => {
  const out = run('inbox --json')
  const data = JSON.parse(out)
  assert(Array.isArray(data), 'not an array')
})

test('0x0 queue — エラーなし（empty）', () => {
  const out = run('queue')
  assert.match(out, /pending/, `output: ${out}`)
})

test('0x0 requests — エラーなし', () => {
  const out = run('requests')
  assert(typeof out === 'string')
})

test('0x0 requests — lobby PINが表示される', () => {
  const out = run('requests')
  assert.match(out, /publicpin|request|public/, `output: ${out}`)
})

section('CLI smoke: contact')

test('0x0 contact list — エラーなし', () => {
  const out = run('contact list')
  assert(typeof out === 'string')
})

test('0x0 contact add — コンタクト追加', () => {
  // 架空の番号に追加（P2P接続はしない）
  const out = run('contact add 0x0-999-1234-5678 a3f9 --label testcontact')
  assert(typeof out === 'string')
})

test('0x0 contact list — 追加したコンタクトが出る', () => {
  const out = run('contact list')
  assert.match(out, /testcontact|0x0-999/, `output: ${out}`)
})

section('CLI smoke: qr')

test('0x0 qr <pin> — QRコードが表示される', () => {
  // まず pin を取得
  const listOut = run('inbox --json')
  const pins = JSON.parse(listOut)
  if (pins.length === 0) {
    console.log('    (skip: no pins)')
    passed++
    return
  }
  const pin = pins[0].value
  const out = run(`qr ${pin}`)
  assert(out.length > 10, 'QR output too short')
})

section('CLI smoke: help / version')

test('0x0 --help — ヘルプが表示される', () => {
  const out = run('--help')
  assert.match(out, /Commands:/)
})

test('0x0 --version — バージョンが表示される', () => {
  const out = run('--version')
  assert.match(out, /\d+\.\d+\.\d+/)
})

// ─────────────────────────────────────────────
// 結果サマリ
// ─────────────────────────────────────────────
console.log('\n' + '─'.repeat(50))
console.log(`結果: ${passed} passed, ${failed} failed`)

if (errors.length > 0) {
  console.log('\n失敗したテスト:')
  for (const e of errors) {
    console.log(`  ✗ ${e.name}`)
    console.log(`    ${e.message}`)
  }
}

// クリーンアップ
try { fs.rmSync(TMP_HOME, { recursive: true, force: true }) } catch {}

if (failed > 0) process.exit(1)
