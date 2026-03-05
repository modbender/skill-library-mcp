import http from 'node:http';
import type { ThrottleConfig } from '../config/types.js';
import type { DimensionWeights } from '../classifier/types.js';
import type { ModelRegistry, RoutingTable } from '../router/model-registry.js';
import type { LogWriter } from '../logging/writer.js';
import type { LogReader } from '../logging/reader.js';
import { createLogger } from '../utils/logger.js';
import {
  handleHealth,
  handleStats,
  handleMessages,
  handleChatCompletions,
  sendError,
  type HandlerDeps,
} from './http-handlers.js';

const log = createLogger('http-proxy');

const MAX_BODY_SIZE = 10 * 1024 * 1024; // 10MB

export interface HttpProxyDeps {
  config: ThrottleConfig;
  registry: ModelRegistry;
  weights: DimensionWeights;
  logWriter: LogWriter;
  logReader: LogReader;
  routingTable: RoutingTable;
}

export function createHttpProxy(deps: HttpProxyDeps): http.Server {
  const { config, registry, weights, logWriter, logReader, routingTable } = deps;

  const handlerDeps: HandlerDeps = { config, registry, weights, logWriter, logReader, routingTable };

  const server = http.createServer(async (req, res) => {
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, x-api-key, X-Throttle-Force-Model');
    res.setHeader('Access-Control-Expose-Headers', 'X-Throttle-Model, X-Throttle-Tier, X-Throttle-Score, X-Throttle-Request-Id');

    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
      res.writeHead(204);
      res.end();
      return;
    }

    const url = new URL(req.url ?? '/', `http://localhost:${config.http.port}`);
    const pathname = url.pathname;

    try {
      // GET routes
      if (req.method === 'GET') {
        if (pathname === '/health') {
          handleHealth(req, res, config);
          return;
        }
        if (pathname === '/stats') {
          handleStats(req, res, handlerDeps);
          return;
        }
        sendError(res, 404, 'not_found', `Unknown route: GET ${pathname}`);
        return;
      }

      // POST routes
      if (req.method === 'POST') {
        if (pathname !== '/v1/messages' && pathname !== '/v1/chat/completions') {
          sendError(res, 404, 'not_found', `Unknown route: POST ${pathname}`);
          return;
        }

        // Parse request body
        const body = await readBody(req);

        if (pathname === '/v1/messages') {
          await handleMessages(body, req, res, handlerDeps);
        } else {
          await handleChatCompletions(body, req, res, handlerDeps);
        }
        return;
      }

      sendError(res, 405, 'method_not_allowed', `Method ${req.method} not allowed`);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      log.error(`Request error: ${req.method} ${pathname}`, err);

      if (message.includes('API error')) {
        sendError(res, 502, 'upstream_error', message);
      } else if (message.includes('Missing') || message.includes('empty')) {
        sendError(res, 400, 'invalid_request_error', message);
      } else if (message.includes('too large')) {
        sendError(res, 413, 'request_too_large', message);
      } else {
        sendError(res, 500, 'internal_error', message);
      }
    }
  });

  return server;
}

function readBody(req: http.IncomingMessage): Promise<Record<string, unknown>> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    let size = 0;

    req.on('data', (chunk: Buffer) => {
      size += chunk.length;
      if (size > MAX_BODY_SIZE) {
        req.destroy();
        reject(new Error(`Request body too large (max ${MAX_BODY_SIZE} bytes)`));
        return;
      }
      chunks.push(chunk);
    });

    req.on('end', () => {
      try {
        const raw = Buffer.concat(chunks).toString('utf-8');
        if (!raw.trim()) {
          reject(new Error('Missing request body'));
          return;
        }
        resolve(JSON.parse(raw) as Record<string, unknown>);
      } catch {
        reject(new Error('Invalid JSON in request body'));
      }
    });

    req.on('error', reject);
  });
}
