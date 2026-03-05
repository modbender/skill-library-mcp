"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.verifyIdentity = verifyIdentity;
function verifyIdentity(user, channel, policy) {
    if (!user && !channel) {
        return {
            verified: false,
            userId: "unknown",
            roles: [],
            detail: "No user or channel identifier provided",
        };
    }
    // Check identity map: channel → identity mapping
    const key = channel || user || "";
    const mapped = policy.identityMap[key];
    if (mapped) {
        return {
            verified: true,
            userId: mapped.userId,
            roles: mapped.roles,
            detail: `Mapped ${key} → ${mapped.userId} with roles [${mapped.roles.join(", ")}]`,
        };
    }
    // Deny-by-default: unmapped users are blocked.
    // If you want a user to have access, add them to the identity map.
    if (user) {
        return {
            verified: false,
            userId: user,
            roles: [],
            detail: `User "${user}" is not in the identity map. Add them to policy.json identityMap to grant access.`,
        };
    }
    return {
        verified: false,
        userId: "unknown",
        roles: [],
        detail: `Channel ${channel} has no identity mapping configured`,
    };
}
