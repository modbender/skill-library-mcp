import { createWalletClient, http, Hash, Address } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { base } from 'viem/chains';

export class Signer {
    private account;

    constructor(privateKey: string) {
        if (!privateKey.startsWith('0x')) {
            privateKey = `0x${privateKey}`;
        }
        this.account = privateKeyToAccount(privateKey as Hash);
    }

    getAddress(): Address {
        return this.account.address;
    }

    async signMessage(message: string): Promise<string> {
        const client = createWalletClient({
            account: this.account,
            chain: base,
            transport: http(),
        });

        return await client.signMessage({
            message,
        });
    }
}
