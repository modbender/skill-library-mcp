/**
 * Mach-O Binary Parser - ported from Harkonnen concepts
 * Parses macOS/iOS executables for security analysis
 */

const { calculateEntropy } = require('./entropy');

// Mach-O magic numbers
const MAGIC = {
  MH_MAGIC: 0xfeedface,      // 32-bit
  MH_CIGAM: 0xcefaedfe,      // 32-bit, swapped
  MH_MAGIC_64: 0xfeedfacf,   // 64-bit
  MH_CIGAM_64: 0xcffaedfe,   // 64-bit, swapped
  FAT_MAGIC: 0xcafebabe,     // Universal binary
  FAT_CIGAM: 0xbebafeca      // Universal, swapped
};

// Load commands we care about
const LC = {
  LC_SEGMENT: 0x1,
  LC_SEGMENT_64: 0x19,
  LC_LOAD_DYLIB: 0xc,
  LC_LOAD_WEAK_DYLIB: 0x80000018,
  LC_REEXPORT_DYLIB: 0x8000001f,
  LC_CODE_SIGNATURE: 0x1d,
  LC_ENCRYPTION_INFO: 0x21,
  LC_ENCRYPTION_INFO_64: 0x2c,
  LC_DYLD_INFO: 0x22,
  LC_DYLD_INFO_ONLY: 0x80000022
};

// Suspicious dylibs (Frida, injection frameworks, etc.)
const SUSPICIOUS_DYLIBS = [
  'FridaGadget',
  'frida',
  'cynject',
  'libcycript',
  'MobileSubstrate',
  'SubstrateLoader',
  'SubstrateInserter',
  'substrate',
  'SSLKillSwitch',
  'TrustMe',
  'xcon',
  'libReveal',
  'RevealServer',
  'shadow'
];

// Suspicious segment names
const SUSPICIOUS_SEGMENTS = [
  '__INJECT',
  '__IMPORT',
  'UPX0',
  'UPX1',
  '__MALWARE',
  '__PACKED'
];

/**
 * Parse Mach-O binary
 * @param {Buffer} buffer - Binary data
 * @returns {object|null} Parsed info or null if not Mach-O
 */
function parseMachO(buffer) {
  if (buffer.length < 4) return null;

  const magicBE = buffer.readUInt32BE(0);

  // Check for FAT/Universal binary (always big-endian header)
  if (magicBE === MAGIC.FAT_MAGIC || magicBE === MAGIC.FAT_CIGAM) {
    return parseFatBinary(buffer);
  }

  // Check for regular Mach-O
  if (!isMachO(buffer)) return null;

  return parseSingleMachO(buffer, 0);
}

/**
 * Check if buffer starts with Mach-O magic (including FAT)
 */
function isMachO(buffer) {
  if (buffer.length < 4) return false;
  const magic = buffer.readUInt32LE(0);
  const magicBE = buffer.readUInt32BE(0);
  
  // Check regular Mach-O
  if (magic === MAGIC.MH_MAGIC || magic === MAGIC.MH_CIGAM ||
      magic === MAGIC.MH_MAGIC_64 || magic === MAGIC.MH_CIGAM_64) {
    return true;
  }
  
  // Check FAT/Universal (big-endian header)
  if (magicBE === MAGIC.FAT_MAGIC || magicBE === MAGIC.FAT_CIGAM) {
    return true;
  }
  
  return false;
}

/**
 * Parse a FAT/Universal binary
 */
function parseFatBinary(buffer) {
  const magic = buffer.readUInt32BE(0);
  const nArch = buffer.readUInt32BE(4);

  if (nArch > 10) return null; // Sanity check

  const architectures = [];
  let offset = 8;

  for (let i = 0; i < nArch && offset + 20 <= buffer.length; i++) {
    const cpuType = buffer.readUInt32BE(offset);
    const cpuSubtype = buffer.readUInt32BE(offset + 4);
    const archOffset = buffer.readUInt32BE(offset + 8);
    const archSize = buffer.readUInt32BE(offset + 12);

    if (archOffset + archSize <= buffer.length) {
      const archBuffer = buffer.slice(archOffset, archOffset + archSize);
      const parsed = parseSingleMachO(archBuffer, archOffset);
      if (parsed) {
        parsed.cpuType = cpuType;
        parsed.cpuSubtype = cpuSubtype;
        architectures.push(parsed);
      }
    }
    offset += 20;
  }

  return {
    type: 'fat',
    architectures
  };
}

/**
 * Parse a single Mach-O binary
 */
