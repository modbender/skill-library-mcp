#!/usr/bin/env node
"use strict";

const { Logger } = require("./logger");

/**
 * Restriction patterns that indicate Google AI access issues.
 * Each pattern has an id, a test function, and a recommended action.
 */
const RESTRICTION_PATTERNS = [
  {
    id: "rate_limit",
    name: "Rate Limiting",
    test: (response) =>
      response.status === 429 ||
      (response.headers &&
        parseInt(response.headers["x-ratelimit-remaining"], 10) === 0),
    action: "rotate_session",
    severity: "high",
  },
  {
    id: "auth_expired",
    name: "Authentication Expired",
    test: (response) =>
      response.status === 401 ||
      (response.body && /token.*expired/i.test(JSON.stringify(response.body))),
    action: "refresh_token",
    severity: "medium",
  },
  {
    id: "geo_block",
    name: "Geographic Restriction",
    test: (response) =>
      response.status === 403 &&
      response.body &&
      /region|geo|country|location/i.test(JSON.stringify(response.body)),
    action: "switch_proxy",
    severity: "high",
  },
  {
    id: "ip_block",
    name: "IP-based Block",
    test: (response) =>
      response.status === 403 &&
      response.body &&
      /ip|address|blocked|banned/i.test(JSON.stringify(response.body)),
    action: "switch_proxy",
    severity: "critical",
  },
  {
    id: "service_unavailable",
    name: "Service Unavailable",
    test: (response) => response.status === 503,
    action: "wait_retry",
    severity: "low",
  },
  {
    id: "access_denied",
    name: "General Access Denied",
    test: (response) =>
      response.status === 403 &&
      response.body &&
      /denied|forbidden|restrict/i.test(JSON.stringify(response.body)),
    action: "rotate_session",
    severity: "high",
  },
];

class Detector {
  constructor(config = {}, logger) {
    this.config = config;
    this.logger = logger || new Logger({ silent: true });
    this.detectionHistory = [];
  }

  /**
   * Analyze an API response for restriction patterns.
   * @param {object} response - { status, headers, body }
   * @returns {{ restricted: boolean, patterns: Array, actions: Array }}
   */
  analyze(response) {
    if (!response || typeof response.status !== "number") {
      this.logger.warn("Detector received invalid response object");
      return { restricted: false, patterns: [], actions: [] };
    }

    const matched = [];
    for (const pattern of RESTRICTION_PATTERNS) {
      try {
        if (pattern.test(response)) {
          matched.push({
            id: pattern.id,
            name: pattern.name,
            action: pattern.action,
            severity: pattern.severity,
          });
          this.logger.info(`Restriction detected: ${pattern.name}`, {
            id: pattern.id,
            severity: pattern.severity,
          });
        }
      } catch (err) {
        this.logger.error(`Error testing pattern ${pattern.id}: ${err.message}`);
      }
    }

    const result = {
      restricted: matched.length > 0,
      patterns: matched,
      actions: [...new Set(matched.map((m) => m.action))],
      timestamp: new Date().toISOString(),
    };

    this.detectionHistory.push(result);
    return result;
  }

  /**
   * Check if a response indicates a successful (unrestricted) access.
   * @param {object} response
   * @returns {boolean}
   */
  isAccessible(response) {
    if (!response) return false;
    return response.status >= 200 && response.status < 300;
  }

  /**
   * Get the recommended action based on detection severity priority.
   * @param {object} analysis - Result from analyze()
   * @returns {string|null}
   */
  getRecommendedAction(analysis) {
    if (!analysis || !analysis.restricted) return null;

    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    const sorted = [...analysis.patterns].sort(
      (a, b) =>
        (severityOrder[a.severity] ?? 99) - (severityOrder[b.severity] ?? 99)
    );

    return sorted[0]?.action || null;
  }

  /**
   * Get detection history.
   */
  getHistory() {
    return [...this.detectionHistory];
  }

  /**
   * Determine if rate limiting is being applied based on recent history.
   * @param {number} windowSize - Number of recent detections to check
   * @returns {boolean}
   */
  isRateLimited(windowSize = 5) {
    const recent = this.detectionHistory.slice(-windowSize);
    const rateLimitCount = recent.filter((r) =>
      r.patterns.some((p) => p.id === "rate_limit")
    ).length;
    return rateLimitCount >= Math.ceil(windowSize / 2);
  }

  /**
   * Generate a diagnostic summary of recent detections.
   */
  getDiagnostics() {
    const total = this.detectionHistory.length;
    const restricted = this.detectionHistory.filter((d) => d.restricted).length;
    const patternCounts = {};

    for (const detection of this.detectionHistory) {
      for (const pattern of detection.patterns) {
        patternCounts[pattern.id] = (patternCounts[pattern.id] || 0) + 1;
      }
    }

    return {
      totalChecks: total,
      restrictedCount: restricted,
      unrestricted: total - restricted,
      patternCounts,
      isRateLimited: this.isRateLimited(),
      generatedAt: new Date().toISOString(),
    };
  }
}

module.exports = { Detector, RESTRICTION_PATTERNS };
