const { ethers } = require('ethers');

/**
 * Computes a deterministic thread hash using abi.encode (Standard Solidity Encoding)
 * to avoid collisions inherent in abi.encodePacked.
 * 
 * @param {string} sender - The original sender's address (UP)
 * @param {number} timestamp - The original message timestamp
 * @param {string} subject - The original message subject
 * @param {string} body - The original message body
 * @returns {string} The keccak256 hash
 */
function computeReplyToHash(sender, timestamp, subject, body) {
    const abiCoder = new ethers.AbiCoder();
    const encoded = abiCoder.encode(
        ['address', 'uint256', 'string', 'string'],
        [sender, timestamp, subject, body]
    );
    return ethers.keccak256(encoded);
}

module.exports = {
    computeReplyToHash
};
