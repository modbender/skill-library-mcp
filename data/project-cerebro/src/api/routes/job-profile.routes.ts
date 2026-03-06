/**
 * Job Profile routes - manage user's job search profile
 */

import { FastifyInstance } from 'fastify';
import * as fs from 'fs';
import * as path from 'path';
import { logger } from '../../lib/logger';

const PROFILE_PATH = path.join(process.cwd(), 'data', 'job_profile.json');

export function registerJobProfileRoutes(server: FastifyInstance): void {
  /**
   * GET /api/job-profile
   * Get the user's job profile
   */
  server.get('/api/job-profile', async () => {
    try {
      if (!fs.existsSync(PROFILE_PATH)) {
        return { profile: null };
      }
      const data = fs.readFileSync(PROFILE_PATH, 'utf-8');
      return { profile: JSON.parse(data) };
    } catch (error) {
      logger.error('Failed to read job profile', error as Error);
      return { profile: null };
    }
  });

  /**
   * POST /api/job-profile
   * Save the user's job profile
   */
  server.post<{ Body: { profile: any } }>(
    '/api/job-profile',
    async (request, reply) => {
      try {
        const { profile } = request.body;
        
        // Ensure data directory exists
        const dataDir = path.dirname(PROFILE_PATH);
        if (!fs.existsSync(dataDir)) {
          fs.mkdirSync(dataDir, { recursive: true });
        }
        
        fs.writeFileSync(PROFILE_PATH, JSON.stringify(profile, null, 2));
        logger.info('Job profile saved');
        return { success: true };
      } catch (error) {
        logger.error('Failed to save job profile', error as Error);
        reply.code(500);
        return { error: 'Failed to save profile' };
      }
    }
  );
}
