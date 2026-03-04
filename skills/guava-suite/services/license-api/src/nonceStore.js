// NonceStore — nonce lifecycle management
// Why: Single responsibility for challenge nonce creation, validation, and consumption
import crypto from "node:crypto";
import { LicenseError, ErrorCode } from "./errors.js";

export class NonceStore {
    /**
     * @param {object} opts
     * @param {number} [opts.ttlMs=300000] - Nonce time-to-live in milliseconds (default 5 min)
     */
    constructor({ ttlMs = 5 * 60 * 1000 } = {}) {
        this.ttlMs = ttlMs;
        /** @type {Map<string, {address: string, expiresAt: number, used: boolean}>} */
        this._store = new Map();
    }

    /**
     * Issue a new challenge nonce for the given address.
     * @param {string} address - Ethereum address (checksummed or lowercase)
     * @returns {{ nonce: string, expiresAt: number }}
     */
    issue(address) {
        const nonce = crypto.randomUUID();
        const expiresAt = Date.now() + this.ttlMs;
        this._store.set(nonce, {
            address: address.toLowerCase(),
            expiresAt,
            used: false,
        });
        return { nonce, expiresAt };
    }

    /**
     * Consume a nonce — marks it as used if valid.
     * @param {string} nonce
     * @param {string} address
     * @param {number} [now=Date.now()]
     * @returns {void}
     * @throws {LicenseError} if nonce is unknown, replayed, expired, or address mismatch
     */
    consume(nonce, address, now = Date.now()) {
        const rec = this._store.get(nonce);
        if (!rec) throw new LicenseError(ErrorCode.NONCE_UNKNOWN);
        if (rec.used) throw new LicenseError(ErrorCode.NONCE_REPLAY);
        if (now > rec.expiresAt) throw new LicenseError(ErrorCode.EXPIRED_CHALLENGE);
        if ((address || "").toLowerCase() !== rec.address) {
            throw new LicenseError(ErrorCode.ADDRESS_MISMATCH);
        }
        rec.used = true;
    }

    /** Cleanup expired nonces to prevent memory leak in long-running service */
    prune() {
        const now = Date.now();
        for (const [k, v] of this._store) {
            if (now > v.expiresAt) this._store.delete(k);
        }
    }
}
