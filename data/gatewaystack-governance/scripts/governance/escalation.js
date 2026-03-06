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
exports.classifyInjectionSeverity = classifyInjectionSeverity;
exports.isFirstTimeToolUse = isFirstTimeToolUse;
exports.recordToolUse = recordToolUse;
exports.hashArgs = hashArgs;
exports.generateApprovalToken = generateApprovalToken;
exports.checkApprovalToken = checkApprovalToken;
exports.hasApprovedToken = hasApprovedToken;
exports.consumeApprovedToken = consumeApprovedToken;
exports.approveToken = approveToken;
exports.formatReviewBlock = formatReviewBlock;
const fs = __importStar(require("fs"));
const crypto = __importStar(require("crypto"));
const constants_js_1 = require("./constants.js");
function classifyInjectionSeverity(matches) {
    if (matches.length === 0)
        return "NONE";
    for (const m of matches) {
        if (m.startsWith("HIGH:") ||
            m.startsWith("EXTRACTION:") ||
            m.startsWith("OBFUSCATED:")) {
            return "HIGH";
        }
    }
    for (const m of matches) {
        if (m.startsWith("MEDIUM:") ||
            m.startsWith("MULTILANG:") ||
            m.startsWith("CANARY:")) {
            return "MEDIUM";
        }
    }
    return "LOW";
}
function loadToolUsageState() {
    try {
        const data = fs.readFileSync(constants_js_1.FIRST_USE_STATE_PATH, "utf-8");
        return JSON.parse(data);
    }
    catch {
        return { agents: {} };
    }
}
function saveToolUsageState(state) {
    fs.writeFileSync(constants_js_1.FIRST_USE_STATE_PATH, JSON.stringify(state, null, 2));
}
function isFirstTimeToolUse(agentId, toolName) {
    const state = loadToolUsageState();
    const tools = state.agents[agentId] || [];
    return !tools.includes(toolName);
}
function recordToolUse(agentId, toolName) {
    const state = loadToolUsageState();
    if (!state.agents[agentId]) {
        state.agents[agentId] = [];
    }
    if (!state.agents[agentId].includes(toolName)) {
        state.agents[agentId].push(toolName);
    }
    saveToolUsageState(state);
}
function loadPendingReviews() {
    try {
        const data = fs.readFileSync(constants_js_1.PENDING_REVIEWS_PATH, "utf-8");
        return JSON.parse(data);
    }
    catch {
        return { reviews: [] };
    }
}
function savePendingReviews(state) {
    fs.writeFileSync(constants_js_1.PENDING_REVIEWS_PATH, JSON.stringify(state, null, 2));
}
function cleanExpiredReviews(state) {
    const now = Date.now();
    state.reviews = state.reviews.filter((r) => now - r.createdAt < r.ttlSeconds * 1000);
    return state;
}
function hashArgs(args) {
    return crypto.createHash("sha256").update(args).digest("hex").substring(0, 16);
}
function generateApprovalToken(toolName, argsHash, ttlSeconds) {
    const token = `gw-rev-${crypto.randomBytes(8).toString("hex")}`;
    const state = cleanExpiredReviews(loadPendingReviews());
    state.reviews.push({
        token,
        toolName,
        argsHash,
        createdAt: Date.now(),
        ttlSeconds,
        approved: false,
    });
    savePendingReviews(state);
    return token;
}
function checkApprovalToken(token, toolName, argsHash) {
    const state = cleanExpiredReviews(loadPendingReviews());
    const review = state.reviews.find((r) => r.token === token &&
        r.toolName === toolName &&
        r.argsHash === argsHash &&
        r.approved);
    if (review) {
        // Consume the token
        state.reviews = state.reviews.filter((r) => r.token !== token);
        savePendingReviews(state);
        return true;
    }
    return false;
}
/**
 * Check if any approved token exists for this tool + args combination.
 * Used by before_tool_call to allow retries after approval.
 */
function hasApprovedToken(toolName, argsHash) {
    const state = cleanExpiredReviews(loadPendingReviews());
    return state.reviews.some((r) => r.toolName === toolName && r.argsHash === argsHash && r.approved);
}
/**
 * Consume the first matching approved token for this tool + args.
 */
function consumeApprovedToken(toolName, argsHash) {
    const state = cleanExpiredReviews(loadPendingReviews());
    const idx = state.reviews.findIndex((r) => r.toolName === toolName && r.argsHash === argsHash && r.approved);
    if (idx >= 0) {
        state.reviews.splice(idx, 1);
        savePendingReviews(state);
        return true;
    }
    return false;
}
/**
 * Approve a pending review token (called by CLI `gatewaystack approve <token>`).
 */
function approveToken(token) {
    const state = cleanExpiredReviews(loadPendingReviews());
    const review = state.reviews.find((r) => r.token === token && !r.approved);
    if (!review) {
        return {
            success: false,
            detail: `Token "${token}" not found or expired`,
        };
    }
    review.approved = true;
    savePendingReviews(state);
    return {
        success: true,
        detail: `Approved: tool="${review.toolName}" (token expires in ${review.ttlSeconds}s)`,
    };
}
// ---------------------------------------------------------------------------
// Review block formatting
// ---------------------------------------------------------------------------
function formatReviewBlock(reason, token) {
    return (`[REVIEW REQUIRED] ${reason}\n\n` +
        `To approve this tool call, run:\n` +
        `  gatewaystack-governance approve ${token}\n\n` +
        `Then retry the tool call. Token expires in 5 minutes.`);
}
