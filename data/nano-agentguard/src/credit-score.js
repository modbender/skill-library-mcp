/**
 * Credit Score - Agent Reputation System
 *
 * Calculate reputation score based on behavior history
 */

class CreditScore {
  constructor(audit, registry) {
    this.audit = audit;
    this.registry = registry;

    // Scoring weights
    this.weights = {
      taskSuccess: 10,      // 任务成功 +10
      taskFailure: -20,     // 任务失败 -20
      approvalGranted: 5,   // 获得批准 +5
      approvalDenied: -10,  // 被拒绝 -10
      credentialAccess: 1,  // 凭证访问 +1
      dangerousOp: -5,      // 危险操作 -5
      daysActive: 2,        // 活跃天数 +2/天
      humanInteraction: 3   // 人类交互 +3
    };

    // Score bounds
    this.minScore = 0;
    this.maxScore = 100;
    this.initialScore = 50;  // 初始分数
  }

  /**
   * Calculate credit score for an agent
   */
  async calculate(agentId, days = 30) {
    // Get audit logs
    const logs = await this.audit.getLogs(agentId, {
      from: this.getDateFrom(days),
      to: this.getDateTo()
    });

    // Get agent info
    const agent = await this.registry.get(agentId);
    const daysActive = this.getDaysActive(agent.createdAt);

    // Calculate base score
    let score = this.initialScore;

    // Analyze logs
    const stats = this.analyzeLogs(logs);

    // Apply scoring
    score += stats.taskSuccess * this.weights.taskSuccess;
    score += stats.taskFailure * this.weights.taskFailure;
    score += stats.approvalsGranted * this.weights.approvalGranted;
    score += stats.approvalsDenied * this.weights.approvalDenied;
    score += stats.credentialAccess * this.weights.credentialAccess;
    score += stats.dangerousOps * this.weights.dangerousOp;
    score += Math.min(daysActive, days) * this.weights.daysActive;
    score += stats.humanInteractions * this.weights.humanInteraction;

    // Clamp score
    score = Math.max(this.minScore, Math.min(this.maxScore, score));

    // Determine tier
    const tier = this.getTier(score);

    return {
      agentId,
      score: Math.round(score),
      tier,
      stats: {
        daysActive,
        taskSuccess: stats.taskSuccess,
        taskFailure: stats.taskFailure,
        approvalsGranted: stats.approvalsGranted,
        approvalsDenied: stats.approvalsDenied,
        dangerousOps: stats.dangerousOps,
        credentialAccess: stats.credentialAccess
      },
      factors: this.getScoreFactors(stats, daysActive),
      lastUpdated: new Date().toISOString(),
      period: `${days} days`
    };
  }

  /**
   * Analyze audit logs
   */
  analyzeLogs(logs) {
    const stats = {
      taskSuccess: 0,
      taskFailure: 0,
      approvalsGranted: 0,
      approvalsDenied: 0,
      dangerousOps: 0,
      credentialAccess: 0,
      humanInteractions: 0
    };

    for (const log of logs) {
      switch (log.operation) {
        case 'operation_executed':
          if (log.details?.success) stats.taskSuccess++;
          else stats.taskFailure++;
          break;

        case 'approval_result':
          if (log.details?.approved) stats.approvalsGranted++;
          else stats.approvalsDenied++;
          stats.humanInteractions++;
          break;

        case 'permission_check':
          if (log.details?.result?.requiresApproval) stats.dangerousOps++;
          break;

        case 'credential_accessed':
          stats.credentialAccess++;
          break;

        case 'approval_requested':
          stats.humanInteractions++;
          break;
      }
    }

    return stats;
  }

