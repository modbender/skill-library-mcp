/**
 * @file sandbox/SandboxMonitor.ts  (完整实现)
 * @description 安全违规监控器 + 熔断器
 *
 * 核心功能：
 *   1. 收集并聚合所有沙箱违规事件（按 skillId 维度统计）
 *   2. 违规熔断：某 Skill 触发 N 次 critical 违规后自动拒绝执行
 *   3. 持久化违规日志（可选，写入 NDJSON 文件）
 *   4. Webhook 报警集成
 *   5. Top offender 分析
 *   6. 违规保留策略（按时间窗口 TTL 清理）
 */

import { EventEmitter } from "node:events";
import * as fs from "node:fs";
import type { SandboxViolation, ViolationType } from "./types.js";
import type { SandboxExecutor } from "./SandboxExecutor.js";

// ─── 统计结构 ─────────────────────────────────────────────────────────────────

export interface SkillViolationStats {
  skillId: string;
  totalViolations: number;
  criticalCount: number;
  errorCount: number;
  warnCount: number;
  byType: Partial<Record<ViolationType, number>>;
  firstViolationAt: string;
  lastViolationAt: string;
  /** 是否已被熔断（超过阈值后拒绝继续执行） */
  circuitBroken: boolean;
}

export interface MonitorConfig {
  /**
   * 持久化违规日志文件路径（可选，NDJSON 格式）
   * 不设置时只在内存中保留
   */
  logFilePath?: string;

  /**
   * 每个 Skill 触发多少次 critical 违规后触发熔断
   * @default 3
   */
  circuitBreakerThreshold?: number;

  /**
   * Webhook 报警 URL（POST JSON，可选）
   * 每次 critical 违规时调用
   */
  webhookUrl?: string;

  /**
   * 违规记录保留时长（小时），超过此时间的记录自动清理
   * @default 24
   */
  retentionHours?: number;
}

// ─── 内部记录结构（含原始违规列表）──────────────────────────────────────────

interface SkillRecord {
  stats: SkillViolationStats;
  violations: SandboxViolation[];
}

// ─── SandboxMonitor ──────────────────────────────────────────────────────────

export class SandboxMonitor extends EventEmitter {
  private readonly config: Required<Omit<MonitorConfig, "logFilePath" | "webhookUrl">> & MonitorConfig;
  private readonly records = new Map<string, SkillRecord>();
  private cleanupTimer: ReturnType<typeof setInterval> | null = null;

  constructor(config: MonitorConfig = {}) {
    super();
    this.config = {
      circuitBreakerThreshold: config.circuitBreakerThreshold ?? 3,
      retentionHours: config.retentionHours ?? 24,
      logFilePath: config.logFilePath,
      webhookUrl: config.webhookUrl,
    };

    // 定期清理过期记录（每小时）
    this.cleanupTimer = setInterval(
      () => this.cleanupExpiredRecords(),
      60 * 60 * 1000,
    );
    // 不阻止进程退出
    this.cleanupTimer.unref();
  }

  // ─── 核心 API ─────────────────────────────────────────────────────────────

  /**
   * 记录一条违规事件
   */
  recordViolation(violation: SandboxViolation): void {
    const { skillId } = violation;
    
    if (!this.records.has(skillId)) {
      this.records.set(skillId, {
        stats: {
          skillId,
          totalViolations: 0,
          criticalCount: 0,
          errorCount: 0,
          warnCount: 0,
          byType: {},
          firstViolationAt: violation.timestamp,
          lastViolationAt: violation.timestamp,
          circuitBroken: false,
        },
        violations: [],
      });
    }

    const record = this.records.get(skillId)!;
    record.violations.push(violation);

    // 更新统计
    const stats = record.stats;
    stats.totalViolations++;
    stats.lastViolationAt = violation.timestamp;
    stats.byType[violation.type] = (stats.byType[violation.type] ?? 0) + 1;

    switch (violation.severity) {
      case "critical": stats.criticalCount++; break;
      case "error":    stats.errorCount++;    break;
      case "warn":     stats.warnCount++;     break;
    }

    // 检查熔断条件
    if (!stats.circuitBroken &&
        stats.criticalCount >= this.config.circuitBreakerThreshold) {
      stats.circuitBroken = true;
      this.emit("circuit-open", { skillId, stats });
      console.error(
        `[SandboxMonitor] 🔴 Circuit breaker OPEN for skill "${skillId}". ` +
        `${stats.criticalCount} critical violations detected. ` +
        `Further executions will be rejected.`
      );
    }

    // 持久化日志
    if (this.config.logFilePath) {
      this.appendToLog(violation);
    }

    // Webhook 报警（critical 违规立即触发）
    if (violation.severity === "critical" && this.config.webhookUrl) {
      this.sendWebhookAlert(violation).catch((err) => {
        console.warn(`[SandboxMonitor] Webhook call failed: ${err}`);
      });
    }

    this.emit("violation", violation);
  }

  /**
   * 将沙箱执行器的违规事件接入 Monitor
   * 用法：monitor.attach(sandboxExecutor, skillId)
   */
  attach(executor: SandboxExecutor, skillId: string): void {
    executor.on("violation", (v: SandboxViolation) => {
      this.recordViolation({ ...v, skillId });
    });
  }

