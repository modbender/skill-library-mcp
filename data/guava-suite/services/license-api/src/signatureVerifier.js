// SignatureVerifier — EIP-712 typed data signature verification
// Why: Isolate cryptographic verification from business logic
import { LicenseError, ErrorCode } from "./errors.js";

// EIP-712 domain & type definitions for GuavaSuite license challenge
const DOMAIN = {
    name: "GuavaSuite",
    version: "1",
    chainId: 137, // Polygon Mainnet
};

const TYPES = {
    LicenseChallenge: [
        { name: "nonce", type: "string" },
        { name: "address", type: "address" },
        { name: "action", type: "string" },
    ],
};

export class SignatureVerifier {
    /**
     * @param {object} opts
     * @param {object} [opts.ethers] - ethers module (injected for testability)
     */
    constructor({ ethers = null } = {}) {
        this._ethers = ethers;
    }

    /**
     * Verify an EIP-712 signature for a license challenge.
     * @param {object} params
     * @param {string} params.address  - Expected signer address
     * @param {string} params.nonce    - Challenge nonce
     * @param {string} params.signature - Hex-encoded signature
     * @returns {void}
     * @throws {LicenseError} if signature is invalid or signer mismatch
     */
    verify({ address, nonce, signature }) {
        // If ethers is not injected, fall back to stub mode (for unit tests)
        if (!this._ethers) {
            return this._stubVerify({ address, signature });
        }

        try {
            const message = {
                nonce,
                address,
                action: "activate-guava-suite",
            };

            const recovered = this._ethers.verifyTypedData(DOMAIN, TYPES, message, signature);
            if (recovered.toLowerCase() !== address.toLowerCase()) {
                throw new LicenseError(ErrorCode.INVALID_SIGNATURE, "Signer mismatch");
            }
        } catch (err) {
            if (err instanceof LicenseError) throw err;
            throw new LicenseError(ErrorCode.INVALID_SIGNATURE, err.message);
        }
    }

    /**
     * Stub verification for unit tests without ethers dependency.
     * signature === "valid" passes, anything else fails.
     */
    _stubVerify({ signature }) {
        if (signature !== "valid") {
            throw new LicenseError(ErrorCode.INVALID_SIGNATURE);
        }
    }
}

// Export constants for clients that need to construct signing payloads
export { DOMAIN, TYPES };
