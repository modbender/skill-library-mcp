/**
 * Compliance Reporter - GDPR/CCPA Compliance Audit
 *
 * Generate compliance reports for AI agents
 */

class ComplianceReporter {
  constructor(audit, registry, scope) {
    this.audit = audit;
    this.registry = registry;
    this.scope = scope;

    // Data processing categories
    this.dataCategories = {
      personal: ['name', 'email', 'phone', 'address'],
      sensitive: ['health', 'financial', 'biometric', 'location'],
      technical: ['ip', 'device_id', 'user_agent', 'session_id'],
      behavioral: ['clicks', 'views', 'searches', 'preferences']
    };

    // Legal bases
    this.legalBases = {
      consent: '用户同意',
      contract: '合同履行',
      legal: '法律义务',
      vital: '生命利益',
      public: '公共利益',
      legitimate: '合法利益'
    };
  }

  /**
   * Generate GDPR compliance report
   */
  async gdprReport(agentId, options = {}) {
    const agent = await this.registry.get(agentId);
    const logs = await this.audit.getLogs(agentId, options);

    // Analyze data processing activities
    const activities = this.analyzeDataProcessing(logs);

    // Check consent records
    const consentRecords = this.extractConsentRecords(logs);

    // Identify data subjects
    const dataSubjects = this.identifyDataSubjects(logs);

    // Check retention compliance
    const retention = this.checkRetention(agent, logs);

    // Generate report
    const report = {
      reportType: 'GDPR',
      generatedAt: new Date().toISOString(),
      agent: {
        id: agent.id,
        owner: agent.owner,
        status: agent.status,
        createdAt: agent.createdAt
      },
      summary: {
        totalProcessingActivities: activities.length,
        uniqueDataSubjects: dataSubjects.length,
        consentRecords: consentRecords.length,
        retentionViolations: retention.violations.length,
        complianceScore: this.calculateComplianceScore(activities, consentRecords, retention)
      },
      dataProcessing: {
        categories: this.categorizeProcessing(activities),
        purposes: this.extractPurposes(activities),
        legalBases: this.extractLegalBases(activities),
        dataTypes: this.extractDataTypes(activities)
      },
      consent: {
        records: consentRecords,
        coverage: this.calculateConsentCoverage(activities, consentRecords),
        gaps: this.identifyConsentGaps(activities, consentRecords)
      },
      dataSubjects: {
        count: dataSubjects.length,
        types: this.categorizeDataSubjects(dataSubjects),
        rightsExercised: this.extractRightsExercises(logs)
      },
      retention: {
        policy: retention.policy,
        violations: retention.violations,
        recommendation: retention.recommendation
      },
      risks: this.assessRisks(activities, consentRecords, retention),
      recommendations: this.generateRecommendations(activities, consentRecords, retention)
    };

    return report;
  }

  /**
   * Generate CCPA compliance report
   */
  async ccpaReport(agentId, options = {}) {
    const agent = await this.registry.get(agentId);
    const logs = await this.audit.getLogs(agentId, options);

    const activities = this.analyzeDataProcessing(logs);
    const saleActivities = this.identifySaleActivities(activities);
    const consumerRequests = this.extractConsumerRequests(logs);

    const report = {
      reportType: 'CCPA',
      generatedAt: new Date().toISOString(),
      agent: {
        id: agent.id,
        owner: agent.owner,
        status: agent.status
      },
      summary: {
        totalProcessingActivities: activities.length,
        dataSales: saleActivities.length,
        consumerRequests: consumerRequests.length,
        complianceScore: this.calculateCCPACompliance(activities, saleActivities, consumerRequests)
      },
      dataCollection: {
        categories: this.categorizeProcessing(activities),
        sources: this.extractSources(activities),
        thirdParties: this.extractThirdParties(activities)
      },
      dataSales: {
        activities: saleActivities,
        optOutMechanism: this.checkOptOutMechanism(agent),
        doNotSellHonored: this.checkDoNotSellHonored(logs)
      },
      consumerRights: {
        requests: consumerRequests,
        responseTimes: this.calculateResponseTimes(consumerRequests),
        fulfillment: this.checkFulfillment(consumerRequests)
      },
      risks: this.assessCCPARisks(activities, saleActivities, consumerRequests),
      recommendations: this.generateCCPARecommendations(activities, saleActivities, consumerRequests)
    };

    return report;
  }

