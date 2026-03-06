import { describe, it, expect } from 'vitest';
import { Signer } from '../src/lib/signer';

describe('Signer', () => {
    const TEST_KEY = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'; // Well known anvil key
    const EXPECTED_ADDRESS = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266';

    it('should derive the correct address from private key', () => {
        const signer = new Signer(TEST_KEY);
        expect(signer.getAddress().toLowerCase()).toBe(EXPECTED_ADDRESS.toLowerCase());
    });

    it('should sign a message correctly', async () => {
        const signer = new Signer(TEST_KEY);
        const message = "hello gatex402";
        const signature = await signer.signMessage(message);

        expect(signature).toBeDefined();
        expect(signature.startsWith('0x')).toBe(true);
        expect(signature.length).toBe(132); // Standard EIP-191 signature length
    });
});
