import path from 'node:path';
import crypto from 'node:crypto';
import YAML from 'yaml';

import {
  VettingReport,
  VettingConfig,
  SkillManifest,
  Finding,
  FindingCategory,
  NetworkCall,
  ToolsInterface,
} from './types.js';
import { AstAnalyzer } from './analyzers/ast-analyzer.js';
import { PatternAnalyzer } from './analyzers/pattern-analyzer.js';
import { MetadataAnalyzer } from './analyzers/metadata-analyzer.js';
import { DependencyAnalyzer } from './analyzers/dependency-analyzer.js';
import { sanitisePath, getAllowedRoots, truncateEvidence } from './utils/sanitise.js';
import { parseVettrignore, isExcluded } from './utils/vettrignore.js';

const VERSION = '2.0.3';

const TEXT_EXTENSIONS = new Set([
  '.ts', '.js', '.mjs', '.cjs', '.mts', '.cts', '.jsx', '.tsx',
  '.json', '.md', '.yaml', '.yml', '.txt',
]);

const CODE_EXTENSIONS = new Set(['.ts', '.js', '.mjs', '.cjs', '.mts', '.cts', '.jsx', '.tsx']);

const CATEGORY_WEIGHTS: Record<FindingCategory, number> = {
  PROMPT_INJECTION: 1.5,
  CODE_OBFUSCATION: 1.5,
  SHELL_INJECTION: 1.3,
  PERMISSION_RISK: 1.0,
  NETWORK_RISK: 0.5,
  DEPENDENCY_RISK: 1.2,
  TYPO_SQUATTING: 1.0,
  PATH_TRAVERSAL: 0.8,
};

export class VettrEngine {
  private config: VettingConfig;
  private astAnalyzer: AstAnalyzer;
  private patternAnalyzer: PatternAnalyzer;
  private metadataAnalyzer: MetadataAnalyzer;
  private dependencyAnalyzer: DependencyAnalyzer;

  constructor(config: VettingConfig) {
    this.config = config;
    this.astAnalyzer = new AstAnalyzer();
    this.patternAnalyzer = new PatternAnalyzer();
    this.metadataAnalyzer = new MetadataAnalyzer();
    this.dependencyAnalyzer = new DependencyAnalyzer();
  }

  async vetSkill(skillPath: string, tools: ToolsInterface): Promise<VettingReport> {
    const resolvedPath = sanitisePath(skillPath, getAllowedRoots({ allowCwd: this.config.allowCwd }));

    const stats = await tools.stat(resolvedPath);
    if (!stats.isDirectory()) {
      throw new Error('Skill path must be a directory');
    }

    // Initialise AST analyser (loads WASM grammars)
    await this.astAnalyzer.init();

    const findings: Finding[] = [];
    let fileCount = 0;
    let totalLines = 0;
    const networkCalls: NetworkCall[] = [];
    let manifest: SkillManifest = { name: 'unknown', version: '0.0.0' };

    // Load .vettrignore if present
    const { patterns: ignorePatterns, findings: ignoreFindings } =
      await this.loadVettrignore(resolvedPath, tools);
    findings.push(...ignoreFindings);

    const files = await this.collectFiles(resolvedPath, tools, undefined, ignorePatterns);

    for (const file of files) {
      if (file.includes('node_modules')) continue;

      const ext = path.extname(file).toLowerCase();

      // Skip binary files
      if (!TEXT_EXTENSIONS.has(ext)) continue;

      let content: string;
      try {
        content = await tools.readFile(file);
      } catch {
        continue;
      }

      fileCount++;
      totalLines += content.split('\n').length;

      // Code files: AST analysis + regex for non-structural patterns
      if (CODE_EXTENSIONS.has(ext)) {
        const astFindings = this.astAnalyzer.analyze(file, content, ext);
        findings.push(...astFindings);

        const regexFindings = this.patternAnalyzer.analyze(file, content);
        findings.push(...regexFindings);

        // Extract network calls via AST
        const calls = this.astAnalyzer.extractNetworkCalls(file, content, ext);
        for (const call of calls) {
          const allowed = this.isHostAllowed(call.url);
          networkCalls.push({ url: call.url, file, line: call.line, allowed });

          if (!allowed) {
            findings.push({
              id: crypto.randomBytes(8).toString('hex'),
              severity: 'WARNING',
              category: 'NETWORK_RISK',
              message: 'Network call to non-whitelisted host',
              file,
              line: call.line,
              evidence: truncateEvidence(call.url),
            });
          }
        }
      }

      // package.json
      if (file.endsWith('package.json')) {
        try {
          const pkg = JSON.parse(content) as Record<string, unknown>;
          const depFindings = this.dependencyAnalyzer.analyze(pkg, resolvedPath, this.config);
          findings.push(...depFindings);
        } catch {
          findings.push({
            id: crypto.randomBytes(8).toString('hex'),
            severity: 'WARNING',
            category: 'CODE_OBFUSCATION',
            message: 'Malformed package.json',
            file,
            evidence: truncateEvidence(content, 50),
          });
        }
      }

      // SKILL.md (case-insensitive for Windows compatibility)
      if (file.toLowerCase().endsWith('skill.md')) {
        manifest = this.parseSkillManifest(content, file, findings);
        const metaFindings = this.metadataAnalyzer.analyze(manifest, resolvedPath, this.config);
        findings.push(...metaFindings);
      }
    }

    const riskScore = this.calculateRiskScore(findings, networkCalls);
    const riskLevel = this.getRiskLevel(riskScore);
    const checksumSha256 = await this.calculateChecksum(files, tools, resolvedPath);

    return {
      skillName: manifest.name || path.basename(resolvedPath),
      riskScore,
      riskLevel,
      findings: this.deduplicateFindings(findings),
      metadata: {
        authorVerified: !findings.some(
          (f) => f.category === 'PERMISSION_RISK' && f.message.includes('author'),
        ),
        hasExternalDeps: findings.some((f) => f.category === 'DEPENDENCY_RISK'),
        networkCalls,
        fileCount,
        totalLines,
        checksumSha256,
      },
      recommendation: this.getRecommendation(riskScore, findings),
      vettedAt: new Date().toISOString(),
      vettrVersion: VERSION,
    };
  }