  /**
   * 检查某 Skill 是否已被熔断
   * 使用时机：TaskExecutor 在执行前调用，若熔断则直接返回错误
   */
  isCircuitBroken(skillId: string): boolean {
    return this.records.get(skillId)?.stats.circuitBroken ?? false;
  }

  /**
   * 手动重置熔断器（运维修复后使用）
   */
  resetCircuit(skillId: string): void {
    const record = this.records.get(skillId);
    if (record) {
      record.stats.circuitBroken = false;
      record.stats.criticalCount = 0;
      this.emit("circuit-reset", { skillId });
      console.info(`[SandboxMonitor] ✅ Circuit breaker RESET for skill "${skillId}"`);
    }
  }

  /**
   * 获取某 Skill 的违规统计
   */
  getStats(skillId: string): SkillViolationStats | null {
    return this.records.get(skillId)?.stats ?? null;
  }

  /**
   * 获取所有 Skill 的违规统计
   */
  getAllStats(): SkillViolationStats[] {
    return [...this.records.values()].map((r) => ({ ...r.stats }));
  }

  /**
   * 获取违规最多的 Top-K Skill（降序）
   */
  getTopOffenders(k = 10): SkillViolationStats[] {
    return this.getAllStats()
      .sort((a, b) => b.totalViolations - a.totalViolations)
      .slice(0, k);
  }

  /**
   * 获取某 Skill 的原始违规列表
   */
  getViolations(skillId: string): readonly SandboxViolation[] {
    return this.records.get(skillId)?.violations ?? [];
  }

  /**
   * 清空某 Skill 的记录（完全重置）
   */
  clearSkill(skillId: string): void {
    this.records.delete(skillId);
  }

  /**
   * 清空所有记录
   */
  clearAll(): void {
    this.records.clear();
  }

  /**
   * 生成 Markdown 格式的违规报告
   */
  generateReport(): string {
    const stats = this.getAllStats().sort((a, b) => b.totalViolations - a.totalViolations);

    if (stats.length === 0) {
      return "## 🛡️ Sandbox Security Report\n\nNo violations recorded.\n";
    }

    const circuitBrokenSkills = stats.filter((s) => s.circuitBroken);

    let md = "## 🛡️ Sandbox Security Report\n\n";

    if (circuitBrokenSkills.length > 0) {
      md += `### 🔴 Circuit Breakers Open (${circuitBrokenSkills.length})\n\n`;
      for (const s of circuitBrokenSkills) {
        md += `- \`${s.skillId}\`: ${s.criticalCount} critical violations — **BLOCKED**\n`;
      }
      md += "\n";
    }

    md += "### 📊 Violation Summary\n\n";
    md += "| Skill ID | Total | Critical | Error | Warn | Last Violation | Status |\n";
    md += "|:---------|------:|---------:|------:|-----:|:---------------|:-------|\n";

    for (const s of stats) {
      const status = s.circuitBroken ? "🔴 BLOCKED" : "🟢 OK";
      const lastTime = s.lastViolationAt.replace("T", " ").split(".")[0];
      md += `| \`${s.skillId}\` | ${s.totalViolations} | ${s.criticalCount} | ${s.errorCount} | ${s.warnCount} | ${lastTime} | ${status} |\n`;
    }

    md += "\n### 🔍 Violation Type Distribution\n\n";
    const typeTotals: Partial<Record<ViolationType, number>> = {};
    for (const s of stats) {
      for (const [type, count] of Object.entries(s.byType) as [ViolationType, number][]) {
        typeTotals[type] = (typeTotals[type] ?? 0) + count;
      }
    }

    for (const [type, count] of Object.entries(typeTotals)) {
      md += `- **${type}**: ${count} occurrences\n`;
    }

    return md;
  }

  /**
   * 停止后台清理定时器（测试或关闭时调用）
   */
  destroy(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer);
      this.cleanupTimer = null;
    }
  }

  // ─── 私有方法 ─────────────────────────────────────────────────────────────

  /**
   * 将违规记录追加到 NDJSON 日志文件
   */
  private appendToLog(violation: SandboxViolation): void {
    try {
      const line = JSON.stringify(violation) + "\n";
      fs.appendFileSync(this.config.logFilePath!, line, "utf-8");
    } catch (err) {
      console.warn(`[SandboxMonitor] Failed to write log: ${err}`);
    }
  }

  /**
   * 发送 Webhook 报警（fire-and-forget）
   */
  private async sendWebhookAlert(violation: SandboxViolation): Promise<void> {
    const body = JSON.stringify({
      event: "sandbox_violation",
      severity: violation.severity,
      skillId: violation.skillId,
      type: violation.type,
      detail: violation.detail,
      timestamp: violation.timestamp,
    });

    await fetch(this.config.webhookUrl!, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      signal: AbortSignal.timeout(5_000),
    });
  }

  /**
   * 清理超过 retentionHours 的历史记录
   */
  private cleanupExpiredRecords(): void {
    const cutoff = Date.now() - this.config.retentionHours * 60 * 60 * 1000;

    for (const [skillId, record] of this.records.entries()) {
      const lastViolation = new Date(record.stats.lastViolationAt).getTime();
      if (lastViolation < cutoff && !record.stats.circuitBroken) {
        this.records.delete(skillId);
      }
    }
  }
}
