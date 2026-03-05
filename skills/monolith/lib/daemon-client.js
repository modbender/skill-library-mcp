import net from 'node:net';
import { SOCKET_PATH } from './constants.js';

/**
 * Unix socket HTTP client for the Monolith daemon.
 */
export class DaemonClient {
  constructor(socketPath = SOCKET_PATH) {
    this.socketPath = socketPath;
  }

  /**
   * Send a request to the daemon and return the parsed response.
   * @param {string} method - HTTP method (GET, POST)
   * @param {string} path - Request path (e.g., /sign)
   * @param {object} [body] - JSON body for POST requests
   * @returns {Promise<{status: number, data: object}>}
   */
  async request(method, path, body = null) {
    return new Promise((resolve, reject) => {
      const socket = net.createConnection({ path: this.socketPath });
      let responseData = '';

      socket.on('connect', () => {
        let request = `${method} ${path} HTTP/1.1\r\n`;
        request += 'Host: localhost\r\n';

        if (body) {
          const bodyStr = JSON.stringify(body);
          request += 'Content-Type: application/json\r\n';
          request += `Content-Length: ${Buffer.byteLength(bodyStr)}\r\n`;
          request += '\r\n';
          request += bodyStr;
        } else {
          request += '\r\n';
        }

        socket.write(request);
      });

      socket.on('data', (data) => {
        responseData += data.toString();
      });

      socket.on('end', () => {
        try {
          const parsed = parseHTTPResponse(responseData);
          resolve(parsed);
        } catch (err) {
          reject(new Error(`Failed to parse daemon response: ${err.message}`));
        }
      });

      socket.on('error', (err) => {
        if (err.code === 'ENOENT') {
          reject(
            new Error(
              'Daemon not running. Start the Monolith daemon first.'
            )
          );
        } else if (err.code === 'ECONNREFUSED') {
          reject(new Error('Daemon refused connection. Check daemon status.'));
        } else {
          reject(new Error(`Daemon connection error: ${err.message}`));
        }
      });

      socket.setTimeout(30000, () => {
        socket.destroy();
        reject(new Error('Daemon request timed out'));
      });
    });
  }

  // Convenience methods
  async health() {
    return this.request('GET', '/health');
  }

  async capabilities() {
    return this.request('GET', '/capabilities');
  }

  async address() {
    return this.request('GET', '/address');
  }

  async policy() {
    return this.request('GET', '/policy');
  }

  async decode(intent) {
    return this.request('POST', '/decode', intent);
  }

  async sign(intent) {
    return this.request('POST', '/sign', intent);
  }

  async panic() {
    return this.request('POST', '/panic');
  }

  async auditLog() {
    return this.request('GET', '/audit-log');
  }

  async policyUpdate(changes) {
    return this.request('POST', '/policy/update', changes);
  }

  async allowlistUpdate(changes) {
    return this.request('POST', '/allowlist', changes);
  }

  async setup(params) {
    return this.request('POST', '/setup', params);
  }

  async setupDeploy() {
    return this.request('POST', '/setup/deploy');
  }
}

/**
 * Parse a raw HTTP response string.
 */
function parseHTTPResponse(raw) {
  const headerEnd = raw.indexOf('\r\n\r\n');
  if (headerEnd === -1) {
    throw new Error('Invalid HTTP response');
  }

  const headerPart = raw.substring(0, headerEnd);
  const bodyPart = raw.substring(headerEnd + 4);

  const statusLine = headerPart.split('\r\n')[0];
  const statusMatch = statusLine.match(/HTTP\/[\d.]+ (\d+)/);
  const status = statusMatch ? parseInt(statusMatch[1], 10) : 0;

  let data = null;
  if (bodyPart.trim()) {
    try {
      data = JSON.parse(bodyPart);
    } catch {
      data = { raw: bodyPart };
    }
  }

  return { status, data };
}

// Default singleton
export const daemon = new DaemonClient();
