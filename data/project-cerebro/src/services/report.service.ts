/**
 * Report service - handles report generation for brains
 */

import * as fs from 'fs';
import * as path from 'path';
import { logger } from '../lib/logger';
import { format, toZonedTime } from 'date-fns-tz';

export type ReportKind = 'morning' | 'night';

const REPORT_TZ = 'America/Chicago';
function localIsoDate(d: Date): string {
  return format(toZonedTime(d, REPORT_TZ), 'yyyy-MM-dd', { timeZone: REPORT_TZ });
}
function localTime(d: Date): string {
  return format(toZonedTime(d, REPORT_TZ), 'h:mm:ss a', { timeZone: REPORT_TZ });
}

export interface Report {
  brainId: string;
  kind: ReportKind;
  date: string;
  content: string;
  timestamp: number;
}

export class ReportService {
  private basePath: string;

  constructor(basePath: string = path.join(process.cwd(), 'data')) {
    this.basePath = basePath;
  }

  /**
   * Write a report for a brain
   */
  async writeReport(brainId: string, kind: ReportKind, content: string, date?: string): Promise<void> {
    const reportDate = date || localIsoDate(new Date());
    const reportsPath = path.join(this.basePath, brainId, 'reports');
    
    // Ensure directory exists
    await fs.promises.mkdir(reportsPath, { recursive: true });

    const reportFile = path.join(reportsPath, `${reportDate}-${kind}.md`);
    const timestamp = localTime(new Date());
    const entry = `\n\n---\n[${timestamp}] ${kind.toUpperCase()} RUN\n\n${content}\n`;

    try {
      // Check if file exists
      await fs.promises.access(reportFile, fs.constants.F_OK);
      // Append to existing file
      await fs.promises.appendFile(reportFile, entry);
    } catch {
      // Create new file
      const header = `# ${reportDate} ${kind.toUpperCase()} REPORTS\n`;
      await fs.promises.writeFile(reportFile, header + entry.trimStart());
    }

    logger.info('Report written', { brainId, kind, date: reportDate });
  }

  /**
   * Read a report for a brain
   */
  async readReport(brainId: string, kind: ReportKind, date?: string): Promise<string> {
    const reportDate = date || localIsoDate(new Date());
    const reportFile = path.join(this.basePath, brainId, 'reports', `${reportDate}-${kind}.md`);

    try {
      return await fs.promises.readFile(reportFile, 'utf-8');
    } catch {
      return '';
    }
  }

  /**
   * Read all reports for a brain on a specific date
   */
  async readReportsForDate(brainId: string, date?: string): Promise<Report[]> {
    const reportDate = date || localIsoDate(new Date());
    const reports: Report[] = [];

    for (const kind of ['morning', 'night'] as const) {
      const content = await this.readReport(brainId, kind, reportDate);
      if (content && content.trim().length > 0) {
        reports.push({
          brainId,
          kind,
          date: reportDate,
          content,
          timestamp: Date.now(),
        });
      }
    }

    return reports;
  }

  /**
   * Get all reports for a date across all brains
   */
  async getAllReportsForDate(brainIds: string[], date?: string): Promise<Report[]> {
    const reportDate = date || localIsoDate(new Date());
    const allReports: Report[] = [];

    for (const brainId of brainIds) {
      const reports = await this.readReportsForDate(brainId, reportDate);
      allReports.push(...reports);
    }

    return allReports;
  }
}