function parseSingleMachO(buffer, baseOffset = 0) {
  const magic = buffer.readUInt32LE(0);
  const is64 = (magic === MAGIC.MH_MAGIC_64 || magic === MAGIC.MH_CIGAM_64);
  const swapped = (magic === MAGIC.MH_CIGAM || magic === MAGIC.MH_CIGAM_64);

  const readU32 = swapped
    ? (off) => buffer.readUInt32BE(off)
    : (off) => buffer.readUInt32LE(off);

  // Parse header
  const headerSize = is64 ? 32 : 28;
  if (buffer.length < headerSize) return null;

  const cpuType = readU32(4);
  const cpuSubtype = readU32(8);
  const fileType = readU32(12);
  const nCmds = readU32(16);
  const sizeOfCmds = readU32(20);
  const flags = readU32(24);

  const result = {
    type: 'macho',
    is64,
    cpuType,
    cpuSubtype,
    fileType,
    flags,
    segments: [],
    dylibs: [],
    hasCodeSignature: false,
    isEncrypted: false,
    suspiciousFindings: [],
    entropy: calculateEntropy(buffer)
  };

  // Parse load commands
  let cmdOffset = headerSize;

  for (let i = 0; i < nCmds && cmdOffset + 8 <= buffer.length; i++) {
    const cmd = readU32(cmdOffset);
    const cmdSize = readU32(cmdOffset + 4);

    if (cmdSize < 8 || cmdOffset + cmdSize > buffer.length) break;

    // Parse segment
    if (cmd === LC.LC_SEGMENT || cmd === LC.LC_SEGMENT_64) {
      const segName = readCString(buffer, cmdOffset + 8, 16);
      result.segments.push(segName);

      if (SUSPICIOUS_SEGMENTS.some(s => segName.includes(s))) {
        result.suspiciousFindings.push(`Suspicious segment: ${segName}`);
      }
    }

    // Parse dylib loads
    if (cmd === LC.LC_LOAD_DYLIB || cmd === LC.LC_LOAD_WEAK_DYLIB || cmd === LC.LC_REEXPORT_DYLIB) {
      const nameOffset = readU32(cmdOffset + 8);
      if (cmdOffset + nameOffset < buffer.length) {
        const dylibName = readCString(buffer, cmdOffset + nameOffset, cmdSize - nameOffset);
        result.dylibs.push(dylibName);

        if (SUSPICIOUS_DYLIBS.some(s => dylibName.toLowerCase().includes(s.toLowerCase()))) {
          result.suspiciousFindings.push(`Suspicious dylib: ${dylibName}`);
        }
      }
    }

    // Check for code signature
    if (cmd === LC.LC_CODE_SIGNATURE) {
      result.hasCodeSignature = true;
    }

    // Check for encryption
    if (cmd === LC.LC_ENCRYPTION_INFO || cmd === LC.LC_ENCRYPTION_INFO_64) {
      const cryptId = readU32(cmdOffset + (cmd === LC.LC_ENCRYPTION_INFO_64 ? 16 : 12));
      if (cryptId !== 0) {
        result.isEncrypted = true;
        result.suspiciousFindings.push('Binary is encrypted');
      }
    }

    cmdOffset += cmdSize;
  }

  // Flag analysis
  const PIE = 0x200000;
  const ALLOW_STACK_EXECUTION = 0x20000;
  const NO_HEAP_EXECUTION = 0x1000000;

  if (!(flags & PIE)) {
    result.suspiciousFindings.push('PIE (ASLR) disabled');
  }
  if (flags & ALLOW_STACK_EXECUTION) {
    result.suspiciousFindings.push('Executable stack allowed');
  }
  if (!(flags & NO_HEAP_EXECUTION)) {
    result.suspiciousFindings.push('Executable heap allowed');
  }

  // High entropy check
  if (result.entropy > 7.0) {
    result.suspiciousFindings.push(`High entropy (${result.entropy.toFixed(2)}) - possibly packed`);
  }

  return result;
}

/**
 * Read null-terminated C string from buffer
 */
function readCString(buffer, offset, maxLen) {
  let end = offset;
  const limit = Math.min(offset + maxLen, buffer.length);

  while (end < limit && buffer[end] !== 0) {
    end++;
  }

  return buffer.slice(offset, end).toString('utf8');
}

/**
 * Calculate threat score for Mach-O binary
 * @returns {number} Score 0-100
 */
function calculateThreatScore(parsed) {
  if (!parsed) return 0;

  let score = 0;

  // Handle FAT binaries
  if (parsed.type === 'fat') {
    // Average score across architectures
    const scores = parsed.architectures.map(a => calculateThreatScore(a));
    return Math.max(...scores);
  }

  // Suspicious findings
  score += parsed.suspiciousFindings.length * 15;

  // Encryption without signature is suspicious
  if (parsed.isEncrypted && !parsed.hasCodeSignature) {
    score += 20;
  }

  // Missing code signature on modern macOS is unusual for legitimate apps
  if (!parsed.hasCodeSignature) {
    score += 10;
  }

  // High entropy
  if (parsed.entropy > 7.5) {
    score += 25;
  } else if (parsed.entropy > 7.0) {
    score += 15;
  }

  return Math.min(score, 100);
}

module.exports = {
  parseMachO,
  isMachO,
  calculateThreatScore,
  MAGIC,
  SUSPICIOUS_DYLIBS,
  SUSPICIOUS_SEGMENTS
};
