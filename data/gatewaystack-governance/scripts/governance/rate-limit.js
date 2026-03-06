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
exports.checkRateLimit = checkRateLimit;
const fs = __importStar(require("fs"));
const constants_js_1 = require("./constants.js");
const LOCK_PATH = constants_js_1.RATE_LIMIT_STATE_PATH + ".lock";
const LOCK_TIMEOUT_MS = 5000;
const LOCK_RETRY_MS = 50;
function isLockStale() {
    try {
        const pidStr = fs.readFileSync(LOCK_PATH, "utf-8").trim();
        const pid = parseInt(pidStr, 10);
        if (isNaN(pid))
            return true;
        // process.kill(pid, 0) throws if the process doesn't exist
        process.kill(pid, 0);
        return false; // process is alive, lock is valid
    }
    catch {
        return true; // can't read or process is dead — stale lock
    }
}
function acquireLock() {
    const deadline = Date.now() + LOCK_TIMEOUT_MS;
    while (Date.now() < deadline) {
        try {
            // O_EXCL: fail if file exists — atomic advisory lock
            fs.writeFileSync(LOCK_PATH, String(process.pid), { flag: "wx" });
            return true;
        }
        catch {
            // Lock file exists — check if the holding process is still alive
            if (isLockStale()) {
                try {
                    fs.unlinkSync(LOCK_PATH);
                    continue; // retry immediately after clearing stale lock
                }
                catch {
                    // another process beat us to cleanup — retry normally
                }
            }
            // Lock held by a live process — spin-wait
            const start = Date.now();
            while (Date.now() - start < LOCK_RETRY_MS) {
                // busy wait
            }
        }
    }
    return false;
}
function releaseLock() {
    try {
        fs.unlinkSync(LOCK_PATH);
    }
    catch {
        // Lock already released or never acquired
    }
}
function loadRateLimitState() {
    if (fs.existsSync(constants_js_1.RATE_LIMIT_STATE_PATH)) {
        try {
            return JSON.parse(fs.readFileSync(constants_js_1.RATE_LIMIT_STATE_PATH, "utf-8"));
        }
        catch {
            return {};
        }
    }
    return {};
}
function saveRateLimitState(state) {
    fs.writeFileSync(constants_js_1.RATE_LIMIT_STATE_PATH, JSON.stringify(state, null, 2));
}
function _checkRateLimitInner(userId, session, policy) {
    const state = loadRateLimitState();
    const now = Date.now();
    // Per-user check
    const userKey = `user:${userId}`;
    const userState = state[userKey] || { calls: [] };
    const userWindow = policy.rateLimits.perUser.windowSeconds * 1000;
    userState.calls = userState.calls.filter((c) => now - c.timestamp < userWindow);
    if (userState.calls.length >= policy.rateLimits.perUser.maxCalls) {
        return {
            allowed: false,
            detail: `User ${userId} exceeded rate limit: ${policy.rateLimits.perUser.maxCalls} calls per ${policy.rateLimits.perUser.windowSeconds}s (current: ${userState.calls.length})`,
        };
    }
    // Per-session check
    if (session) {
        const sessionKey = `session:${session}`;
        const sessionState = state[sessionKey] || { calls: [] };
        const sessionWindow = policy.rateLimits.perSession.windowSeconds * 1000;
        sessionState.calls = sessionState.calls.filter((c) => now - c.timestamp < sessionWindow);
        if (sessionState.calls.length >= policy.rateLimits.perSession.maxCalls) {
            return {
                allowed: false,
                detail: `Session ${session} exceeded rate limit: ${policy.rateLimits.perSession.maxCalls} calls per ${policy.rateLimits.perSession.windowSeconds}s`,
            };
        }
        sessionState.calls.push({ timestamp: now });
        state[sessionKey] = sessionState;
    }
    userState.calls.push({ timestamp: now });
    state[userKey] = userState;
    saveRateLimitState(state);
    return {
        allowed: true,
        detail: `Rate limit OK: ${userState.calls.length}/${policy.rateLimits.perUser.maxCalls} calls in window`,
    };
}
function checkRateLimit(userId, session, policy) {
    if (!acquireLock()) {
        return {
            allowed: false,
            detail: "Rate limit state lock timeout — concurrent access. Try again.",
        };
    }
    try {
        return _checkRateLimitInner(userId, session, policy);
    }
    finally {
        releaseLock();
    }
}
