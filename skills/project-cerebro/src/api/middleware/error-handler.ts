/**
 * Error handler middleware
 */

import { FastifyError, FastifyReply, FastifyRequest } from 'fastify';
import { logger } from '../../lib/logger';
import { CerebroError } from '../../lib/errors';

export async function errorHandler(
  error: FastifyError | Error,
  request: FastifyRequest,
  reply: FastifyReply
): Promise<void> {
  // Log the error
  logger.error('Request error', error, {
    method: request.method,
    url: request.url,
    params: request.params,
  });

  // Handle CerebroError
  if (error instanceof CerebroError) {
    reply.code(error.statusCode).send({
      error: {
        code: error.code,
        message: error.message,
        context: error.context,
      },
    });
    return;
  }

  // Handle Fastify validation errors
  if ('validation' in error) {
    reply.code(400).send({
      error: {
        code: 'VALIDATION_ERROR',
        message: error.message,
        validation: (error as any).validation,
      },
    });
    return;
  }

  // Default error response
  reply.code(500).send({
    error: {
      code: 'INTERNAL_ERROR',
      message: 'Internal server error',
    },
  });
}
