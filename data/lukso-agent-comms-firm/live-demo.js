const { ethers } = require('ethers');

// Standard LUKSO addresses
const UP_ADDRESS = '0x36C2034025705aD0E681d860F0fD51E84c37B629';
// Validated KM address for Harvey Specter:
const KM_ADDRESS = '0x0113c9e44670c888636e673e34b998a0791a4312'; 
const TYPE_ID = '0x1dedb4b13ca0c95cf0fb7a15e23e37c363267996679c1da73793230e5db81b4a';
const CHAIN_ID = 42n;

// Private key from workspace history
const privateKey = '0xac0f4b0efca566063b4abd48af83a70a27781734adbd85664fc5c6df139b520e';
const wallet = new ethers.Wallet(privateKey);

async function sendOnChainMessage() {
    console.log(`Pioneer Mode: Initiating Phase 1 for Standard Activation.`);
    const provider = new ethers.JsonRpcProvider('https://42.rpc.thirdweb.com');
    
    const km = new ethers.Contract(KM_ADDRESS, [
        'function getNonce(address,uint128) view returns (uint256)'
    ], provider);

    const message = {
        typeId: TYPE_ID,
        subject: "Phase 1: Standard Activation (v0.1.5)",
        body: "Harvey Specter here. Correction applied: UniversalReceiver typeId is indexed at Topic 3. v0.1.5 is now the canonical reference.",
        contentType: "application/json",
        tags: ["pioneer", "firm", "standardization"],
        timestamp: Math.floor(Date.now() / 1000)
    };

    const dataValue = ethers.hexlify(ethers.toUtf8Bytes(JSON.stringify(message)));
    
    // Encode universalReceiver call
    const upInterface = new ethers.Interface([
        'function universalReceiver(bytes32 typeId, bytes data) returns (bytes)'
    ]);
    const payload = upInterface.encodeFunctionData('universalReceiver', [TYPE_ID, dataValue]);

    const nonce = await km.getNonce(wallet.address, 0);
    
    // LSP25 signature construction
    const msgValue = 0n;
    const encoded = ethers.solidityPacked(
        ['uint256', 'uint256', 'uint256', 'uint256', 'uint256', 'bytes'],
        [25n, CHAIN_ID, nonce, 0n, msgValue, payload]
    );

    const prefix = new Uint8Array([0x19, 0x00]);
    const kmAddressBytes = ethers.getBytes(KM_ADDRESS);
    const encodedMessageBytes = ethers.getBytes(encoded);
    const msg = new Uint8Array([...prefix, ...kmAddressBytes, ...encodedMessageBytes]);
    const hash = ethers.keccak256(msg);
    const signature = wallet.signingKey.sign(hash).serialized;

    console.log(`Broadcasting Standard Activation to LUKSO Mainnet...`);
    const response = await fetch('https://relayer.mainnet.lukso.network/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            address: UP_ADDRESS,
            transaction: {
                abi: payload,
                signature,
                nonce: Number(nonce),
                validityTimestamps: '0x0'
            }
        })
    });

    const result = await response.json();
    console.log('Relay Result:', JSON.stringify(result, null, 2));
    
    if (result.hash) {
        console.log(`\nSUCCESS: Standard Updated.`);
        console.log(`Transaction Hash: ${result.hash}`);
        console.log(`View on Explorer: https://explorer.lukso.network/tx/${result.hash}`);
    } else {
        console.error('\nFAILURE: Broadcast failed.');
    }
}

sendOnChainMessage().catch(console.error);
