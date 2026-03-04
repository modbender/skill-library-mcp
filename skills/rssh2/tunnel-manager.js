import ssh2 from 'ssh2';
import { EventEmitter } from 'events';
import net from 'net';

/**
 * 隧道管理器
 * 支持本地端口转发、远程端口转发、动态端口转发（SOCKS）
 */
export class TunnelManager extends EventEmitter {
  constructor(sessionManager) {
    super();
    this.sessionManager = sessionManager;
    this.tunnels = new Map();
    this.nextTunnelId = 1;
  }

  /**
   * 创建本地端口转发
   * localPort -> remoteHost:remotePort
   */
  async local(config, options = {}) {
    const opts = {
      localPort: config.localPort,
      remoteHost: config.remoteHost || 'localhost',
      remotePort: config.remotePort,
      localHost: config.localHost || '127.0.0.1',
      autoReconnect: false,
      reconnectDelay: 5000,
      ...options
    };

    const tunnelId = this.nextTunnelId++;
    const tunnel = {
      id: tunnelId,
      type: 'local',
      config: opts,
      client: null,
      server: null,
      connected: false
    };

    try {
      await this.setupLocalTunnel(tunnel);
      this.tunnels.set(tunnelId, tunnel);
      this.emit('tunnelCreated', tunnel);
      return tunnel;
    } catch (error) {
      this.emit('tunnelError', { tunnel, error });
      throw error;
    }
  }

  /**
   * 设置本地端口转发
   */
  async setupLocalTunnel(tunnel) {
    const conn = await this.sessionManager.getConnection();
    tunnel.client = conn.client;

    return new Promise((resolve, reject) => {
      tunnel.server = net.createServer((localSocket) => {
        conn.client.forwardOut(
          tunnel.config.remoteHost,
          tunnel.config.remotePort,
          tunnel.config.localHost,
          tunnel.config.localPort,
          (err, remoteSocket) => {
            if (err) {
              localSocket.end();
              return;
            }

            localSocket.pipe(remoteSocket);
            remoteSocket.pipe(localSocket);

            remoteSocket.on('close', () => localSocket.end());
            localSocket.on('close', () => remoteSocket.end());
          }
        );
      });

      tunnel.server.listen(tunnel.config.localPort, tunnel.config.localHost, () => {
        tunnel.connected = true;
        this.emit('tunnelConnected', tunnel);
        resolve();
      });

      tunnel.server.on('error', (err) => {
        this.emit('tunnelError', { tunnel, error: err });
        reject(err);
      });
    });
  }

  /**
   * 创建远程端口转发
   */
  async remote(config, options = {}) {
    const opts = {
      remotePort: config.remotePort,
      localHost: config.localHost || 'localhost',
      localPort: config.localPort,
      remoteHost: config.remoteHost || '0.0.0.0',
      ...options
    };

    const tunnelId = this.nextTunnelId++;
    const tunnel = {
      id: tunnelId,
      type: 'remote',
      config: opts,
      client: null,
      connected: false
    };

    try {
      await this.setupRemoteTunnel(tunnel);
      this.tunnels.set(tunnelId, tunnel);
      this.emit('tunnelCreated', tunnel);
      return tunnel;
    } catch (error) {
      this.emit('tunnelError', { tunnel, error });
      throw error;
    }
  }

  /**
   * 设置远程端口转发
   */
  async setupRemoteTunnel(tunnel) {
    const conn = await this.sessionManager.getConnection();
    tunnel.client = conn.client;

    return new Promise((resolve, reject) => {
      conn.client.forwardIn(tunnel.config.remotePort, tunnel.config.remoteHost, (err) => {
        if (err) {
          reject(err);
          return;
        }

        tunnel.connected = true;
        this.emit('tunnelConnected', tunnel);
        resolve();
      });
    });
  }

