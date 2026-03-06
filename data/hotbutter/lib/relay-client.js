const WebSocket = require('ws');
const crypto = require('crypto');

const DEFAULT_RELAY = 'wss://hotbutter.ai';
const RECONNECT_DELAYS = [2000, 4000, 8000, 16000];

class RelayClient {
  constructor(options = {}) {
    this.relayUrl = options.relayUrl || DEFAULT_RELAY;
    this.agentId = options.agentId || crypto.randomUUID();
    this.agentName = options.agentName || 'Agent';
    this.ws = null;
    this.sessionId = null;
    this.pairingCode = null;
    this.handlers = {};
    this._reconnectAttempt = 0;
    this._shouldReconnect = true;
  }

  on(event, fn) {
    this.handlers[event] = fn;
  }

  _emit(event, data) {
    if (this.handlers[event]) this.handlers[event](data);
  }

  connect() {
    const wsUrl = this.relayUrl.replace(/^http/, 'ws') + '/ws/agent';
    this.ws = new WebSocket(wsUrl);

    this.ws.on('open', () => {
      this._reconnectAttempt = 0;
      this._send({
        type: 'agent:register',
        agentId: this.agentId,
        agentName: this.agentName,
      });
      this._emit('connected');
    });

    this.ws.on('message', (raw) => {
      let msg;
      try { msg = JSON.parse(raw); } catch { return; }

      switch (msg.type) {
        case 'relay:code':
          this.pairingCode = msg.code;
          this._emit('code', msg.code);
          break;
        case 'relay:paired':
          this.sessionId = msg.sessionId;
          this._emit('paired', { sessionId: msg.sessionId });
          break;
        case 'relay:message':
          this._emit('message', { sessionId: msg.sessionId, text: msg.text, timestamp: msg.timestamp });
          break;
        case 'relay:client-disconnected':
          this.sessionId = null;
          this._emit('client-disconnected', { sessionId: msg.sessionId });
          break;
        case 'relay:error':
          this._emit('error', { error: msg.error });
          break;
      }
    });

    this.ws.on('close', () => {
      this._emit('disconnected');
      this._tryReconnect();
    });

    this.ws.on('error', (err) => {
      this._emit('error', { error: err.message });
    });
  }

  sendMessage(text) {
    if (!this.sessionId) return;
    this._send({
      type: 'agent:message',
      sessionId: this.sessionId,
      text,
    });
  }

  sendTyping(active) {
    if (!this.sessionId) return;
    this._send({
      type: 'agent:typing',
      sessionId: this.sessionId,
      active,
    });
  }

  disconnect() {
    this._shouldReconnect = false;
    if (this.ws) this.ws.close();
  }

  _send(obj) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(obj));
    }
  }

  _tryReconnect() {
    if (!this._shouldReconnect) return;
    const delay = RECONNECT_DELAYS[this._reconnectAttempt] || RECONNECT_DELAYS[RECONNECT_DELAYS.length - 1];
    this._reconnectAttempt++;
    this._emit('reconnecting', { attempt: this._reconnectAttempt, delay });
    setTimeout(() => this.connect(), delay);
  }
}

module.exports = { RelayClient };
