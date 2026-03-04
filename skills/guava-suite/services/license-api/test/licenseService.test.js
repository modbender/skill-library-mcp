import { describe, it, expect } from "vitest";
import { LicenseService } from "../src/licenseService.js";

describe("LicenseService (W2 RED)", () => {
  it("rejects nonce replay", () => {
    const svc = new LicenseService();
    const c = svc.issueChallenge("0xabc");

    const first = svc.verify({
      address: "0xabc",
      nonce: c.nonce,
      signature: "valid",
      hasPass: true,
      now: Date.now(),
    });
    expect(first.ok).toBe(true);

    const second = svc.verify({
      address: "0xabc",
      nonce: c.nonce,
      signature: "valid",
      hasPass: true,
      now: Date.now(),
    });
    expect(second.ok).toBe(false);
    expect(second.code).toBe("NONCE_REPLAY");
  });

  it("rejects invalid signature", () => {
    const svc = new LicenseService();
    const c = svc.issueChallenge("0xabc");
    const res = svc.verify({
      address: "0xabc",
      nonce: c.nonce,
      signature: "invalid",
      hasPass: true,
      now: Date.now(),
    });
    expect(res.ok).toBe(false);
    expect(res.code).toBe("INVALID_SIGNATURE");
  });

  it("rejects expired challenge", () => {
    const svc = new LicenseService();
    const c = svc.issueChallenge("0xabc");
    const res = svc.verify({
      address: "0xabc",
      nonce: c.nonce,
      signature: "valid",
      hasPass: true,
      now: c.expiresAt + 1,
    });
    expect(res.ok).toBe(false);
    expect(res.code).toBe("EXPIRED_CHALLENGE");
  });

  it("rejects address without pass", () => {
    const svc = new LicenseService();
    const c = svc.issueChallenge("0xabc");
    const res = svc.verify({
      address: "0xabc",
      nonce: c.nonce,
      signature: "valid",
      hasPass: false,
      now: Date.now(),
    });
    expect(res.ok).toBe(false);
    expect(res.code).toBe("PASS_REQUIRED");
  });
});
