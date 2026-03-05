const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const tar = require('tar');
const https = require('https');

// Constants for encryption (must match backup.js)
const IV_SIZE = 12;
const AUTH_TAG_SIZE = 16;
const SALT_SIZE = 32;
const PBKDF2_ITERATIONS = 100000;
const KEY_SIZE = 32;

/**
 * Derive encryption key using PBKDF2 with salt
 * @param {Buffer} secretKey - Source secret key
 * @param {Buffer} salt - Random salt from encrypted data
 * @returns {Buffer} 32-byte derived key
 */
function deriveKey(secretKey, salt) {
  return crypto.pbkdf2Sync(secretKey, salt, PBKDF2_ITERATIONS, KEY_SIZE, 'sha256');
}

/**
 * Validate CID format to prevent SSRF
 * @param {string} cid - Content Identifier to validate
 * @returns {boolean} - True if valid
 */
function validateCID(cid) {
  if (!cid || typeof cid !== 'string') return false;
  if (cid.length < 32 || cid.length > 128) return false;
  const validPattern = /^[A-Za-z0-9]+$/;
  if (!validPattern.test(cid)) return false;
  if (cid.startsWith('Qm') && cid.length === 46) return true;
  if (cid.startsWith('baf') && cid.length >= 59) return true;
  return false;
}

/**
 * Clean up temporary file
 * @param {string} filePath - File to delete
 */
function cleanupFile(filePath) {
  try {
    if (fs.existsSync(filePath)) {
      const stat = fs.statSync(filePath);
      if (stat.isDirectory()) {
        fs.rmSync(filePath, { recursive: true });
      } else {
        fs.unlinkSync(filePath);
      }
    }
  } catch (err) {
    console.error('Failed to clean up', filePath, err.message);
  }
}

/**
 * Download file from Pinata gateway with retry logic
 * @param {string} cid - Content identifier
 * @param {string} destPath - Destination path
 * @param {number} retries - Number of retry attempts
 * @returns {Promise}
 */
function downloadFromPinata(cid, destPath, retries = 3) {
  return new Promise((resolve, reject) => {
    const attempt = (left) => {
      const url = `https://gateway.pinata.cloud/ipfs/${cid}`;
      const file = fs.createWriteStream(destPath);
      
      https.get(url, response => {
        if (response.statusCode === 429 && left > 0) {
          console.log(`Rate limited, retrying in ${1000 * (4 - left)}ms`);
          file.close();
          setTimeout(() => attempt(left - 1), 1000 * (4 - left));
          return;
        }
        
        if (response.statusCode !== 200) {
          file.close();
          cleanupFile(destPath);
          reject(new Error(`Failed to download CID ${cid}, status ${response.statusCode}`));
          return;
        }
        
        response.pipe(file);
        file.on('finish', () => {
          file.close(() => resolve());
        });
      }).on('error', err => {
        cleanupFile(destPath);
        if (left > 0) {
          console.log(`Download error, retrying ${left} more times`);
          setTimeout(() => attempt(left - 1), 1000);
        } else {
          reject(err);
        }
      });
    };
    
    attempt(retries);
  });
}

