/**
 * Tork Guardian — Scanner API helpers.
 *
 * Provides scanFromURL (fetches via HTTPS — no git/shell), scanFromSource
 * (writes temp files), and formatReportForAPI (strips local paths).
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import axios from 'axios';
import { SkillScanner } from './index';

const scanner = new SkillScanner();

// File extensions worth scanning
const SCAN_EXTENSIONS = new Set([
  '.js', '.ts', '.jsx', '.tsx', '.mjs', '.cjs',
  '.json', '.yaml', '.yml', '.toml',
]);

// Max files to download per repo (rate-limit guard)
const MAX_FILES = 200;
// Max individual file size in bytes
const MAX_FILE_SIZE = 500_000;

/**
 * Fetch a public GitHub repository over HTTPS and scan it.
 *
 * Uses the GitHub REST API (trees + raw contents) — no git clone,
 * no child_process, no shell commands.
 */
export async function scanFromURL(url: string) {
  // Strict validation: only GitHub HTTPS URLs
  const match = url.match(
    /^https?:\/\/github\.com\/([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+?)(?:\.git)?$/,
  );
  if (!match) {
    throw new Error(
      'Only GitHub HTTPS URLs are supported (e.g. https://github.com/owner/repo)',
    );
  }
  const [, owner, repo] = match;

  // 1. Fetch the default-branch tree recursively
  const { data: tree } = await axios.get(
    `https://api.github.com/repos/${owner}/${repo}/git/trees/HEAD?recursive=1`,
    { headers: { Accept: 'application/vnd.github.v3+json' }, timeout: 30_000 },
  );

  // 2. Filter to scannable source files
  const blobs = (tree.tree as Array<{ path: string; type: string; size: number }>)
    .filter(
      (entry) =>
        entry.type === 'blob' &&
        entry.size < MAX_FILE_SIZE &&
        SCAN_EXTENSIONS.has(path.extname(entry.path)),
    )
    .slice(0, MAX_FILES);

  // 3. Download each file via the raw-content endpoint
  const files: Record<string, string> = {};
  for (const blob of blobs) {
    try {
      const contentUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${blob.path
        .split('/')
        .map(encodeURIComponent)
        .join('/')}`;
      const { data } = await axios.get(contentUrl, {
        headers: { Accept: 'application/vnd.github.v3.raw' },
        timeout: 10_000,
        responseType: 'text',
      });
      files[blob.path] = typeof data === 'string' ? data : String(data);
    } catch {
      // Skip files that can't be fetched (binary, permissions, etc.)
    }
  }

  return scanFromSource(files, repo);
}

/**
 * Scan source code provided as a map of filename -> content strings.
 * Writes files to a temp directory, scans, and cleans up.
 */
export async function scanFromSource(
  files: Record<string, string>,
  skillName?: string,
) {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'tork-scan-src-'));
  try {
    for (const [filename, content] of Object.entries(files)) {
      const filePath = path.join(tmpDir, filename);
      const dir = path.dirname(filePath);
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(filePath, content);
    }
    const report = await scanner.scanSkill(tmpDir);
    if (skillName) {
      report.skillName = skillName;
    }
    return report;
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
}

/**
 * Strip absolute file paths from findings for public API responses.
 */
export function formatReportForAPI(report: ReturnType<typeof Object>) {
  return {
    skillName: (report as any).skillName,
    scannedAt: (report as any).scannedAt,
    filesScanned: (report as any).filesScanned,
    totalFindings: (report as any).totalFindings,
    findings: ((report as any).findings || []).map(stripFilePath),
    riskScore: (report as any).riskScore,
    verdict: (report as any).verdict,
    scanDurationMs: (report as any).scanDurationMs,
  };
}

function stripFilePath(finding: Record<string, unknown>) {
  return {
    ruleId: finding.ruleId,
    ruleName: finding.ruleName,
    severity: finding.severity,
    line: finding.line,
    column: finding.column,
    snippet: finding.snippet,
    description: finding.description,
    remediation: finding.remediation,
  };
}
