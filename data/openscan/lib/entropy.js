/**
 * Entropy calculation - ported from Harkonnen static-analysis.h
 * Shannon entropy for detecting packed/encrypted binaries
 */

/**
 * Calculate Shannon entropy of a buffer
 * @param {Buffer} buffer - Binary data to analyze
 * @returns {number} Entropy value 0-8 (8 = maximum randomness)
 */
function calculateEntropy(buffer) {
  if (!buffer || buffer.length === 0) return 0;

  // Count byte frequencies
  const byteCounts = new Array(256).fill(0);
  for (let i = 0; i < buffer.length; i++) {
    byteCounts[buffer[i]]++;
  }

  // Calculate Shannon entropy
  let entropy = 0;
  const size = buffer.length;

  for (let i = 0; i < 256; i++) {
    if (byteCounts[i] > 0) {
      const probability = byteCounts[i] / size;
      entropy -= probability * Math.log2(probability);
    }
  }

  return entropy;
}

/**
 * Calculate entropy for sections of a binary
 * Useful for detecting packed sections within otherwise normal binaries
 * @param {Buffer} buffer - Binary data
 * @param {number} chunkSize - Size of each chunk to analyze
 * @returns {Array<{offset: number, entropy: number}>}
 */
function calculateSectionEntropy(buffer, chunkSize = 4096) {
  const results = [];

  for (let offset = 0; offset < buffer.length; offset += chunkSize) {
    const end = Math.min(offset + chunkSize, buffer.length);
    const chunk = buffer.slice(offset, end);
    results.push({
      offset,
      size: chunk.length,
      entropy: calculateEntropy(chunk)
    });
  }

  return results;
}

/**
 * Detect if binary is likely packed/encrypted based on entropy
 * @param {Buffer} buffer 
 * @returns {{isPacked: boolean, entropy: number, highEntropyRegions: number}}
 */
function detectPacking(buffer) {
  const overallEntropy = calculateEntropy(buffer);
  const sections = calculateSectionEntropy(buffer);

  // Count sections with very high entropy (>7.5)
  const highEntropyRegions = sections.filter(s => s.entropy > 7.5).length;

  return {
    isPacked: overallEntropy > 7.0 || highEntropyRegions > sections.length * 0.5,
    entropy: overallEntropy,
    highEntropyRegions,
    totalRegions: sections.length
  };
}

module.exports = {
  calculateEntropy,
  calculateSectionEntropy,
  detectPacking
};
