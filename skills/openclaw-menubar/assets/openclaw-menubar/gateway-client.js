/**
 * OpenClaw Gateway WebSocket Client
 * Connects to OpenClaw Gateway via WebSocket for real-time communication
 */

class GatewayClient {
    constructor(url, token = null) {
        this.url = url.replace(/^http/, 'ws'); // Convert http:// to ws://
        this.token = token;
        this.ws = null;
        this.connected = false;
        this.requestId = 0;
        this.pendingRequests = new Map();
        this.reconnectTimer = null;
        this.reconnectDelay = 1000;
        this.onMessage = null;
        this.onStatusChange = null;
    }

    connect() {
        return new Promise((resolve, reject) => {
            try {
                // Build WebSocket URL
                let wsUrl = `${this.url}/ws`;
                if (this.token) {
                    wsUrl += `?token=${encodeURIComponent(this.token)}`;
                }

                console.log('Connecting to:', wsUrl);
                this.ws = new WebSocket(wsUrl);

                this.ws.onopen = () => {
                    console.log('✅ WebSocket connected');
                    this.connected = true;
                    this.reconnectDelay = 1000;
                    if (this.onStatusChange) {
                        this.onStatusChange('connected');
                    }
                    resolve();
                };

                this.ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        this.handleMessage(data);
                    } catch (error) {
                        console.error('Failed to parse message:', error);
                    }
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    reject(error);
                };

                this.ws.onclose = () => {
                    console.log('WebSocket closed');
                    this.connected = false;
                    if (this.onStatusChange) {
                        this.onStatusChange('disconnected');
                    }
                    
                    // Auto-reconnect
                    this.scheduleReconnect();
                };

            } catch (error) {
                reject(error);
            }
        });
    }

    scheduleReconnect() {
        if (this.reconnectTimer) {
            return;
        }

        this.reconnectTimer = setTimeout(() => {
            this.reconnectTimer = null;
            console.log('Reconnecting...');
            this.connect().catch(err => {
                console.error('Reconnect failed:', err);
                this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
            });
        }, this.reconnectDelay);
    }

    handleMessage(data) {
        // Handle authentication challenge
        if (data.type === 'event' && data.event === 'connect.challenge') {
            this.handleAuthChallenge(data.payload);
            return;
        }

        // Handle RPC responses
        if (data.id && this.pendingRequests.has(data.id)) {
            const { resolve, reject } = this.pendingRequests.get(data.id);
            this.pendingRequests.delete(data.id);

            if (data.error) {
                reject(new Error(data.error));
            } else {
                resolve(data.result || data);
            }
            return;
        }

        // Handle push notifications / events
        if (this.onMessage) {
            this.onMessage(data);
        }
    }

    handleAuthChallenge(payload) {
        // Respond to authentication challenge
        const response = {
            type: 'auth',
            nonce: payload.nonce
        };

        if (this.token) {
            response.token = this.token;
        }

        this.ws.send(JSON.stringify(response));
        console.log('📝 Sent auth response');
    }

    async request(method, params = {}, timeoutMs = 120000) {
        if (!this.connected) {
            throw new Error('Not connected to gateway');
        }

        return new Promise((resolve, reject) => {
            const id = ++this.requestId;
            
            const timeout = setTimeout(() => {
                this.pendingRequests.delete(id);
                reject(new Error('Request timeout'));
            }, timeoutMs);

            this.pendingRequests.set(id, {
                resolve: (result) => {
                    clearTimeout(timeout);
                    resolve(result);
                },
                reject: (error) => {
                    clearTimeout(timeout);
                    reject(error);
                }
            });

            // Send RPC request
            this.ws.send(JSON.stringify({
                id,
                method,
                params
            }));
        });
    }

    async sendMessage(message, sessionKey = 'agent:main:main', options = {}) {
        return this.request('sessions/send', {
            sessionKey,
            message,
            deliver: false, // Don't deliver via channels
            ...options
        });
    }

    disconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }

        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        this.connected = false;
    }
}

module.exports = GatewayClient;
