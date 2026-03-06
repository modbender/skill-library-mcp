// TokenBalanceChecker — $GUAVA ERC-20 balance verification via Polygon RPC
// Why: Separates on-chain token gate logic from license flow
// Why no ethers: Zero external deps — raw JSON-RPC with Node built-in fetch
import { LicenseError, ErrorCode } from "./errors.js";

// --- Constants ---

// $GUAVA token on Polygon Mainnet
const GUAVA_TOKEN = "0x25cBD481901990bF0ed2ff9c5F3C0d4f743AC7B8";

// ERC-20 balanceOf(address) selector: keccak256("balanceOf(address)")[0:4]
const BALANCE_OF_SELECTOR = "0x70a08231";

// Default Polygon RPC (public, rate-limited but sufficient for auth checks)
const DEFAULT_RPC = "https://polygon-rpc.com";

// Default threshold: 1M $GUAVA (18 decimals) = 1_000_000 * 10^18
// Why 1M: low enough for early adopters, high enough to be meaningful
const DEFAULT_THRESHOLD = BigInt("1000000000000000000000000"); // 1M * 10^18

export class TokenBalanceChecker {
    /**
     * @param {object} [opts]
     * @param {string} [opts.tokenAddress] - ERC-20 contract address
     * @param {string} [opts.rpcUrl] - Polygon JSON-RPC endpoint
     * @param {bigint} [opts.threshold] - Minimum balance required (raw, 18 decimals)
     * @param {Function} [opts.fetchFn] - Injected fetch for testing
     */
    constructor({
        tokenAddress = GUAVA_TOKEN,
        rpcUrl = DEFAULT_RPC,
        threshold = DEFAULT_THRESHOLD,
        fetchFn = globalThis.fetch,
    } = {}) {
        this._tokenAddress = tokenAddress;
        this._rpcUrl = rpcUrl;
        this._threshold = threshold;
        this._fetch = fetchFn;
    }

    /**
     * Check if an address holds enough $GUAVA to access GuavaSuite.
     * @param {string} address - Ethereum/Polygon address (0x...)
     * @returns {Promise<{ ok: boolean, balance: bigint, threshold: bigint, humanBalance: string }>}
     */
    async check(address) {
        if (!address || !address.startsWith("0x")) {
            throw new LicenseError(ErrorCode.INVALID_REQUEST, "Valid address required");
        }

        const balance = await this._getBalance(address);

        return {
            ok: balance >= this._threshold,
            balance,
            threshold: this._threshold,
            // Human-readable: divide by 10^18, show as integer
            humanBalance: (balance / BigInt(10 ** 18)).toString(),
            humanThreshold: (this._threshold / BigInt(10 ** 18)).toString(),
        };
    }

    /**
     * Raw JSON-RPC eth_call to get ERC-20 balanceOf.
     * @param {string} address
     * @returns {Promise<bigint>}
     * @private
     */
    async _getBalance(address) {
        // Encode calldata: balanceOf(address)
        // address is left-padded to 32 bytes
        const paddedAddress = address.toLowerCase().replace("0x", "").padStart(64, "0");
        const data = BALANCE_OF_SELECTOR + paddedAddress;

        const body = JSON.stringify({
            jsonrpc: "2.0",
            id: 1,
            method: "eth_call",
            params: [
                { to: this._tokenAddress, data },
                "latest",
            ],
        });

        try {
            const res = await this._fetch(this._rpcUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body,
            });

            if (!res.ok) {
                throw new Error(`RPC returned ${res.status}`);
            }

            const json = await res.json();

            if (json.error) {
                throw new Error(json.error.message || "RPC error");
            }

            // Result is hex-encoded uint256
            const hex = json.result;
            if (!hex || hex === "0x") return BigInt(0);
            return BigInt(hex);
        } catch (err) {
            if (err instanceof LicenseError) throw err;
            // Network errors shouldn't block — log and return 0
            // Why: fail-closed in SuiteGate handles this gracefully via grace period
            console.error("[TokenBalanceChecker] RPC error:", err.message);
            throw new LicenseError(
                ErrorCode.INTERNAL_ERROR,
                `Balance check failed: ${err.message}`
            );
        }
    }
}

// Export constants for configuration
export { GUAVA_TOKEN, DEFAULT_THRESHOLD, DEFAULT_RPC };
