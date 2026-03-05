/**
 * Report routes
 */

import { FastifyInstance } from 'fastify';
import { ReportService, ReportKind } from '../../services';
import * as fs from 'fs';
import * as path from 'path';

export function registerReportRoutes(
  server: FastifyInstance,
  reportService: ReportService
): void {
  /**
   * GET /api/reports
   * Get reports for a brain
   */
  server.get<{
    Querystring: {
      brainId: string;
      limit?: number;
    };
  }>('/api/reports', async (request, reply) => {
    const { brainId, limit = 10 } = request.query;

    if (!brainId) {
      reply.code(400);
      return { error: 'brainId is required' };
    }

    const safeBrain = brainId.replace(/[^a-zA-Z0-9_-]/g, '');
    const reportsDir = path.join(process.cwd(), 'data', safeBrain, 'reports');
    const maxLimit = Math.max(1, Math.min(50, Number(limit)));

    let files: string[] = [];
    try {
      files = await fs.promises.readdir(reportsDir);
    } catch {
      return { reports: [] };
    }

    const items = await Promise.all(
      files
        .filter((f) => f.endsWith('.md'))
        .map(async (f) => {
          const full = path.join(reportsDir, f);
          const stat = await fs.promises.stat(full);
          const match = f.match(/(\d{4}-\d{2}-\d{2})-(morning|night)\.md/);

          if (!match) return null;

          const content = await fs.promises.readFile(full, 'utf-8');
          return {
            date: match[1],
            kind: match[2] as ReportKind,
            content,
            mtime: stat.mtime.toISOString(),
          };
        })
    );

    const reports = items
      .filter((r) => r !== null)
      .sort((a: any, b: any) => (a.mtime < b.mtime ? 1 : -1))
      .slice(0, maxLimit);

    return { reports };
  });

  /**
   * GET /api/reports/:brainId/:date/:kind
   * Get specific report
   */
  server.get<{
    Params: {
      brainId: string;
      date: string;
      kind: ReportKind;
    };
  }>('/api/reports/:brainId/:date/:kind', async (request, reply) => {
    const { brainId, date, kind } = request.params;
    const content = await reportService.readReport(brainId, kind, date);

    if (!content) {
      reply.code(404);
      return { error: 'Report not found' };
    }

    return { brainId, date, kind, content };
  });
}
