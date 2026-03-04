import { createPublicClient, http } from 'viem';
import { mainnet } from 'viem/chains';

// ENS resolution always goes to Ethereum mainnet (read-only, no daemon needed)
const client = createPublicClient({
  chain: mainnet,
  transport: http('https://ethereum-rpc.publicnode.com'),
});

/**
 * Resolve an ENS name to an address.
 * @param {string} name - ENS name (e.g., "vitalik.eth")
 * @returns {Promise<{address: string|null, error: string|null}>}
 */
export async function resolveENS(name) {
  try {
    const address = await client.getEnsAddress({ name });
    if (!address) {
      return { address: null, error: `ENS name not found: ${name}` };
    }
    return { address, error: null };
  } catch (err) {
    return { address: null, error: `ENS resolution failed for ${name}: ${err.message}` };
  }
}

/**
 * Reverse-resolve an address to an ENS name.
 * @param {string} address - Ethereum address
 * @returns {Promise<{name: string|null, error: string|null}>}
 */
export async function reverseResolveENS(address) {
  try {
    const name = await client.getEnsName({ address });
    if (!name) {
      return { name: null, error: null };
    }
    return { name, error: null };
  } catch (err) {
    return { name: null, error: `ENS reverse resolution failed: ${err.message}` };
  }
}
