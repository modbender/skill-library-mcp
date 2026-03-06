"use strict";
/**
 * GatewayStack Governance — OpenClaw Plugin
 *
 * Registers a `before_tool_call` hook that automatically runs governance
 * checks on every tool invocation. The agent cannot bypass this — it runs
 * at the process level before any tool executes.
 *
 * Identity mapping uses OpenClaw agent IDs (e.g. "main", "ops", "dev")
 * rather than human users, since OpenClaw is a single-user personal AI.
 */
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
const path = __importStar(require("path"));
const os = __importStar(require("os"));
const governance_gateway_js_1 = require("../scripts/governance-gateway.js");
const policy_js_1 = require("../scripts/governance/policy.js");
const dlp_js_1 = require("../scripts/governance/dlp.js");
// Resolve policy path: check plugin directory first, then ~/.openclaw default
function resolvePolicyPath() {
    const pluginDir = path.resolve(__dirname, "..");
    const localPolicy = path.join(pluginDir, "policy.json");
    // Also check OpenClaw skills directory (for backward compat with skill installs)
    const openclawSkillPolicy = path.join(os.homedir(), ".openclaw", "skills", "gatewaystack-governance", "policy.json");
    // Prefer local plugin directory policy
    try {
        require("fs").accessSync(localPolicy);
        return localPolicy;
    }
    catch {
        // Fall through
    }
    // Try OpenClaw skills directory
    try {
        require("fs").accessSync(openclawSkillPolicy);
        return openclawSkillPolicy;
    }
    catch {
        // Fall through
    }
    // Default to local — will produce a clear error from checkGovernance
    return localPolicy;
}
const plugin = {
    id: "gatewaystack-governance",
    name: "GatewayStack Governance",
    description: "Automatic governance for every tool call — identity, scope, rate limiting, injection detection, audit logging, plus opt-in output DLP, escalation, and behavioral monitoring",
    register(api) {
        const policyPath = resolvePolicyPath();
        api.on("before_tool_call", async (event, ctx) => {
            const result = await (0, governance_gateway_js_1.checkGovernance)({
                toolName: event.toolName,
                args: JSON.stringify(event.params),
                userId: ctx.agentId ?? "unknown",
                session: ctx.sessionKey,
                policyPath,
            });
            if (!result.allowed) {
                return { block: true, blockReason: result.reason };
            }
            // Review verdict is already handled above (allowed: false, block: true)
            // but we set blockReason with the review instructions from formatReviewBlock
            return {};
        }, { priority: 0 });
        // --- Output DLP hooks ---
        // Cache policy at registration time for DLP hooks (avoids re-reading JSON on every call)
        let cachedPolicy = null;
        try {
            cachedPolicy = (0, policy_js_1.loadPolicy)(policyPath);
        }
        catch {
            // Policy load failure is already handled by before_tool_call
        }
        if (cachedPolicy?.outputDlp?.enabled) {
            const dlpMode = cachedPolicy.outputDlp.mode;
            if (dlpMode === "log") {
                // Log mode: observe output via after_tool_call (cannot modify)
                api.on("after_tool_call", async (event) => {
                    if (!event.output || !cachedPolicy)
                        return;
                    try {
                        const result = (0, dlp_js_1.scanOutput)(event.output, cachedPolicy);
                        (0, dlp_js_1.logDlpScan)(result, event.toolName, cachedPolicy);
                    }
                    catch {
                        // DLP scan failure should not break the agent
                    }
                }, { priority: 100 });
            }
            if (dlpMode === "block") {
                // Block mode: redact output via tool_result_persist
                api.on("tool_result_persist", async (event) => {
                    if (!event.output || !cachedPolicy)
                        return {};
                    try {
                        const scanResult = (0, dlp_js_1.scanOutput)(event.output, cachedPolicy);
                        (0, dlp_js_1.logDlpScan)(scanResult, event.toolName, cachedPolicy);
                        if (scanResult.hasMatches) {
                            const redacted = (0, dlp_js_1.redactOutput)(event.output, cachedPolicy);
                            return { output: redacted };
                        }
                    }
                    catch {
                        // DLP failure should not break the agent
                    }
                    return {};
                }, { priority: 0 });
            }
        }
        if (api.logger) {
            api.logger.info(`GatewayStack Governance loaded (policy: ${policyPath})`);
        }
    },
};
exports.default = plugin;