  /**
   * Analyze data processing activities from logs
   */
  analyzeDataProcessing(logs) {
    const activities = [];

    for (const log of logs) {
      if (this.isDataProcessing(log)) {
        activities.push({
          timestamp: log.timestamp,
          operation: log.operation,
          dataType: this.identifyDataType(log),
          purpose: this.extractPurpose(log),
          legalBasis: this.extractLegalBasis(log),
          dataSubject: this.extractDataSubject(log),
          details: log.details
        });
      }
    }

    return activities;
  }

  /**
   * Check if log entry is data processing
   */
  isDataProcessing(log) {
    const processingOps = [
      'credential_accessed',
      'operation_executed',
      'api_call',
      'data_read',
      'data_write',
      'data_delete',
      'data_export'
    ];
    return processingOps.includes(log.operation);
  }

  /**
   * Identify data type from log
   */
  identifyDataType(log) {
    const details = log.details || {};

    // Check for personal data indicators
    if (details.email || details.phone || details.name) return 'personal';
    if (details.health || details.medical) return 'sensitive';
    if (details.ip || details.deviceId) return 'technical';
    if (details.clicks || details.views) return 'behavioral';

    return 'unknown';
  }

  /**
   * Extract purpose from log
   */
  extractPurpose(log) {
    return log.details?.purpose || log.details?.operation || 'unspecified';
  }

  /**
   * Extract legal basis from log
   */
  extractLegalBasis(log) {
    return log.details?.legalBasis || 'unspecified';
  }

  /**
   * Extract data subject from log
   */
  extractDataSubject(log) {
    return log.details?.userId || log.details?.subjectId || 'anonymous';
  }

  /**
   * Extract consent records from logs
   */
  extractConsentRecords(logs) {
    return logs
      .filter(log => log.operation === 'consent_given' || log.details?.consent)
      .map(log => ({
        timestamp: log.timestamp,
        subjectId: this.extractDataSubject(log),
        purpose: log.details?.purpose,
        granted: log.details?.consent === true
      }));
  }

  /**
   * Identify unique data subjects
   */
  identifyDataSubjects(logs) {
    const subjects = new Set();
    for (const log of logs) {
      const subject = this.extractDataSubject(log);
      if (subject !== 'anonymous') {
        subjects.add(subject);
      }
    }
    return Array.from(subjects);
  }

  /**
   * Check retention compliance
   */
  checkRetention(agent, logs) {
    const policy = agent.retentionPolicy || {
      defaultDays: 90,
      categories: {}
    };

    const violations = [];
    const now = Date.now();

    for (const log of logs) {
      const logTime = new Date(log.timestamp).getTime();
      const age = (now - logTime) / (1000 * 60 * 60 * 24);
      const category = this.identifyDataType(log);
      const maxDays = policy.categories[category] || policy.defaultDays;

      if (age > maxDays) {
        violations.push({
          logId: log.hash,
          category,
          age: Math.round(age),
          maxAllowed: maxDays,
          exceeded: Math.round(age - maxDays)
        });
      }
    }

    return {
      policy,
      violations,
      recommendation: violations.length > 0
        ? `发现 ${violations.length} 条数据超期未删除，建议立即清理`
        : '数据保留符合策略'
    };
  }

  /**
   * Categorize processing activities
   */
  categorizeProcessing(activities) {
    const categories = {};

    for (const activity of activities) {
      const type = activity.dataType;
      categories[type] = (categories[type] || 0) + 1;
    }

    return categories;
  }

  /**
   * Extract purposes from activities
   */
  extractPurposes(activities) {
    const purposes = {};
    for (const activity of activities) {
      const purpose = activity.purpose;
      purposes[purpose] = (purposes[purpose] || 0) + 1;
    }
    return purposes;
  }

  /**
   * Extract legal bases from activities
   */
  extractLegalBases(activities) {
    const bases = {};
    for (const activity of activities) {
      const basis = activity.legalBasis;
      bases[basis] = (bases[basis] || 0) + 1;
    }
    return bases;
  }

  /**
   * Extract data types from activities
   */
  extractDataTypes(activities) {
    const types = new Set();
    for (const activity of activities) {
      types.add(activity.dataType);
    }
    return Array.from(types);
  }

