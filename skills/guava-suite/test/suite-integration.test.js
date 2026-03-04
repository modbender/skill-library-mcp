// Tests for tokenBalanceChecker, licenseService (async), and suiteBridge
// Uses Node built-in test runner (node:test) — zero dependencies
import { describe, it, mock } from "node:test";
import assert from "node:assert/strict";
import { TokenBalanceChecker, DEFAULT_THRESHOLD, GUAVA_TOKEN } from "../services/license-api/src/tokenBalanceChecker.js";
import { LicenseService } from "../services/license-api/src/licenseService.js";
import { SuiteGate } from "../services/license-api/src/suiteGate.js";
import { SuiteBridge } from "../services/license-api/src/suiteBridge.js";
import { TokenIssuer } from "../services/license-api/src/tokenIssuer.js";
import { ErrorCode } from "../services/license-api/src/errors.js";

// Helper: create a valid JWT for SuiteGate activation
const TEST_SECRET = "test-secret-key-for-suite";
const issuer = new TokenIssuer({ secret: TEST_SECRET, expiresIn: "1h" });
function createTestJwt() {
    return issuer.issue({ address: "0xtest" }).token;
}

// ── TokenBalanceChecker Tests ──

describe("TokenBalanceChecker", () => {
    const ADDR = "0x1234567890abcdef1234567890abcdef12345678";

    it("returns ok=true when balance >= threshold", async () => {
        // Mock fetch: return 10M tokens (> 1M default threshold)
        const tenMillion = BigInt("10000000000000000000000000"); // 10M * 10^18
        const hexBalance = "0x" + tenMillion.toString(16).padStart(64, "0");

        const mockFetch = mock.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ jsonrpc: "2.0", id: 1, result: hexBalance }),
            })
        );

        const checker = new TokenBalanceChecker({ fetchFn: mockFetch });
        const result = await checker.check(ADDR);

        assert.equal(result.ok, true);
        assert.equal(result.balance, tenMillion);
        assert.equal(result.humanBalance, "10000000");
        assert.equal(result.humanThreshold, "1000000");
    });

    it("returns ok=false when balance < threshold", async () => {
        // Mock fetch: return 100 tokens (< 1M threshold)
        const hundred = BigInt("100000000000000000000"); // 100 * 10^18
        const hexBalance = "0x" + hundred.toString(16).padStart(64, "0");

        const mockFetch = mock.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ jsonrpc: "2.0", id: 1, result: hexBalance }),
            })
        );

        const checker = new TokenBalanceChecker({ fetchFn: mockFetch });
        const result = await checker.check(ADDR);

        assert.equal(result.ok, false);
        assert.equal(result.humanBalance, "100");
    });

    it("returns ok=true when balance exactly equals threshold", async () => {
        const hexBalance = "0x" + DEFAULT_THRESHOLD.toString(16).padStart(64, "0");

        const mockFetch = mock.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ jsonrpc: "2.0", id: 1, result: hexBalance }),
            })
        );

        const checker = new TokenBalanceChecker({ fetchFn: mockFetch });
        const result = await checker.check(ADDR);

        assert.equal(result.ok, true);
    });

    it("throws on invalid address", async () => {
        const checker = new TokenBalanceChecker({ fetchFn: mock.fn() });
        await assert.rejects(() => checker.check("not-an-address"), {
            code: ErrorCode.INVALID_REQUEST,
        });
    });

    it("throws on RPC error", async () => {
        const mockFetch = mock.fn(() =>
            Promise.resolve({
                ok: false,
                status: 500,
            })
        );

        const checker = new TokenBalanceChecker({ fetchFn: mockFetch });
        await assert.rejects(() => checker.check(ADDR), {
            code: ErrorCode.INTERNAL_ERROR,
        });
    });

    it("handles zero balance (0x result)", async () => {
        const mockFetch = mock.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ jsonrpc: "2.0", id: 1, result: "0x" }),
            })
        );

        const checker = new TokenBalanceChecker({ fetchFn: mockFetch });
        const result = await checker.check(ADDR);

        assert.equal(result.ok, false);
        assert.equal(result.balance, BigInt(0));
        assert.equal(result.humanBalance, "0");
    });

    it("uses custom threshold when specified", async () => {
        const customThreshold = BigInt("500000000000000000000000"); // 500K
        const balance = BigInt("600000000000000000000000"); // 600K
        const hexBalance = "0x" + balance.toString(16).padStart(64, "0");

        const mockFetch = mock.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ jsonrpc: "2.0", id: 1, result: hexBalance }),
            })
        );

        const checker = new TokenBalanceChecker({ threshold: customThreshold, fetchFn: mockFetch });
        const result = await checker.check(ADDR);

        assert.equal(result.ok, true);
        assert.equal(result.humanBalance, "600000");
        assert.equal(result.humanThreshold, "500000");
    });

    it("exports correct token address", () => {
        assert.equal(GUAVA_TOKEN, "0x25cBD481901990bF0ed2ff9c5F3C0d4f743AC7B8");
    });
});

// ── LicenseService (async + balance check) Tests ──

