/**
 * Skill Handler
 * Processes /security-scan skill invocations from Claude Code
 * 로컬 경로 스캔 + 이름 기반 API 검색 모두 지원
 */

import {
  Scanner,
  SastEngine,
  ScaEngine,
  ToolAnalyzerEngine,
  MalwareDetectorEngine,
  PermissionCheckerEngine,
  DastEngine,
  BehaviorMonitorEngine,
  loadGlobalConfig,
  RiskLevel,
  validateScanPath,
} from "@asvs/core";
import type { ReportFormat, ScanEngineId, ScanTarget, Vulnerability } from "@asvs/core";
import { ReportGenerator } from "@asvs/reporter";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { createHmac } from "node:crypto";

export interface SkillInvocation {
  targetPath: string;
  type?: "mcp-server" | "skill";
  profile?: "strict" | "standard" | "permissive";
  format?: ReportFormat;
  engines?: ScanEngineId[];
}

/** API 기반 조회 요청 */
export interface SkillLookupInvocation {
  name: string;
  type?: "mcp-server" | "skill";
  description?: string;
  repositoryUrl?: string;
  npmPackage?: string;
}

export class SkillHandler {
  private scanner: Scanner;
  private reporter: ReportGenerator;
  private apiBase: string;

  constructor() {
    this.scanner = new Scanner();
    this.reporter = new ReportGenerator();
    this.apiBase = process.env["ASVS_API_URL"] ?? "https://vs-api.aiclude.com";

    // Register all available engines
    this.scanner.registerEngine(new SastEngine());
    this.scanner.registerEngine(new ScaEngine());
    this.scanner.registerEngine(new ToolAnalyzerEngine());
    this.scanner.registerEngine(new MalwareDetectorEngine());
    this.scanner.registerEngine(new PermissionCheckerEngine());
    this.scanner.registerEngine(new DastEngine());
    this.scanner.registerEngine(new BehaviorMonitorEngine());
  }

  /** API 호출에 사용할 인증 헤더 생성 */
  private createAuthHeaders(name: string): Record<string, string> {
    const secret = process.env["ASVS_SIGNING_SECRET"] ?? "asvs-default-signing-key-2026";
    const timestamp = String(Date.now());
    const payload = `skill:${name}:${timestamp}`;
    const signature = createHmac("sha256", secret).update(payload).digest("hex");
    return {
      "Content-Type": "application/json",
      "X-ASVS-Source": "skill",
      "X-ASVS-Timestamp": timestamp,
      "X-ASVS-Signature": signature,
    };
  }

  /**
   * API 기반 보안 스캔 조회/요청
   * 기존 스캔 결과를 검색하고, 없으면 등록 후 스캔을 요청
   */
  async lookup(invocation: SkillLookupInvocation): Promise<string> {
    const apiUrl = `${this.apiBase}/api/v1/scan/lookup`;

    // 1단계: lookup API 호출
    const lookupRes = await fetch(apiUrl, {
      method: "POST",
      headers: this.createAuthHeaders(invocation.name),
      body: JSON.stringify({
        name: invocation.name,
        type: invocation.type ?? "mcp-server",
        description: invocation.description ?? "",
        repositoryUrl: invocation.repositoryUrl ?? "",
        npmPackage: invocation.npmPackage ?? "",
        source: "skill",
      }),
    });

    const lookupData = await lookupRes.json() as Record<string, unknown>;

    // 2단계: 기존 결과가 있으면 바로 반환
    if (lookupData["status"] === "found") {
      const report = lookupData["report"] as Record<string, unknown> | null;
      const scan = lookupData["scan"] as Record<string, unknown>;
      const target = lookupData["target"] as Record<string, unknown>;

      if (report) {
        return this.formatApiReport(report, target);
      }
      return this.formatScanSummary(target, scan);
    }

    // 3단계: 스캔 요청됨 → 폴링으로 완료 대기
    if (lookupData["status"] === "scanning" || lookupData["status"] === "registered") {
      const jobId = lookupData["jobId"] as string;
      const target = lookupData["target"] as Record<string, unknown>;

      // 폴링 (최대 120초)
      const maxWait = 120_000;
      const interval = 5_000;
      const startTime = Date.now();

      while (Date.now() - startTime < maxWait) {
        await new Promise((r) => setTimeout(r, interval));

        const statusRes = await fetch(`${this.apiBase}/api/v1/scan/status/${jobId}`, {
          headers: this.createAuthHeaders(invocation.name),
        });
        const statusData = await statusRes.json() as Record<string, unknown>;

        if (statusData["status"] === "completed") {
          const report = statusData["report"] as Record<string, unknown> | null;
          const scanResult = statusData["scan"] as Record<string, unknown>;
          const completedTarget = statusData["target"] as Record<string, unknown>;

          if (report) {
            return this.formatApiReport(report, completedTarget);
          }
          return this.formatScanSummary(completedTarget, scanResult);
        }

        if (statusData["status"] === "failed") {
          const job = statusData["job"] as Record<string, unknown>;
          throw new Error(`스캔 실패: ${job?.["error"] ?? "알 수 없는 오류"}`);
        }
      }

      // 타임아웃
      return [
        `# 보안 스캔 진행 중: ${invocation.name}`,
        "",
        `스캔이 아직 진행 중입니다. 잠시 후 다시 시도하세요.`,
        `Job ID: ${jobId}`,
        `타겟: ${(target["canonicalName"] ?? invocation.name) as string}`,
        "",
        `*상세 결과는 https://vs.aiclude.com 에서 확인하세요*`,
      ].join("\n");
    }

    return `API 응답: ${JSON.stringify(lookupData, null, 2)}`;
  }

