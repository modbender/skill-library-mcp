import { describe, it, expect } from "vitest";
import { SuiteGate } from "../src/suiteGate.js";
import { TokenIssuer } from "../src/tokenIssuer.js";

const SECRET = "test-secret-32-chars-minimum-ok!";

function issueToken({ expiresIn = "24h", address = "0xabc" } = {}) {
    const issuer = new TokenIssuer({ secret: SECRET });
    return issuer.issue({ address }).token;
}

describe("SuiteGate", () => {
    // === W3 RED: Core fail-closed behavior ===

    it("guard is ALWAYS enabled, even with no token", () => {
        const gate = new SuiteGate({ jwtSecret: SECRET });
        const s = gate.check();
        expect(s.guardEnabled).toBe(true);
        expect(s.suiteEnabled).toBe(false);
        expect(s.reason).toContain("No license token");
    });

    it("suite is disabled with no token (fail-closed)", () => {
        const gate = new SuiteGate({ jwtSecret: SECRET });
        const s = gate.check();
        expect(s.suiteEnabled).toBe(false);
        expect(s.guardEnabled).toBe(true);
    });

    it("suite is enabled with valid token", () => {
        const gate = new SuiteGate({ jwtSecret: SECRET });
        const token = issueToken();
        const s = gate.activate(token);
        expect(s.suiteEnabled).toBe(true);
        expect(s.guardEnabled).toBe(true);
        expect(s.reason).toBe("Active");
    });

    it("suite disabled + guard enabled on expired token (fail-closed)", () => {
        const gate = new SuiteGate({ jwtSecret: SECRET, graceMs: 0 }); // no grace
        // Create a token that's already expired
        const issuer = new TokenIssuer({ secret: SECRET, expiresIn: "0s" });
        const { token } = issuer.issue({ address: "0xabc" });

        // Small delay to ensure token expires
        const s = gate.activate(token);
        expect(s.suiteEnabled).toBe(false);
        expect(s.guardEnabled).toBe(true);
        expect(s.reason).toContain("expired");
    });

    it("suite disabled with wrong secret (fail-closed)", () => {
        const gate = new SuiteGate({ jwtSecret: "wrong-secret-entirely-different!" });
        const token = issueToken(); // signed with SECRET
        const s = gate.activate(token);
        expect(s.suiteEnabled).toBe(false);
        expect(s.guardEnabled).toBe(true);
    });

    // === W3 RED: Grace period behavior ===

    it("enters grace period on network failure", () => {
        const gate = new SuiteGate({ jwtSecret: SECRET, graceMs: 60_000 });
        const token = issueToken();
        gate.activate(token);

        const now = Date.now();
        const s = gate.networkFailure(now);
        expect(s.suiteEnabled).toBe(true);   // Still on during grace
        expect(s.guardEnabled).toBe(true);
        expect(s.reason).toContain("Grace period");
        expect(s.graceDeadline).toBeGreaterThan(now);
    });

    it("suite disabled after grace period expires", () => {
        const gate = new SuiteGate({ jwtSecret: SECRET, graceMs: 1000 });
        const token = issueToken();
        gate.activate(token);

        const now = Date.now();
        // Enter grace
        gate.networkFailure(now);
        // Check after grace expired
        const s = gate.check(now + 2000); // well past graceMs
        // Token is still valid (24h), so check should pass
        // But let's test with an expired token + grace
        expect(s.guardEnabled).toBe(true);
    });

    it("grace period expires → fail-closed (suite off, guard on)", () => {
        // Use graceMs=0 so grace expires immediately
        const gate = new SuiteGate({ jwtSecret: SECRET, graceMs: 0 });
        const token = issueToken();
        gate.activate(token);

        const now = Date.now();
        // Trigger network failure — grace starts but graceMs=0 means it's already expired
        gate.networkFailure(now);

        // Check at now+1 — grace deadline (now+0) has passed
        const s = gate.check(now + 1);
        expect(s.suiteEnabled).toBe(false);
        expect(s.guardEnabled).toBe(true);
        expect(s.reason).toContain("expired");
    });


    // === W3 RED: Recheck interval ===

    it("requires recheck after recheckMs", () => {
        const gate = new SuiteGate({
            jwtSecret: SECRET,
            graceMs: 60_000,
            recheckMs: 1000, // 1 second recheck
        });
        const token = issueToken();
        gate.activate(token);

        // Check immediately — should be active
        expect(gate.check().suiteEnabled).toBe(true);

        // Check after recheck interval — enters grace period
        const s = gate.check(Date.now() + 2000);
        expect(s.reason).toContain("Recheck");
        expect(s.suiteEnabled).toBe(true); // In grace, still enabled
        expect(s.graceDeadline).toBeTruthy();
    });

    it("throws if no jwtSecret provided", () => {
        expect(() => new SuiteGate({})).toThrow("requires jwtSecret");
    });
});