describe("LicenseService (async)", () => {
    const ADDR = "0x1234567890abcdef1234567890abcdef12345678";

    function createMockBalanceChecker(ok, humanBalance = "1000000") {
        return {
            check: mock.fn(() => Promise.resolve({
                ok,
                balance: ok ? DEFAULT_THRESHOLD : BigInt(0),
                threshold: DEFAULT_THRESHOLD,
                humanBalance,
                humanThreshold: "1000000",
            })),
        };
    }

    it("issues JWT when hasPass=true (bypass balance check)", async () => {
        const service = new LicenseService({
            balanceChecker: createMockBalanceChecker(false),
        });

        const { nonce } = service.issueChallenge(ADDR);
        const result = await service.verify({
            address: ADDR, nonce, signature: "valid", hasPass: true,
        });

        assert.equal(result.ok, true);
        assert.equal(result.code, "OK");
        assert.ok(result.token);
    });

    it("issues JWT when $GUAVA balance sufficient", async () => {
        const service = new LicenseService({
            balanceChecker: createMockBalanceChecker(true),
        });

        const { nonce } = service.issueChallenge(ADDR);
        const result = await service.verify({
            address: ADDR, nonce, signature: "valid", hasPass: false,
        });

        assert.equal(result.ok, true);
        assert.equal(result.code, "OK");
        assert.ok(result.token);
        assert.deepEqual(result.balance, {
            current: "1000000",
            required: "1000000",
        });
    });

    it("rejects when $GUAVA balance insufficient", async () => {
        const service = new LicenseService({
            balanceChecker: createMockBalanceChecker(false, "100"),
        });

        const { nonce } = service.issueChallenge(ADDR);
        const result = await service.verify({
            address: ADDR, nonce, signature: "valid", hasPass: false,
        });

        assert.equal(result.ok, false);
        assert.equal(result.code, ErrorCode.INSUFFICIENT_BALANCE);
        assert.deepEqual(result.balance, {
            current: "100",
            required: "1000000",
        });
    });

    it("rejects invalid signature even with balance", async () => {
        const service = new LicenseService({
            balanceChecker: createMockBalanceChecker(true),
        });

        const { nonce } = service.issueChallenge(ADDR);
        const result = await service.verify({
            address: ADDR, nonce, signature: "invalid", hasPass: false,
        });

        assert.equal(result.ok, false);
        assert.equal(result.code, ErrorCode.INVALID_SIGNATURE);
    });
});

// ── SuiteBridge Tests ──

describe("SuiteBridge", () => {
    function createGate(jwtSecret = "test-secret-key-for-suite") {
        return new SuiteGate({ jwtSecret });
    }

    it("returns enforce mode when suite is inactive", () => {
        const gate = createGate();
        const bridge = new SuiteBridge({ gate });

        assert.equal(bridge.getMode(), "enforce");
    });

    it("returns strict mode when suite is active", () => {
        const gate = createGate();
        gate.activate(createTestJwt());
        const bridge = new SuiteBridge({ gate });

        assert.equal(bridge.getMode(), "strict");
    });

    it("shouldBlock returns true for CRITICAL in enforce mode", () => {
        const gate = createGate();
        const bridge = new SuiteBridge({ gate });

        const result = bridge.shouldBlock("CRITICAL");
        assert.equal(result.block, true);
    });

    it("shouldBlock returns false for HIGH in enforce mode", () => {
        const gate = createGate();
        const bridge = new SuiteBridge({ gate });

        const result = bridge.shouldBlock("HIGH");
        assert.equal(result.block, false);
    });

    it("shouldBlock returns true for HIGH in strict mode (suite active)", () => {
        const gate = createGate();
        gate.activate(createTestJwt());

        const bridge = new SuiteBridge({ gate });
        const result = bridge.shouldBlock("HIGH");
        assert.equal(result.block, true);
    });

    it("shouldBlock returns false for MEDIUM in strict mode", () => {
        const gate = createGate();
        gate.activate(createTestJwt());

        const bridge = new SuiteBridge({ gate });
        const result = bridge.shouldBlock("MEDIUM");
        assert.equal(result.block, false);
    });

    it("getStatus shows features correctly", () => {
        const gate = createGate();
        const bridge = new SuiteBridge({ gate });
        const status = bridge.getStatus();

        // OSS features always on
        assert.equal(status.features.staticScan, true);
        assert.equal(status.features.runtimeGuard, true);
        assert.equal(status.features.auditLog, true);

        // Suite features off when inactive
        assert.equal(status.features.strictMode, false);
        assert.equal(status.features.soulLock, false);
        assert.equal(status.features.memoryGuard, false);
        assert.equal(status.features.onchainVerify, false);
    });

    it("checkModeChange detects transition", () => {
        const gate = createGate();
        let lastChange = null;
        const bridge = new SuiteBridge({
            gate,
            onModeChange: (from, to) => { lastChange = { from, to }; },
        });

        // Initially enforce
        assert.equal(bridge.checkModeChange().changed, false);

        // Activate suite → strict
        gate.activate(createTestJwt());

        const change = bridge.checkModeChange();
        assert.equal(change.changed, true);
        assert.equal(change.mode, "strict");
        assert.deepEqual(lastChange, { from: "enforce", to: "strict" });
    });

    it("throws if no gate provided", () => {
        assert.throws(() => new SuiteBridge({}), /requires a SuiteGate/);
    });
});
