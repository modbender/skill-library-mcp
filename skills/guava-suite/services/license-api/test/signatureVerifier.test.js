import { describe, it, expect } from "vitest";
import { SignatureVerifier } from "../src/signatureVerifier.js";
import { ErrorCode } from "../src/errors.js";

describe("SignatureVerifier (stub mode)", () => {
    it("accepts valid stub signature", () => {
        const v = new SignatureVerifier();
        expect(() =>
            v.verify({ address: "0xabc", nonce: "some-nonce", signature: "valid" })
        ).not.toThrow();
    });

    it("rejects invalid stub signature", () => {
        const v = new SignatureVerifier();
        try {
            v.verify({ address: "0xabc", nonce: "some-nonce", signature: "garbage" });
            expect.unreachable();
        } catch (e) {
            expect(e.code).toBe(ErrorCode.INVALID_SIGNATURE);
        }
    });
});

describe("SignatureVerifier (ethers injected)", () => {
    it("accepts matching signer", () => {
        const mockEthers = {
            verifyTypedData: () => "0xABC",
        };
        const v = new SignatureVerifier({ ethers: mockEthers });
        expect(() =>
            v.verify({ address: "0xABC", nonce: "n1", signature: "0xsig" })
        ).not.toThrow();
    });

    it("rejects mismatched signer", () => {
        const mockEthers = {
            verifyTypedData: () => "0xDEF",
        };
        const v = new SignatureVerifier({ ethers: mockEthers });
        try {
            v.verify({ address: "0xABC", nonce: "n1", signature: "0xsig" });
            expect.unreachable();
        } catch (e) {
            expect(e.code).toBe(ErrorCode.INVALID_SIGNATURE);
        }
    });

    it("wraps ethers errors as INVALID_SIGNATURE", () => {
        const mockEthers = {
            verifyTypedData: () => { throw new Error("bad sig encoding"); },
        };
        const v = new SignatureVerifier({ ethers: mockEthers });
        try {
            v.verify({ address: "0xABC", nonce: "n1", signature: "0xbad" });
            expect.unreachable();
        } catch (e) {
            expect(e.code).toBe(ErrorCode.INVALID_SIGNATURE);
            expect(e.message).toContain("bad sig encoding");
        }
    });
});
