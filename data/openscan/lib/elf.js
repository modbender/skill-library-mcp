/**
 * ELF Binary Parser - for Linux executable analysis
 * Parses ELF headers, sections, and detects suspicious patterns
 */

const { calculateEntropy } = require('./entropy');

// ELF magic
const ELF_MAGIC = Buffer.from([0x7f, 0x45, 0x4c, 0x46]); // \x7fELF

// ELF classes
const ELFCLASS32 = 1;
const ELFCLASS64 = 2;

// Section header types
const SHT = {
  SHT_NULL: 0,
  SHT_PROGBITS: 1,
  SHT_SYMTAB: 2,
  SHT_STRTAB: 3,
  SHT_DYNAMIC: 6,
  SHT_NOTE: 7,
  SHT_NOBITS: 8,
  SHT_DYNSYM: 11
};

// Suspicious shared objects
const SUSPICIOUS_LIBS = [
  'libfrida',
  'libcycript',
  'libsubstrate',
  'preload',
  'inject',
  'hook',
  'keylog',
  'rootkit',
  'backdoor'
];

// Suspicious section names
const SUSPICIOUS_SECTIONS = [
  '.evil',
  '.malware',
  '.inject',
  '.packed',
  'UPX',
  '.upx',
  '.aspack',
  '.petite',
  '.nsp'
];

/**
 * Check if buffer is ELF
 */
function isELF(buffer) {
  if (buffer.length < 4) return false;
  return buffer.slice(0, 4).equals(ELF_MAGIC);
}

/**
 * Parse ELF binary
 * @param {Buffer} buffer - Binary data
 * @returns {object|null} Parsed info or null if not ELF
 */
function parseELF(buffer) {
  if (!isELF(buffer)) return null;
  if (buffer.length < 52) return null; // Minimum ELF header size

  const elfClass = buffer[4];
  const is64 = elfClass === ELFCLASS64;
  const dataEncoding = buffer[5]; // 1 = little endian, 2 = big endian
  const isLE = dataEncoding === 1;

  const readU16 = isLE
    ? (off) => buffer.readUInt16LE(off)
    : (off) => buffer.readUInt16BE(off);

  const readU32 = isLE
    ? (off) => buffer.readUInt32LE(off)
    : (off) => buffer.readUInt32BE(off);

  const readU64 = isLE
    ? (off) => buffer.readBigUInt64LE(off)
    : (off) => buffer.readBigUInt64BE(off);

  // Parse ELF header
  const result = {
    type: 'elf',
    is64,
    isLE,
    osABI: buffer[7],
    elfType: readU16(16),
    machine: readU16(18),
    entryPoint: is64 ? Number(readU64(24)) : readU32(24),
    sections: [],
    dynamicLibs: [],
    suspiciousFindings: [],
    entropy: calculateEntropy(buffer),
    hasDebugInfo: false,
    isStripped: true,
    hasPIE: false,
    hasStackCanary: false,
    hasNX: false,
    hasRelRO: false
  };

  // Get section header info
  const shOff = is64 ? Number(readU64(40)) : readU32(32);
  const shEntSize = is64 ? readU16(58) : readU16(46);
  const shNum = is64 ? readU16(60) : readU16(48);
  const shStrIndex = is64 ? readU16(62) : readU16(50);

  if (shOff === 0 || shNum === 0 || shOff + shNum * shEntSize > buffer.length) {
    // No section headers or invalid
    return result;
  }

  // First, get the section string table
  let strTabOff = 0;
  let strTabSize = 0;

  if (shStrIndex < shNum) {
    const strTabSecOff = shOff + shStrIndex * shEntSize;
    if (is64) {
      strTabOff = Number(readU64(strTabSecOff + 24));
      strTabSize = Number(readU64(strTabSecOff + 32));
    } else {
      strTabOff = readU32(strTabSecOff + 16);
      strTabSize = readU32(strTabSecOff + 20);
    }
  }

  // Parse section headers
  for (let i = 0; i < shNum; i++) {
    const secOff = shOff + i * shEntSize;
    if (secOff + shEntSize > buffer.length) break;

    const shName = readU32(secOff);
    const shType = readU32(secOff + 4);
    const shFlags = is64 ? Number(readU64(secOff + 8)) : readU32(secOff + 8);
    const shAddr = is64 ? Number(readU64(secOff + 16)) : readU32(secOff + 12);
    const shOffset = is64 ? Number(readU64(secOff + 24)) : readU32(secOff + 16);
    const shSize = is64 ? Number(readU64(secOff + 32)) : readU32(secOff + 20);

    // Get section name from string table
    let sectionName = '';
    if (strTabOff > 0 && shName < strTabSize) {
      const nameStart = strTabOff + shName;
      let nameEnd = nameStart;
      while (nameEnd < buffer.length && nameEnd < strTabOff + strTabSize && buffer[nameEnd] !== 0) {
        nameEnd++;
      }
      sectionName = buffer.slice(nameStart, nameEnd).toString('utf8');
    }

    result.sections.push({
      name: sectionName,
      type: shType,
      flags: shFlags,
      addr: shAddr,
      offset: shOffset,
      size: shSize
    });

    // Check for suspicious section names
    if (SUSPICIOUS_SECTIONS.some(s => sectionName.toLowerCase().includes(s.toLowerCase()))) {
      result.suspiciousFindings.push(`Suspicious section: ${sectionName}`);
    }

    // Check for debug info
    if (sectionName.startsWith('.debug') || sectionName === '.symtab') {
      result.hasDebugInfo = true;
      result.isStripped = false;
    }

    // Check for stack canary
    if (sectionName === '.note.gnu.build-id') {
      result.hasStackCanary = true;
    }
  }

  // Parse dynamic section for libraries
  const dynSection = result.sections.find(s => s.type === SHT.SHT_DYNAMIC);
  const dynStrSection = result.sections.find(s => s.name === '.dynstr');

  if (dynSection && dynStrSection && dynSection.offset + dynSection.size <= buffer.length) {
    parseDynamicSection(buffer, dynSection, dynStrSection, result, is64, readU64, readU32);
  }

  // Analyze program headers for security features
  const phOff = is64 ? Number(readU64(32)) : readU32(28);
  const phEntSize = is64 ? readU16(54) : readU16(42);
  const phNum = is64 ? readU16(56) : readU16(44);

  if (phOff > 0 && phNum > 0 && phOff + phNum * phEntSize <= buffer.length) {
    for (let i = 0; i < phNum; i++) {
      const phEntry = phOff + i * phEntSize;
      const pType = readU32(phEntry);
      const pFlags = is64 ? readU32(phEntry + 4) : readU32(phEntry + 24);

      // PT_GNU_STACK (0x6474e551) - check NX
      if (pType === 0x6474e551) {
        result.hasNX = !(pFlags & 1); // No execute if PF_X not set
      }

      // PT_GNU_RELRO (0x6474e552)
      if (pType === 0x6474e552) {
        result.hasRelRO = true;
      }
    }
  }

  // Check ELF type for PIE
  // ET_DYN (3) can be PIE
  if (result.elfType === 3) {
    result.hasPIE = true;
  }

  // High entropy check
  if (result.entropy > 7.0) {
    result.suspiciousFindings.push(`High entropy (${result.entropy.toFixed(2)}) - possibly packed`);
  }

  // Security feature warnings
  if (!result.hasPIE) {
    result.suspiciousFindings.push('ASLR/PIE disabled');
  }
  if (!result.hasNX) {
    result.suspiciousFindings.push('NX (No-Execute) disabled - executable stack');
  }

  return result;
}

