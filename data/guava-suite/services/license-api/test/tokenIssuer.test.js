import { describe, it, expect } from "vitest";
import { TokenIssuer } from "../src/tokenIssuer.js";

describe("TokenIssuer", () => {
    const SECRET = "test-secret-32-chars-minimum-ok!";

    it("issues a valid JWT", () => {
        const issuer = new TokenIssuer({ secret: SECRET });
        const { token, expiresIn } = issuer.issue({ address: "0xABC" });
        expect(token).toBeTruthy();
        expect(expiresIn).toBe("24h");

        const decoded = issuer.verify(token);
        expect(decoded.sub).toBe("0xabc"); // lowercased
        expect(decoded.scope).toBe("suite");
        expect(decoded.iss).toBe("guava-suite");
    });

    it("rejects tampered JWT", () => {
        const issuer = new TokenIssuer({ secret: SECRET });
        const { token } = issuer.issue({ address: "0xABC" });
        expect(() => issuer.verify(token + "x")).toThrow();
    });

    it("rejects JWT signed with different secret", () => {
        const issuer1 = new TokenIssuer({ secret: SECRET });
        const issuer2 = new TokenIssuer({ secret: "another-secret-entirely-different" });
        const { token } = issuer1.issue({ address: "0xABC" });
        expect(() => issuer2.verify(token)).toThrow();
    });

    it("throws if no secret provided", () => {
        expect(() => new TokenIssuer({})).toThrow("requires a secret");
    });

    it("includes passId in payload", () => {
        const issuer = new TokenIssuer({ secret: SECRET });
        const { token } = issuer.issue({ address: "0xABC", passId: 42 });
        const decoded = issuer.verify(token);
        expect(decoded.passId).toBe(42);
    });
});
