import { describe, it, expect } from "vitest";
import { NonceStore } from "../src/nonceStore.js";
import { ErrorCode } from "../src/errors.js";

describe("NonceStore", () => {
    it("issues and consumes a nonce", () => {
        const store = new NonceStore();
        const { nonce } = store.issue("0xabc");
        expect(() => store.consume(nonce, "0xabc")).not.toThrow();
    });

    it("rejects unknown nonce", () => {
        const store = new NonceStore();
        try {
            store.consume("bogus", "0xabc");
            expect.unreachable();
        } catch (e) {
            expect(e.code).toBe(ErrorCode.NONCE_UNKNOWN);
        }
    });

    it("rejects replay (consume twice)", () => {
        const store = new NonceStore();
        const { nonce } = store.issue("0xabc");
        store.consume(nonce, "0xabc");
        try {
            store.consume(nonce, "0xabc");
            expect.unreachable();
        } catch (e) {
            expect(e.code).toBe(ErrorCode.NONCE_REPLAY);
        }
    });

    it("rejects expired nonce", () => {
        const store = new NonceStore({ ttlMs: 100 });
        const { nonce, expiresAt } = store.issue("0xabc");
        try {
            store.consume(nonce, "0xabc", expiresAt + 1);
            expect.unreachable();
        } catch (e) {
            expect(e.code).toBe(ErrorCode.EXPIRED_CHALLENGE);
        }
    });

    it("rejects address mismatch", () => {
        const store = new NonceStore();
        const { nonce } = store.issue("0xabc");
        try {
            store.consume(nonce, "0xdef");
            expect.unreachable();
        } catch (e) {
            expect(e.code).toBe(ErrorCode.ADDRESS_MISMATCH);
        }
    });

    it("prunes expired entries", () => {
        const store = new NonceStore({ ttlMs: 1 });
        store.issue("0xabc");
        store.issue("0xdef");
        // Simulate time passing
        store._store.forEach((v) => { v.expiresAt = 0; });
        store.prune();
        expect(store._store.size).toBe(0);
    });
});