  private async collectFiles(
    dir: string,
    tools: ToolsInterface,
    rootDir?: string,
    ignorePatterns?: string[],
  ): Promise<string[]> {
    const results: string[] = [];
    const entries = await tools.readdir(dir);
    const effectiveRoot = rootDir ?? dir;

    for (const entry of entries) {
      if (entry.startsWith('.')) continue;
      if (entry === 'node_modules') continue;

      const fullPath = path.join(dir, entry);

      try {
        // Use lstat to detect symlinks without following them
        const stats = await tools.lstat(fullPath);

        // Skip symlinks entirely to prevent escape attacks
        if (stats.isSymbolicLink()) {
          continue;
        }

        // Verify path stays within root directory (defense in depth)
        // Use case-insensitive comparison on Windows
        const realPath = await tools.realpath(fullPath);
        const realRoot = await tools.realpath(effectiveRoot);
        const isWindows = process.platform === 'win32';
        const normalizedRealPath = isWindows ? realPath.toLowerCase() : realPath;
        const normalizedRealRoot = isWindows ? realRoot.toLowerCase() : realRoot;
        if (
          !normalizedRealPath.startsWith(normalizedRealRoot + path.sep) &&
          normalizedRealPath !== normalizedRealRoot
        ) {
          continue;
        }

        // Check vettrignore exclusion
        const relativePath = path.relative(effectiveRoot, fullPath);
        if (ignorePatterns && ignorePatterns.length > 0 && isExcluded(relativePath, ignorePatterns)) {
          continue;
        }

        if (stats.isDirectory()) {
          const subFiles = await this.collectFiles(fullPath, tools, effectiveRoot, ignorePatterns);
          results.push(...subFiles);
        } else if (stats.isFile()) {
          results.push(fullPath);
        }
      } catch {
        // Skip inaccessible paths
      }
    }

    return results;
  }

  private async loadVettrignore(
    skillPath: string,
    tools: ToolsInterface,
  ): Promise<{ patterns: string[]; findings: Finding[] }> {
    const ignorePath = path.join(skillPath, '.vettrignore');
    const findings: Finding[] = [];

    try {
      const content = await tools.readFile(ignorePath);
      const result = parseVettrignore(content);

      for (const warning of result.warnings) {
        findings.push({
          id: crypto.randomBytes(8).toString('hex'),
          severity: 'INFO',
          category: 'PERMISSION_RISK',
          message: `.vettrignore warning: ${warning}`,
          file: ignorePath,
          evidence: warning,
        });
      }

      return { patterns: result.patterns, findings };
    } catch {
      // .vettrignore missing or unreadable — scan everything
      // Only add a finding if the file exists but is unreadable
      try {
        await tools.stat(ignorePath);
        // File exists but readFile failed — unreadable
        findings.push({
          id: crypto.randomBytes(8).toString('hex'),
          severity: 'INFO',
          category: 'PERMISSION_RISK',
          message: 'Unreadable .vettrignore file; scanning all files',
          file: ignorePath,
          evidence: 'File exists but could not be read',
        });
      } catch {
        // File doesn't exist — no finding needed
      }

      return { patterns: [], findings };
    }
  }

