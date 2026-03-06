/**
 * Job Applications routes
 */

import { FastifyInstance } from 'fastify';
import {
  JobApplicationsRepository,
  CreateJobApplicationInput,
  JobApplicationStatus,
} from '../../data/repositories/job-applications.repository';

export function registerJobApplicationsRoutes(
  server: FastifyInstance,
  jobApplicationsRepo: JobApplicationsRepository
): void {
  /**
   * GET /api/job-applications
   * Get all job applications
   */
  server.get<{ Querystring: { status?: JobApplicationStatus; limit?: string } }>(
    '/api/job-applications',
    async (request) => {
      const { status, limit } = request.query;
      const applications = jobApplicationsRepo.getAll({
        status,
        limit: limit ? parseInt(limit) : undefined,
      });
      return { applications };
    }
  );

  /**
   * GET /api/job-applications/stats
   * Get job application statistics
   */
  server.get('/api/job-applications/stats', async () => {
    const stats = jobApplicationsRepo.getStats();
    return { stats };
  });

  /**
   * GET /api/job-applications/follow-ups
   * Get pending follow-ups
   */
  server.get('/api/job-applications/follow-ups', async () => {
    const followUps = jobApplicationsRepo.getPendingFollowUps();
    return { followUps };
  });

  /**
   * GET /api/job-applications/:id
   * Get job application by ID
   */
  server.get<{ Params: { id: string } }>(
    '/api/job-applications/:id',
    async (request, reply) => {
      const { id } = request.params;
      const application = jobApplicationsRepo.getById(id);
      if (!application) {
        reply.code(404);
        return { error: 'Job application not found' };
      }
      return application;
    }
  );

  /**
   * GET /api/job-applications/by-job-id/:jobId
   * Get job application by external job ID
   */
  server.get<{ Params: { jobId: string } }>(
    '/api/job-applications/by-job-id/:jobId',
    async (request, reply) => {
      const { jobId } = request.params;
      const application = jobApplicationsRepo.getByJobId(jobId);
      if (!application) {
        reply.code(404);
        return { error: 'Job application not found' };
      }
      return application;
    }
  );

  /**
   * POST /api/job-applications
   * Create a job application
   */
  server.post<{ Body: CreateJobApplicationInput }>(
    '/api/job-applications',
    async (request, reply) => {
      const input = request.body;
      if (!input.company || !input.position) {
        reply.code(400);
        return { error: 'Missing required fields: company, position' };
      }

      // Check for duplicates
      if (jobApplicationsRepo.exists(input.jobId, input.company, input.position)) {
        reply.code(409);
        return { error: 'Job application already exists' };
      }

      const application = jobApplicationsRepo.create(input);
      return application;
    }
  );

  /**
   * PATCH /api/job-applications/:id
   * Update a job application
   */
  server.patch<{ Params: { id: string }; Body: Partial<CreateJobApplicationInput & { status: JobApplicationStatus }> }>(
    '/api/job-applications/:id',
    async (request, reply) => {
      const { id } = request.params;
      const updates = request.body;
      const application = jobApplicationsRepo.update(id, updates);
      if (!application) {
        reply.code(404);
        return { error: 'Job application not found' };
      }
      return application;
    }
  );

  /**
   * POST /api/job-applications/:id/apply
   * Mark job as applied (sets status, appliedAt, followUpAt)
   */
  server.post<{ Params: { id: string }; Body?: { followUpDays?: number } }>(
    '/api/job-applications/:id/apply',
    async (request, reply) => {
      const { id } = request.params;
      const followUpDays = request.body?.followUpDays ?? 3;
      const application = jobApplicationsRepo.markApplied(id, followUpDays);
      if (!application) {
        reply.code(404);
        return { error: 'Job application not found' };
      }
      return application;
    }
  );

  /**
   * DELETE /api/job-applications/:id
   * Delete a job application
   */
  server.delete<{ Params: { id: string } }>(
    '/api/job-applications/:id',
    async (request, reply) => {
      const { id } = request.params;
      const deleted = jobApplicationsRepo.delete(id);
      if (!deleted) {
        reply.code(404);
        return { error: 'Job application not found' };
      }
      return { success: true };
    }
  );
}
