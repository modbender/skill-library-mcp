// LicenseService — Facade composing NonceStore + SignatureVerifier + TokenIssuer + TokenBalanceChecker
// Why: Keeps the public API stable while delegating to single-responsibility modules
import { NonceStore } from "./nonceStore.js";
import { SignatureVerifier } from "./signatureVerifier.js";
import { TokenIssuer } from "./tokenIssuer.js";
import { TokenBalanceChecker } from "./tokenBalanceChecker.js";
import { LicenseError, ErrorCode } from "./errors.js";

export class LicenseService {
  /**
   * @param {object} [opts]
   * @param {number} [opts.ttlMs=300000] - Nonce TTL
   * @param {string} [opts.jwtSecret="dev-secret-CHANGE-ME"] - JWT signing secret
   * @param {string} [opts.jwtExpiresIn="24h"] - JWT lifetime
   * @param {object} [opts.ethers] - ethers module for real EIP-712 verification
   * @param {object} [opts.balanceChecker] - Injected TokenBalanceChecker (for testing)
   * @param {bigint} [opts.guavaThreshold] - $GUAVA minimum balance
   */
  constructor({
    ttlMs = 5 * 60 * 1000,
    jwtSecret = "dev-secret-CHANGE-ME",
    jwtExpiresIn = "24h",
    ethers = null,
    balanceChecker = null,
    guavaThreshold = undefined,
  } = {}) {
    this.nonces = new NonceStore({ ttlMs });
    this.signer = new SignatureVerifier({ ethers });
    this.tokens = new TokenIssuer({ secret: jwtSecret, expiresIn: jwtExpiresIn });
    this.balanceChecker = balanceChecker || new TokenBalanceChecker(
      guavaThreshold !== undefined ? { threshold: guavaThreshold } : {}
    );
  }

  /**
   * Issue a challenge nonce for the given address.
   * @param {string} address
   * @returns {{ nonce: string, expiresAt: number }}
   */
  issueChallenge(address) {
    if (!address) throw new LicenseError(ErrorCode.INVALID_REQUEST, "address required");
    return this.nonces.issue(address);
  }

  /**
   * Verify a signed challenge and issue a JWT if valid.
   * Supports two modes:
   *   - Legacy: { hasPass: true } skips balance check (for Founders Pass NFT holders)
   *   - Token Gate: checks $GUAVA balance on Polygon
   *
   * @param {object} params
   * @returns {Promise<{ ok: boolean, code: string, token?: string, expiresIn?: string, balance?: object }>}
   */
  async verify({ address, nonce, signature, hasPass, now = Date.now() }) {
    try {
      // 1. Nonce validation (replay, expiry, address match)
      this.nonces.consume(nonce, address, now);

      // 2. Signature verification
      this.signer.verify({ address, nonce, signature });

      // 3. Access check: Founders Pass (legacy) OR $GUAVA balance
      let balanceInfo = null;
      if (hasPass) {
        // Founders Pass holders bypass balance check
        // Why: NFT holders already paid — don't double-gate them
      } else {
        // Token gate: check $GUAVA balance on Polygon
        balanceInfo = await this.balanceChecker.check(address);
        if (!balanceInfo.ok) {
          return {
            ok: false,
            code: ErrorCode.INSUFFICIENT_BALANCE,
            balance: {
              current: balanceInfo.humanBalance,
              required: balanceInfo.humanThreshold,
            },
          };
        }
      }

      // 4. Issue JWT
      const { token, expiresIn } = this.tokens.issue({ address });

      return {
        ok: true,
        code: "OK",
        token,
        expiresIn,
        ...(balanceInfo ? {
          balance: {
            current: balanceInfo.humanBalance,
            required: balanceInfo.humanThreshold,
          },
        } : {}),
      };
    } catch (err) {
      if (err instanceof LicenseError) {
        return { ok: false, code: err.code };
      }
      return { ok: false, code: ErrorCode.INTERNAL_ERROR };
    }
  }
}
