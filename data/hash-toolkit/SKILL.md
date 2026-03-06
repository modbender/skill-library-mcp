---
id: hash-toolkit
version: 1.0.0
name: Hash Toolkit
description: Content hashing for deduplication with MD5, SHA256, and perceptual hashing
author: NeoClaw Team
category: utility
tags:
  - hashing
  - deduplication
  - md5
  - sha256
dependencies: []
---

# Hash Toolkit

Multi-algorithm hashing for content deduplication and verification.

## Implementation

```javascript
const crypto = require('crypto');

/**
 * Generate hash using specified algorithm
 * @param {string|Buffer} content - Content to hash
 * @param {string} algorithm - Hash algorithm
 * @returns {string} Hash string
 */
function generateHash(content, algorithm = 'sha256') {
  const hash = crypto.createHash(algorithm);
  hash.update(Buffer.isBuffer(content) ? content : String(content));
  return hash.digest('hex');
}

/**
 * Generate multiple hashes at once
 */
function generateMultipleHashes(content) {
  return {
    md5: generateHash(content, 'md5'),
    sha1: generateHash(content, 'sha1'),
    sha256: generateHash(content, 'sha256'),
    sha512: generateHash(content, 'sha512').substring(0, 32) // Truncated
  };
}

/**
 * Generate perceptual hash (for images/content similarity)
 * Simplified implementation
 */
function generatePerceptualHash(content) {
  // Simplified perceptual hash
  // In production: use actual perceptual hashing algorithm
  const normalized = String(content).toLowerCase().replace(/\s+/g, ' ');
  return generateHash(normalized, 'sha256').substring(0, 16);
}

/**
 * Check if content is duplicate based on hash
 */
function checkDuplicate(contentHash, knownHashes) {
  return {
    isDuplicate: knownHashes.has(contentHash),
    hash: contentHash,
    algorithm: 'sha256'
  };
}

/**
 * Calculate similarity between two hashes
 * (for perceptual hashes)
 */
function calculateHashSimilarity(hash1, hash2) {
  if (hash1.length !== hash2.length) return 0;

  let matches = 0;
  for (let i = 0; i < hash1.length; i++) {
    if (hash1[i] === hash2[i]) matches++;
  }

  return matches / hash1.length;
}

// Export for OpenClaw
module.exports = {
  generateHash,
  generateMultipleHashes,
  generatePerceptualHash,
  checkDuplicate,
  calculateHashSimilarity
};
```

## Usage

```javascript
// Generate SHA256 hash
const hash = skills.hashToolkit.generateHash(content, 'sha256');

// Generate multiple hashes
const hashes = skills.hashToolkit.generateMultipleHashes(content);
console.log(hashes.md5, hashes.sha256);

// Check for duplicates
const knownHashes = new Set(['abc123...']);
const result = skills.hashToolkit.checkDuplicate(hash, knownHashes);
if (result.isDuplicate) {
  console.log('Duplicate content detected');
}

// Perceptual hash for similarity
const phash = skills.hashToolkit.generatePerceptualHash(imageData);
```

## Configuration

```json
{
  "defaultAlgorithm": "sha256",
  "enablePerceptual": true
}
```
