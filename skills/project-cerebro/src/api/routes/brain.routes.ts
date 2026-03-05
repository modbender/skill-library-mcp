/**
 * Brain routes
 */

import { FastifyInstance } from 'fastify';
import { BrainService } from '../../services';

export function registerBrainRoutes(
  server: FastifyInstance,
  brainService: BrainService
): void {
  /**
   * POST /api/brains/:id/toggle
   * Toggle auto mode for a brain
   */
  server.post<{
    Params: { id: string };
    Body: { enabled: boolean };
  }>('/api/brains/:id/toggle', async (request, reply) => {
    const { id } = request.params;
    const { enabled } = request.body;

    await brainService.toggleAutoMode(id, enabled);

    return {
      success: true,
      brainId: id,
      autoMode: enabled,
    };
  });

  /**
   * POST /api/brains/:id/force-run
   * Force run a brain
   */
  server.post<{
    Params: { id: string };
  }>('/api/brains/:id/force-run', async (request, reply) => {
    const { id } = request.params;

    await brainService.forceRun(id);

    return {
      success: true,
      brainId: id,
    };
  });

  /**
   * GET /api/brains
   * Get all brains
   */
  server.get('/api/brains', async () => {
    const brains = brainService.getAllStates();
    return { brains };
  });

  /**
   * GET /api/brains/:id
   * Get specific brain
   */
  server.get<{
    Params: { id: string };
  }>('/api/brains/:id', async (request, reply) => {
    const { id } = request.params;
    const brain = brainService.get(id);
    return brain.getState();
  });
}
