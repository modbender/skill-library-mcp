"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.checkGovernance = checkGovernance;
const policy_js_1 = require("./policy.js");
const utils_js_1 = require("./utils.js");
const identity_js_1 = require("./identity.js");
const scope_js_1 = require("./scope.js");
const rate_limit_js_1 = require("./rate-limit.js");
const injection_js_1 = require("./injection.js");
const audit_js_1 = require("./audit.js");
const escalation_js_1 = require("./escalation.js");
const behavioral_js_1 = require("./behavioral.js");
async function checkGovernance(params) {
    const policy = (0, policy_js_1.loadPolicy)(params.policyPath);
    const requestId = (0, utils_js_1.generateRequestId)();
    const checks = {};
    // 0. Check for pre-approved escalation token
    if (policy.escalation?.enabled && params.args) {
        const argsH = (0, escalation_js_1.hashArgs)(params.args);
        if ((0, escalation_js_1.hasApprovedToken)(params.toolName, argsH)) {
            (0, escalation_js_1.consumeApprovedToken)(params.toolName, argsH);
            (0, escalation_js_1.recordToolUse)(params.userId, params.toolName);
            checks["escalation"] = {
                passed: true,
                detail: "Approved via escalation token",
            };
            const entry = {
                timestamp: new Date().toISOString(),
                requestId,
                action: "tool-check",
                tool: params.toolName,
                user: params.userId,
                session: params.session,
                allowed: true,
                reason: "Approved via escalation token",
                checks,
            };
            (0, audit_js_1.writeAuditLog)(entry, policy);
            return {
                allowed: true,
                requestId,
                verdict: "allow",
            };
        }
    }
    // 1. Identity verification
    const identity = (0, identity_js_1.verifyIdentity)(params.userId, undefined, policy);
    checks["identity"] = {
        passed: identity.verified,
        detail: identity.detail,
    };
    if (!identity.verified) {
        const entry = {
            timestamp: new Date().toISOString(),
            requestId,
            action: "tool-check",
            tool: params.toolName,
            user: params.userId,
            session: params.session,
            allowed: false,
            reason: "Identity verification failed",
            checks,
        };
        (0, audit_js_1.writeAuditLog)(entry, policy);
        return {
            allowed: false,
            reason: `Identity verification failed: ${identity.detail}`,
            requestId,
        };
    }
    // 2. Scope enforcement
    const scope = (0, scope_js_1.checkScope)(params.toolName, identity.roles, policy);
    checks["scope"] = { passed: scope.allowed, detail: scope.detail };
    if (!scope.allowed) {
        const entry = {
            timestamp: new Date().toISOString(),
            requestId,
            action: "tool-check",
            tool: params.toolName,
            user: params.userId,
            resolvedIdentity: identity.userId,
            roles: identity.roles,
            session: params.session,
            allowed: false,
            reason: "Scope check failed",
            checks,
        };
        (0, audit_js_1.writeAuditLog)(entry, policy);
        return {
            allowed: false,
            reason: `Scope check failed: ${scope.detail}`,
            requestId,
        };
    }
    // 3. Rate limiting
    const rateLimit = (0, rate_limit_js_1.checkRateLimit)(identity.userId, params.session, policy);
    checks["rateLimit"] = {
        passed: rateLimit.allowed,
        detail: rateLimit.detail,
    };
    if (!rateLimit.allowed) {
        const entry = {
            timestamp: new Date().toISOString(),
            requestId,
            action: "tool-check",
            tool: params.toolName,
            user: params.userId,
            resolvedIdentity: identity.userId,
            roles: identity.roles,
            session: params.session,
            allowed: false,
            reason: "Rate limit exceeded",
            checks,
        };
        (0, audit_js_1.writeAuditLog)(entry, policy);
        return {
            allowed: false,
            reason: `Rate limit exceeded: ${rateLimit.detail}`,
            requestId,
        };
    }
    // 4. Injection detection
    if (params.args) {
        const injection = (0, injection_js_1.detectInjection)(params.args, policy);
        checks["injection"] = {
            passed: injection.clean,
            detail: injection.clean
                ? injection.detail
                : `${injection.detail}: ${injection.matches.join("; ")}`,
        };
        if (!injection.clean) {
            const severity = (0, escalation_js_1.classifyInjectionSeverity)(injection.matches);
            // Step 4: MEDIUM + escalation enabled → review instead of block
            if (severity === "MEDIUM" &&
                policy.escalation?.enabled &&
                policy.escalation.reviewOnMediumInjection) {
                const argsH = (0, escalation_js_1.hashArgs)(params.args);
                const token = (0, escalation_js_1.generateApprovalToken)(params.toolName, argsH, policy.escalation.tokenTTLSeconds);
                const reviewReason = `Medium-severity injection detected: ${injection.matches.join("; ")}`;
                const entry = {
                    timestamp: new Date().toISOString(),
                    requestId,
                    action: "tool-check",
                    tool: params.toolName,
                    user: params.userId,
                    resolvedIdentity: identity.userId,
                    roles: identity.roles,
                    session: params.session,
                    allowed: false,
                    reason: "Escalation: review required (medium injection)",
                    checks,
                };
                (0, audit_js_1.writeAuditLog)(entry, policy);
                return {
                    allowed: false,
                    reason: (0, escalation_js_1.formatReviewBlock)(reviewReason, token),
                    requestId,
                    patterns: injection.matches,
                    verdict: "review",
                    reviewReason,
                };
            }
            // HIGH or LOW (without escalation) → block
            const entry = {
                timestamp: new Date().toISOString(),
                requestId,
                action: "tool-check",
                tool: params.toolName,
                user: params.userId,
                resolvedIdentity: identity.userId,
                roles: identity.roles,
                session: params.session,
                allowed: false,
                reason: "Prompt injection detected",
                checks,
            };
            (0, audit_js_1.writeAuditLog)(entry, policy);
            return {
                allowed: false,
                reason: `Blocked: potential prompt injection detected in tool arguments. ${injection.matches.length} pattern(s) matched.`,
                requestId,
                patterns: injection.matches,
                verdict: "block",
            };
        }
        // Check args length
        const toolPolicy = policy.allowedTools[params.toolName];
        if (toolPolicy?.maxArgsLength &&
            params.args.length > toolPolicy.maxArgsLength) {
            checks["argsLength"] = {
                passed: false,
                detail: `Args length ${params.args.length} exceeds limit ${toolPolicy.maxArgsLength}`,
            };
            const entry = {
                timestamp: new Date().toISOString(),
                requestId,
                action: "tool-check",
                tool: params.toolName,
                user: params.userId,
                resolvedIdentity: identity.userId,
                roles: identity.roles,
                session: params.session,
                allowed: false,
                reason: "Arguments too long",
                checks,
            };
            (0, audit_js_1.writeAuditLog)(entry, policy);
            return {
                allowed: false,
                reason: `Tool arguments exceed maximum length (${params.args.length} > ${toolPolicy.maxArgsLength})`,
                requestId,
            };
        }
    }
    // 4.5. First-time tool usage review
    if (policy.escalation?.enabled &&
        policy.escalation.reviewOnFirstToolUse &&
        (0, escalation_js_1.isFirstTimeToolUse)(params.userId, params.toolName)) {
        const argsH = (0, escalation_js_1.hashArgs)(params.args || "");
        const token = (0, escalation_js_1.generateApprovalToken)(params.toolName, argsH, policy.escalation.tokenTTLSeconds);
        const reviewReason = `First-time use of tool "${params.toolName}" by "${params.userId}"`;
        checks["firstUse"] = {
            passed: false,
            detail: reviewReason,
        };
        const entry = {
            timestamp: new Date().toISOString(),
            requestId,
            action: "tool-check",
            tool: params.toolName,
            user: params.userId,
            resolvedIdentity: identity.userId,
            roles: identity.roles,
            session: params.session,
            allowed: false,
            reason: "Escalation: review required (first tool use)",
            checks,
        };
        (0, audit_js_1.writeAuditLog)(entry, policy);
        return {
            allowed: false,
            reason: (0, escalation_js_1.formatReviewBlock)(reviewReason, token),
            requestId,
            verdict: "review",
            reviewReason,
        };
    }
    // 5. Behavioral monitoring
    if (policy.behavioralMonitoring?.enabled) {
        const auditPath = policy.auditLog?.path || "audit.jsonl";
        const windowCalls = (0, behavioral_js_1.countCurrentWindowCalls)(auditPath, policy.behavioralMonitoring.monitoringWindowSeconds);
        const anomalies = (0, behavioral_js_1.detectAnomalies)(params.toolName, windowCalls, params.userId, policy);
        if (anomalies.length > 0) {
            checks["behavioral"] = {
                passed: false,
                detail: anomalies.map((a) => `[${a.severity}] ${a.type}: ${a.detail}`).join("; "),
            };
            const action = policy.behavioralMonitoring.action;
            if (action === "block") {
                const entry = {
                    timestamp: new Date().toISOString(),
                    requestId,
                    action: "tool-check",
                    tool: params.toolName,
                    user: params.userId,
                    resolvedIdentity: identity.userId,
                    roles: identity.roles,
                    session: params.session,
                    allowed: false,
                    reason: "Behavioral anomaly detected",
                    checks,
                    anomalies,
                };
                (0, audit_js_1.writeAuditLog)(entry, policy);
                return {
                    allowed: false,
                    reason: `Blocked: behavioral anomaly detected — ${anomalies.map((a) => a.detail).join("; ")}`,
                    requestId,
                    verdict: "block",
                };
            }
            if (action === "review" && policy.escalation?.enabled) {
                const argsH = (0, escalation_js_1.hashArgs)(params.args || "");
                const token = (0, escalation_js_1.generateApprovalToken)(params.toolName, argsH, policy.escalation.tokenTTLSeconds);
                const reviewReason = `Behavioral anomaly: ${anomalies.map((a) => a.detail).join("; ")}`;
                const entry = {
                    timestamp: new Date().toISOString(),
                    requestId,
                    action: "tool-check",
                    tool: params.toolName,
                    user: params.userId,
                    resolvedIdentity: identity.userId,
                    roles: identity.roles,
                    session: params.session,
                    allowed: false,
                    reason: "Escalation: review required (behavioral anomaly)",
                    checks,
                    anomalies,
                };
                (0, audit_js_1.writeAuditLog)(entry, policy);
                return {
                    allowed: false,
                    reason: (0, escalation_js_1.formatReviewBlock)(reviewReason, token),
                    requestId,
                    verdict: "review",
                    reviewReason,
                };
            }
            // action === "log" — continue but log the anomaly
            const entry = {
                timestamp: new Date().toISOString(),
                requestId,
                action: "behavioral-anomaly",
                tool: params.toolName,
                user: params.userId,
                resolvedIdentity: identity.userId,
                roles: identity.roles,
                session: params.session,
                allowed: true,
                reason: "Behavioral anomaly logged (action: log)",
                anomalies,
            };
            (0, audit_js_1.writeAuditLog)(entry, policy);
        }
        else {
            checks["behavioral"] = {
                passed: true,
                detail: "No anomalies detected",
            };
        }
    }
    // All checks passed — record tool use for escalation tracking
    if (policy.escalation?.enabled) {
        (0, escalation_js_1.recordToolUse)(params.userId, params.toolName);
    }
    const entry = {
        timestamp: new Date().toISOString(),
        requestId,
        action: "tool-check",
        tool: params.toolName,
        user: params.userId,
        resolvedIdentity: identity.userId,
        roles: identity.roles,
        session: params.session,
        allowed: true,
        reason: "All governance checks passed",
        checks,
    };
    (0, audit_js_1.writeAuditLog)(entry, policy);
    return {
        allowed: true,
        requestId,
        identity: identity.userId,
        roles: identity.roles,
        verdict: "allow",
    };
}
