"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.checkScope = checkScope;
function checkScope(tool, roles, policy) {
    const toolPolicy = policy.allowedTools[tool];
    // Deny-by-default: tool must be explicitly allowlisted
    if (!toolPolicy) {
        return {
            allowed: false,
            detail: `Tool "${tool}" is not in the allowlist. Deny-by-default policy enforced.`,
        };
    }
    // If tool has role restrictions, check them
    if (toolPolicy.roles && toolPolicy.roles.length > 0) {
        const hasRole = roles.some((r) => toolPolicy.roles.includes(r));
        if (!hasRole) {
            return {
                allowed: false,
                detail: `Tool "${tool}" requires roles [${toolPolicy.roles.join(", ")}] but user has [${roles.join(", ")}]`,
            };
        }
    }
    return {
        allowed: true,
        detail: `Tool "${tool}" is allowlisted for roles [${roles.join(", ")}]`,
    };
}
