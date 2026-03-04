"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.validatePolicy = validatePolicy;
/**
 * Detects regex patterns likely to cause catastrophic backtracking (ReDoS).
 * Catches nested quantifiers like (a+)+, (a*)+, (a+)*, (a|b+)+ and
 * overlapping alternations with quantifiers.
 */
function isReDoSVulnerable(pattern) {
    // Nested quantifiers: a group with an inner quantifier followed by an outer quantifier
    // e.g. (a+)+, (a+)*, (.*)+, (a|b+)+, ([a-z]+)*
    const nestedQuantifier = /\([^)]*[+*]\)?[+*{]/;
    if (nestedQuantifier.test(pattern)) {
        return true;
    }
    // Overlapping alternation with quantifier: (a|a)+ or similar
    // Simplified check: group with alternation followed by quantifier where
    // alternatives share character classes
    const groupWithAlt = /\(([^)]+\|[^)]+)\)[+*{]/;
    const match = pattern.match(groupWithAlt);
    if (match) {
        const alternatives = match[1].split("|");
        // If any two alternatives are identical or both use wildcards, flag it
        for (let i = 0; i < alternatives.length; i++) {
            for (let j = i + 1; j < alternatives.length; j++) {
                if (alternatives[i].trim() === alternatives[j].trim()) {
                    return true;
                }
            }
        }
    }
    return false;
}
function validatePolicy(policy) {
    const errors = [];
    const warnings = [];
    if (typeof policy !== "object" || policy === null) {
        return { valid: false, errors: ["Policy must be a non-null object"], warnings };
    }
    const p = policy;
    // --- Required top-level fields ---
    if (!p.allowedTools || typeof p.allowedTools !== "object") {
        errors.push("Missing or invalid 'allowedTools' (must be an object)");
    }
    if (!p.rateLimits || typeof p.rateLimits !== "object") {
        errors.push("Missing or invalid 'rateLimits' (must be an object)");
    }
    else {
        const rl = p.rateLimits;
        for (const key of ["perUser", "perSession"]) {
            if (!rl[key] || typeof rl[key] !== "object") {
                errors.push(`Missing or invalid 'rateLimits.${key}' (must be an object)`);
            }
            else {
                const bucket = rl[key];
                if (typeof bucket.maxCalls !== "number" || bucket.maxCalls < 0) {
                    errors.push(`'rateLimits.${key}.maxCalls' must be a non-negative number`);
                }
                if (typeof bucket.windowSeconds !== "number" || bucket.windowSeconds < 0) {
                    errors.push(`'rateLimits.${key}.windowSeconds' must be a non-negative number`);
                }
            }
        }
    }
    if (!p.identityMap || typeof p.identityMap !== "object") {
        errors.push("Missing or invalid 'identityMap' (must be an object)");
    }
    if (!p.injectionDetection || typeof p.injectionDetection !== "object") {
        errors.push("Missing or invalid 'injectionDetection' (must be an object)");
    }
    else {
        const id = p.injectionDetection;
        if (typeof id.enabled !== "boolean") {
            errors.push("'injectionDetection.enabled' must be a boolean");
        }
        if (!["low", "medium", "high"].includes(id.sensitivity)) {
            errors.push("'injectionDetection.sensitivity' must be 'low', 'medium', or 'high'");
        }
        // Validate new optional fields
        if (id.obfuscationDetection !== undefined && typeof id.obfuscationDetection !== "boolean") {
            errors.push("'injectionDetection.obfuscationDetection' must be a boolean");
        }
        if (id.multiLanguage !== undefined && typeof id.multiLanguage !== "boolean") {
            errors.push("'injectionDetection.multiLanguage' must be a boolean");
        }
        if (id.canaryTokens !== undefined) {
            if (!Array.isArray(id.canaryTokens)) {
                errors.push("'injectionDetection.canaryTokens' must be an array of strings");
            }
            else {
                for (let i = 0; i < id.canaryTokens.length; i++) {
                    if (typeof id.canaryTokens[i] !== "string") {
                        errors.push(`'injectionDetection.canaryTokens[${i}]' must be a string`);
                    }
                }
                if (id.canaryTokens.length > 100) {
                    warnings.push(`'injectionDetection.canaryTokens' has ${id.canaryTokens.length} entries (>100) — consider reducing for performance`);
                }
            }
        }
        // Validate custom patterns
        if (id.customPatterns !== undefined) {
            if (!Array.isArray(id.customPatterns)) {
                errors.push("'injectionDetection.customPatterns' must be an array");
            }
            else {
                for (let i = 0; i < id.customPatterns.length; i++) {
                    const pat = id.customPatterns[i];
                    if (typeof pat !== "string") {
                        warnings.push(`customPatterns[${i}] is not a string`);
                        continue;
                    }
                    try {
                        new RegExp(pat);
                    }
                    catch {
                        warnings.push(`customPatterns[${i}] is not a valid regex: "${pat}"`);
                        continue;
                    }
                    if (isReDoSVulnerable(pat)) {
                        warnings.push(`customPatterns[${i}] may be vulnerable to ReDoS (catastrophic backtracking): "${pat}"`);
                    }
                }
            }
        }
    }
    if (!p.auditLog || typeof p.auditLog !== "object") {
        errors.push("Missing or invalid 'auditLog' (must be an object)");
    }
    // --- Optional feature sections ---
    if (p.outputDlp !== undefined) {
        if (typeof p.outputDlp !== "object" || p.outputDlp === null) {
            errors.push("'outputDlp' must be an object");
        }
        else {
            const dlp = p.outputDlp;
            if (typeof dlp.enabled !== "boolean") {
                errors.push("'outputDlp.enabled' must be a boolean");
            }
            if (!["log", "block"].includes(dlp.mode)) {
                errors.push("'outputDlp.mode' must be 'log' or 'block'");
            }
            if (!["mask", "remove"].includes(dlp.redactionMode)) {
                errors.push("'outputDlp.redactionMode' must be 'mask' or 'remove'");
            }
            if (dlp.customPatterns !== undefined) {
                if (!Array.isArray(dlp.customPatterns)) {
                    errors.push("'outputDlp.customPatterns' must be an array");
                }
                else {
                    for (let i = 0; i < dlp.customPatterns.length; i++) {
                        if (typeof dlp.customPatterns[i] !== "string") {
                            errors.push(`'outputDlp.customPatterns[${i}]' must be a string`);
                        }
                    }
                }
            }
        }
    }
    if (p.escalation !== undefined) {
        if (typeof p.escalation !== "object" || p.escalation === null) {
            errors.push("'escalation' must be an object");
        }
        else {
            const esc = p.escalation;
            if (typeof esc.enabled !== "boolean") {
                errors.push("'escalation.enabled' must be a boolean");
            }
            if (typeof esc.reviewOnMediumInjection !== "boolean") {
                errors.push("'escalation.reviewOnMediumInjection' must be a boolean");
            }
            if (typeof esc.reviewOnFirstToolUse !== "boolean") {
                errors.push("'escalation.reviewOnFirstToolUse' must be a boolean");
            }
            if (typeof esc.tokenTTLSeconds !== "number" || esc.tokenTTLSeconds < 0) {
                errors.push("'escalation.tokenTTLSeconds' must be a non-negative number");
            }
        }
    }
    if (p.behavioralMonitoring !== undefined) {
        if (typeof p.behavioralMonitoring !== "object" || p.behavioralMonitoring === null) {
            errors.push("'behavioralMonitoring' must be an object");
        }
        else {
            const bm = p.behavioralMonitoring;
            if (typeof bm.enabled !== "boolean") {
                errors.push("'behavioralMonitoring.enabled' must be a boolean");
            }
            if (typeof bm.spikeThreshold !== "number" || bm.spikeThreshold <= 0) {
                errors.push("'behavioralMonitoring.spikeThreshold' must be a positive number");
            }
            if (typeof bm.monitoringWindowSeconds !== "number" || bm.monitoringWindowSeconds < 0) {
                errors.push("'behavioralMonitoring.monitoringWindowSeconds' must be a non-negative number");
            }
            if (!["log", "review", "block"].includes(bm.action)) {
                errors.push("'behavioralMonitoring.action' must be 'log', 'review', or 'block'");
            }
        }
    }
    // --- Warnings (non-fatal) ---
    // Empty collections
    if (p.allowedTools && typeof p.allowedTools === "object" && Object.keys(p.allowedTools).length === 0) {
        warnings.push("'allowedTools' is empty — all tools will be denied");
    }
    if (p.identityMap && typeof p.identityMap === "object" && Object.keys(p.identityMap).length === 0) {
        warnings.push("'identityMap' is empty — all users will be denied");
    }
    // Cross-reference: roles referenced by tools but not assigned to any identity
    if (p.allowedTools && typeof p.allowedTools === "object" &&
        p.identityMap && typeof p.identityMap === "object") {
        const allIdentityRoles = new Set();
        for (const entry of Object.values(p.identityMap)) {
            if (entry && typeof entry === "object" && Array.isArray(entry.roles)) {
                for (const r of entry.roles) {
                    allIdentityRoles.add(r);
                }
            }
        }
        for (const [toolName, toolConfig] of Object.entries(p.allowedTools)) {
            if (toolConfig && typeof toolConfig === "object" && Array.isArray(toolConfig.roles)) {
                for (const role of toolConfig.roles) {
                    if (!allIdentityRoles.has(role)) {
                        warnings.push(`Tool "${toolName}" requires role "${role}" but no identity has it`);
                    }
                }
            }
        }
    }
    return { valid: errors.length === 0, errors, warnings };
}
