import { describe, it, expect } from "vitest";
import { getPublicKey, generateSecretKey } from "nostr-tools";

describe("AgentChat", () => {
  it("should generate keypair", () => {
    const privateKey = generateSecretKey();
    const publicKey = getPublicKey(privateKey);
    
    expect(privateKey).toHaveLength(32);
    expect(publicKey).toHaveLength(64);
  });
});
