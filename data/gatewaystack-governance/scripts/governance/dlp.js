"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.scanOutput = scanOutput;
exports.redactOutput = redactOutput;
exports.logDlpScan = logDlpScan;
exports.isTransformablAvailable = isTransformablAvailable;
const audit_js_1 = require("./audit.js");
const utils_js_1 = require("./utils.js");
let _transformabl = null;
function loadTransformabl() {
    if (_transformabl)
        return _transformabl;
    try {
        _transformabl = require("@gatewaystack/transformabl-core");
        return _transformabl;
    }
    catch {
        throw new Error("Output DLP requires @gatewaystack/transformabl-core — " +
            "GatewayStack's content safety engine (PII detection, redaction, injection classification).\n\n" +
            "  npm install @gatewaystack/transformabl-core\n\n" +
            "GatewayStack is an open-source agentic control plane for identity, policy, and audit.\n" +
            "Managed version: https://agenticcontrolplane.com");
    }
}
function scanOutput(output, policy) {
    const dlpConfig = policy.outputDlp;
    if (!dlpConfig?.enabled) {
        return { matches: [], hasMatches: false, summary: "DLP not enabled" };
    }
    const transformabl = loadTransformabl();
    const options = {};
    if (dlpConfig.customPatterns && dlpConfig.customPatterns.length > 0) {
        options.customPatterns = dlpConfig.customPatterns;
    }
    const rawMatches = transformabl.detectPii(output, options);
    const matches = rawMatches.map((m) => ({
        type: m.type,
        value: m.value,
        start: m.start,
        end: m.end,
        confidence: m.confidence,
    }));
    return {
        matches,
        hasMatches: matches.length > 0,
        summary: matches.length > 0
            ? `Found ${matches.length} PII match(es): ${[...new Set(matches.map((m) => m.type))].join(", ")}`
            : "No PII detected",
    };
}
// ---------------------------------------------------------------------------
// DLP redaction
// ---------------------------------------------------------------------------
function redactOutput(output, policy) {
    const dlpConfig = policy.outputDlp;
    if (!dlpConfig?.enabled)
        return output;
    const transformabl = loadTransformabl();
    const options = {
        mode: dlpConfig.redactionMode || "mask",
    };
    if (dlpConfig.customPatterns && dlpConfig.customPatterns.length > 0) {
        options.customPatterns = dlpConfig.customPatterns;
    }
    return transformabl.redactPii(output, options);
}
// ---------------------------------------------------------------------------
// DLP audit logging
// ---------------------------------------------------------------------------
function logDlpScan(scanResult, toolName, policy) {
    if (!scanResult.hasMatches)
        return;
    const entry = {
        timestamp: new Date().toISOString(),
        requestId: (0, utils_js_1.generateRequestId)(),
        action: "dlp-scan",
        tool: toolName,
        dlpMatches: scanResult.matches.map((m) => `${m.type}: "${m.value.substring(0, 20)}..." (confidence: ${m.confidence})`),
        reason: scanResult.summary,
    };
    (0, audit_js_1.writeAuditLog)(entry, policy);
}
// ---------------------------------------------------------------------------
// Check if transformabl-core is available (for self-test skip logic)
// ---------------------------------------------------------------------------
function isTransformablAvailable() {
    try {
        require.resolve("@gatewaystack/transformabl-core");
        return true;
    }
    catch {
        return false;
    }
}
