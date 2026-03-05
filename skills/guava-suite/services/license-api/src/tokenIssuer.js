// TokenIssuer — JWT license token issuance
// Why: Separates token minting from verification logic
import jwt from "jsonwebtoken";

export class TokenIssuer {
    /**
     * @param {object} opts
     * @param {string} opts.secret - HMAC secret for JWT signing
     * @param {string} [opts.expiresIn="24h"] - Token lifetime
     * @param {string} [opts.issuer="guava-suite"] - Token issuer claim
     */
    constructor({ secret, expiresIn = "24h", issuer = "guava-suite" }) {
        if (!secret) throw new Error("TokenIssuer requires a secret");
        this._secret = secret;
        this._expiresIn = expiresIn;
        this._issuer = issuer;
    }

    /**
     * Issue a short-lived JWT for an authenticated pass holder.
     * @param {object} params
     * @param {string} params.address - Verified wallet address
     * @param {number} [params.passId] - GuavaSuitePass token ID
     * @returns {{ token: string, expiresIn: string }}
     */
    issue({ address, passId }) {
        const payload = {
            sub: address.toLowerCase(),
            passId: passId || 0,
            scope: "suite",
        };
        const token = jwt.sign(payload, this._secret, {
            expiresIn: this._expiresIn,
            issuer: this._issuer,
        });
        return { token, expiresIn: this._expiresIn };
    }

    /**
     * Verify and decode a JWT.
     * @param {string} token
     * @returns {object} Decoded payload
     * @throws {Error} If token is invalid or expired
     */
    verify(token) {
        return jwt.verify(token, this._secret, { issuer: this._issuer });
    }
}
