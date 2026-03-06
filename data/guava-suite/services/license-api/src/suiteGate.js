// SuiteGate — Runtime middleware for GuavaSuite activation
// Why: fail-closed design — suite features only available with valid JWT
// Guard (OSS) always runs regardless of suite status

import { TokenIssuer } from "./tokenIssuer.js";

/**
 * @typedef {Object} GateStatus
 * @property {boolean} suiteEnabled - true if suite features are active
 * @property {boolean} guardEnabled - true always (OSS, never disabled)
 * @property {string} reason - human-readable status
 * @property {number|null} expiresAt - JWT expiry timestamp (ms), null if no token
 * @property {number|null} graceDealine - grace period deadline (ms), null if not in grace
 */

export class SuiteGate {
    /**
     * @param {object} opts
     * @param {string} opts.jwtSecret - Secret for JWT verification
     * @param {number} [opts.graceMs=3600000] - Grace period in ms (default 1h)
     * @param {number} [opts.recheckMs=86400000] - Re-verification interval (default 24h)
     */
    constructor({ jwtSecret, graceMs = 60 * 60 * 1000, recheckMs = 24 * 60 * 60 * 1000 }) {
        if (!jwtSecret) throw new Error("SuiteGate requires jwtSecret");
        this._issuer = new TokenIssuer({ secret: jwtSecret });
        this._graceMs = graceMs;
        this._recheckMs = recheckMs;

        // State
        this._token = null;
        this._decoded = null;
        this._lastVerifiedAt = null;
        this._graceDeadline = null;
    }

    /**
     * Activate suite with a valid JWT token.
     * @param {string} token
     * @returns {GateStatus}
     */
    activate(token) {
        try {
            this._decoded = this._issuer.verify(token);
            this._token = token;
            this._lastVerifiedAt = Date.now();
            this._graceDeadline = null; // Clear grace period on fresh activation
            return this.status();
        } catch {
            // Invalid token — do not activate, enter or maintain fail-closed
            return this._failClosed("Invalid or expired token");
        }
    }

    /**
     * Check current gate status. Called by suite features before executing.
     * @param {number} [now=Date.now()]
     * @returns {GateStatus}
     */
    check(now = Date.now()) {
        // No token ever set — guard-only mode
        if (!this._token) {
            return this._failClosed("No license token");
        }

        // If grace deadline is active, honor it (fail-closed if expired)
        // Why: networkFailure() or token expiry set a grace window.
        // Even if the stored JWT hasn't technically expired yet, the grace
        // deadline represents a real-world inability to re-verify.
        if (this._graceDeadline !== null) {
            if (now > this._graceDeadline) {
                return this._failClosed("Grace period expired");
            }
            return {
                suiteEnabled: true,
                guardEnabled: true,
                reason: "Grace period active",
                expiresAt: null,
                graceDeadline: this._graceDeadline,
            };
        }

        // Re-verify the token
        try {
            this._decoded = this._issuer.verify(this._token);
        } catch {
            // Token expired or invalid — enter grace period if not already
            return this._enterGrace(now, "Token expired");
        }

        // Token valid — check if recheck interval passed
        if (this._lastVerifiedAt && (now - this._lastVerifiedAt) > this._recheckMs) {
            // Recheck needed — enter grace until re-verified
            return this._enterGrace(now, "Recheck interval exceeded");
        }

        return {
            suiteEnabled: true,
            guardEnabled: true,
            reason: "Active",
            expiresAt: this._decoded.exp ? this._decoded.exp * 1000 : null,
            graceDeadline: null,
        };
    }


    /**
     * Simulate network failure scenario — token can't be re-verified.
     * Grace period allows continued operation for graceMs.
     * @param {number} [now=Date.now()]
     * @returns {GateStatus}
     */
    networkFailure(now = Date.now()) {
        return this._enterGrace(now, "Network failure — grace period active");
    }

    /**
     * @returns {GateStatus}
     */
    status() {
        return this.check();
    }

    /** @private */
    _enterGrace(now, reason) {
        if (!this._graceDeadline) {
            this._graceDeadline = now + this._graceMs;
        }

        if (now <= this._graceDeadline) {
            return {
                suiteEnabled: true,
                guardEnabled: true,
                reason: `Grace period: ${reason}`,
                expiresAt: null,
                graceDeadline: this._graceDeadline,
            };
        }

        // Grace expired — fail-closed
        return this._failClosed(`Grace period expired: ${reason}`);
    }

    /** @private */
    _failClosed(reason) {
        return {
            suiteEnabled: false,  // Suite OFF
            guardEnabled: true,    // Guard ALWAYS ON
            reason,
            expiresAt: null,
            graceDeadline: null,
        };
    }
}
