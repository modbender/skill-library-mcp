/**
 * Brains CRUD routes
 */

import { FastifyInstance } from 'fastify';
import { BrainsRepository, CreateBrainInput } from '../../data/repositories/brains.repository';

export function registerBrainsCrudRoutes(
  server: FastifyInstance,
  brainsRepo: BrainsRepository
): void {
  /**
   * GET /api/brains-db
   * Get all brains from DB
   */
  server.get('/api/brains-db', async () => {
    const brains = brainsRepo.getAll();
    return { brains };
  });

  /**
   * GET /api/brains-db/:id
   * Get brain by ID
   */
  server.get<{ Params: { id: string } }>(
    '/api/brains-db/:id',
    async (request, reply) => {
      const { id } = request.params;
      const brain = brainsRepo.getById(id);
      if (!brain) {
        reply.code(404);
        return { error: 'Brain not found' };
      }
      return brain;
    }
  );

  /**
   * POST /api/brains-db
   * Create a new brain
   */
  server.post<{ Body: CreateBrainInput }>(
    '/api/brains-db',
    async (request, reply) => {
      const input = request.body;
      if (!input.id || !input.name || !input.channelKey) {
        reply.code(400);
        return { error: 'Missing required fields: id, name, channelKey' };
      }
      const existing = brainsRepo.getById(input.id);
      if (existing) {
        reply.code(409);
        return { error: 'Brain with this ID already exists' };
      }
      const brain = brainsRepo.create(input);
      return brain;
    }
  );

  /**
   * PATCH /api/brains-db/:id
   * Update a brain
   */
  server.patch<{ Params: { id: string }; Body: Partial<CreateBrainInput> }>(
    '/api/brains-db/:id',
    async (request, reply) => {
      const { id } = request.params;
      const updates = request.body;
      const brain = brainsRepo.update(id, updates);
      if (!brain) {
        reply.code(404);
        return { error: 'Brain not found' };
      }
      return brain;
    }
  );

  /**
   * DELETE /api/brains-db/:id
   * Delete a brain
   */
  server.delete<{ Params: { id: string } }>(
    '/api/brains-db/:id',
    async (request, reply) => {
      const { id } = request.params;
      const deleted = brainsRepo.delete(id);
      if (!deleted) {
        reply.code(404);
        return { error: 'Brain not found' };
      }
      return { success: true };
    }
  );
}
