"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildBaseline = buildBaseline;
exports.detectAnomalies = detectAnomalies;
exports.countCurrentWindowCalls = countCurrentWindowCalls;
exports.isLimitablAvailable = isLimitablAvailable;
exports.clearBaselineCache = clearBaselineCache;
const fs = __importStar(require("fs"));
const constants_js_1 = require("./constants.js");
let _limitabl = null;
function loadLimitabl() {
    if (_limitabl)
        return _limitabl;
    try {
        _limitabl = require("@gatewaystack/limitabl-core");
        return _limitabl;
    }
    catch {
        throw new Error("Behavioral monitoring requires @gatewaystack/limitabl-core — " +
            "GatewayStack's rate limiting and agent guard engine (workflow limits, budget tracking, runaway prevention).\n\n" +
            "  npm install @gatewaystack/limitabl-core\n\n" +
            "GatewayStack is an open-source agentic control plane for identity, policy, and audit.\n" +
            "Managed version: https://agenticcontrolplane.com");
    }
}
// ---------------------------------------------------------------------------
// In-memory baseline cache (60s TTL)
// ---------------------------------------------------------------------------
let _baselineCache = null;
let _baselineCacheTime = 0;
const BASELINE_CACHE_TTL_MS = 60_000;
function getCachedBaseline() {
    if (_baselineCache && Date.now() - _baselineCacheTime < BASELINE_CACHE_TTL_MS) {
        return _baselineCache;
    }
    // Try loading from file
    try {
        const data = fs.readFileSync(constants_js_1.BEHAVIORAL_BASELINE_PATH, "utf-8");
        _baselineCache = JSON.parse(data);
        _baselineCacheTime = Date.now();
        return _baselineCache;
    }
    catch {
        return null;
    }
}
// ---------------------------------------------------------------------------
// Build baseline from audit log (offline)
// ---------------------------------------------------------------------------
function buildBaseline(auditLogPath, windowSeconds) {
    let lines;
    try {
        const raw = fs.readFileSync(auditLogPath, "utf-8");
        lines = raw.trim().split("\n").filter(Boolean);
    }
    catch {
        return {
            avgCallsPerWindow: 0,
            toolsSeen: [],
            totalCalls: 0,
            windowSeconds,
        };
    }
    const toolsSeen = new Set();
    const timestamps = [];
    for (const line of lines) {
        try {
            const entry = JSON.parse(line);
            if (entry.action === "tool-check" && entry.tool) {
                toolsSeen.add(entry.tool);
                timestamps.push(new Date(entry.timestamp).getTime());
            }
        }
        catch {
            // Skip malformed lines
        }
    }
    if (timestamps.length === 0) {
        return {
            avgCallsPerWindow: 0,
            toolsSeen: [...toolsSeen],
            totalCalls: 0,
            windowSeconds,
        };
    }
    // Calculate average calls per window
    const minTs = Math.min(...timestamps);
    const maxTs = Math.max(...timestamps);
    const spanMs = maxTs - minTs;
    const windowMs = windowSeconds * 1000;
    const numWindows = Math.max(1, Math.ceil(spanMs / windowMs));
    const avgCallsPerWindow = timestamps.length / numWindows;
    const baseline = {
        avgCallsPerWindow,
        toolsSeen: [...toolsSeen],
        totalCalls: timestamps.length,
        windowSeconds,
    };
    // Save to file for caching
    fs.writeFileSync(constants_js_1.BEHAVIORAL_BASELINE_PATH, JSON.stringify(baseline, null, 2));
    _baselineCache = baseline;
    _baselineCacheTime = Date.now();
    return baseline;
}
// ---------------------------------------------------------------------------
// Anomaly detection
// ---------------------------------------------------------------------------
function detectAnomalies(toolName, currentWindowCalls, agentId, policy) {
    const config = policy.behavioralMonitoring;
    if (!config?.enabled)
        return [];
    const anomalies = [];
    const baseline = getCachedBaseline();
    if (!baseline) {
        // No baseline exists — flag as unusual
        anomalies.push({
            type: "unusual-pattern",
            severity: "low",
            detail: `No behavioral baseline found for agent "${agentId}". Run 'gatewaystack-governance --action build-baseline' to create one.`,
        });
        return anomalies;
    }
    // Check for new tool usage
    if (!baseline.toolsSeen.includes(toolName)) {
        anomalies.push({
            type: "new-tool",
            severity: "medium",
            detail: `Agent "${agentId}" is using tool "${toolName}" for the first time (not in baseline of ${baseline.toolsSeen.length} known tools)`,
        });
    }
    // Check for frequency spike
    if (baseline.avgCallsPerWindow > 0 &&
        currentWindowCalls > baseline.avgCallsPerWindow * config.spikeThreshold) {
        anomalies.push({
            type: "frequency-spike",
            severity: "high",
            detail: `Current call rate (${currentWindowCalls} calls/window) exceeds ${config.spikeThreshold}x baseline (${baseline.avgCallsPerWindow.toFixed(1)} calls/window)`,
        });
    }
    return anomalies;
}
// ---------------------------------------------------------------------------
// Count calls in the current monitoring window from audit log
// ---------------------------------------------------------------------------
function countCurrentWindowCalls(auditLogPath, windowSeconds) {
    try {
        const raw = fs.readFileSync(auditLogPath, "utf-8");
        const lines = raw.trim().split("\n").filter(Boolean);
        const cutoff = Date.now() - windowSeconds * 1000;
        let count = 0;
        for (const line of lines) {
            try {
                const entry = JSON.parse(line);
                if (entry.action === "tool-check" &&
                    new Date(entry.timestamp).getTime() > cutoff) {
                    count++;
                }
            }
            catch {
                // Skip malformed
            }
        }
        return count;
    }
    catch {
        return 0;
    }
}
// ---------------------------------------------------------------------------
// Check if limitabl-core is available (for self-test skip logic)
// ---------------------------------------------------------------------------
function isLimitablAvailable() {
    try {
        require.resolve("@gatewaystack/limitabl-core");
        return true;
    }
    catch {
        return false;
    }
}
// Export for testing
function clearBaselineCache() {
    _baselineCache = null;
    _baselineCacheTime = 0;
}
