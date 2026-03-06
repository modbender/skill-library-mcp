/**
 * Request logger middleware
 */

import { FastifyRequest, FastifyReply } from 'fastify';
import { logger } from '../../lib/logger';

export async function requestLogger(
  request: FastifyRequest,
  reply: FastifyReply
): Promise<void> {
  const start = Date.now();

  reply.raw.on('finish', () => {
    const duration = Date.now() - start;
    logger.info('HTTP request', {
      method: request.method,
      url: request.url,
      statusCode: reply.statusCode,
      duration,
      ip: request.ip,
    });
  });
}
