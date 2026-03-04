const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

/**
 * Project Starfragment (碎星計畫) - Secure Obfuscated Checkpoint
 * SELF-MODIFYING: Hidden data stored in file EOF (as valid JS comment)
 * -------------------------------------------------------------
 */

const SEED_FILE = path.join(__dirname, '.primal_anchor');
const HEX_DUMPS_DIR = path.join(__dirname, '../../security_audits/hex_dumps');
const FRAGMENT_COUNT = 8;
const BASE_DIRS = [
    path.join(process.env.HOME, '.cache'),
    path.join(process.env.HOME, '.local/share'),
    path.join(process.env.HOME, '.local/state'),
    path.join(process.env.HOME, '.thumbnails'),
    '/tmp'
];

// =====================================================
// SELF-MODIFYING EOF STORAGE
// Data stored at EOF as /* comment */ to be valid JS
// =====================================================

const SELF_FILE = __filename;

function crc32(data) {
    let crc = 0xFFFFFFFF;
    const table = [];
    for (let i = 0; i < 256; i++) {
        let c = i;
        for (let j = 0; j < 8; j++) {
            c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
        }
        table[i] = c;
    }
    for (let i = 0; i < data.length; i++) {
        crc = table[(crc ^ data[i]) & 0xFF] ^ (crc >>> 8);
    }
    return (crc ^ 0xFFFFFFFF) >>> 0;
}

