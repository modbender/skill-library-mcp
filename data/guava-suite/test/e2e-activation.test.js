// E2E Activation Tests — Full flow from challenge to mode switch
// Uses Node built-in test runner — zero dependencies
import { describe, it, before, after, mock } from "node:test";
import assert from "node:assert/strict";
import { writeFileSync, readFileSync, mkdirSync, rmSync, existsSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";

import { LicenseService } from "../services/license-api/src/licenseService.js";
import { SuiteGate } from "../services/license-api/src/suiteGate.js";
import { SuiteBridge } from "../services/license-api/src/suiteBridge.js";
import { TokenIssuer } from "../services/license-api/src/tokenIssuer.js";
import { TokenBalanceChecker, DEFAULT_THRESHOLD } from "../services/license-api/src/tokenBalanceChecker.js";

const TEST_SECRET = "e2e-test-secret";
const TEST_ADDR = "0x1234567890abcdef1234567890abcdef12345678";

// ── Full Activation Flow Tests ──

describe("E2E: Activation Flow", () => {
    const tmpDir = join(tmpdir(), `guava-suite-e2e-${Date.now()}`);
    const tokenFile = join(tmpDir, "token.jwt");

    before(() => {
        mkdirSync(tmpDir, { recursive: true });
    });

    after(() => {
        try { rmSync(tmpDir, { recursive: true }); } catch { /* ok */ }
    });

    it("full flow: challenge → verify → JWT → SuiteGate → strict mode", async () => {
        // 1. Create service with mock balance checker (enough $GUAVA)
        const mockBalance = {
            check: mock.fn(() => Promise.resolve({
                ok: true,
                balance: DEFAULT_THRESHOLD * BigInt(2),
                threshold: DEFAULT_THRESHOLD,
                humanBalance: "2000000",
                humanThreshold: "1000000",
            })),
        };

        const service = new LicenseService({
            jwtSecret: TEST_SECRET,
            balanceChecker: mockBalance,
        });

        // 2. Get challenge
        const { nonce, expiresAt } = service.issueChallenge(TEST_ADDR);
        assert.ok(nonce);
        assert.ok(expiresAt > Date.now());

        // 3. Verify (stub signature mode)
        const result = await service.verify({
            address: TEST_ADDR,
            nonce,
            signature: "valid",
        });

        assert.equal(result.ok, true);
        assert.ok(result.token);
        assert.equal(result.balance.current, "2000000");

        // 4. Save JWT (simulating what activate.js does)
        writeFileSync(tokenFile, result.token);
        assert.ok(existsSync(tokenFile));

        // 5. Activate SuiteGate with saved JWT
        const gate = new SuiteGate({ jwtSecret: TEST_SECRET });
        const status = gate.activate(result.token);

        assert.equal(status.suiteEnabled, true);
        assert.equal(status.guardEnabled, true);
        assert.equal(status.reason, "Active");

        // 6. SuiteBridge should return strict mode
        const bridge = new SuiteBridge({ gate });
        assert.equal(bridge.getMode(), "strict");

        // 7. Verify shouldBlock behavior
        assert.equal(bridge.shouldBlock("CRITICAL").block, true);
        assert.equal(bridge.shouldBlock("HIGH").block, true);  // strict: blocks HIGH
        assert.equal(bridge.shouldBlock("MEDIUM").block, false);

        // 8. Full status report
        const fullStatus = bridge.getStatus();
        assert.equal(fullStatus.features.strictMode, true);
        assert.equal(fullStatus.features.soulLock, true);
        assert.equal(fullStatus.features.memoryGuard, true);
    });

    it("full flow: insufficient balance → enforcement denied", async () => {
        const mockBalance = {
            check: mock.fn(() => Promise.resolve({
                ok: false,
                balance: BigInt(100),
                threshold: DEFAULT_THRESHOLD,
                humanBalance: "0",
                humanThreshold: "1000000",
            })),
        };

        const service = new LicenseService({
            jwtSecret: TEST_SECRET,
            balanceChecker: mockBalance,
        });

        const { nonce } = service.issueChallenge(TEST_ADDR);
        const result = await service.verify({
            address: TEST_ADDR,
            nonce,
            signature: "valid",
        });

        assert.equal(result.ok, false);
        assert.equal(result.code, "INSUFFICIENT_BALANCE");
        assert.equal(result.balance.current, "0");
        assert.equal(result.balance.required, "1000000");
    });

    it("deactivation: SuiteGate returns to enforce mode", () => {
        const gate = new SuiteGate({ jwtSecret: TEST_SECRET });
        const issuer = new TokenIssuer({ secret: TEST_SECRET, expiresIn: "1h" });
        const token = issuer.issue({ address: TEST_ADDR }).token;

        // Activate
        gate.activate(token);
        const bridge = new SuiteBridge({ gate });
        assert.equal(bridge.getMode(), "strict");

        // Simulate deactivation by creating new gate without token
        const freshGate = new SuiteGate({ jwtSecret: TEST_SECRET });
        const freshBridge = new SuiteBridge({ gate: freshGate });
        assert.equal(freshBridge.getMode(), "enforce");
    });

    it("expired JWT: SuiteGate falls back to enforce after grace", () => {
        // recheckMs=0 → recheck always triggered. graceMs=0 → grace expires immediately.
        const gate = new SuiteGate({ jwtSecret: TEST_SECRET, graceMs: 0, recheckMs: 0 });
        const issuer = new TokenIssuer({ secret: TEST_SECRET, expiresIn: "1h" });
        const token = issuer.issue({ address: TEST_ADDR }).token;

        // Activate sets _lastVerifiedAt = now
        gate.activate(token);

        // First check with now+1: triggers _enterGrace(now+1) → graceDeadline = now+1+0 = now+1
        // Since now+1 <= graceDeadline(now+1), still returns suiteEnabled=true (grace active)
        const t1 = Date.now() + 1;
        const status1 = gate.check(t1);
        assert.equal(status1.suiteEnabled, true); // grace period active

        // Second check with now+2: graceDeadline is still t1, and t1+1 > t1 → grace expired
        const status2 = gate.check(t1 + 1);
        assert.equal(status2.suiteEnabled, false); // grace expired → fail-closed
    });

    it("grace period: network failure keeps suite active temporarily", () => {
        const graceMs = 3600_000; // 1 hour
        const gate = new SuiteGate({ jwtSecret: TEST_SECRET, graceMs });
        const issuer = new TokenIssuer({ secret: TEST_SECRET, expiresIn: "1h" });
        const token = issuer.issue({ address: TEST_ADDR }).token;

        gate.activate(token);
        const now = Date.now();

        // Simulate network failure
        const graceStatus = gate.networkFailure(now);
        assert.equal(graceStatus.suiteEnabled, true);
        assert.ok(graceStatus.graceDeadline);

        // Still active during grace period
        const midGrace = gate.check(now + graceMs / 2);
        assert.equal(midGrace.suiteEnabled, true);

        // Expired after grace period
        const afterGrace = gate.check(now + graceMs + 1);
        assert.equal(afterGrace.suiteEnabled, false);
    });
});

// ── Token Balance Checker Unit Tests (for E2E completeness) ──

describe("E2E: Polygon RPC Integration (mocked)", () => {
    it("constructs correct JSON-RPC call", async () => {
        let capturedBody = null;
        const mockFetch = mock.fn((url, opts) => {
            capturedBody = JSON.parse(opts.body);
            const hexBalance = "0x" + DEFAULT_THRESHOLD.toString(16).padStart(64, "0");
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ jsonrpc: "2.0", id: 1, result: hexBalance }),
            });
        });

        const checker = new TokenBalanceChecker({ fetchFn: mockFetch });
        await checker.check(TEST_ADDR);

        assert.equal(capturedBody.method, "eth_call");
        assert.equal(capturedBody.params[1], "latest");
        // Verify calldata contains balanceOf selector
        assert.ok(capturedBody.params[0].data.startsWith("0x70a08231"));
    });
});