  /**
   * Calculate compliance score (0-100)
   */
  calculateComplianceScore(activities, consentRecords, retention) {
    let score = 100;

    // Penalize missing legal basis
    const missingBasis = activities.filter(a => a.legalBasis === 'unspecified').length;
    score -= Math.min(missingBasis * 5, 30);

    // Penalize missing consent
    const consentCoverage = this.calculateConsentCoverage(activities, consentRecords);
    score -= (100 - consentCoverage) * 0.3;

    // Penalize retention violations
    score -= Math.min(retention.violations.length * 10, 40);

    return Math.max(0, Math.min(100, Math.round(score)));
  }

  /**
   * Calculate consent coverage percentage
   */
  calculateConsentCoverage(activities, consentRecords) {
    if (activities.length === 0) return 100;

    const consentedSubjects = new Set(
      consentRecords.filter(r => r.granted).map(r => r.subjectId)
    );

    let covered = 0;
    for (const activity of activities) {
      if (consentedSubjects.has(activity.dataSubject)) {
        covered++;
      }
    }

    return Math.round((covered / activities.length) * 100);
  }

  /**
   * Identify consent gaps
   */
  identifyConsentGaps(activities, consentRecords) {
    const consentedSubjects = new Set(
      consentRecords.filter(r => r.granted).map(r => r.subjectId)
    );

    const gaps = [];
    for (const activity of activities) {
      if (!consentedSubjects.has(activity.dataSubject) && activity.dataSubject !== 'anonymous') {
        gaps.push({
          subjectId: activity.dataSubject,
          activity: activity.operation,
          timestamp: activity.timestamp
        });
      }
    }

    return gaps.slice(0, 10); // Return top 10
  }

  /**
   * Categorize data subjects
   */
  categorizeDataSubjects(dataSubjects) {
    return {
      total: dataSubjects.length,
      identified: dataSubjects.filter(s => s !== 'anonymous').length,
      anonymous: dataSubjects.filter(s => s === 'anonymous').length
    };
  }

  /**
   * Extract rights exercises from logs
   */
  extractRightsExercises(logs) {
    const rightsLogs = logs.filter(log =>
      log.operation === 'subject_access_request' ||
      log.operation === 'subject_deletion_request' ||
      log.operation === 'subject_portability_request'
    );

    return rightsLogs.map(log => ({
      type: log.operation,
      subjectId: this.extractDataSubject(log),
      timestamp: log.timestamp,
      fulfilled: log.details?.fulfilled || false
    }));
  }

  /**
   * Assess compliance risks
   */
  assessRisks(activities, consentRecords, retention) {
    const risks = [];

    // Check for missing legal basis
    const missingBasis = activities.filter(a => a.legalBasis === 'unspecified').length;
    if (missingBasis > 0) {
      risks.push({
        level: missingBasis > 10 ? 'high' : 'medium',
        category: 'legal_basis',
        description: `${missingBasis} 次数据处理活动缺少法律依据`,
        impact: '可能违反GDPR第6条'
      });
    }

    // Check consent coverage
    const coverage = this.calculateConsentCoverage(activities, consentRecords);
    if (coverage < 80) {
      risks.push({
        level: coverage < 50 ? 'high' : 'medium',
        category: 'consent',
        description: `同意覆盖率仅 ${coverage}%`,
        impact: '可能违反GDPR第7条'
      });
    }

    // Check retention violations
    if (retention.violations.length > 0) {
      risks.push({
        level: retention.violations.length > 10 ? 'high' : 'medium',
        category: 'retention',
        description: `${retention.violations.length} 条数据超期未删除`,
        impact: '可能违反GDPR第5条(1)(e)'
      });
    }

    return risks.sort((a, b) => {
      const order = { high: 0, medium: 1, low: 2 };
      return order[a.level] - order[b.level];
    });
  }

  /**
   * Generate recommendations
   */
  generateRecommendations(activities, consentRecords, retention) {
    const recommendations = [];

    // Legal basis recommendations
    const missingBasis = activities.filter(a => a.legalBasis === 'unspecified').length;
    if (missingBasis > 0) {
      recommendations.push({
        priority: 'high',
        action: '为所有数据处理活动添加法律依据',
        details: `需要为 ${missingBasis} 次活动补充法律依据（同意/合同/合法利益等）`
      });
    }

    // Consent recommendations
    const coverage = this.calculateConsentCoverage(activities, consentRecords);
    if (coverage < 100) {
      recommendations.push({
        priority: 'medium',
        action: '提高同意覆盖率',
        details: `当前 ${coverage}%，建议达到 100%`
      });
    }

    // Retention recommendations
    if (retention.violations.length > 0) {
      recommendations.push({
        priority: 'high',
        action: '清理超期数据',
        details: `删除 ${retention.violations.length} 条超期数据`
      });
    }

    return recommendations;
  }

