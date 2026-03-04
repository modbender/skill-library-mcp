/**
 * Upload routes
 */

import { FastifyInstance } from 'fastify';
import * as fs from 'fs';
import * as path from 'path';
import { logger } from '../../lib/logger';

export function registerUploadRoutes(server: FastifyInstance): void {
  /**
   * POST /api/upload
   * Upload a file to a brain's intake directory
   */
  server.post('/api/upload', async (request, reply) => {
    const data = await request.file();
    
    if (!data) {
      reply.code(400);
      return { error: 'No file uploaded' };
    }

    // Try to get brainId from fields or body
    let brainId = 'default';
    
    // Check multipart fields
    if (data.fields?.brainId) {
      brainId = (data.fields.brainId as any).value;
    }
    
    // Fallback to query param or default
    const queryBrainId = (request.query as any)?.brainId;
    if (queryBrainId) {
      brainId = queryBrainId;
    }

    const safeBrain = brainId.replace(/[^a-zA-Z0-9_-]/g, '') || 'default';
    const intakeDir = path.join(process.cwd(), 'data', safeBrain, 'intake');
    
    logger.info('File upload request', { 
      filename: data.filename, 
      brainId: safeBrain, 
      targetDir: intakeDir,
      fields: Object.keys(data.fields || {})
    });
    
    if (!fs.existsSync(intakeDir)) {
      fs.mkdirSync(intakeDir, { recursive: true });
      logger.info('Created intake directory', { intakeDir });
    }

    const filename = data.filename || `upload-${Date.now()}`;
    const outPath = path.join(intakeDir, filename);
    await fs.promises.writeFile(outPath, await data.toBuffer());

    logger.info('File uploaded successfully', { outPath, brainId: safeBrain });

    return {
      success: true,
      brainId: safeBrain,
      path: outPath,
      filename,
    };
  });
}
