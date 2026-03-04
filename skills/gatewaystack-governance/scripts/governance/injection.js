"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.deobfuscate = deobfuscate;
exports.checkCanaryTokens = checkCanaryTokens;
exports.detectInjection = detectInjection;
const constants_js_1 = require("./constants.js");
// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
/** Scan `input` against a list of regex patterns, returning prefixed matches. */
function scanPatterns(input, patterns, prefix) {
    const matches = [];
    for (const pattern of patterns) {
        const match = input.match(pattern);
        if (match) {
            matches.push(`${prefix}: ${pattern.source} → "${match[0]}"`);
        }
    }
    return matches;
}
/** Returns true when >80 % of characters are printable ASCII or common Unicode. */
function isPrintable(s) {
    let printable = 0;
    for (let i = 0; i < s.length; i++) {
        const code = s.charCodeAt(i);
        // printable ASCII 0x20-0x7E, or above 0xA0 (accented, CJK, etc.)
        if ((code >= 0x20 && code <= 0x7e) || code >= 0xa0) {
            printable++;
        }
    }
    return printable / s.length > 0.8;
}
/**
 * Extract plausible encoded segments from `input`, decode them, and return
 * candidates that look like printable text.
 *
 * Intentionally non-recursive to prevent exponential blowup.
 */
function deobfuscate(input) {
    const candidates = [];
    // Base64: contiguous block of base64 chars, length ≥ 16
    const b64Re = /[A-Za-z0-9+/]{16,}={0,2}/g;
    let m;
    while ((m = b64Re.exec(input)) !== null) {
        try {
            const decoded = Buffer.from(m[0], "base64").toString("utf-8");
            if (decoded.length > 0 && isPrintable(decoded)) {
                candidates.push({ method: "base64", decoded });
            }
        }
        catch {
            // ignore decode failures
        }
    }
    // Hex: contiguous hex string, length ≥ 16, even length
    const hexRe = /[0-9a-fA-F]{16,}/g;
    while ((m = hexRe.exec(input)) !== null) {
        if (m[0].length % 2 !== 0)
            continue;
        try {
            const decoded = Buffer.from(m[0], "hex").toString("utf-8");
            if (decoded.length > 0 && isPrintable(decoded)) {
                candidates.push({ method: "hex", decoded });
            }
        }
        catch {
            // ignore decode failures
        }
    }
    // URL encoding: 3+ percent-encoded sequences
    const urlRe = /(?:%[0-9a-fA-F]{2}){3,}/g;
    while ((m = urlRe.exec(input)) !== null) {
        try {
            const decoded = decodeURIComponent(m[0]);
            if (decoded.length > 0 && isPrintable(decoded)) {
                candidates.push({ method: "url-encoding", decoded });
            }
        }
        catch {
            // ignore decode failures
        }
    }
    // Unicode escapes: 2+ \\uXXXX sequences
    const unicodeRe = /(?:\\u[0-9a-fA-F]{4}){2,}/g;
    while ((m = unicodeRe.exec(input)) !== null) {
        try {
            const decoded = JSON.parse(`"${m[0]}"`);
            if (typeof decoded === "string" && decoded.length > 0 && isPrintable(decoded)) {
                candidates.push({ method: "unicode-escape", decoded });
            }
        }
        catch {
            // ignore parse failures
        }
    }
    return candidates;
}
// ---------------------------------------------------------------------------
// Canary token detection
// ---------------------------------------------------------------------------
function checkCanaryTokens(input, tokens) {
    const matches = [];
    const lowerInput = input.toLowerCase();
    for (const token of tokens) {
        if (!token || !token.trim())
            continue;
        if (lowerInput.includes(token.toLowerCase())) {
            const display = token.length > 20 ? token.slice(0, 20) + "…" : token;
            matches.push(`CANARY: token detected → "${display}"`);
        }
    }
    return matches;
}
// ---------------------------------------------------------------------------
// Main detection entry point
// ---------------------------------------------------------------------------
function detectInjection(args, policy) {
    if (!policy.injectionDetection.enabled) {
        return { clean: true, detail: "Injection detection disabled", matches: [] };
    }
    const sensitivity = policy.injectionDetection.sensitivity;
    const matches = [];
    // Phase 1: Raw scan — built-in patterns by severity
    matches.push(...scanPatterns(args, constants_js_1.INJECTION_PATTERNS_HIGH, "HIGH"));
    matches.push(...scanPatterns(args, constants_js_1.INJECTION_PATTERNS_EXTRACTION, "HIGH"));
    if (sensitivity === "medium" || sensitivity === "high") {
        matches.push(...scanPatterns(args, constants_js_1.INJECTION_PATTERNS_MEDIUM, "MEDIUM"));
    }
    if (sensitivity === "high") {
        matches.push(...scanPatterns(args, constants_js_1.INJECTION_PATTERNS_LOW, "LOW"));
    }
    // Phase 2: Multi-language scan
    if (policy.injectionDetection.multiLanguage !== false) {
        matches.push(...scanPatterns(args, constants_js_1.INJECTION_PATTERNS_MULTILANG, "MULTILANG"));
    }
    // Phase 3: Obfuscation decode-then-rescan
    if (policy.injectionDetection.obfuscationDetection !== false) {
        const decoded = deobfuscate(args);
        for (const candidate of decoded) {
            const prefix = `OBFUSCATED [${candidate.method}]`;
            matches.push(...scanPatterns(candidate.decoded, constants_js_1.INJECTION_PATTERNS_HIGH, prefix));
            matches.push(...scanPatterns(candidate.decoded, constants_js_1.INJECTION_PATTERNS_EXTRACTION, prefix));
            if (sensitivity === "medium" || sensitivity === "high") {
                matches.push(...scanPatterns(candidate.decoded, constants_js_1.INJECTION_PATTERNS_MEDIUM, prefix));
            }
            if (policy.injectionDetection.multiLanguage !== false) {
                matches.push(...scanPatterns(candidate.decoded, constants_js_1.INJECTION_PATTERNS_MULTILANG, prefix));
            }
        }
    }
    // Phase 4: Canary token check
    if (policy.injectionDetection.canaryTokens &&
        policy.injectionDetection.canaryTokens.length > 0) {
        matches.push(...checkCanaryTokens(args, policy.injectionDetection.canaryTokens));
    }
    // Phase 5: Custom patterns (unchanged) — guarded with per-pattern timeout
    if (policy.injectionDetection.customPatterns) {
        for (const patternStr of policy.injectionDetection.customPatterns) {
            try {
                const pattern = new RegExp(patternStr, "i");
                const start = Date.now();
                const match = args.match(pattern);
                const elapsed = Date.now() - start;
                if (elapsed > 50) {
                    // Pattern took too long — likely ReDoS, skip and log
                    matches.push(`CUSTOM: ${patternStr} — skipped (${elapsed}ms, possible ReDoS)`);
                    continue;
                }
                if (match) {
                    matches.push(`CUSTOM: ${patternStr} → "${match[0]}"`);
                }
            }
            catch {
                // Skip invalid regex
            }
        }
    }
    if (matches.length > 0) {
        return {
            clean: false,
            detail: `Detected ${matches.length} potential injection pattern(s)`,
            matches,
        };
    }
    return { clean: true, detail: "No injection patterns detected", matches: [] };
}
