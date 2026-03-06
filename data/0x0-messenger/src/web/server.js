import http from 'http'
import os from 'os'
import path from 'path'
import { fileURLToPath } from 'url'
import express from 'express'
import { WebSocketServer } from 'ws'
import { createApiHandler } from './api.js'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const DIST = path.resolve(__dirname, '../../dist/web')

export async function startWebServer(port = 3000, { lan = false } = {}) {
  const app = express()

  // ビルド済みフロントエンド配信
  app.use(express.static(DIST))
  app.get('*', (_req, res) => res.sendFile(path.join(DIST, 'index.html')))

  const server = http.createServer(app)

  // WebSocket: デフォルトはローカルホストのみ、--lan で LAN 公開
  const wss = new WebSocketServer({ server, maxPayload: 1024 * 1024 })
  wss.on('connection', (ws) => {
    createApiHandler(ws)
  })

  const host = lan ? '0.0.0.0' : '127.0.0.1'
  return new Promise((resolve, reject) => {
    server.listen(port, host, () => {
      resolve({ server, wss, port, lan })
    })
    server.on('error', (err) => {
      if (err.code === 'EADDRINUSE') {
        resolve(startWebServer(port + 1))
      } else {
        reject(err)
      }
    })
  })
}

export function getLanIps() {
  const interfaces = os.networkInterfaces()
  const ips = []
  for (const iface of Object.values(interfaces)) {
    for (const entry of iface ?? []) {
      if (entry.family === 'IPv4' && !entry.internal) {
        ips.push(entry.address)
      }
    }
  }
  return ips
}
