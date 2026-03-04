import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, relative, resolve } from "node:path";
import { homedir } from "node:os";
import { DETECTION_RULES } from "./patterns.js";
import type { Finding, SkillReport, ScanResult, DetectionRule } from "./types.js";

const SCAN_EXTENSIONS = /\.(js|ts|mjs|cjs|json|md|txt|yaml|yml|sh|bash|py|toml)$/;
const MAX_FILE_SIZE = 1024 * 1024; // 1MB
const SKIP_DIRS = new Set(["node_modules", ".git", "dist", "build", ".cache"]);

function walkDir(dir: string, files: string[] = []): string[] {
  if (!existsSync(dir)) return files;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (SKIP_DIRS.has(entry.name)) continue;
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      walkDir(full, files);
    } else if (entry.isFile() && SCAN_EXTENSIONS.test(entry.name)) {
      try {
        if (statSync(full).size <= MAX_FILE_SIZE) {
          files.push(full);
        }
      } catch {
        // skip unreadable
      }
    }
  }
  return files;
}

function scanFile(filePath: string, rules: DetectionRule[]): Finding[] {
  const findings: Finding[] = [];
  let content: string;
  try {
    content = readFileSync(filePath, "utf-8");
  } catch {
    return findings;
  }

  const lines = content.split("\n");

  for (const rule of rules) {
    if (rule.fileFilter && !rule.fileFilter.test(filePath)) continue;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const match = rule.pattern.exec(line);
      if (match) {
        findings.push({
          severity: rule.severity,
          rule: rule.id,
          description: rule.description,
          file: filePath,
          line: i + 1,
          match: match[0].slice(0, 100),
        });
        break; // one finding per rule per file
      }
    }
  }

  return findings;
}

function calculateScore(findings: Finding[]): number {
  if (findings.length === 0) return 100;
  const weights = { critical: 40, high: 20, medium: 10, low: 3, info: 1 };
  const penalty = findings.reduce((sum, f) => sum + (weights[f.severity] || 0), 0);
  return Math.max(0, 100 - penalty);
}

export function scanSkill(skillPath: string): SkillReport {
  const name = skillPath.split("/").pop() || skillPath;
  const absPath = resolve(skillPath);
  const files = walkDir(absPath);
  const findings: Finding[] = [];

  for (const file of files) {
    const fileFindings = scanFile(file, DETECTION_RULES);
    for (const f of fileFindings) {
      f.file = relative(absPath, f.file);
    }
    findings.push(...fileFindings);
  }

  // Sort: critical first
  const order = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
  findings.sort((a, b) => order[a.severity] - order[b.severity]);

  return {
    name,
    path: absPath,
    findings,
    scannedFiles: files.length,
    score: calculateScore(findings),
  };
}

export function getDefaultSkillPaths(): string[] {
  const paths: string[] = [];
  const home = homedir();

  // ClawHub installed skills
  const clawSkills = join(home, ".openclaw", "skills");
  if (existsSync(clawSkills)) {
    for (const entry of readdirSync(clawSkills, { withFileTypes: true })) {
      if (entry.isDirectory()) {
        paths.push(join(clawSkills, entry.name));
      }
    }
  }

  // npm global skills (OpenClaw built-in)
  const npmSkills = join(home, ".npm-global", "lib", "node_modules", "openclaw", "skills");
  if (existsSync(npmSkills)) {
    for (const entry of readdirSync(npmSkills, { withFileTypes: true })) {
      if (entry.isDirectory()) {
        paths.push(join(npmSkills, entry.name));
      }
    }
  }

  return paths;
}

export function runScan(skillPaths?: string[]): ScanResult {
  const paths = skillPaths || getDefaultSkillPaths();
  const skills: SkillReport[] = [];

  for (const p of paths) {
    skills.push(scanSkill(p));
  }

  // Sort: worst scores first
  skills.sort((a, b) => a.score - b.score);

  const allFindings = skills.flatMap((s) => s.findings);

  return {
    timestamp: new Date().toISOString(),
    skillsScanned: skills.length,
    totalFindings: allFindings.length,
    critical: allFindings.filter((f) => f.severity === "critical").length,
    high: allFindings.filter((f) => f.severity === "high").length,
    medium: allFindings.filter((f) => f.severity === "medium").length,
    low: allFindings.filter((f) => f.severity === "low").length,
    skills,
  };
}
