import WebSocket, { WebSocketServer } from 'ws';
import { EventEmitter } from 'events';

export class Transport extends EventEmitter {
  private server: WebSocketServer | null = null;
  private connections = new Map<string, WebSocket>();

  async listen(port: number, host: string = '0.0.0.0'): Promise<void> {
    return new Promise((resolve, reject) => {
      this.server = new WebSocketServer({ port, host }, () => resolve());
      this.server.on('error', reject);
      this.server.on('connection', (ws) => {
        ws.on('message', (data) => {
          this.emit('data', data.toString(), ws);
        });
      });
    });
  }

  async connect(address: string): Promise<WebSocket> {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(`ws://${address}`);
      ws.on('open', () => {
        this.connections.set(address, ws);
        ws.on('message', (data) => {
          this.emit('data', data.toString(), ws);
        });
        resolve(ws);
      });
      ws.on('error', reject);
    });
  }

  send(ws: WebSocket, data: string): void {
    if (ws.readyState === WebSocket.OPEN) ws.send(data);
  }

  registerSocket(id: string, ws: WebSocket): void {
    this.connections.set(id, ws);
  }

  getSocket(id: string): WebSocket | undefined {
    return this.connections.get(id);
  }

  async close(): Promise<void> {
    for (const ws of this.connections.values()) ws.close();
    this.connections.clear();
    if (this.server) {
      await new Promise<void>((r) => this.server!.close(() => r()));
      this.server = null;
    }
  }
}
