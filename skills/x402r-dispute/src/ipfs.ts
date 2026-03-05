/**
 * IPFS pinning — uses Pinata JWT, falls back to placeholder CID.
 */

import { getConfig } from "./config.js";

/**
 * Pin JSON to IPFS.
 * 1. Pinata JWT (required for production use)
 * 2. Placeholder CID fallback (dev/testing only)
 */
export async function pinToIpfs(data: Record<string, unknown>): Promise<string> {
  const config = getConfig();

  if (config.pinataJwt) {
    console.log("  Pinning to IPFS via Pinata...");
    try {
      const response = await fetch("https://api.pinata.cloud/pinning/pinJSONToIPFS", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${config.pinataJwt}`,
        },
        body: JSON.stringify({
          pinataContent: data,
          pinataMetadata: { name: `x402r-evidence-${Date.now()}` },
        }),
      });
      if (response.ok) {
        const result = (await response.json()) as { IpfsHash: string };
        console.log(`  Pinned: ${result.IpfsHash}`);
        return result.IpfsHash;
      }
      console.warn(`  Pinata failed (${response.status})`);
    } catch (err) {
      console.warn(`  Pinata error:`, err instanceof Error ? err.message : err);
    }
  }

  // Placeholder fallback
  console.log("  (Using placeholder CID — set pinataJwt in config for production)");
  return "QmXyxi3LYRb33bThaHLtotFxcG4FXnDowC2d5EjwYqE4iR";
}
