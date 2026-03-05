const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const tar = require('tar');
const { uploadToIPFS } = require('./upload');
const { anchorCID } = require('./anchor');

// Constants for encryption
const IV_SIZE = 12;
const AUTH_TAG_SIZE = 16;
const SALT_SIZE = 32;
const PBKDF2_ITERATIONS = 100000;
const KEY_SIZE = 32;

// Paths to backup (go up 2 levels to reach workspace root)
const filesToBackup = [
  'IDENTITY.md',
  'SOUL.md',
  'USER.md',
  'TOOLS.md',
];
const memoryDir = path.resolve(__dirname, '../..', 'memory');

/**
 * Derive encryption key using PBKDF2 with random salt
 * @param {Buffer} secretKey - Source secret key
 * @param {Buffer} salt - Random salt
 * @returns {Buffer} 32-byte derived key
 */
function deriveKey(secretKey, salt) {
  return crypto.pbkdf2Sync(secretKey, salt, PBKDF2_ITERATIONS, KEY_SIZE, 'sha256');
}

/**
 * Clean up temporary files
 * @param {string[]} files - Array of file paths to delete
 */
function cleanupFiles(files) {
  for (const file of files) {
    try {
      if (fs.existsSync(file)) {
        fs.unlinkSync(file);
        console.log('Cleaned up:', path.basename(file));
      }
    } catch (err) {
      console.error('Failed to clean up', file, err.message);
    }
  }
}

/**
 * Validate CID format to prevent SSRF
 * @param {string} cid - Content Identifier to validate
 * @returns {boolean} - True if valid
 */
function validateCID(cid) {
  // CIDv0: Qm + 44 base58 chars
  // CIDv1: starts with bafy, bafk, bafz, etc + base32 chars
  if (!cid || typeof cid !== 'string') return false;
  
  // Basic length check
  if (cid.length < 32 || cid.length > 128) return false;
  
  // Check for valid characters (base58 for CIDv0, base32 for CIDv1)
  const validPattern = /^[A-Za-z0-9]+$/;
  if (!validPattern.test(cid)) return false;
  
  // CIDv0 check
  if (cid.startsWith('Qm') && cid.length === 46) return true;
  
  // CIDv1 check (various codecs)
  if (cid.startsWith('baf') && cid.length >= 59) return true;
  
  return false;
}

async function createBackup() {
  const tempFiles = [];
  const entry = { timestamp: new Date().toISOString() };
  
  try {
    // Create a temporary tar.gz archive
    const archivePath = path.resolve(__dirname, 'backup.tar.gz');
    const tarFiles = filesToBackup.map(f => path.resolve(__dirname, '..', f));
    const cwd = path.resolve(__dirname, '../..');
    
    await tar.c(
      {
        gzip: true,
        file: archivePath,
        cwd,
      },
      [...filesToBackup, 'memory']
    );
    tempFiles.push(archivePath);

    // Generate SHA-256 hash of archive before encryption
    const archiveBuffer = fs.readFileSync(archivePath);
    const checksum = crypto.createHash('sha256').update(archiveBuffer).digest('hex');
    const checksumPath = path.resolve(__dirname, 'checksum.txt');
    fs.writeFileSync(checksumPath, checksum);
    tempFiles.push(checksumPath);
    console.log('Archive checksum:', checksum);

    // Create payload with archive + checksum
    const payloadPath = path.resolve(__dirname, 'payload.tar');
    await tar.c(
      {
        file: payloadPath,
        cwd: __dirname,
      },
      ['backup.tar.gz', 'checksum.txt']
    );
    tempFiles.push(payloadPath);

    // Load wallet secret key
    const walletPath = path.resolve(__dirname, '../..', 'x1_vault_cli', 'wallet.json');
    if (!fs.existsSync(walletPath)) {
      throw new Error(`Wallet not found at ${walletPath}`);
    }
    const wallet = JSON.parse(fs.readFileSync(walletPath, 'utf8'));
    const secretKey = Buffer.from(wallet.secretKey);
    
    // Generate random salt and derive key using PBKDF2
    const salt = crypto.randomBytes(SALT_SIZE);
    const key = deriveKey(secretKey, salt);
    
    // Encrypt the payload with AES-256-GCM
    const iv = crypto.randomBytes(IV_SIZE);
    const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
    const payloadBuffer = fs.readFileSync(payloadPath);
    const encrypted = Buffer.concat([cipher.update(payloadBuffer), cipher.final()]);
    const authTag = cipher.getAuthTag(); // AUTH_TAG_SIZE bytes
    
    // Structure: salt (32) + iv (12) + ciphertext + authTag (16)
    const encryptedData = Buffer.concat([salt, iv, encrypted, authTag]);
    const encryptedPath = archivePath + '.enc';
    fs.writeFileSync(encryptedPath, encryptedData);
    tempFiles.push(encryptedPath);

    // Upload encrypted backup to Pinata
    const cid = await uploadToIPFS(encryptedData);
    
    if (!validateCID(cid)) {
      throw new Error('Invalid CID returned from Pinata');
    }
    
    entry.cid = cid;
    console.log('Backup uploaded, CID:', cid);

    // Anchor CID to X1 blockchain
    try {
      const { signature, explorerUrl } = await anchorCID(cid, walletPath);
      console.log('X1 Transaction:', signature);
      console.log('Explorer:', explorerUrl);
      entry.txHash = signature;
      entry.explorerUrl = explorerUrl;
    } catch (err) {
      console.error('X1 anchoring failed (backup still saved to IPFS):', err.message);
    }

    // Log backup
    const logPath = path.resolve(__dirname, '../..', 'vault-log.json');
    let log = [];
    if (fs.existsSync(logPath)) {
      log = JSON.parse(fs.readFileSync(logPath, 'utf8'));
    }
    log.push(entry);
    fs.writeFileSync(logPath, JSON.stringify(log, null, 2));
    console.log('Logged backup CID to vault-log.json');

  } finally {
    // Always clean up temp files
    cleanupFiles(tempFiles);
  }
}

createBackup().catch(err => {
  console.error('Backup failed:', err);
  process.exit(1);
});