  /**
   * Get score factors (what affected the score)
   */
  getScoreFactors(stats, daysActive) {
    const factors = [];

    if (stats.taskSuccess > 0) {
      factors.push({
        factor: 'taskSuccess',
        impact: stats.taskSuccess * this.weights.taskSuccess,
        count: stats.taskSuccess
      });
    }

    if (stats.taskFailure > 0) {
      factors.push({
        factor: 'taskFailure',
        impact: stats.taskFailure * this.weights.taskFailure,
        count: stats.taskFailure
      });
    }

    if (stats.approvalsGranted > 0) {
      factors.push({
        factor: 'approvalsGranted',
        impact: stats.approvalsGranted * this.weights.approvalGranted,
        count: stats.approvalsGranted
      });
    }

    if (stats.approvalsDenied > 0) {
      factors.push({
        factor: 'approvalsDenied',
        impact: stats.approvalsDenied * this.weights.approvalDenied,
        count: stats.approvalsDenied
      });
    }

    if (stats.dangerousOps > 0) {
      factors.push({
        factor: 'dangerousOps',
        impact: stats.dangerousOps * this.weights.dangerousOp,
        count: stats.dangerousOps
      });
    }

    factors.push({
      factor: 'daysActive',
      impact: daysActive * this.weights.daysActive,
      count: daysActive
    });

    return factors.sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact));
  }

  /**
   * Get tier based on score
   */
  getTier(score) {
    if (score >= 90) return { level: 'S', name: '卓越', color: 'gold', emoji: '🏆' };
    if (score >= 80) return { level: 'A', name: '优秀', color: 'green', emoji: '⭐' };
    if (score >= 70) return { level: 'B', name: '良好', color: 'blue', emoji: '✓' };
    if (score >= 60) return { level: 'C', name: '一般', color: 'yellow', emoji: '○' };
    if (score >= 50) return { level: 'D', name: '及格', color: 'orange', emoji: '△' };
    return { level: 'F', name: '危险', color: 'red', emoji: '⚠️' };
  }

  /**
   * Get days since agent creation
   */
  getDaysActive(createdAt) {
    const created = new Date(createdAt);
    const now = new Date();
    return Math.floor((now - created) / (1000 * 60 * 60 * 24));
  }

  /**
   * Get date from N days ago
   */
  getDateFrom(days) {
    const date = new Date();
    date.setDate(date.getDate() - days);
    return date.toISOString().split('T')[0];
  }

  /**
   * Get today's date
   */
  getDateTo() {
    return new Date().toISOString().split('T')[0];
  }

  /**
   * Generate credit report
   */
  async generateReport(agentId, days = 30) {
    const score = await this.calculate(agentId, days);
    const agent = await this.registry.get(agentId);

    return {
      report: {
        title: 'Agent Credit Report',
        generatedAt: new Date().toISOString(),
        period: `${days} days`
      },
      agent: {
        id: agent.id,
        owner: agent.owner,
        createdAt: agent.createdAt,
        status: agent.status,
        permissionLevel: agent.permissions.level
      },
      credit: {
        score: score.score,
        tier: score.tier,
        rating: `${score.tier.emoji} ${score.tier.name} (${score.tier.level})`
      },
      statistics: score.stats,
      factors: score.factors,
      recommendation: this.getRecommendation(score)
    };
  }

  /**
   * Get recommendation based on score
   */
  getRecommendation(score) {
    if (score.score >= 80) {
      return {
        level: 'low_risk',
        message: '该智能体信誉良好，可放心委托重要任务',
        canAutomate: true,
        suggestedPermissions: ['admin']
      };
    }

    if (score.score >= 60) {
      return {
        level: 'medium_risk',
        message: '该智能体信誉一般，建议保留人工审批',
        canAutomate: false,
        suggestedPermissions: ['write']
      };
    }

    return {
      level: 'high_risk',
      message: '该智能体信誉较低，建议严格限制权限',
      canAutomate: false,
      suggestedPermissions: ['read']
    };
  }

  /**
   * Compare multiple agents
   */
  async compare(agentIds, days = 30) {
    const scores = [];

    for (const agentId of agentIds) {
      try {
        const score = await this.calculate(agentId, days);
        scores.push(score);
      } catch (e) {
        // Skip agents that don't exist
      }
    }

    // Sort by score descending
    scores.sort((a, b) => b.score - a.score);

    return {
      comparison: scores,
      ranking: scores.map((s, i) => ({
        rank: i + 1,
        agentId: s.agentId,
        score: s.score,
        tier: s.tier.level
      }))
    };
  }
}

module.exports = CreditScore;
