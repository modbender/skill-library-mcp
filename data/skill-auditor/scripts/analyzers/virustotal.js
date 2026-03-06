/**
 * VirusTotal Binary Scanner - Hash binaries and check VT API
 * Optional dependency: none (uses built-in crypto + fetch)
 */

const crypto = require('crypto');
const path = require('path');
const fs = require('fs');

// Check if node-fetch is available (Node.js < 18 compatibility)
let fetch;
try {
  fetch = require('node-fetch');
} catch (e) {
  // Use built-in fetch if available (Node.js 18+)
  if (typeof globalThis.fetch !== 'undefined') {
    fetch = globalThis.fetch;
  } else {
    fetch = null;
  }
}

// ─── VirusTotal API integration ────────────────────────────────────

class VirusTotalScanner {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://www.virustotal.com/api/v3';
    this.rateLimitDelay = 15000; // 15 seconds between requests (free tier: 4/min)
    this.lastRequest = 0;
  }

  async scanFile(filePath) {
    if (!this.apiKey) {
      throw new Error('VIRUSTOTAL_API_KEY environment variable not set');
    }

    if (!fetch) {
      throw new Error('Fetch not available — use Node.js 18+ or install node-fetch');
    }

    // Calculate file hash
    const hash = await this.calculateFileHash(filePath);
    
    // Rate limiting
    await this.enforceRateLimit();

    try {
      // Check if file is already known to VirusTotal
      const response = await fetch(`${this.baseUrl}/files/${hash}`, {
        headers: {
          'x-apikey': this.apiKey
        }
      });

      if (response.status === 404) {
        // File not known to VT
        return {
          hash: hash,
          known: false,
          status: 'unknown',
          engines: 0,
          positives: 0,
          permalink: null
        };
      }

      if (!response.ok) {
        throw new Error(`VirusTotal API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      const stats = data.data.attributes.last_analysis_stats;

      return {
        hash: hash,
        known: true,
        status: this.getDetectionStatus(stats),
        engines: stats.harmless + stats.malicious + stats.suspicious + stats.undetected,
        positives: stats.malicious + stats.suspicious,
        harmless: stats.harmless,
        malicious: stats.malicious,
        suspicious: stats.suspicious,
        undetected: stats.undetected,
        permalink: `https://www.virustotal.com/gui/file/${hash}`,
        scanDate: data.data.attributes.last_analysis_date,
        reputation: data.data.attributes.reputation
      };

    } catch (e) {
      throw new Error(`VirusTotal scan failed: ${e.message}`);
    }
  }

  async calculateFileHash(filePath) {
    return new Promise((resolve, reject) => {
      const hash = crypto.createHash('sha256');
      const stream = fs.createReadStream(filePath);
      
      stream.on('error', reject);
      stream.on('data', chunk => hash.update(chunk));
      stream.on('end', () => resolve(hash.digest('hex')));
    });
  }

  async enforceRateLimit() {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequest;
    if (timeSinceLastRequest < this.rateLimitDelay) {
      const delay = this.rateLimitDelay - timeSinceLastRequest;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
    this.lastRequest = Date.now();
  }

  getDetectionStatus(stats) {
    if (stats.malicious > 0) return 'malicious';
    if (stats.suspicious > 0) return 'suspicious';
    if (stats.harmless > 0 && stats.undetected === 0) return 'clean';
    return 'unknown';
  }
}

// ─── Binary file detection ─────────────────────────────────────────

const SCANNABLE_BINARY_EXTENSIONS = new Set([
  '.exe', '.dll', '.com', '.scr', '.pif', '.bat', '.cmd',
  '.msi', '.pkg', '.deb', '.rpm', '.dmg', '.app',
  '.bin', '.so', '.dylib', '.wasm',
  '.jar', '.class', '.apk', '.ipa'
]);

function isBinaryExecutable(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return SCANNABLE_BINARY_EXTENSIONS.has(ext);
}

// ─── Main scanner function ─────────────────────────────────────────

async function scanFile(filePath, skillDir, options = {}) {
  const findings = [];
  const relativePath = path.relative(skillDir, filePath);

  // Only scan executable binaries
  if (!isBinaryExecutable(filePath)) {
    return findings;
  }

  // Check if VirusTotal is enabled and API key is available
  const apiKey = process.env.VIRUSTOTAL_API_KEY;
  if (!options.useVirusTotal || !apiKey) {
    findings.push({
      id: 'vt-not-configured',
      category: 'Binary File',
      severity: 'info',
      file: relativePath,
      line: 0,
      snippet: `[Executable binary: ${path.basename(filePath)}]`,
      explanation: 'Executable binary detected but VirusTotal scanning not enabled. Use --use-virustotal flag and set VIRUSTOTAL_API_KEY',
      analyzer: 'virustotal'
    });
    return findings;
  }

  try {
    const scanner = new VirusTotalScanner(apiKey);
    const result = await scanner.scanFile(filePath);

    if (!result.known) {
      findings.push({
        id: 'vt-unknown-binary',
        category: 'Binary File',
        severity: 'medium',
        file: relativePath,
        line: 0,
        snippet: `[Unknown binary: ${path.basename(filePath)}]`,
        explanation: `Binary file not known to VirusTotal (SHA256: ${result.hash}) — could be custom/private malware`,
        analyzer: 'virustotal',
        virustotal: result
      });
    } else {
      // Known file - create finding based on detection status
      let severity, explanation;
      
      switch (result.status) {
        case 'malicious':
          severity = 'critical';
          explanation = `MALWARE DETECTED — ${result.malicious}/${result.engines} security engines flagged this binary as malicious`;
          break;
        
        case 'suspicious':
          severity = 'high';
          explanation = `Suspicious binary — ${result.suspicious}/${result.engines} security engines flagged this as potentially harmful`;
          break;
        
        case 'clean':
          severity = 'low';
          explanation = `Binary verified clean by ${result.harmless}/${result.engines} security engines`;
          break;
        
        default:
          severity = 'medium';
          explanation = `Mixed results from VirusTotal scan — ${result.positives}/${result.engines} positive detections`;
      }

      findings.push({
        id: 'vt-scan-result',
        category: result.status === 'malicious' ? 'Malware' : 'Binary File',
        severity: severity,
        file: relativePath,
        line: 0,
        snippet: `[Scanned binary: ${path.basename(filePath)}]`,
        explanation: explanation + ` — View report: ${result.permalink}`,
        analyzer: 'virustotal',
        virustotal: result
      });
    }

  } catch (e) {
    findings.push({
      id: 'vt-scan-error',
      category: 'Error',
      severity: 'medium',
      file: relativePath,
      line: 0,
      snippet: `[Binary scan failed: ${path.basename(filePath)}]`,
      explanation: `VirusTotal scan failed: ${e.message}`,
      analyzer: 'virustotal'
    });
  }

  return findings;
}

// ─── Capability detection ──────────────────────────────────────────

function checkCapability() {
  const hasApiKey = !!process.env.VIRUSTOTAL_API_KEY;
  const hasFetch = !!fetch;
  
  return {
    available: hasApiKey && hasFetch,
    dependencies: fetch ? [] : ['node-fetch (for Node.js < 18)'],
    requirements: [
      'VIRUSTOTAL_API_KEY environment variable',
      'Internet connection'
    ],
    installCommand: hasFetch ? 'Set VIRUSTOTAL_API_KEY env var' : 'npm install node-fetch',
    description: 'Binary malware scanning using VirusTotal API',
    status: {
      apiKey: hasApiKey ? 'configured' : 'missing',
      fetch: hasFetch ? 'available' : 'missing'
    }
  };
}

module.exports = {
  scanFile,
  checkCapability,
  VirusTotalScanner,
  isBinaryExecutable
};