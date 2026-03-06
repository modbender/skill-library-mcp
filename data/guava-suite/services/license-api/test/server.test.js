import { describe, it, expect, beforeAll, afterAll } from "vitest";
import http from "node:http";
import { server } from "../src/server.js";

const PORT = 13100; // Test port to avoid conflict

function fetch(path, { method = "POST", body } = {}) {
    return new Promise((resolve, reject) => {
        const data = body ? JSON.stringify(body) : "";
        const req = http.request(
            {
                hostname: "127.0.0.1", port: PORT, path, method,
                headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(data) }
            },
            (res) => {
                const chunks = [];
                res.on("data", (c) => chunks.push(c));
                res.on("end", () => {
                    const text = Buffer.concat(chunks).toString();
                    try { resolve({ status: res.statusCode, body: JSON.parse(text) }); }
                    catch { resolve({ status: res.statusCode, body: text }); }
                });
            }
        );
        req.on("error", reject);
        req.end(data);
    });
}

describe("License API HTTP endpoints", () => {
    beforeAll(() => new Promise((resolve) => server.listen(PORT, resolve)));
    afterAll(() => new Promise((resolve) => server.close(resolve)));

    it("GET /health returns 200", async () => {
        const res = await fetch("/health", { method: "GET" });
        expect(res.status).toBe(200);
        expect(res.body.ok).toBe(true);
        expect(res.body.service).toBe("license-api");
    });

    it("POST /license/challenge returns nonce", async () => {
        const res = await fetch("/license/challenge", {
            body: { address: "0x4F0C2d66AAe133A023Abb81a07640275e72Ed5d7" },
        });
        expect(res.status).toBe(200);
        expect(res.body.ok).toBe(true);
        expect(res.body.nonce).toBeTruthy();
        expect(res.body.expiresAt).toBeGreaterThan(Date.now());
    });

    it("POST /license/challenge rejects missing address", async () => {
        const res = await fetch("/license/challenge", { body: {} });
        expect(res.status).toBe(400);
        expect(res.body.ok).toBe(false);
    });

    it("full flow: challenge → verify → JWT", async () => {
        const addr = "0x4F0C2d66AAe133A023Abb81a07640275e72Ed5d7";

        // 1. Get challenge
        const challengeRes = await fetch("/license/challenge", { body: { address: addr } });
        expect(challengeRes.status).toBe(200);
        const { nonce } = challengeRes.body;

        // 2. Verify with stub signature
        const verifyRes = await fetch("/license/verify", {
            body: { address: addr, nonce, signature: "valid", hasPass: true },
        });
        expect(verifyRes.status).toBe(200);
        expect(verifyRes.body.ok).toBe(true);
        expect(verifyRes.body.token).toBeTruthy();
        expect(verifyRes.body.expiresIn).toBe("24h");
    });

    it("verify rejects replay", async () => {
        const addr = "0xabc";
        const c = await fetch("/license/challenge", { body: { address: addr } });
        const { nonce } = c.body;

        // First verify — OK
        await fetch("/license/verify", {
            body: { address: addr, nonce, signature: "valid", hasPass: true },
        });

        // Second verify — replay rejected
        const replay = await fetch("/license/verify", {
            body: { address: addr, nonce, signature: "valid", hasPass: true },
        });
        expect(replay.body.ok).toBe(false);
        expect(replay.body.code).toBe("NONCE_REPLAY");
    });

    it("verify rejects invalid signature", async () => {
        const addr = "0xabc";
        const c = await fetch("/license/challenge", { body: { address: addr } });
        const res = await fetch("/license/verify", {
            body: { address: addr, nonce: c.body.nonce, signature: "bad", hasPass: true },
        });
        expect(res.body.ok).toBe(false);
        expect(res.body.code).toBe("INVALID_SIGNATURE");
    });

    it("verify rejects without pass", async () => {
        const addr = "0xabc";
        const c = await fetch("/license/challenge", { body: { address: addr } });
        const res = await fetch("/license/verify", {
            body: { address: addr, nonce: c.body.nonce, signature: "valid", hasPass: false },
        });
        expect(res.body.ok).toBe(false);
        expect(res.body.code).toBe("PASS_REQUIRED");
    });

    it("returns 404 for unknown routes", async () => {
        const res = await fetch("/unknown", { method: "GET" });
        expect(res.status).toBe(404);
    });
});
