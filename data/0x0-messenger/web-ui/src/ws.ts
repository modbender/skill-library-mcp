type EventHandler = (data: unknown) => void

class WsClient {
  private ws: WebSocket | null = null
  private handlers: Map<string, EventHandler[]> = new Map()
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null

  connect() {
    this.ws = new WebSocket(`ws://localhost:${location.port || 3000}`)

    this.ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data)
        const handlers = this.handlers.get(msg.event) || []
        handlers.forEach(h => h(msg))
      } catch {}
    }

    this.ws.onclose = () => {
      this.reconnectTimer = setTimeout(() => this.connect(), 2000)
    }

    this.ws.onerror = () => {
      this.ws?.close()
    }
  }

  on(event: string, handler: EventHandler) {
    if (!this.handlers.has(event)) this.handlers.set(event, [])
    this.handlers.get(event)!.push(handler)
  }

  send(cmd: string, payload: Record<string, unknown> = {}) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ cmd, ...payload }))
    }
  }

  destroy() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.ws?.close()
  }
}

export const ws = new WsClient()