  private parseSkillManifest(content: string, file: string, findings: Finding[]): SkillManifest {
    const match = content.match(/^---\n([\s\S]+?)\n---/);

    if (!match?.[1]) {
      findings.push({
        id: crypto.randomBytes(8).toString('hex'),
        severity: 'INFO',
        category: 'PERMISSION_RISK',
        message: 'No YAML frontmatter found in SKILL.md',
        file,
        evidence: 'Missing --- delimiters',
      });
      return { name: 'unknown', version: '0.0.0' };
    }

    try {
      const parsed = YAML.parse(match[1]) as Record<string, unknown>;
      return {
        name: typeof parsed['name'] === 'string' ? parsed['name'] : 'unknown',
        version: typeof parsed['version'] === 'string' ? parsed['version'] : '0.0.0',
        author: typeof parsed['author'] === 'string' ? parsed['author'] : undefined,
        description: typeof parsed['description'] === 'string' ? parsed['description'] : undefined,
        tools: Array.isArray(parsed['tools']) ? (parsed['tools'] as string[]) : undefined,
        permissions: Array.isArray(parsed['permissions'])
          ? (parsed['permissions'] as string[])
          : undefined,
      };
    } catch (err) {
      findings.push({
        id: crypto.randomBytes(8).toString('hex'),
        severity: 'WARNING',
        category: 'CODE_OBFUSCATION',
        message: 'Invalid YAML in SKILL.md frontmatter',
        file,
        evidence: err instanceof Error ? err.message : 'Parse error',
      });
      return { name: 'unknown', version: '0.0.0' };
    }
  }

  private isHostAllowed(url: string): boolean {
    try {
      const parsed = new URL(url);
      return this.config.allowedHosts.includes(parsed.hostname);
    } catch {
      return false;
    }
  }

  private calculateRiskScore(findings: Finding[], networkCalls: NetworkCall[]): number {
    let score = 0;

    for (const f of findings) {
      const categoryWeight = CATEGORY_WEIGHTS[f.category] ?? 1.0;
      switch (f.severity) {
        case 'CRITICAL':
          score += 25 * categoryWeight;
          break;
        case 'WARNING':
          score += 10 * categoryWeight;
          break;
        case 'INFO':
          score += 2 * categoryWeight;
          break;
      }
    }

    const disallowedCalls = networkCalls.filter((c) => !c.allowed).length;
    score += disallowedCalls * 5;

    const excessCalls = Math.max(0, networkCalls.length - this.config.maxNetworkCalls);
    score += excessCalls * 3;

    return Math.min(100, Math.round(score));
  }

  private getRiskLevel(score: number): VettingReport['riskLevel'] {
    if (score === 0) return 'SAFE';
    if (score < 20) return 'LOW';
    if (score < 40) return 'MEDIUM';
    if (score < 70) return 'HIGH';
    return 'CRITICAL';
  }

  private getRecommendation(
    score: number,
    findings: Finding[],
  ): VettingReport['recommendation'] {
    const hasCritical = findings.some((f) => f.severity === 'CRITICAL');
    if (hasCritical || score >= this.config.maxRiskScore) {
      return 'BLOCK';
    }

    if (score > 20) {
      return 'REVIEW';
    }

    return 'INSTALL';
  }

  private deduplicateFindings(findings: Finding[]): Finding[] {
    const seen = new Set<string>();
    return findings.filter((f) => {
      const key = `${f.category}:${f.message}:${f.file}:${f.line ?? ''}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  private async calculateChecksum(
    files: string[],
    tools: ToolsInterface,
    rootDir: string,
  ): Promise<string> {
    const hash = crypto.createHash('sha256');
    // Use relative paths for stable checksums across machines
    const relativeFiles = files.map((f) => path.relative(rootDir, f));
    const sortedFiles = [...relativeFiles].sort();

    for (const relFile of sortedFiles) {
      const absFile = path.join(rootDir, relFile);
      try {
        const content = await tools.readFile(absFile);
        // Hash relative path (not absolute) for machine-independent checksums
        hash.update(relFile);
        hash.update(content);
      } catch {
        // Skip unreadable files
      }
    }

    return hash.digest('hex');
  }
}