  // CCPA-specific methods

  identifySaleActivities(activities) {
    return activities.filter(a =>
      a.details?.sale === true ||
      a.details?.shared === true ||
      a.purpose?.includes('sale')
    );
  }

  extractConsumerRequests(logs) {
    return logs
      .filter(log => log.operation.includes('consumer_request'))
      .map(log => ({
        type: log.details?.requestType,
        timestamp: log.timestamp,
        responseTime: log.details?.responseTime,
        fulfilled: log.details?.fulfilled
      }));
  }

  checkOptOutMechanism(agent) {
    return agent.ccpaOptOut?.enabled || false;
  }

  checkDoNotSellHonored(logs) {
    const dnsLogs = logs.filter(log => log.operation === 'do_not_sell_honored');
    return dnsLogs.length > 0;
  }

  calculateResponseTimes(requests) {
    if (requests.length === 0) return { avg: 0, max: 0 };

    const times = requests
      .filter(r => r.responseTime)
      .map(r => r.responseTime);

    return {
      avg: times.length > 0 ? Math.round(times.reduce((a, b) => a + b, 0) / times.length) : 0,
      max: times.length > 0 ? Math.max(...times) : 0
    };
  }

  checkFulfillment(requests) {
    if (requests.length === 0) return { rate: 100, pending: 0 };

    const fulfilled = requests.filter(r => r.fulfilled).length;
    return {
      rate: Math.round((fulfilled / requests.length) * 100),
      pending: requests.length - fulfilled
    };
  }

  calculateCCPACompliance(activities, saleActivities, requests) {
    let score = 100;

    // Penalize sales without opt-out
    if (saleActivities.length > 0) {
      score -= 10;
    }

    // Penalize slow response times
    const responseTimes = this.calculateResponseTimes(requests);
    if (responseTimes.avg > 45) { // CCPA requires 45 days
      score -= 20;
    }

    // Penalize unfulfilled requests
    const fulfillment = this.checkFulfillment(requests);
    score -= (100 - fulfillment.rate) * 0.2;

    return Math.max(0, Math.min(100, Math.round(score)));
  }

  assessCCPARisks(activities, saleActivities, requests) {
    const risks = [];

    if (saleActivities.length > 0) {
      risks.push({
        level: 'medium',
        category: 'data_sales',
        description: `发现 ${saleActivities.length} 次数据销售活动`,
        impact: '必须提供退出机制'
      });
    }

    const responseTimes = this.calculateResponseTimes(requests);
    if (responseTimes.avg > 45) {
      risks.push({
        level: 'high',
        category: 'response_time',
        description: `平均响应时间 ${responseTimes.avg} 天，超过 45 天限制`,
        impact: '违反CCPA第1798.130条'
      });
    }

    return risks;
  }

  generateCCPARecommendations(activities, saleActivities, requests) {
    const recommendations = [];

    if (saleActivities.length > 0) {
      recommendations.push({
        priority: 'high',
        action: '实现"不要出售我的信息"退出机制',
        details: 'CCPA要求必须提供退出选项'
      });
    }

    const responseTimes = this.calculateResponseTimes(requests);
    if (responseTimes.avg > 30) {
      recommendations.push({
        priority: 'medium',
        action: '缩短消费者请求响应时间',
        details: `当前平均 ${responseTimes.avg} 天，建议 30 天内`
      });
    }

    return recommendations;
  }

  extractSources(activities) {
    const sources = new Set();
    for (const activity of activities) {
      if (activity.details?.source) {
        sources.add(activity.details.source);
      }
    }
    return Array.from(sources);
  }

  extractThirdParties(activities) {
    const parties = new Set();
    for (const activity of activities) {
      if (activity.details?.thirdParty) {
        parties.add(activity.details.thirdParty);
      }
    }
    return Array.from(parties);
  }
}

module.exports = ComplianceReporter;