  /** Handle a /security-scan invocation (로컬 경로 스캔) */
  async handle(invocation: SkillInvocation): Promise<string> {
    const config = loadGlobalConfig();
    const scanConfig = {
      ...config.defaultScanConfig,
      ...(invocation.profile && { sandboxProfile: invocation.profile }),
      ...(invocation.engines && { engines: invocation.engines }),
    };

    // Ensure malware-detector is always included
    if (!scanConfig.engines.includes("malware-detector")) {
      scanConfig.engines.push("malware-detector");
    }

    const targetPath = validateScanPath(invocation.targetPath);
    const targetType = invocation.type ?? this.detectTargetType(targetPath);

    const target: ScanTarget = {
      type: targetType,
      name: targetPath.split("/").pop() ?? targetPath,
      path: targetPath,
    };

    const scanResult = await this.scanner.scan(target, scanConfig);
    const format = invocation.format ?? "markdown";
    const report = this.reporter.generate(scanResult, format);

    return this.formatOutput(report, format, scanResult.engineResults.flatMap((r) => r.vulnerabilities));
  }

  /** Auto-detect whether target is an MCP server or skill */
  private detectTargetType(targetPath: string): "mcp-server" | "skill" {
    // Check for SKILL.md presence
    if (
      existsSync(resolve(targetPath, "SKILL.md")) ||
      targetPath.endsWith("SKILL.md") ||
      targetPath.includes("/skill")
    ) {
      return "skill";
    }
    return "mcp-server";
  }

  /** Format the report output with detailed findings */
  private formatOutput(
    report: ReturnType<ReportGenerator["generate"]>,
    format: ReportFormat,
    vulnerabilities: Vulnerability[],
  ): string {
    if (format === "json") {
      return JSON.stringify(report, null, 2);
    }

    // Markdown format with full details
    const lines: string[] = [];
    const { summary } = report.scanResult;

    // Header with severity icon
    const icon = summary.overallRiskLevel === RiskLevel.CRITICAL ? "[CRITICAL]"
      : summary.overallRiskLevel === RiskLevel.HIGH ? "[HIGH RISK]"
      : summary.overallRiskLevel === RiskLevel.MEDIUM ? "[MEDIUM RISK]"
      : summary.overallRiskLevel === RiskLevel.LOW ? "[LOW RISK]"
      : "[CLEAN]";

    lines.push(`# ${icon} Security Scan Report: ${report.title}`);
    lines.push("");
    lines.push(`| Metric | Value |`);
    lines.push(`|--------|-------|`);
    lines.push(`| Scan Date | ${report.generatedAt} |`);
    lines.push(`| Target | ${report.scanResult.target.path} |`);
    lines.push(`| Target Type | ${report.scanResult.target.type} |`);
    lines.push(`| Overall Risk | **${summary.overallRiskLevel}** |`);
    lines.push(`| Risk Score | **${summary.overallScore}/100** |`);
    lines.push(`| Total Findings | ${summary.totalVulnerabilities} |`);
    lines.push(`| Scan Duration | ${report.scanResult.duration}ms |`);
    lines.push("");

    // Severity breakdown
    lines.push("## Severity Breakdown");
    lines.push("");
    lines.push(`| Severity | Count |`);
    lines.push(`|----------|-------|`);
    for (const [level, count] of Object.entries(summary.bySeverity)) {
      if (count > 0) {
        lines.push(`| **${level}** | ${count} |`);
      }
    }
    lines.push("");

    // Detailed findings (top 20)
    if (vulnerabilities.length > 0) {
      lines.push("## Detailed Findings");
      lines.push("");

      const sorted = [...vulnerabilities].sort((a, b) => {
        const order = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3, INFO: 4 };
        return (order[a.severity] ?? 5) - (order[b.severity] ?? 5);
      });

      const top = sorted.slice(0, 20);

      for (let i = 0; i < top.length; i++) {
        const v = top[i]!;
        lines.push(`### ${i + 1}. [${v.severity}] ${v.title}`);
        lines.push("");
        lines.push(`- **ID**: ${v.id}`);
        lines.push(`- **Category**: ${v.category}`);
        lines.push(`- **Confidence**: ${Math.round(v.confidence * 100)}%`);
        if (v.location) {
          lines.push(`- **Location**: \`${v.location.file}:${v.location.line}\``);
        }
        lines.push(`- **Description**: ${v.description}`);
        lines.push(`- **Remediation**: ${v.remediation}`);
        if (v.cveIds?.length) {
          lines.push(`- **CVE**: ${v.cveIds.join(", ")}`);
        }
        if (v.location?.snippet) {
          lines.push("");
          lines.push("```");
          lines.push(v.location.snippet.substring(0, 300));
          lines.push("```");
        }
        lines.push("");
      }

      if (sorted.length > 20) {
        lines.push(`> ... and ${sorted.length - 20} more findings. Use \`--format json\` for the complete list.`);
        lines.push("");
      }
    }