/**
 * Parse the dynamic section for library dependencies
 */
function parseDynamicSection(buffer, dynSection, dynStrSection, result, is64, readU64, readU32) {
  const entrySize = is64 ? 16 : 8;
  const DT_NEEDED = 1;
  const DT_NULL = 0;

  for (let off = dynSection.offset; off < dynSection.offset + dynSection.size; off += entrySize) {
    if (off + entrySize > buffer.length) break;

    const tag = is64 ? Number(readU64(off)) : readU32(off);
    const val = is64 ? Number(readU64(off + 8)) : readU32(off + 4);

    if (tag === DT_NULL) break;

    if (tag === DT_NEEDED) {
      // val is offset into .dynstr
      const strStart = dynStrSection.offset + val;
      if (strStart < buffer.length) {
        let strEnd = strStart;
        while (strEnd < buffer.length && buffer[strEnd] !== 0) {
          strEnd++;
        }
        const libName = buffer.slice(strStart, strEnd).toString('utf8');
        result.dynamicLibs.push(libName);

        if (SUSPICIOUS_LIBS.some(s => libName.toLowerCase().includes(s.toLowerCase()))) {
          result.suspiciousFindings.push(`Suspicious library: ${libName}`);
        }
      }
    }
  }
}

/**
 * Calculate threat score for ELF binary
 * @returns {number} Score 0-100
 */
function calculateThreatScore(parsed) {
  if (!parsed) return 0;

  let score = 0;

  // Suspicious findings
  score += parsed.suspiciousFindings.length * 15;

  // Security features missing
  if (!parsed.hasPIE) score += 10;
  if (!parsed.hasNX) score += 15;
  if (!parsed.hasRelRO) score += 5;

  // Stripped binary with suspicious patterns is more concerning
  if (parsed.isStripped && parsed.suspiciousFindings.length > 0) {
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
  parseELF,
  isELF,
  calculateThreatScore,
  SUSPICIOUS_LIBS,
  SUSPICIOUS_SECTIONS
};