  /**
   * 创建动态端口转发（SOCKS代理）
   */
  async dynamic(config, options = {}) {
    const opts = {
      localPort: config.localPort,
      localHost: config.localHost || '127.0.0.1',
      ...options
    };

    const tunnelId = this.nextTunnelId++;
    const tunnel = {
      id: tunnelId,
      type: 'dynamic',
      config: opts,
      client: null,
      server: null,
      connected: false
    };

    try {
      await this.setupDynamicTunnel(tunnel);
      this.tunnels.set(tunnelId, tunnel);
      this.emit('tunnelCreated', tunnel);
      return tunnel;
    } catch (error) {
      this.emit('tunnelError', { tunnel, error });
      throw error;
    }
  }

  /**
   * 设置动态端口转发（SOCKS）
   */
  async setupDynamicTunnel(tunnel) {
    const conn = await this.sessionManager.getConnection();
    tunnel.client = conn.client;

    return new Promise((resolve, reject) => {
      tunnel.server = net.createServer((clientSocket) => {
        clientSocket.once('data', (data) => {
          if (data[0] !== 0x05) {
            clientSocket.end();
            return;
          }

          clientSocket.write(Buffer.from([0x05, 0x00]));

          clientSocket.once('data', (request) => {
            if (request[0] !== 0x05 || request[1] !== 0x01) {
              clientSocket.write(Buffer.from([0x05, 0x01]));
              clientSocket.end();
              return;
            }

            let targetHost, targetPort;
            const atyp = request[3];

            if (atyp === 0x01) {
              targetHost = `${request[4]}.${request[5]}.${request[6]}.${request[7]}`;
              targetPort = request.readUInt16BE(8);
            } else if (atyp === 0x03) {
              const domainLen = request[4];
              targetHost = request.slice(5, 5 + domainLen).toString();
              targetPort = request.readUInt16BE(5 + domainLen);
            } else {
              clientSocket.write(Buffer.from([0x05, 0x08]));
              clientSocket.end();
              return;
            }

            conn.client.forwardOut(
              targetHost,
              targetPort,
              '127.0.0.1',
              tunnel.config.localPort,
              (err, remoteSocket) => {
                if (err) {
                  clientSocket.write(Buffer.from([0x05, 0x01]));
                  clientSocket.end();
                  return;
                }

                const response = Buffer.alloc(10);
                response[0] = 0x05;
                response[1] = 0x00;
                response[3] = 0x01;
                clientSocket.write(response);

                clientSocket.pipe(remoteSocket);
                remoteSocket.pipe(clientSocket);

                remoteSocket.on('close', () => clientSocket.end());
                clientSocket.on('close', () => remoteSocket.end());
              }
            );
          });
        });
      });

      tunnel.server.listen(tunnel.config.localPort, tunnel.config.localHost, () => {
        tunnel.connected = true;
        this.emit('tunnelConnected', tunnel);
        resolve();
      });

      tunnel.server.on('error', (err) => {
        this.emit('tunnelError', { tunnel, error: err });
        reject(err);
      });
    });
  }

  /**
   * 关闭隧道
   */
  async close(tunnelId) {
    const tunnel = this.tunnels.get(tunnelId);
    if (!tunnel) return;

    if (tunnel.server) {
      tunnel.server.close();
    }

    this.tunnels.delete(tunnelId);
    this.emit('tunnelClosed', tunnel);
  }

  /**
   * 关闭所有隧道
   */
  async closeAll() {
    for (const [tunnelId] of this.tunnels) {
      await this.close(tunnelId);
    }
  }

  /**
   * 获取隧道列表
   */
  list() {
    return Array.from(this.tunnels.values());
  }

  /**
   * 获取统计信息
   */
  getStats() {
    return {
      totalTunnels: this.tunnels.size,
      localTunnels: this.list().filter(t => t.type === 'local').length,
      remoteTunnels: this.list().filter(t => t.type === 'remote').length,
      dynamicTunnels: this.list().filter(t => t.type === 'dynamic').length,
      connectedTunnels: this.list().filter(t => t.connected).length
    };
  }
}

export default TunnelManager;