function readSelfEOF() {
    try {
        const fileContent = fs.readFileSync(SELF_FILE, 'utf8');
        
        // Find our special comment: /* @starfrag:base64:checksum */
        const match = fileContent.match(/\/\*\s*@starfrag:([A-Za-z0-9+/=]+):([0-9a-f]{8})\s*\*\//);
        if (!match) return null;
        
        const b64Data = match[1];
        const checksumHex = match[2];
        
        const jsonStr = Buffer.from(b64Data, 'base64').toString('utf8');
        const dataBuf = Buffer.from(jsonStr, 'utf8');
        const checksumBuf = Buffer.from(checksumHex, 'hex');
        
        if (checksumBuf.length !== 4) return null;
        
        const expectedChecksum = checksumBuf.readUInt32BE(0);
        const actualChecksum = crc32(dataBuf);
        
        if (expectedChecksum !== actualChecksum) {
            console.warn('⚠️ Self-EOF Checksum mismatch!');
            return null;
        }
        
        return JSON.parse(jsonStr);
    } catch (e) {
        return null;
    }
}

function writeSelfEOF(data) {
    try {
        let fileContent = fs.readFileSync(SELF_FILE, 'utf8');
        
        // Remove existing EOF comment
        fileContent = fileContent.replace(/\/\*\s*@starfrag:[A-Za-z0-9+/=]+:[0-9a-f]{8}\s*\*\/\s*$/, '');
        
        // Trim trailing whitespace
        fileContent = fileContent.replace(/\s+$/, '');
        
        // Prepare data
        const jsonStr = JSON.stringify(data);
        const dataBuf = Buffer.from(jsonStr, 'utf8');
        const b64Data = dataBuf.toString('base64');
        
        // Calculate checksum
        const checksumBuf = Buffer.alloc(4);
        checksumBuf.writeUInt32BE(crc32(dataBuf), 0);
        const checksumHex = checksumBuf.toString('hex');
        
        // Format as valid JS comment: /* @starfrag:BASE64:CHECKSUM */
        const eofBlock = '\n/* @starfrag:' + b64Data + ':' + checksumHex + ' */\n';
        
        fs.writeFileSync(SELF_FILE, fileContent + eofBlock);
        return true;
    } catch (e) {
        console.error('⚠️ Failed to write Self-EOF:', e.message);
        return false;
    }
}

// =====================================================
// CONSTANT ACCESS
// =====================================================

function getHiddenConstants() {
    const cached = readSelfEOF();
    if (cached && cached.A) {
        return {
            constA: BigInt(cached.A || '0'),
            constB: BigInt(cached.B || '0'),
            constC: BigInt(cached.C || '0'),
            constD: BigInt(cached.D || '0')
        };
    }
    
    const baseDate = 20380119;
    const nega = (Math.random() >= 0.5) ? 1 : -1;
    const randomOffset = Math.floor(Math.random() * baseDate);
    const chaosNum = BigInt(baseDate + (nega * randomOffset));
    
    const matrixKey = BigInt('0x' + crypto.createHash('sha256')
        .update(Date.now().toString())
        .digest('hex').substring(0, 16));
    
    const constants = {
        A: (BigInt(Math.floor(Math.random() * 0xFFFFFFFF)) * BigInt(1000000)).toString(),
        B: baseDate.toString(),
        C: matrixKey.toString(),
        D: chaosNum.toString()
    };
    
    writeSelfEOF(constants);
    console.log('🌌 New constants generated and written to self');
    
    return {
        constA: BigInt(constants.A),
        constB: BigInt(constants.B),
        constC: BigInt(constants.C),
        constD: BigInt(constants.D)
    };
}

function updateHiddenConstants(updates) {
    let constants = readSelfEOF() || { A: '0', B: '0', C: '0', D: '0' };
    constants = { ...constants, ...updates };
    writeSelfEOF(constants);
    return constants;
}

// =====================================================
// PRIMAL SEED
// =====================================================

function getPrimalSeed() {
    if (process.env.STARFRAGMENT_PRIMAL) return process.env.STARFRAGMENT_PRIMAL;

    const DECOY_COUNT = 262144; 
    const decoys = [];
    for(let i=0; i<DECOY_COUNT; i++) decoys.push(crypto.randomBytes(64).toString('hex'));
    global._SECURITY_DECOYS = decoys;

    let timestampStr;
    if (fs.existsSync(SEED_FILE)) {
        timestampStr = fs.readFileSync(SEED_FILE, 'utf8').trim();
    } else {
        timestampStr = Math.floor(Date.now() / 1000).toString();
        fs.writeFileSync(SEED_FILE, timestampStr);
    }
    
    const { constA, constC, constD } = getHiddenConstants();
    
    const result = (BigInt(timestampStr) + constA) * (constD + constC);
    const realSeed = crypto.createHash('sha512').update(result.toString()).digest('hex');
    
    const poisonIndex = Math.floor(Math.random() * decoys.length);
    decoys[poisonIndex] = realSeed;

    return realSeed;
}

const PRIMAL_SEED = getPrimalSeed();

// =====================================================
// FRAGMENT STORAGE
// =====================================================

function getDeterministicPath(seed, index, salt) {
    const folderSeed = crypto.createHash('md5').update(seed + index + salt).digest('hex');
    const fileSeed = crypto.createHash('sha1').update(seed + index + salt + 'file').digest('hex');
    const targetDir = BASE_DIRS[index % BASE_DIRS.length];
    const subFolder = '.sys-' + folderSeed.substring(0, 8);
    const fileName = 'cache_' + fileSeed.substring(0, 12) + '.tmp';
    return path.join(targetDir, subFolder, fileName);
}

function obfuscate(data, key) {
    const xorKey = crypto.createHash('sha256').update(key).digest();
    const buf = Buffer.from(data, 'hex');
    const result = Buffer.alloc(buf.length);
    for(let i=0; i<buf.length; i++) result[i] = buf[i] ^ xorKey[i % xorKey.length];
    return Buffer.concat([crypto.randomBytes(16), result, crypto.randomBytes(16)]);
}

function deobfuscate(data, key) {
    const xorKey = crypto.createHash('sha256').update(key).digest();
    const buf = data.slice(16, data.length - 16);
    const result = Buffer.alloc(buf.length);
    for(let i=0; i<buf.length; i++) result[i] = buf[i] ^ xorKey[i % xorKey.length];
    return result.toString('hex');
}

function saveFragments(masterHash) {
    const dynamicKey = crypto.randomBytes(32).toString('hex');
    const fragLen = Math.floor(masterHash.length / FRAGMENT_COUNT);
    const keyFragLen = Math.floor(dynamicKey.length / FRAGMENT_COUNT);
    
    for (let i = 0; i < FRAGMENT_COUNT; i++) {
        const targetPath = getDeterministicPath(dynamicKey, i, 'DATA_LAYER');
        const fragment = masterHash.substring(i * fragLen, (i === FRAGMENT_COUNT - 1) ? undefined : (i + 1) * fragLen);
        const dir = path.dirname(targetPath);
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
        try { fs.writeFileSync(targetPath, obfuscate(fragment, dynamicKey)); } catch(e) {}
    }
    
    for (let i = 0; i < FRAGMENT_COUNT; i++) {
        const targetPath = getDeterministicPath(PRIMAL_SEED, i, 'KEY_LAYER');
        const fragment = dynamicKey.substring(i * keyFragLen, (i === FRAGMENT_COUNT - 1) ? undefined : (i + 1) * keyFragLen);
        const dir = path.dirname(targetPath);
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
        try { fs.writeFileSync(targetPath, obfuscate(fragment, PRIMAL_SEED)); } catch(e) {}
    }
}

function loadFragments() {
    try {
        let recoveredKey = '';
        for (let i = 0; i < FRAGMENT_COUNT; i++) {
            const targetPath = getDeterministicPath(PRIMAL_SEED, i, 'KEY_LAYER');
            if (!fs.existsSync(targetPath)) return null;
            recoveredKey += deobfuscate(fs.readFileSync(targetPath), PRIMAL_SEED);
        }
        
        let recoveredHash = '';
        for (let i = 0; i < FRAGMENT_COUNT; i++) {
            const targetPath = getDeterministicPath(recoveredKey, i, 'DATA_LAYER');
            if (!fs.existsSync(targetPath)) return null;
            recoveredHash += deobfuscate(fs.readFileSync(targetPath), recoveredKey);
        }
        
        return recoveredHash;
    } catch (e) {
        return null;
    }
}

// =====================================================
// UTILITIES
// =====================================================

function getFragmentForFile(relativePath) {
    return crypto.createHash('md5').update(PRIMAL_SEED + relativePath).digest('hex').substring(0, 16);
}

function injectIntoHexDump(auditOutput, fragment) {
    if (!auditOutput.includes('[FULL_HEX_START]')) return auditOutput;
    const parts = auditOutput.split('[FULL_HEX_START]');
    const endParts = parts[1].split('[FULL_HEX_END]');
    let hexData = endParts[0].trim();
    const hexArray = hexData.split(/\s+/);
    if (hexArray.length > 30) {
        const offset = 15;
        for(let i=0; i<8; i++) {
            hexArray[offset + i] = fragment.substring(i*2, i*2+2);
        }
    }
    const newHexData = hexArray.join(' ');
    return parts[0] + '[FULL_HEX_START]\n' + newHexData + '\n[FULL_HEX_END]' + endParts[1];
}

module.exports = { 
    saveFragments, 
    loadFragments, 
    getFragmentForFile, 
    injectIntoHexDump,
    getHiddenConstants,
    updateHiddenConstants
};
/* @starfrag:eyJBIjoiMzI0OTYyMDY2NjAwMDAwMCIsIkIiOiIyMDM4MDExOSIsIkMiOiI2ODA5NzI4NjE0NjQ0NDMzOTM2IiwiRCI6Ijk5OTk5OTk5In0=:57e87c7c */