async function restoreBackup(cid, onlyPath = null) {
  if (!validateCID(cid)) {
    throw new Error(`Invalid CID format: ${cid}`);
  }

  const tempFiles = [];
  const encryptedPath = path.resolve(__dirname, 'downloaded.enc');
  tempFiles.push(encryptedPath);

  try {
    await downloadFromPinata(cid, encryptedPath);
    console.log('Downloaded from Pinata');

    // Load wallet secret key
    const walletPath = path.resolve(__dirname, '../..', 'x1_vault_cli', 'wallet.json');
    if (!fs.existsSync(walletPath)) {
      throw new Error(`Wallet not found at ${walletPath}`);
    }
    const wallet = JSON.parse(fs.readFileSync(walletPath, 'utf8'));
    const secretKey = Buffer.from(wallet.secretKey);
    
    // Read encrypted file
    const data = fs.readFileSync(encryptedPath);
    
    // Extract components: salt + iv + ciphertext + authTag
    if (data.length < SALT_SIZE + IV_SIZE + AUTH_TAG_SIZE + 1) {
      throw new Error('Encrypted file too small to be valid');
    }
    
    const salt = data.slice(0, SALT_SIZE);
    const iv = data.slice(SALT_SIZE, SALT_SIZE + IV_SIZE);
    const authTag = data.slice(data.length - AUTH_TAG_SIZE);
    const ciphertext = data.slice(SALT_SIZE + IV_SIZE, data.length - AUTH_TAG_SIZE);
    
    // Derive key using PBKDF2
    const key = deriveKey(secretKey, salt);
    
    // Decrypt
    const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv);
    decipher.setAuthTag(authTag);
    const decrypted = Buffer.concat([decipher.update(ciphertext), decipher.final()]);
    
    // Write decrypted payload
    const payloadPath = path.resolve(__dirname, 'payload.tar');
    tempFiles.push(payloadPath);
    fs.writeFileSync(payloadPath, decrypted);
    console.log('Decrypted payload extracted');

    // Extract payload
    const tempDir = path.resolve(__dirname, 'temp_restore');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }
    tempFiles.push(tempDir);
    
    await tar.x({ file: payloadPath, cwd: tempDir });
    console.log('Payload extracted');

    // Verify checksum
    const checksumPath = path.join(tempDir, 'checksum.txt');
    const archivePath = path.join(tempDir, 'backup.tar.gz');
    
    if (!fs.existsSync(checksumPath) || !fs.existsSync(archivePath)) {
      throw new Error('Payload missing checksum.txt or backup.tar.gz');
    }
    
    const expectedChecksum = fs.readFileSync(checksumPath, 'utf8').trim();
    const archiveBuffer = fs.readFileSync(archivePath);
    const actualChecksum = crypto.createHash('sha256').update(archiveBuffer).digest('hex');
    
    console.log('Expected checksum:', expectedChecksum);
    console.log('Actual checksum:', actualChecksum);
    
    if (expectedChecksum !== actualChecksum) {
      throw new Error(`Checksum mismatch! Expected ${expectedChecksum}, got ${actualChecksum}`);
    }
    
    console.log('✓ Checksum verified — archive integrity confirmed');

    // Extract archive to workspace
    const cwd = path.resolve(__dirname, '../..');
    
    if (onlyPath) {
      console.log(`Restoring only: ${onlyPath}`);
      const files = await tar.list({ file: archivePath });
      const matchingFiles = files.filter(f => f.startsWith(onlyPath));
      
      if (matchingFiles.length === 0) {
        throw new Error(`No files found matching: ${onlyPath}`);
      }
      
      console.log(`Found ${matchingFiles.length} matching files`);
      await tar.x({ file: archivePath, cwd, filter: (p) => p.startsWith(onlyPath) });
      console.log(`Restored ${onlyPath} to workspace`);
    } else {
      await tar.x({ file: archivePath, cwd });
      console.log('Backup restored to workspace');
    }
    
  } finally {
    // Always clean up temp files
    for (const file of tempFiles) {
      cleanupFile(file);
    }
  }
}

// Parse arguments
const cid = process.argv[2];
const onlyFlag = process.argv.indexOf('--only');
const onlyPath = onlyFlag !== -1 && process.argv[onlyFlag + 1] 
  ? process.argv[onlyFlag + 1] 
  : null;

if (!cid) {
  console.error('Usage: node restore.js <CID> [--only <path>]');
  console.error('Example: node restore.js QmAbC123 --only memory/');
  process.exit(1);
}

restoreBackup(cid, onlyPath).catch(err => {
  console.error('Restore failed:', err);
  process.exit(1);
});
