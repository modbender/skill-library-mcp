/**
 * Status routes
 */

import { FastifyInstance } from 'fastify';
import { BrainService } from '../../services';

export function registerStatusRoutes(
  server: FastifyInstance,
  brainService: BrainService
): void {
  /**
   * GET /api/status
   * Get system status and brain states
   */
  server.get('/api/status', async () => {
    const brains = brainService.getAllStates();

    return {
      status: 'online',
      timestamp: Date.now(),
      brains,
    };
  });

  /**
   * GET /api/health
   * Health check endpoint
   */
  server.get('/api/health', async () => {
    return {
      status: 'healthy',
      timestamp: Date.now(),
    };
  });
}