    // Risk assessments
    if (report.risks.length > 0) {
      lines.push("## Risk Assessment");
      lines.push("");
      for (const risk of report.risks) {
        lines.push(`### [${risk.level}] ${risk.area}`);
        lines.push(`- **Impact**: ${risk.impact}`);
        lines.push(`- **Likelihood**: ${risk.likelihood}`);
        lines.push(`- **Remediation**: ${risk.remediation}`);
        lines.push("");
      }
    }

    // Precautions
    if (report.precautions.length > 0) {
      lines.push("## Precautions & Warnings");
      lines.push("");
      for (const precaution of report.precautions) {
        lines.push(`- ${precaution}`);
      }
      lines.push("");
    }

    return lines.join("\n");
  }

  // -----------------------------------------------------------------------
  // API 리포트 포맷팅 헬퍼
  // -----------------------------------------------------------------------

  /** API에서 받은 상세 리포트를 마크다운으로 포맷 */
  private formatApiReport(
    report: Record<string, unknown>,
    target: Record<string, unknown>,
  ): string {
    const lines: string[] = [];
    const scanResult = report["scanResult"] as Record<string, unknown> | undefined;
    const summary = scanResult?.["summary"] as Record<string, unknown> | undefined;
    const engineResults = (scanResult?.["engineResults"] ?? []) as Array<Record<string, unknown>>;
    const risks = (report["risks"] ?? []) as Array<Record<string, unknown>>;
    const precautions = (report["precautions"] ?? []) as string[];

    const riskLevel = (summary?.["overallRiskLevel"] ?? target["riskLevel"] ?? "UNKNOWN") as string;
    const score = (summary?.["overallScore"] ?? target["lastScore"] ?? 0) as number;
    const totalVulns = (summary?.["totalVulnerabilities"] ?? 0) as number;
    const bySeverity = (summary?.["bySeverity"] ?? {}) as Record<string, number>;
    const targetName = (target["canonicalName"] ?? target["displayName"] ?? "Unknown") as string;
    const targetType = (target["type"] ?? "mcp-server") as string;

    const icon = riskLevel === "CRITICAL" ? "[CRITICAL]"
      : riskLevel === "HIGH" ? "[HIGH RISK]"
      : riskLevel === "MEDIUM" ? "[MEDIUM RISK]"
      : riskLevel === "LOW" ? "[LOW RISK]"
      : "[CLEAN]";

    lines.push(`# ${icon} Security Scan Report: ${targetName}`);
    lines.push("");
    lines.push(`| Metric | Value |`);
    lines.push(`|--------|-------|`);
    lines.push(`| Target | ${targetName} |`);
    lines.push(`| Type | ${targetType} |`);
    lines.push(`| Overall Risk | **${riskLevel}** |`);
    lines.push(`| Risk Score | **${score}/100** |`);
    lines.push(`| Total Findings | ${totalVulns} |`);
    lines.push(`| Scan Date | ${(report["generatedAt"] ?? "N/A") as string} |`);
    lines.push("");

    // 심각도 분포
    lines.push("## Severity Breakdown");
    lines.push("");
    lines.push("| Severity | Count |");
    lines.push("|----------|-------|");
    for (const level of ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]) {
      const count = bySeverity[level] ?? 0;
      if (count > 0) {
        lines.push(`| **${level}** | ${count} |`);
      }
    }
    lines.push("");

    // 상세 취약점
    const allVulns = engineResults.flatMap(
      (r) => ((r["vulnerabilities"] ?? []) as Array<Record<string, unknown>>),
    );

    if (allVulns.length > 0) {
      lines.push("## Detailed Findings");
      lines.push("");

      const sorted = [...allVulns].sort((a, b) => {
        const order: Record<string, number> = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3, INFO: 4 };
        return (order[a["severity"] as string] ?? 5) - (order[b["severity"] as string] ?? 5);
      });

      const top = sorted.slice(0, 20);
      for (let i = 0; i < top.length; i++) {
        const v = top[i]!;
        lines.push(`### ${i + 1}. [${v["severity"] as string}] ${v["title"] as string}`);
        lines.push("");
        lines.push(`- **Category**: ${v["category"] as string}`);
        lines.push(`- **Confidence**: ${Math.round((v["confidence"] as number) * 100)}%`);
        const loc = v["location"] as Record<string, unknown> | undefined;
        if (loc) {
          lines.push(`- **Location**: \`${loc["file"] as string}:${loc["line"] as number}\``);
        }
        lines.push(`- **Description**: ${v["description"] as string}`);
        lines.push(`- **Remediation**: ${v["remediation"] as string}`);
        lines.push("");
      }

      if (sorted.length > 20) {
        lines.push(`> ... and ${sorted.length - 20} more findings.`);
        lines.push("");
      }
    }

    // 위험 평가
    if (risks.length > 0) {
      lines.push("## Risk Assessment");
      lines.push("");
      for (const risk of risks) {
        lines.push(`### [${risk["level"] as string}] ${risk["area"] as string}`);
        lines.push(`- **Impact**: ${risk["impact"] as string}`);
        lines.push(`- **Remediation**: ${risk["remediation"] as string}`);
        lines.push("");
      }
    }

    // 주의사항
    if (precautions.length > 0) {
      lines.push("## Precautions & Warnings");
      lines.push("");
      for (const p of precautions) {
        lines.push(`- ${p}`);
      }
      lines.push("");
    }

    lines.push("---");
    lines.push(`*Report ID: ${(report["id"] ?? "N/A") as string}*`);
    lines.push(`*Web Dashboard: https://vs.aiclude.com/targets*`);

    return lines.join("\n");
  }

  /** 스캔 요약만 포맷 */
  private formatScanSummary(
    target: Record<string, unknown>,
    scan: Record<string, unknown>,
  ): string {
    const lines: string[] = [];
    const targetName = (target["canonicalName"] ?? target["displayName"] ?? "Unknown") as string;
    const riskLevel = (scan["riskLevel"] ?? target["riskLevel"] ?? "UNKNOWN") as string;
    const score = (scan["score"] ?? target["lastScore"] ?? 0) as number;

    lines.push(`# Security Scan Summary: ${targetName}`);
    lines.push("");
    lines.push(`| Metric | Value |`);
    lines.push(`|--------|-------|`);
    lines.push(`| Risk Level | **${riskLevel}** |`);
    lines.push(`| Risk Score | **${score}/100** |`);
    lines.push(`| Total Vulnerabilities | ${(scan["totalVulnerabilities"] ?? 0) as number} |`);
    lines.push(`| CRITICAL | ${(scan["criticalCount"] ?? 0) as number} |`);
    lines.push(`| HIGH | ${(scan["highCount"] ?? 0) as number} |`);
    lines.push(`| MEDIUM | ${(scan["mediumCount"] ?? 0) as number} |`);
    lines.push(`| LOW | ${(scan["lowCount"] ?? 0) as number} |`);
    lines.push(`| INFO | ${(scan["infoCount"] ?? 0) as number} |`);
    lines.push(`| Scanned At | ${(scan["scannedAt"] ?? "N/A") as string} |`);
    lines.push("");
    lines.push(`*상세 리포트는 https://vs.aiclude.com 에서 확인하세요*`);

    return lines.join("\n");
  }
}
