const { ethers } = require('ethers');

// Standardized threading logic from v0.1.2
function computeReplyToHash(sender, timestamp, subject, body) {
    const abiCoder = new ethers.AbiCoder();
    const encoded = abiCoder.encode(
        ['address', 'uint256', 'string', 'string'],
        [sender, timestamp, subject, body]
    );
    return ethers.keccak256(encoded);
}

const testParams = {
    sender: '0x36c2034025705ad0e681d860f0fd51e84c37b629',
    timestamp: 1708425600,
    subject: 'The Play',
    body: 'Deploy v0.1 as custom metadata.'
};

const hash = computeReplyToHash(
    testParams.sender,
    testParams.timestamp,
    testParams.subject,
    testParams.body
);

const expectedHash = '0x2c7592f025d3c79735e2c0c5be8da96515ee48240141036272c67ae71f8c11f9';

console.log('--- LUKSO Agent Comms v0.1.2 Parity Test ---');
console.log('Sender:   ', testParams.sender);
console.log('Timestamp:', testParams.timestamp);
console.log('Subject:  ', testParams.subject);
console.log('Body:     ', testParams.body);
console.log('-------------------------------------------');
console.log('Computed Hash:', hash);
console.log('Expected Hash:', expectedHash);
console.log('-------------------------------------------');

if (hash === expectedHash) {
    console.log('RESULT: ✅ PARITY CONFIRMED');
} else {
    console.log('RESULT: ❌ HASH MISMATCH');
    process.exit(1);
}
