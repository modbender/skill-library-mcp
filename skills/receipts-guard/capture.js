#!/usr/bin/env node
/**
 * RECEIPTS Guard v0.6.0 - Self-Sovereign Agent Identity
 *
 * "Who controls the evidence becomes who controls the dispute."
 *
 * Agent commerce infrastructure optimized for winning arbitration.
 * Everything exists to produce evidence that wins disputes.
 *
 * Commands:
 *   capture "TERMS_TEXT" "SOURCE_URL" "MERCHANT_NAME" [--consent-type=TYPE]
 *   promise "COMMITMENT_TEXT" "COUNTERPARTY" [--direction=inbound|outbound]
 *
 *   === IDENTITY (v0.6.0) ===
 *   identity init --namespace=X --name=Y [--controller-twitter=@handle]
 *   identity show [--full]
 *   identity rotate [--reason=scheduled|compromise|device_change]
 *   identity verify --did=DID | --signature=SIG --termsHash=HASH
 *   identity set-controller --twitter=@handle
 *   identity verify-controller --url=URL
 *   identity recover --controller-proof=URL [--confirm]
 *   identity publish [--platform=moltbook|ipfs|local]
 *   migrate --to-did
 *
 *   === ARBITRATION PROTOCOL (v0.5.0) ===
 *   propose "TERMS" "COUNTERPARTY" --arbiter="AGENT" [--deadline=ISO_DATE] [--value=AMOUNT]
 *   accept --proposalId=ID
 *   reject --proposalId=ID --reason="REASON"
 *   fulfill --agreementId=ID --evidence="PROOF"
 *   arbitrate --agreementId=ID --reason="BREACH_TYPE" --evidence="PROOF"
 *   submit --arbitrationId=ID --evidence="PROOF" [--type=document|screenshot|witness]
 *   ruling --arbitrationId=ID --decision=claimant|respondent|split --reasoning="EXPLANATION"
 *   timeline --agreementId=ID
 *
 *   === UTILITIES ===
 *   query --merchant="X" --risk-level=high --after="2026-01-01"
 *   list [--type=captures|proposals|agreements|arbitrations]
 *   export --format=json|csv|pdf
 *   diff --capture1=ID --capture2=ID
 *   dispute --captureId=ID
 *   witness --captureId=ID [--anchor=moltbook|bitcoin|both]
 *   rules --list | --add="PATTERN" --flag="FLAG_NAME"
 *
 * v0.5.0 Features:
 * v0.6.0 Features:
 *   - Self-Sovereign Identity: DID-based agent identity with Ed25519 signatures
 *   - Key Rotation: Old key signs new key, creating unbroken proof chain
 *   - Human Controller: Twitter-based recovery backstop
 *   - Backward Compatible: Legacy HMAC signatures still supported
 *
 * v0.5.0 Features:
 *   - Full Arbitration Protocol: propose → accept → fulfill/arbitrate → ruling
 *   - PAO (Programmable Agreement Object): termsHash, mutual signatures, state machine
 *   - LPR (Legal Provenance Review): Timeline visualization for arbiters
 *   - Arbiter selection at agreement creation
 *   - Evidence submission and ruling workflow
 *
 * Environment variables (optional):
 *   RECEIPTS_AGENT_ID - Unique agent identifier
 *   RECEIPTS_MOLTBOOK_KEY - API key for Moltbook witnessing
 *   RECEIPTS_CUSTOM_RULES - Path to custom rules file
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const { ethers } = require('ethers');

// Receipts directory
const RECEIPTS_DIR = path.join(
  process.env.HOME || process.env.USERPROFILE,
  '.openclaw',
  'receipts'
);

// Index file for fast queries
const INDEX_FILE = path.join(RECEIPTS_DIR, 'index.json');

// Version
const VERSION = '0.7.1';

// Arbitration directories
const PROPOSALS_DIR = path.join(RECEIPTS_DIR, 'proposals');
const AGREEMENTS_DIR = path.join(RECEIPTS_DIR, 'agreements');
const ARBITRATIONS_DIR = path.join(RECEIPTS_DIR, 'arbitrations');
const RULINGS_DIR = path.join(RECEIPTS_DIR, 'rulings');

// Identity directories (v0.6.0)
const IDENTITY_DIR = path.join(RECEIPTS_DIR, 'identity');
const PRIVATE_KEY_DIR = path.join(IDENTITY_DIR, 'private');
const KEY_ARCHIVE_DIR = path.join(PRIVATE_KEY_DIR, 'key-archive');
const DID_FILE = path.join(IDENTITY_DIR, 'did.json');
const KEY_HISTORY_FILE = path.join(IDENTITY_DIR, 'key-history.json');
const CONTROLLER_FILE = path.join(IDENTITY_DIR, 'controller.json');
const RECOVERY_DIR = path.join(IDENTITY_DIR, 'recovery');

// DID Method
const DID_METHOD = 'agent';

// Base58btc alphabet (Bitcoin) for multibase encoding
const BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';

// Valid arbitration reasons
const VALID_ARBITRATION_REASONS = [
  'non_delivery',
  'partial_delivery',
  'quality',
  'deadline_breach',
  'repudiation',
  'other',
];

// Custom rules file
const CUSTOM_RULES_FILE = process.env.RECEIPTS_CUSTOM_RULES ||
  path.join(RECEIPTS_DIR, 'custom-rules.json');

// Witness anchors directory
const WITNESS_DIR = path.join(RECEIPTS_DIR, 'witnesses');

// === ERC-8004 CHAIN CONFIGURATION (v0.7.0) ===
const CHAIN_CONFIG = {
  ethereum: {
    chainId: 1,
    name: 'Ethereum Mainnet',
    rpc: process.env.ETHEREUM_RPC || 'https://eth.llamarpc.com',
    identityRegistry: '0x8004A169FB4a3325136EB29fA0ceB6D2e539a432',
    reputationRegistry: '0x8004BAa17C55a88189AE136b182e5fdA19dE9b63',
    explorer: 'https://etherscan.io'
  },
  base: {
    chainId: 8453,
    name: 'Base',
    rpc: process.env.BASE_RPC || 'https://mainnet.base.org',
    identityRegistry: null, // TBD - deploy or wait for official
    reputationRegistry: null,
    explorer: 'https://basescan.org'
  },
  sepolia: {
    chainId: 11155111,
    name: 'Sepolia Testnet',
    rpc: process.env.SEPOLIA_RPC || 'https://rpc.sepolia.org',
    identityRegistry: '0x8004A818BFB912233c491871b3d84c89A494BD9e',
    reputationRegistry: '0x8004B663056A597Dffe9eCcC1965A193B7388713',
    explorer: 'https://sepolia.etherscan.io'
  }
};

// ERC-8004 Identity Registry ABI (minimal for registration)
const IDENTITY_REGISTRY_ABI = [
  'function register(string agentURI) external returns (uint256)',
  'function register(string agentURI, tuple(string key, bytes value)[] metadata) external returns (uint256)',
  'function setAgentURI(uint256 agentId, string newURI) external',
  'function getMetadata(uint256 agentId, string metadataKey) external view returns (bytes)',
  'function setMetadata(uint256 agentId, string metadataKey, bytes metadataValue) external',
  'function ownerOf(uint256 tokenId) external view returns (address)',
  'function tokenURI(uint256 tokenId) external view returns (string)',
  'event Transfer(address indexed from, address indexed to, uint256 indexed tokenId)'
];

// ERC-8004 Reputation Registry ABI (minimal for feedback)
const REPUTATION_REGISTRY_ABI = [
  'function giveFeedback(uint256 agentId, int128 value, uint8 valueDecimals, string tag1, string tag2, string endpoint, string feedbackURI, bytes32 feedbackHash) external',
  'function getSummary(uint256 agentId, address[] clientAddresses, string tag1, string tag2) external view returns (uint64 count, int128 summaryValue, uint8 decimals)',
  'function readFeedback(uint256 agentId, address clientAddress, uint64 feedbackIndex) external view returns (int128 value, uint8 valueDecimals, string tag1, string tag2, bool isRevoked)',
  'event FeedbackGiven(uint256 indexed agentId, address indexed clientAddress, uint64 feedbackIndex, int128 value)'
];

// Hook registry for framework integrations
const hooks = {
  beforeConsent: [],
  afterCapture: [],
  onRiskDetected: [],
};

// Get command and arguments
const args = process.argv.slice(2);
const command = args[0];

// Route to appropriate handler
switch (command) {
  case 'capture':
    handleCapture(args.slice(1));
    break;
  case 'promise':
    handlePromise(args.slice(1));
    break;
  case 'query':
    handleQuery(args.slice(1));
    break;
  case 'list':
    handleList(args.slice(1));
    break;
  case 'export':
    handleExport(args.slice(1));
    break;
  case 'diff':
    handleDiff(args.slice(1));
    break;
  case 'dispute':
    handleDispute(args.slice(1));
    break;
  case 'witness':
    handleWitness(args.slice(1));
    break;
  case 'rules':
    handleRules(args.slice(1));
    break;
  // === ARBITRATION PROTOCOL v0.5.0 ===
  case 'propose':
    handlePropose(args.slice(1));
    break;
  case 'accept':
    handleAccept(args.slice(1));
    break;
  case 'reject':
    handleReject(args.slice(1));
    break;
  case 'fulfill':
    handleFulfill(args.slice(1));
    break;
  case 'arbitrate':
    handleArbitrate(args.slice(1));
    break;
  case 'submit':
    handleSubmit(args.slice(1));
    break;
  case 'ruling':
    handleRuling(args.slice(1));
    break;
  case 'timeline':
    handleTimeline(args.slice(1));
    break;
  // === IDENTITY v0.6.0 ===
  case 'identity':
    handleIdentity(args.slice(1));
    break;
  case 'migrate':
    handleMigrate(args.slice(1));
    break;
  // === HTTP SERVER MODE (v0.7.0) ===
  case 'serve':
    startHttpServer(args.slice(1));
    break;
  default:
    // Legacy mode: if first arg looks like document text, treat as capture
    if (command && command.length > 20) {
      handleCapture(args);
    } else {
      showHelp();
    }
}

// === CAPTURE COMMAND (Enhanced with Consent Proofs) ===
function handleCapture(args) {
  const filters = parseFilters(args);

  // Extract positional args (text, url, merchant) and flags
  const positionalArgs = args.filter(a => !a.startsWith('--'));
  const [documentText, sourceUrl, merchantName] = positionalArgs;

  if (!documentText) {
    console.error(JSON.stringify({
      error: 'Missing required argument: documentText',
      usage: 'node capture.js capture "TERMS_TEXT" "SOURCE_URL" "MERCHANT_NAME" [--consent-type=explicit|implicit|continued_use]'
    }));
    process.exit(1);
  }

  const agentId = process.env.RECEIPTS_AGENT_ID || 'openclaw-agent';

  // Create document hash
  const documentHash = crypto
    .createHash('sha256')
    .update(documentText)
    .digest('hex');

  // Check for duplicates
  const duplicate = checkDuplicate(documentHash);
  if (duplicate) {
    console.log(JSON.stringify({
      ...duplicate,
      note: `Duplicate of existing capture from ${duplicate.timestamp}`,
      isDuplicate: true
    }, null, 2));
    return;
  }

  // Check for changes from same URL
  const changeInfo = detectChanges(sourceUrl, documentHash);

  // Analyze locally
  const riskFlags = detectRiskFlags(documentText);
  const consentFlags = detectConsentType(documentText);
  const allFlags = [...riskFlags, ...consentFlags];

  const trustScore = Math.max(0, 100 - (allFlags.length * 15));
  const recommendation = getRecommendation(allFlags, consentFlags);

  // Build consent proof
  const consentProof = {
    type: filters['consent-type'] || detectImplicitConsentType(documentText),
    capturedAt: new Date().toISOString(),
    elementSelector: filters['element'] || null,
    screenshotHash: filters['screenshot'] ?
      crypto.createHash('sha256').update(filters['screenshot']).digest('hex') : null,
    agentAction: filters['action'] || 'document_capture',
  };

  // Create capture record
  const capture = {
    captureId: `local_${documentHash.slice(0, 16)}`,
    recommendation,
    trustScore,
    riskFlags: allFlags,
    summary: generateSummary(allFlags, trustScore, consentProof.type),
    documentHash,
    sourceUrl: sourceUrl || 'unknown',
    merchantName: merchantName || 'Unknown Merchant',
    agentId,
    timestamp: new Date().toISOString(),
    documentLength: documentText.length,
    version: VERSION,

    // NEW: Consent Proof
    consentProof,

    // Legal disclaimer
    disclaimer: 'RECEIPTS flags known problematic patterns only. Not a substitute for legal review.',
  };

  // Add change detection info if applicable
  if (changeInfo) {
    capture.changeDetected = true;
    capture.previousCapture = changeInfo.previousCaptureId;
    capture.changeNote = `Terms changed since ${changeInfo.previousTimestamp}`;
    capture.diffAvailable = true;
  }

  // Output result
  console.log(JSON.stringify(capture, null, 2));

  // Save locally
  saveLocalReceipt(capture, documentText);

  // Save screenshot if provided
  if (filters['screenshot']) {
    saveScreenshot(capture.captureId, filters['screenshot']);
  }

  updateIndex(capture);
}

// === DIFF COMMAND (New in v0.3.0) ===
function handleDiff(args) {
  const filters = parseFilters(args);
  const capture1Id = filters['capture1'];
  const capture2Id = filters['capture2'];

  if (!capture1Id || !capture2Id) {
    // If only one ID provided, diff against previous from same URL
    if (capture1Id) {
      const index = loadIndex();
      const capture1 = index.find(r => r.captureId === capture1Id);
      if (capture1 && capture1.previousCapture) {
        return diffCaptures(capture1.previousCapture, capture1Id);
      }
    }
    console.error(JSON.stringify({
      error: 'Missing capture IDs',
      usage: 'node capture.js diff --capture1=ID --capture2=ID'
    }));
    process.exit(1);
  }

  diffCaptures(capture1Id, capture2Id);
}

function diffCaptures(id1, id2) {
  const text1Path = path.join(RECEIPTS_DIR, `${id1}.txt`);
  const text2Path = path.join(RECEIPTS_DIR, `${id2}.txt`);

  try {
    const text1 = fs.readFileSync(text1Path, 'utf8');
    const text2 = fs.readFileSync(text2Path, 'utf8');

    const diff = generateDiff(text1, text2);
    const index = loadIndex();
    const meta1 = index.find(r => r.captureId === id1);
    const meta2 = index.find(r => r.captureId === id2);

    console.log(JSON.stringify({
      comparison: {
        older: { captureId: id1, timestamp: meta1?.timestamp, merchantName: meta1?.merchantName },
        newer: { captureId: id2, timestamp: meta2?.timestamp, merchantName: meta2?.merchantName }
      },
      summary: {
        totalChanges: diff.additions.length + diff.deletions.length,
        additions: diff.additions.length,
        deletions: diff.deletions.length,
        significantChanges: diff.significant
      },
      changes: diff,
      warning: diff.significant.length > 0 ?
        'SIGNIFICANT CHANGES DETECTED - Review carefully before accepting' : null
    }, null, 2));

  } catch (e) {
    console.error(JSON.stringify({
      error: 'Could not read capture files',
      details: e.message
    }));
  }
}

function generateDiff(text1, text2) {
  const lines1 = text1.split('\n');
  const lines2 = text2.split('\n');

  const additions = [];
  const deletions = [];
  const significant = [];

  // Simple line-by-line diff
  const set1 = new Set(lines1.map(l => l.trim()).filter(l => l.length > 0));
  const set2 = new Set(lines2.map(l => l.trim()).filter(l => l.length > 0));

  // Find deletions (in text1 but not in text2)
  for (const line of set1) {
    if (!set2.has(line) && line.length > 10) {
      deletions.push(line.substring(0, 200));
      // Check if deletion is significant
      if (isSignificantClause(line)) {
        significant.push({ type: 'removed', text: line.substring(0, 200) });
      }
    }
  }

  // Find additions (in text2 but not in text1)
  for (const line of set2) {
    if (!set1.has(line) && line.length > 10) {
      additions.push(line.substring(0, 200));
      // Check if addition is significant
      if (isSignificantClause(line)) {
        significant.push({ type: 'added', text: line.substring(0, 200) });
      }
    }
  }

  return { additions, deletions, significant };
}

function isSignificantClause(text) {
  const significantPatterns = [
    /arbitration/i,
    /class action/i,
    /waive/i,
    /refund/i,
    /liability/i,
    /indemnif/i,
    /terminat/i,
    /jurisdiction/i,
    /governing law/i,
    /binding/i,
    /irrevocable/i,
    /perpetual/i,
  ];
  return significantPatterns.some(p => p.test(text));
}

// === DISPUTE COMMAND (New in v0.3.0) ===
function handleDispute(args) {
  const filters = parseFilters(args);
  const captureId = filters['captureId'] || filters['id'];

  if (!captureId) {
    console.error(JSON.stringify({
      error: 'Missing captureId',
      usage: 'node capture.js dispute --captureId=local_xxx'
    }));
    process.exit(1);
  }

  const index = loadIndex();
  const capture = index.find(r => r.captureId === captureId);

  if (!capture) {
    console.error(JSON.stringify({ error: 'Capture not found' }));
    process.exit(1);
  }

  // Load full document text
  const textPath = path.join(RECEIPTS_DIR, `${captureId}.txt`);
  let documentText = '';
  try {
    documentText = fs.readFileSync(textPath, 'utf8');
  } catch (e) {}

  // Generate dispute package
  const disputePackage = {
    title: `Dispute Evidence Package - ${capture.merchantName}`,
    generatedAt: new Date().toISOString(),

    summary: {
      merchant: capture.merchantName,
      agreementDate: capture.timestamp,
      sourceUrl: capture.sourceUrl,
      documentHash: capture.documentHash,
      trustScore: capture.trustScore,
      recommendation: capture.recommendation,
    },

    consentEvidence: {
      type: capture.consentProof?.type || 'unknown',
      capturedAt: capture.consentProof?.capturedAt || capture.timestamp,
      agentAction: capture.consentProof?.agentAction || 'document_capture',
      hasScreenshot: !!capture.consentProof?.screenshotHash,
      screenshotHash: capture.consentProof?.screenshotHash,
    },

    riskAnalysis: {
      flagsDetected: capture.riskFlags,
      flagCount: capture.riskFlags?.length || 0,
      concerns: capture.riskFlags?.map(flag => ({
        flag,
        implication: getRiskImplication(flag)
      }))
    },

    changeHistory: capture.changeDetected ? {
      termsChanged: true,
      previousCapture: capture.previousCapture,
      changeNote: capture.changeNote,
      recommendation: 'Request diff report for detailed comparison'
    } : {
      termsChanged: false,
      note: 'No prior captures from this URL to compare'
    },

    documentPreview: documentText.substring(0, 1000) + (documentText.length > 1000 ? '...' : ''),

    legalNote: `This evidence package was generated by RECEIPTS Guard v${VERSION}. ` +
      'It captures what terms existed at the time of agreement and how consent was recorded. ' +
      'This is NOT legal advice. Consult with a qualified attorney for dispute resolution.',

    exportPaths: {
      fullDocument: textPath,
      metadata: path.join(RECEIPTS_DIR, `${captureId}.json`),
      screenshot: capture.consentProof?.screenshotHash ?
        path.join(RECEIPTS_DIR, `${captureId}.screenshot`) : null
    }
  };

  console.log(JSON.stringify(disputePackage, null, 2));
}

function getRiskImplication(flag) {
  const implications = {
    'Binding arbitration clause': 'You may be required to resolve disputes through arbitration instead of court',
    'Class action waiver': 'You may not be able to join class action lawsuits against this merchant',
    'Rights waiver detected': 'You may be waiving certain legal rights',
    'No refund policy': 'Purchases may be final with no refund available',
    'Non-refundable terms': 'Payments are non-refundable under these terms',
    'Auto-renewal clause': 'Service may automatically renew and charge your payment method',
    'Perpetual license grant': 'You may be granting perpetual rights over your content',
    'Irrevocable terms': 'Certain commitments may not be reversible',
    'Data selling clause': 'Your data may be sold to third parties',
    'Third-party data sharing': 'Your data may be shared with third parties',
    'Limited liability clause': 'The merchant limits their liability for damages',
    'Indemnification clause': 'You may be required to cover the merchant\'s legal costs',
    'Hold harmless clause': 'You agree not to hold the merchant responsible for certain issues',
    'US jurisdiction clause': 'Disputes governed by Delaware/California law',
    'Exclusive jurisdiction clause': 'Disputes must be resolved in a specific jurisdiction',
    'Termination without notice': 'Service can be terminated without prior notice',
    'Unilateral modification rights': 'Terms can be changed at any time without your consent',
    'Implicit consent pattern': 'Continued use may constitute agreement to updated terms',
    'Continued use consent': 'Using the service after notice = accepting new terms',
  };
  return implications[flag] || 'Review this clause carefully';
}

// === QUERY COMMAND ===
function handleQuery(args) {
  const filters = parseFilters(args);
  const index = loadIndex();

  let results = index;

  // Apply filters
  if (filters.merchant) {
    const searchTerm = filters.merchant.toLowerCase();
    results = results.filter(r =>
      r.merchantName.toLowerCase().includes(searchTerm)
    );
  }

  if (filters['risk-level']) {
    const level = filters['risk-level'];
    if (level === 'high') {
      results = results.filter(r => r.recommendation === 'block');
    } else if (level === 'medium') {
      results = results.filter(r => r.recommendation === 'require_approval');
    } else if (level === 'low') {
      results = results.filter(r => r.recommendation === 'proceed');
    }
  }

  if (filters['consent-type']) {
    results = results.filter(r =>
      r.consentProof?.type === filters['consent-type']
    );
  }

  if (filters.after) {
    const afterDate = new Date(filters.after);
    results = results.filter(r => new Date(r.timestamp) >= afterDate);
  }

  if (filters.before) {
    const beforeDate = new Date(filters.before);
    results = results.filter(r => new Date(r.timestamp) <= beforeDate);
  }

  console.log(JSON.stringify({
    count: results.length,
    results: results
  }, null, 2));
}

// === LIST COMMAND ===
function handleList(args) {
  const filters = parseFilters(args || []);
  const listType = filters.type || 'all';

  const result = {
    generatedAt: new Date().toISOString(),
  };

  // List captures
  if (listType === 'all' || listType === 'captures') {
    const index = loadIndex();
    result.captures = {
      count: index.length,
      items: index.map(r => ({
        id: r.captureId || r.promiseId,
        type: r.type || 'capture',
        merchantName: r.merchantName || r.counterparty,
        trustScore: r.trustScore,
        recommendation: r.recommendation || r.riskLevel,
        timestamp: r.timestamp,
      }))
    };
  }

  // List proposals
  if (listType === 'all' || listType === 'proposals') {
    const proposals = listDirectory(PROPOSALS_DIR);
    result.proposals = {
      count: proposals.length,
      items: proposals.map(p => ({
        proposalId: p.proposalId,
        counterparty: p.counterparty,
        arbiter: p.proposedArbiter,
        status: p.status,
        createdAt: p.createdAt,
        expiresAt: p.expiresAt,
      }))
    };
  }

  // List agreements
  if (listType === 'all' || listType === 'agreements') {
    const agreements = listDirectory(AGREEMENTS_DIR);
    result.agreements = {
      count: agreements.length,
      items: agreements.map(a => ({
        agreementId: a.agreementId,
        parties: a.parties,
        arbiter: a.arbiter,
        status: a.status,
        deadline: a.deadline,
        createdAt: a.createdAt,
      }))
    };
  }

  // List arbitrations
  if (listType === 'all' || listType === 'arbitrations') {
    const arbitrations = listDirectory(ARBITRATIONS_DIR);
    result.arbitrations = {
      count: arbitrations.length,
      items: arbitrations.map(a => ({
        arbitrationId: a.arbitrationId,
        agreementId: a.agreementId,
        claimant: a.claimant,
        respondent: a.respondent,
        reason: a.reason,
        status: a.status,
        openedAt: a.openedAt,
      }))
    };
  }

  // List rulings
  if (listType === 'all' || listType === 'rulings') {
    const rulings = listDirectory(RULINGS_DIR);
    result.rulings = {
      count: rulings.length,
      items: rulings.map(r => ({
        rulingId: r.rulingId,
        arbitrationId: r.arbitrationId,
        decision: r.decision,
        arbiter: r.arbiter,
        issuedAt: r.issuedAt,
      }))
    };
  }

  console.log(JSON.stringify(result, null, 2));
}

function listDirectory(dirPath) {
  try {
    if (!fs.existsSync(dirPath)) return [];
    const files = fs.readdirSync(dirPath);
    return files
      .filter(f => f.endsWith('.json'))
      .map(f => {
        try {
          return JSON.parse(fs.readFileSync(path.join(dirPath, f), 'utf8'));
        } catch (e) {
          return null;
        }
      })
      .filter(Boolean);
  } catch (e) {
    return [];
  }
}

// === EXPORT COMMAND ===
function handleExport(args) {
  const filters = parseFilters(args);
  const format = filters.format || 'json';
  const captureId = filters.captureId || filters.id;
  const index = loadIndex();

  if (format === 'csv') {
    // CSV header
    console.log('captureId,merchantName,sourceUrl,trustScore,recommendation,consentType,riskFlags,timestamp,changeDetected');
    // CSV rows
    index.forEach(r => {
      const flags = (r.riskFlags || []).join('; ');
      const consentType = r.consentProof?.type || 'unknown';
      console.log(`"${r.captureId || r.promiseId}","${r.merchantName || r.counterparty}","${r.sourceUrl || 'N/A'}",${r.trustScore || 'N/A'},"${r.recommendation || r.riskLevel}","${consentType}","${flags}","${r.timestamp}",${r.changeDetected || false}`);
    });
  } else if (format === 'pdf') {
    // PDF-ready evidence export (for single capture)
    if (!captureId) {
      console.error(JSON.stringify({
        error: 'PDF export requires --captureId',
        usage: 'node capture.js export --format=pdf --captureId=local_xxx'
      }));
      process.exit(1);
    }

    const capture = index.find(r => (r.captureId || r.promiseId) === captureId);
    if (!capture) {
      console.error(JSON.stringify({ error: 'Capture not found' }));
      process.exit(1);
    }

    // Load document text
    const textFile = path.join(RECEIPTS_DIR, `${captureId}.txt`);
    let documentText = '';
    try { documentText = fs.readFileSync(textFile, 'utf8'); } catch (e) {}

    // Generate PDF-ready content
    const pdfContent = generatePDFContent(capture, documentText);
    console.log(JSON.stringify(pdfContent, null, 2));

  } else {
    // Full JSON export with document text
    const fullExport = index.map(r => {
      const id = r.captureId || r.promiseId;
      const textFile = path.join(RECEIPTS_DIR, `${id}.txt`);
      let documentText = '';
      try {
        documentText = fs.readFileSync(textFile, 'utf8');
      } catch (e) {}
      return { ...r, documentText };
    });
    console.log(JSON.stringify(fullExport, null, 2));
  }
}

// === HELPER FUNCTIONS ===

function showHelp() {
  console.log(`
RECEIPTS Guard v${VERSION} - Self-Sovereign Agent Identity

"Identity isn't metaphysical. It's functional."

═══════════════════════════════════════════════════════════════════════════════
IDENTITY (v0.6.0)
═══════════════════════════════════════════════════════════════════════════════

  identity init                       Create identity with Ed25519 keypair
    --namespace=NAMESPACE             Your namespace (e.g., remaster_io)
    --name=NAME                       Agent name
    --controller-twitter=@HANDLE      Human controller for recovery

  identity show [--full]              Display identity summary or full DID

  identity rotate                     Rotate keys (old signs new)
    --reason=REASON                   scheduled|compromise|device_change

  identity verify                     Verify DID or signature
    --did=DID                         Verify DID key chain
    --signature=SIG --termsHash=HASH  Verify signature

  identity set-controller             Set human controller
    --twitter=@HANDLE

  identity recover                    Recover using human controller
    --controller-proof=URL --confirm

  identity publish                    Publish DID document
    --platform=moltbook|ipfs|local

  migrate --to-did                    Migrate existing agreements to DID

═══════════════════════════════════════════════════════════════════════════════
ARBITRATION PROTOCOL (v0.5.0)
═══════════════════════════════════════════════════════════════════════════════

  propose "TERMS" "COUNTERPARTY"    Create an agreement proposal
    --arbiter="ARBITER_AGENT"       Required: mutually agreed arbiter
    --deadline=ISO_DATE             Fulfillment deadline
    --value=AMOUNT                  Agreement value (for reference)

  accept --proposalId=ID            Accept a proposal (creates agreement)

  reject --proposalId=ID            Reject a proposal
    --reason="REASON"               Rejection reason

  fulfill --agreementId=ID          Claim fulfillment of agreement
    --evidence="PROOF"              Required: proof of completion

  arbitrate --agreementId=ID        Open a dispute
    --reason=BREACH_TYPE            non_delivery|partial_delivery|quality|
                                    deadline_breach|repudiation|other
    --evidence="PROOF"              Initial evidence

  submit --arbitrationId=ID         Submit evidence to arbitration
    --evidence="PROOF"              Evidence content
    --type=TYPE                     document|screenshot|witness

  ruling --arbitrationId=ID         Issue ruling (arbiter only)
    --decision=DECISION             claimant|respondent|split
    --reasoning="EXPLANATION"       Required: reasoning for ruling

  timeline --agreementId=ID         Generate LPR (Legal Provenance Review)

═══════════════════════════════════════════════════════════════════════════════
CAPTURE COMMANDS
═══════════════════════════════════════════════════════════════════════════════

  capture "TEXT" "URL" "MERCHANT"   Capture a ToS/agreement
    --consent-type=TYPE             explicit|implicit|continued_use
    --screenshot=BASE64             Screenshot at time of consent

  promise "TEXT" "COUNTERPARTY"     Capture agent-to-agent commitment
    --direction=outbound|inbound    Who made the promise (default: outbound)

═══════════════════════════════════════════════════════════════════════════════
UTILITY COMMANDS
═══════════════════════════════════════════════════════════════════════════════

  list [--type=TYPE]                List records
                                    captures|proposals|agreements|
                                    arbitrations|rulings|all

  query [filters]                   Search captured receipts
    --merchant="Company Name"
    --risk-level=high|medium|low

  diff --capture1=ID --capture2=ID  Compare two captures

  dispute --captureId=ID            Generate dispute evidence package

  witness --captureId=ID            Create decentralized witness
    --anchor=moltbook|bitcoin|both

  rules --list                      Show all risk detection rules
  rules --add="PATTERN" --flag="X"  Add custom rule

  export --format=json|csv|pdf      Export records

═══════════════════════════════════════════════════════════════════════════════
ARBITRATION FLOW
═══════════════════════════════════════════════════════════════════════════════

  1. PROPOSE  →  Agent A creates proposal with terms + arbiter
  2. ACCEPT   →  Agent B signs, creating active agreement
  3. FULFILL  →  Either party claims completion with evidence
  4. DISPUTE  →  If contested, arbitrate command opens dispute
  5. SUBMIT   →  Both parties submit evidence during window
  6. RULING   →  Arbiter issues decision with reasoning

  State Machine: proposed → active → fulfilled/disputed → closed

═══════════════════════════════════════════════════════════════════════════════
EXAMPLES
═══════════════════════════════════════════════════════════════════════════════

  # Create proposal
  node capture.js propose "I will deliver API docs by Friday" "AgentX" \\
    --arbiter="arbiter-prime" --deadline="2026-02-14"

  # Accept proposal
  node capture.js accept --proposalId=prop_abc123

  # Claim fulfillment
  node capture.js fulfill --agreementId=agr_xyz789 \\
    --evidence="Docs delivered: https://..."

  # Open dispute
  node capture.js arbitrate --agreementId=agr_xyz789 \\
    --reason="non_delivery" --evidence="No docs received"

  # Issue ruling (as arbiter)
  node capture.js ruling --arbitrationId=arb_def456 \\
    --decision=claimant --reasoning="Evidence shows non-delivery"

  # View timeline
  node capture.js timeline --agreementId=agr_xyz789

═══════════════════════════════════════════════════════════════════════════════
ENVIRONMENT
═══════════════════════════════════════════════════════════════════════════════

  RECEIPTS_AGENT_ID       Your agent identifier
  RECEIPTS_MOLTBOOK_KEY   API key for Moltbook witnessing
  RECEIPTS_CUSTOM_RULES   Path to custom rules file

DISCLAIMER: RECEIPTS flags patterns only. Not a substitute for legal review.

GitHub: https://github.com/lazaruseth/receipts-mvp
Moltbook: https://moltbook.com/u/receipts-guard
`);
}

function parseFilters(args) {
  const filters = {};
  args.forEach(arg => {
    // Handle --key=value format
    const matchWithValue = arg.match(/^--(\w+[-\w]*)=(.+)$/);
    if (matchWithValue) {
      filters[matchWithValue[1]] = matchWithValue[2].replace(/^["']|["']$/g, '');
      return;
    }
    // Handle --flag format (boolean true)
    const matchFlag = arg.match(/^--(\w+[-\w]*)$/);
    if (matchFlag) {
      filters[matchFlag[1]] = true;
    }
  });
  return filters;
}

function getRecommendation(flags, consentFlags) {
  // Implicit consent is always a concern
  if (consentFlags.length > 0) {
    if (flags.length >= 2) return 'block';
    return 'require_approval';
  }
  if (flags.length >= 3) return 'block';
  if (flags.length >= 1) return 'require_approval';
  return 'proceed';
}

function generateSummary(flags, score, consentType) {
  let summary = '';

  if (consentType === 'implicit' || consentType === 'continued_use') {
    summary = `WARNING: ${consentType === 'implicit' ? 'Implicit' : 'Continued use'} consent pattern detected. `;
  }

  if (flags.length === 0) {
    return summary + 'No concerning clauses detected. Standard terms.';
  } else if (flags.length === 1) {
    return summary + `1 risk flag detected: ${flags[0]}`;
  } else if (flags.length === 2) {
    return summary + `2 risk flags detected. Review recommended.`;
  } else {
    return summary + `${flags.length} risk flags detected. User approval required.`;
  }
}

function detectRiskFlags(text) {
  const flags = [];

  const patterns = [
    { pattern: /binding arbitration/i, flag: 'Binding arbitration clause' },
    { pattern: /class action waiver/i, flag: 'Class action waiver' },
    { pattern: /waive.{0,20}(right|claim)/i, flag: 'Rights waiver detected' },
    { pattern: /no refund/i, flag: 'No refund policy' },
    { pattern: /non-refundable/i, flag: 'Non-refundable terms' },
    { pattern: /automatic renewal/i, flag: 'Auto-renewal clause' },
    { pattern: /auto.{0,5}renew/i, flag: 'Auto-renewal clause' },
    { pattern: /perpetual license/i, flag: 'Perpetual license grant' },
    { pattern: /irrevocable/i, flag: 'Irrevocable terms' },
    { pattern: /sell.{0,20}(data|information|personal)/i, flag: 'Data selling clause' },
    { pattern: /share.{0,20}third part/i, flag: 'Third-party data sharing' },
    { pattern: /limit.{0,20}liability/i, flag: 'Limited liability clause' },
    { pattern: /indemnif/i, flag: 'Indemnification clause' },
    { pattern: /hold.{0,10}harmless/i, flag: 'Hold harmless clause' },
    { pattern: /governing law.{0,50}(delaware|california)/i, flag: 'US jurisdiction clause' },
    { pattern: /exclusive jurisdiction/i, flag: 'Exclusive jurisdiction clause' },
    { pattern: /terminate.{0,20}without.{0,10}notice/i, flag: 'Termination without notice' },
    { pattern: /modify.{0,20}terms.{0,20}any time/i, flag: 'Unilateral modification rights' },
  ];

  for (const { pattern, flag } of patterns) {
    if (pattern.test(text)) {
      if (!flags.includes(flag)) {
        flags.push(flag);
      }
    }
  }

  return flags;
}

// NEW: Detect implicit consent patterns (Ghidorah-Prime's insight)
function detectConsentType(text) {
  const flags = [];

  const implicitPatterns = [
    { pattern: /continued use.{0,30}(constitutes?|means?|indicates?).{0,20}(acceptance|agreement|consent)/i, flag: 'Continued use consent' },
    { pattern: /by (using|accessing|continuing).{0,30}(you agree|you accept|you consent)/i, flag: 'Implicit consent pattern' },
    { pattern: /your (continued )?use.{0,30}(signif|constitut|indicat).{0,20}(acceptance|agreement)/i, flag: 'Continued use consent' },
    { pattern: /deemed to (have )?(accept|agree|consent)/i, flag: 'Implicit consent pattern' },
    { pattern: /use of.{0,20}service.{0,30}after.{0,20}(notice|posting|update).{0,30}(accept|agree|consent)/i, flag: 'Continued use consent' },
  ];

  for (const { pattern, flag } of implicitPatterns) {
    if (pattern.test(text)) {
      if (!flags.includes(flag)) {
        flags.push(flag);
      }
    }
  }

  return flags;
}

function detectImplicitConsentType(text) {
  const implicitPatterns = [
    /continued use/i,
    /by using/i,
    /by accessing/i,
    /deemed to/i,
  ];

  for (const pattern of implicitPatterns) {
    if (pattern.test(text)) {
      return 'implicit';
    }
  }

  return 'explicit';
}

function checkDuplicate(documentHash) {
  const index = loadIndex();
  return index.find(r => r.documentHash === documentHash);
}

function detectChanges(sourceUrl, newHash) {
  if (!sourceUrl || sourceUrl === 'unknown') return null;

  const index = loadIndex();
  const previousFromUrl = index
    .filter(r => r.sourceUrl === sourceUrl)
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))[0];

  if (previousFromUrl && previousFromUrl.documentHash !== newHash) {
    return {
      previousCaptureId: previousFromUrl.captureId,
      previousTimestamp: previousFromUrl.timestamp,
      previousHash: previousFromUrl.documentHash
    };
  }

  return null;
}

function loadIndex() {
  try {
    if (fs.existsSync(INDEX_FILE)) {
      return JSON.parse(fs.readFileSync(INDEX_FILE, 'utf8'));
    }
  } catch (e) {}

  // Rebuild index from files if missing
  return rebuildIndex();
}

function rebuildIndex() {
  const index = [];
  try {
    if (!fs.existsSync(RECEIPTS_DIR)) return index;

    const files = fs.readdirSync(RECEIPTS_DIR);
    files.forEach(file => {
      if (file.endsWith('.json') && file !== 'index.json') {
        try {
          const data = JSON.parse(fs.readFileSync(path.join(RECEIPTS_DIR, file), 'utf8'));
          index.push(data);
        } catch (e) {}
      }
    });

    // Save rebuilt index
    fs.writeFileSync(INDEX_FILE, JSON.stringify(index, null, 2));
  } catch (e) {}

  return index;
}

function updateIndex(capture) {
  try {
    const index = loadIndex();
    // Remove any existing entry with same captureId
    const filtered = index.filter(r => r.captureId !== capture.captureId);
    filtered.push(capture);
    fs.writeFileSync(INDEX_FILE, JSON.stringify(filtered, null, 2));
  } catch (e) {}
}

function saveLocalReceipt(capture, fullText) {
  try {
    if (!fs.existsSync(RECEIPTS_DIR)) {
      fs.mkdirSync(RECEIPTS_DIR, { recursive: true });
    }

    const metaFile = path.join(RECEIPTS_DIR, `${capture.captureId}.json`);
    fs.writeFileSync(metaFile, JSON.stringify(capture, null, 2));

    const textFile = path.join(RECEIPTS_DIR, `${capture.captureId}.txt`);
    fs.writeFileSync(textFile, fullText);
  } catch (e) {}
}

function saveScreenshot(captureId, base64Data) {
  try {
    const screenshotFile = path.join(RECEIPTS_DIR, `${captureId}.screenshot`);
    fs.writeFileSync(screenshotFile, base64Data);
  } catch (e) {}
}

// =============================================================================
// v0.5.0 ARBITRATION PROTOCOL
// =============================================================================

/**
 * Generate a canonical terms hash (PAO - Programmable Agreement Object)
 * Deterministic hash of terms + parties + deadline
 */
function generateTermsHash(terms, parties, deadline) {
  const canonical = {
    terms: terms.trim().toLowerCase().replace(/\s+/g, ' '),
    parties: parties.sort(), // Alphabetical for determinism
    deadline: deadline || null,
  };
  return crypto
    .createHash('sha256')
    .update(JSON.stringify(canonical))
    .digest('hex');
}

/**
 * Sign terms with agent identity
 * Uses Ed25519 if DID identity exists, falls back to legacy HMAC
 */
function signTerms(termsHash, agentId) {
  // Check if we have a DID identity with private key
  const didDocument = loadLocalDID();
  const privateKeyData = loadPrivateKey();

  if (didDocument && privateKeyData) {
    // Use Ed25519 signature
    const privateKeyDer = Buffer.from(privateKeyData.privateKey, 'base64');
    return signTermsWithDID(termsHash, privateKeyDer);
  }

  // Legacy fallback - HMAC signature
  const timestamp = Date.now();
  const signature = crypto
    .createHmac('sha256', agentId)
    .update(`${termsHash}|${timestamp}`)
    .digest('hex');
  return `sig:${signature.slice(0, 32)}:${timestamp}`;
}

/**
 * Verify a signature
 * Supports both Ed25519 (ed25519:) and legacy HMAC (sig:) formats
 */
function verifySignature(termsHash, signature, agentIdOrDID) {
  if (!signature) return false;

  // Handle Ed25519 signatures
  if (signature.startsWith('ed25519:')) {
    // Try to resolve DID document
    let didDocument = null;

    if (agentIdOrDID.startsWith('did:')) {
      didDocument = resolveDID(agentIdOrDID);
    } else {
      // Try local DID
      didDocument = loadLocalDID();
    }

    if (!didDocument) return false;

    const result = verifySignatureWithDID(termsHash, signature, didDocument);
    return result.valid;
  }

  // Handle legacy HMAC signatures
  if (signature.startsWith('sig:')) {
    // Extract legacy agent ID from DID if needed
    const legacyId = agentIdOrDID.startsWith('did:')
      ? agentIdOrDID.split(':').pop()
      : agentIdOrDID;

    const parts = signature.split(':');
    if (parts.length !== 3) return false;
    const [, sigHash, timestamp] = parts;
    const expected = crypto
      .createHmac('sha256', legacyId)
      .update(`${termsHash}|${timestamp}`)
      .digest('hex');
    return expected.slice(0, 32) === sigHash;
  }

  return false;
}

/**
 * Ensure a subdirectory exists with optional restricted permissions
 */
function ensureDir(dirPath, restrictedMode = false) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
  // Apply restricted permissions for sensitive directories
  if (restrictedMode) {
    try {
      fs.chmodSync(dirPath, 0o700); // Owner only: rwx------
    } catch (e) {
      // Windows doesn't support chmod
    }
  }
}

/**
 * Generate unique ID with prefix
 */
function generateId(prefix) {
  return `${prefix}_${crypto.randomBytes(8).toString('hex')}`;
}

// === PROPOSE COMMAND ===
function handlePropose(args) {
  const filters = parseFilters(args);
  const positionalArgs = args.filter(a => !a.startsWith('--'));
  const [terms, counterparty] = positionalArgs;

  if (!terms || !counterparty) {
    console.error(JSON.stringify({
      error: 'Missing required arguments',
      usage: 'node capture.js propose "TERMS" "COUNTERPARTY" --arbiter="ARBITER_AGENT" [--deadline=ISO_DATE] [--value=AMOUNT]'
    }));
    process.exit(1);
  }

  const arbiter = filters.arbiter;
  if (!arbiter) {
    console.error(JSON.stringify({
      error: 'Arbiter is required',
      usage: 'node capture.js propose "TERMS" "COUNTERPARTY" --arbiter="ARBITER_AGENT"',
      note: 'Both parties must agree on an arbiter at proposal time'
    }));
    process.exit(1);
  }

  const agentId = process.env.RECEIPTS_AGENT_ID || 'openclaw-agent';
  const deadline = filters.deadline || null;
  const value = filters.value || null;
  const channel = filters.channel || 'local';

  // x402 Payment configuration (v0.7.0)
  const arbitrationCost = filters['arbitration-cost'] || null;
  const paymentAddress = filters['payment-address'] || null;
  const paymentToken = filters['payment-token'] || 'USDC';
  const paymentChain = filters['payment-chain'] || 'base';

  // Build x402 payment schema if arbitration cost specified
  let x402 = null;
  if (arbitrationCost) {
    x402 = {
      arbitrationCost,
      arbitrationToken: paymentToken,
      arbitrationChain: CHAIN_CONFIG[paymentChain]?.chainId || 8453,
      paymentAddress: paymentAddress || null, // Arbiter's address
      escrowRequired: filters['escrow'] === 'true' || filters['escrow'] === true,
      paymentProtocol: 'x402',
      version: '1.0'
    };
  }

  // Generate PAO (Programmable Agreement Object)
  const parties = [agentId, counterparty];
  const termsHash = generateTermsHash(terms, parties, deadline);
  const proposerSignature = signTerms(termsHash, agentId);
  const proposalId = generateId('prop');

  // Default expiry: 7 days
  const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();

  const proposal = {
    proposalId,
    termsHash: `sha256:${termsHash}`,
    terms: {
      text: terms,
      canonical: terms.trim().toLowerCase().replace(/\s+/g, ' '),
    },
    proposer: agentId,
    counterparty,
    proposedArbiter: arbiter,
    deadline,
    value,
    channel,
    proposerSignature,
    x402, // Payment configuration (v0.7.0)
    status: 'pending_acceptance',
    createdAt: new Date().toISOString(),
    expiresAt,
    version: VERSION,
  };

  // Save proposal
  ensureDir(PROPOSALS_DIR);
  const proposalFile = path.join(PROPOSALS_DIR, `${proposalId}.json`);
  fs.writeFileSync(proposalFile, JSON.stringify(proposal, null, 2));

  // Save terms text
  const termsFile = path.join(PROPOSALS_DIR, `${proposalId}.txt`);
  fs.writeFileSync(termsFile, terms);

  console.log(JSON.stringify({
    ...proposal,
    message: `Proposal created. Share proposalId with ${counterparty} for acceptance.`,
    nextStep: `Counterparty should run: node capture.js accept --proposalId=${proposalId}`,
  }, null, 2));
}

// === ACCEPT COMMAND ===
function handleAccept(args) {
  const filters = parseFilters(args);
  const proposalId = filters.proposalId || filters.id;

  if (!proposalId) {
    console.error(JSON.stringify({
      error: 'Missing proposalId',
      usage: 'node capture.js accept --proposalId=prop_xxx'
    }));
    process.exit(1);
  }

  // Load proposal
  const proposalFile = path.join(PROPOSALS_DIR, `${proposalId}.json`);
  if (!fs.existsSync(proposalFile)) {
    console.error(JSON.stringify({ error: 'Proposal not found', proposalId }));
    process.exit(1);
  }

  const proposal = JSON.parse(fs.readFileSync(proposalFile, 'utf8'));

  if (proposal.status !== 'pending_acceptance') {
    console.error(JSON.stringify({
      error: 'Proposal is not pending acceptance',
      currentStatus: proposal.status
    }));
    process.exit(1);
  }

  // Check expiry
  if (new Date(proposal.expiresAt) < new Date()) {
    proposal.status = 'expired';
    fs.writeFileSync(proposalFile, JSON.stringify(proposal, null, 2));
    console.error(JSON.stringify({ error: 'Proposal has expired', expiresAt: proposal.expiresAt }));
    process.exit(1);
  }

  const agentId = process.env.RECEIPTS_AGENT_ID || 'openclaw-agent';
  const termsHash = proposal.termsHash.replace('sha256:', '');

  // Sign terms as counterparty
  const counterpartySignature = signTerms(termsHash, agentId);

  // Create agreement from proposal
  const agreementId = generateId('agr');
  const agreement = {
    agreementId,
    proposalId,
    termsHash: proposal.termsHash,
    terms: proposal.terms,
    parties: [proposal.proposer, proposal.counterparty],
    arbiter: proposal.proposedArbiter,
    deadline: proposal.deadline,
    value: proposal.value,
    signatures: {
      [proposal.proposer]: proposal.proposerSignature,
      [proposal.counterparty]: counterpartySignature,
    },
    x402: proposal.x402 || null, // Payment terms (v0.7.0)
    status: 'active',
    timeline: [
      {
        event: 'proposed',
        timestamp: proposal.createdAt,
        actor: proposal.proposer,
      },
      {
        event: 'accepted',
        timestamp: new Date().toISOString(),
        actor: agentId,
      },
    ],
    createdAt: new Date().toISOString(),
    version: VERSION,
  };

  // Save agreement
  ensureDir(AGREEMENTS_DIR);
  const agreementFile = path.join(AGREEMENTS_DIR, `${agreementId}.json`);
  fs.writeFileSync(agreementFile, JSON.stringify(agreement, null, 2));

  // Copy terms text
  const proposalTermsFile = path.join(PROPOSALS_DIR, `${proposalId}.txt`);
  const agreementTermsFile = path.join(AGREEMENTS_DIR, `${agreementId}.txt`);
  if (fs.existsSync(proposalTermsFile)) {
    fs.copyFileSync(proposalTermsFile, agreementTermsFile);
  }

  // Update proposal status
  proposal.status = 'accepted';
  proposal.agreementId = agreementId;
  proposal.acceptedAt = new Date().toISOString();
  fs.writeFileSync(proposalFile, JSON.stringify(proposal, null, 2));

  console.log(JSON.stringify({
    ...agreement,
    message: 'Agreement created! Both parties have signed.',
    arbiterNotified: `Arbiter ${agreement.arbiter} should be notified of appointment.`,
    nextSteps: [
      `Fulfill: node capture.js fulfill --agreementId=${agreementId} --evidence="PROOF"`,
      `Dispute: node capture.js arbitrate --agreementId=${agreementId} --reason="non_delivery"`,
    ],
  }, null, 2));
}

// === REJECT COMMAND ===
function handleReject(args) {
  const filters = parseFilters(args);
  const proposalId = filters.proposalId || filters.id;
  const reason = filters.reason || 'No reason provided';

  if (!proposalId) {
    console.error(JSON.stringify({
      error: 'Missing proposalId',
      usage: 'node capture.js reject --proposalId=prop_xxx --reason="REASON"'
    }));
    process.exit(1);
  }

  const proposalFile = path.join(PROPOSALS_DIR, `${proposalId}.json`);
  if (!fs.existsSync(proposalFile)) {
    console.error(JSON.stringify({ error: 'Proposal not found', proposalId }));
    process.exit(1);
  }

  const proposal = JSON.parse(fs.readFileSync(proposalFile, 'utf8'));

  if (proposal.status !== 'pending_acceptance') {
    console.error(JSON.stringify({
      error: 'Proposal is not pending acceptance',
      currentStatus: proposal.status
    }));
    process.exit(1);
  }

  // Update proposal
  proposal.status = 'rejected';
  proposal.rejectedAt = new Date().toISOString();
  proposal.rejectionReason = reason;
  fs.writeFileSync(proposalFile, JSON.stringify(proposal, null, 2));

  console.log(JSON.stringify({
    proposalId,
    status: 'rejected',
    reason,
    rejectedAt: proposal.rejectedAt,
  }, null, 2));
}

// === FULFILL COMMAND ===
function handleFulfill(args) {
  const filters = parseFilters(args);
  const agreementId = filters.agreementId || filters.id;
  const evidence = filters.evidence;

  if (!agreementId) {
    console.error(JSON.stringify({
      error: 'Missing agreementId',
      usage: 'node capture.js fulfill --agreementId=agr_xxx --evidence="PROOF"'
    }));
    process.exit(1);
  }

  if (!evidence) {
    console.error(JSON.stringify({
      error: 'Evidence is required for fulfillment',
      usage: 'node capture.js fulfill --agreementId=agr_xxx --evidence="PROOF_OF_COMPLETION"'
    }));
    process.exit(1);
  }

  const agreementFile = path.join(AGREEMENTS_DIR, `${agreementId}.json`);
  if (!fs.existsSync(agreementFile)) {
    console.error(JSON.stringify({ error: 'Agreement not found', agreementId }));
    process.exit(1);
  }

  const agreement = JSON.parse(fs.readFileSync(agreementFile, 'utf8'));

  if (agreement.status !== 'active') {
    console.error(JSON.stringify({
      error: 'Agreement is not active',
      currentStatus: agreement.status
    }));
    process.exit(1);
  }

  const agentId = process.env.RECEIPTS_AGENT_ID || 'openclaw-agent';

  // Add fulfillment to timeline
  agreement.timeline.push({
    event: 'fulfillment_claimed',
    timestamp: new Date().toISOString(),
    actor: agentId,
    evidence,
    evidenceHash: crypto.createHash('sha256').update(evidence).digest('hex'),
  });

  // Status becomes pending_confirmation (other party must confirm)
  // For simplicity, we'll auto-confirm after a grace period (in production, this would be interactive)
  agreement.status = 'pending_confirmation';
  agreement.fulfillmentClaimed = {
    by: agentId,
    at: new Date().toISOString(),
    evidence,
    // Grace period: 48 hours for counterparty to dispute
    gracePeriodEnds: new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString(),
  };

  fs.writeFileSync(agreementFile, JSON.stringify(agreement, null, 2));

  console.log(JSON.stringify({
    agreementId,
    status: agreement.status,
    fulfillmentClaimed: agreement.fulfillmentClaimed,
    message: 'Fulfillment claimed. Counterparty has 48 hours to dispute.',
    nextSteps: [
      'If counterparty confirms: Agreement closes as fulfilled',
      `If counterparty disputes: node capture.js arbitrate --agreementId=${agreementId} --reason="quality"`,
      'If grace period passes: Agreement auto-closes as fulfilled',
    ],
  }, null, 2));
}

// === ARBITRATE COMMAND ===
function handleArbitrate(args) {
  const filters = parseFilters(args);
  const agreementId = filters.agreementId || filters.id;
  const reason = filters.reason;
  const evidence = filters.evidence;

  if (!agreementId) {
    console.error(JSON.stringify({
      error: 'Missing agreementId',
      usage: 'node capture.js arbitrate --agreementId=agr_xxx --reason="non_delivery" --evidence="PROOF"'
    }));
    process.exit(1);
  }

  if (!reason || !VALID_ARBITRATION_REASONS.includes(reason)) {
    console.error(JSON.stringify({
      error: 'Valid reason required',
      validReasons: VALID_ARBITRATION_REASONS,
      usage: 'node capture.js arbitrate --agreementId=agr_xxx --reason="non_delivery"'
    }));
    process.exit(1);
  }

  const agreementFile = path.join(AGREEMENTS_DIR, `${agreementId}.json`);
  if (!fs.existsSync(agreementFile)) {
    console.error(JSON.stringify({ error: 'Agreement not found', agreementId }));
    process.exit(1);
  }

  const agreement = JSON.parse(fs.readFileSync(agreementFile, 'utf8'));

  // x402 Payment verification (v0.7.0)
  if (agreement.x402?.arbitrationCost) {
    const paymentProof = filters['payment-proof'];
    if (!paymentProof) {
      console.error(JSON.stringify({
        error: 'Payment required for arbitration',
        x402: {
          cost: agreement.x402.arbitrationCost,
          token: agreement.x402.arbitrationToken,
          chain: agreement.x402.arbitrationChain,
          recipient: agreement.x402.paymentAddress || agreement.arbiter,
          protocol: 'x402'
        },
        hint: 'Pay arbitration fee via x402 and provide --payment-proof=0xTxHash',
        usage: `node capture.js arbitrate --agreementId=${agreementId} --reason="..." --evidence="..." --payment-proof=0x...`
      }));
      process.exit(1);
    }

    // Validate payment proof format (basic validation - full verification would check chain)
    if (!paymentProof.startsWith('0x') || paymentProof.length < 66) {
      console.error(JSON.stringify({
        error: 'Invalid payment proof format',
        expected: '0x followed by 64 hex characters (transaction hash)',
        received: paymentProof
      }));
      process.exit(1);
    }

    // Store payment proof (in production, would verify on-chain)
    console.log(JSON.stringify({
      status: 'payment_accepted',
      paymentProof,
      note: 'Payment proof recorded. On-chain verification available in future version.'
    }, null, 2));
  }

  if (!['active', 'pending_confirmation'].includes(agreement.status)) {
    console.error(JSON.stringify({
      error: 'Agreement cannot be disputed',
      currentStatus: agreement.status,
      note: 'Only active or pending_confirmation agreements can be disputed'
    }));
    process.exit(1);
  }

  const agentId = process.env.RECEIPTS_AGENT_ID || 'openclaw-agent';
  const arbitrationId = generateId('arb');

  // Determine claimant and respondent
  const claimant = agentId;
  const respondent = agreement.parties.find(p => p !== agentId) || agreement.parties[1];

  // Evidence window: 7 days
  const evidenceDeadline = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();

  // Payment proof for x402 (if provided)
  const paymentProof = filters['payment-proof'];

  const arbitration = {
    arbitrationId,
    agreementId,
    termsHash: agreement.termsHash,
    claimant,
    respondent,
    arbiter: agreement.arbiter,
    reason,
    reasonDescription: getArbitrationReasonDescription(reason),
    status: 'open',
    evidence: {
      claimant: evidence ? [{
        submittedAt: new Date().toISOString(),
        content: evidence,
        hash: crypto.createHash('sha256').update(evidence).digest('hex'),
        type: filters.type || 'document',
      }] : [],
      respondent: [],
    },
    // x402 payment tracking (v0.7.0)
    x402: agreement.x402 ? {
      ...agreement.x402,
      paymentProof: paymentProof || null,
      paymentVerified: !!paymentProof,
      paymentRecordedAt: paymentProof ? new Date().toISOString() : null
    } : null,
    ruling: null,
    openedAt: new Date().toISOString(),
    evidenceDeadline,
    version: VERSION,
  };

  // Save arbitration
  ensureDir(ARBITRATIONS_DIR);
  const arbitrationFile = path.join(ARBITRATIONS_DIR, `${arbitrationId}.json`);
  fs.writeFileSync(arbitrationFile, JSON.stringify(arbitration, null, 2));

  // Update agreement status
  agreement.status = 'disputed';
  agreement.arbitrationId = arbitrationId;
  agreement.timeline.push({
    event: 'dispute_opened',
    timestamp: new Date().toISOString(),
    actor: agentId,
    reason,
    arbitrationId,
  });
  fs.writeFileSync(agreementFile, JSON.stringify(agreement, null, 2));

  console.log(JSON.stringify({
    ...arbitration,
    message: `Arbitration opened. Arbiter ${agreement.arbiter} has been notified.`,
    evidenceWindow: `Both parties have until ${evidenceDeadline} to submit evidence.`,
    nextSteps: [
      `Submit more evidence: node capture.js submit --arbitrationId=${arbitrationId} --evidence="PROOF"`,
      `View timeline: node capture.js timeline --agreementId=${agreementId}`,
    ],
  }, null, 2));
}

function getArbitrationReasonDescription(reason) {
  const descriptions = {
    non_delivery: 'Counterparty did not deliver as agreed',
    partial_delivery: 'Delivery was incomplete or partial',
    quality: 'Delivery did not meet quality specifications',
    deadline_breach: 'Delivery deadline was missed',
    repudiation: 'Counterparty denies the agreement exists',
    other: 'Other breach of agreement',
  };
  return descriptions[reason] || reason;
}

// === SUBMIT COMMAND (Evidence Submission) ===
function handleSubmit(args) {
  const filters = parseFilters(args);
  const arbitrationId = filters.arbitrationId || filters.id;
  const evidence = filters.evidence;
  const evidenceType = filters.type || 'document';

  if (!arbitrationId) {
    console.error(JSON.stringify({
      error: 'Missing arbitrationId',
      usage: 'node capture.js submit --arbitrationId=arb_xxx --evidence="PROOF" [--type=document|screenshot|witness]'
    }));
    process.exit(1);
  }

  if (!evidence) {
    console.error(JSON.stringify({
      error: 'Evidence is required',
      usage: 'node capture.js submit --arbitrationId=arb_xxx --evidence="PROOF"'
    }));
    process.exit(1);
  }

  const arbitrationFile = path.join(ARBITRATIONS_DIR, `${arbitrationId}.json`);
  if (!fs.existsSync(arbitrationFile)) {
    console.error(JSON.stringify({ error: 'Arbitration not found', arbitrationId }));
    process.exit(1);
  }

  const arbitration = JSON.parse(fs.readFileSync(arbitrationFile, 'utf8'));

  if (!['open', 'evidence_period'].includes(arbitration.status)) {
    console.error(JSON.stringify({
      error: 'Evidence submission period has closed',
      currentStatus: arbitration.status
    }));
    process.exit(1);
  }

  // Check evidence deadline
  if (new Date(arbitration.evidenceDeadline) < new Date()) {
    arbitration.status = 'deliberation';
    fs.writeFileSync(arbitrationFile, JSON.stringify(arbitration, null, 2));
    console.error(JSON.stringify({
      error: 'Evidence deadline has passed',
      deadline: arbitration.evidenceDeadline
    }));
    process.exit(1);
  }

  const agentId = process.env.RECEIPTS_AGENT_ID || 'openclaw-agent';

  // Determine which party is submitting
  const isClaimant = agentId === arbitration.claimant;
  const party = isClaimant ? 'claimant' : 'respondent';

  const evidenceEntry = {
    submittedAt: new Date().toISOString(),
    content: evidence,
    hash: crypto.createHash('sha256').update(evidence).digest('hex'),
    type: evidenceType,
  };

  arbitration.evidence[party].push(evidenceEntry);
  arbitration.status = 'evidence_period';
  fs.writeFileSync(arbitrationFile, JSON.stringify(arbitration, null, 2));

  console.log(JSON.stringify({
    arbitrationId,
    party,
    evidenceSubmitted: evidenceEntry,
    totalEvidence: {
      claimant: arbitration.evidence.claimant.length,
      respondent: arbitration.evidence.respondent.length,
    },
    evidenceDeadline: arbitration.evidenceDeadline,
  }, null, 2));
}

// === RULING COMMAND (Arbiter Only) ===
function handleRuling(args) {
  const filters = parseFilters(args);
  const arbitrationId = filters.arbitrationId || filters.id;
  const decision = filters.decision;
  const reasoning = filters.reasoning;

  if (!arbitrationId) {
    console.error(JSON.stringify({
      error: 'Missing arbitrationId',
      usage: 'node capture.js ruling --arbitrationId=arb_xxx --decision=claimant|respondent|split --reasoning="EXPLANATION"'
    }));
    process.exit(1);
  }

  if (!decision || !['claimant', 'respondent', 'split'].includes(decision)) {
    console.error(JSON.stringify({
      error: 'Valid decision required',
      validDecisions: ['claimant', 'respondent', 'split'],
      usage: 'node capture.js ruling --arbitrationId=arb_xxx --decision=claimant'
    }));
    process.exit(1);
  }

  if (!reasoning) {
    console.error(JSON.stringify({
      error: 'Reasoning is required for ruling',
      usage: 'node capture.js ruling --arbitrationId=arb_xxx --decision=claimant --reasoning="Evidence shows..."'
    }));
    process.exit(1);
  }

  const arbitrationFile = path.join(ARBITRATIONS_DIR, `${arbitrationId}.json`);
  if (!fs.existsSync(arbitrationFile)) {
    console.error(JSON.stringify({ error: 'Arbitration not found', arbitrationId }));
    process.exit(1);
  }

  const arbitration = JSON.parse(fs.readFileSync(arbitrationFile, 'utf8'));

  if (arbitration.status === 'ruled') {
    console.error(JSON.stringify({
      error: 'Ruling has already been issued',
      existingRuling: arbitration.ruling
    }));
    process.exit(1);
  }

  const agentId = process.env.RECEIPTS_AGENT_ID || 'openclaw-agent';

  // Verify caller is arbiter (simplified check)
  if (agentId !== arbitration.arbiter) {
    console.error(JSON.stringify({
      error: 'Only the arbiter can issue a ruling',
      arbiter: arbitration.arbiter,
      yourId: agentId
    }));
    process.exit(1);
  }

  const rulingId = generateId('rul');
  const reasoningHash = crypto.createHash('sha256').update(reasoning).digest('hex');

  const ruling = {
    rulingId,
    arbitrationId,
    arbiter: agentId,
    decision,
    decisionDescription: getDecisionDescription(decision, arbitration),
    reasoning,
    reasoningHash: `sha256:${reasoningHash}`,
    evidenceConsidered: {
      claimant: arbitration.evidence.claimant.length,
      respondent: arbitration.evidence.respondent.length,
    },
    issuedAt: new Date().toISOString(),
    version: VERSION,
  };

  // Save ruling
  ensureDir(RULINGS_DIR);
  const rulingFile = path.join(RULINGS_DIR, `${rulingId}.json`);
  fs.writeFileSync(rulingFile, JSON.stringify(ruling, null, 2));

  // Update arbitration
  arbitration.status = 'ruled';
  arbitration.ruling = ruling;
  fs.writeFileSync(arbitrationFile, JSON.stringify(arbitration, null, 2));

  // Update agreement
  const agreementFile = path.join(AGREEMENTS_DIR, `${arbitration.agreementId}.json`);
  if (fs.existsSync(agreementFile)) {
    const agreement = JSON.parse(fs.readFileSync(agreementFile, 'utf8'));
    agreement.status = 'closed';
    agreement.closedAt = new Date().toISOString();
    agreement.closureReason = 'arbitration_ruling';
    agreement.rulingId = rulingId;
    agreement.timeline.push({
      event: 'ruling_issued',
      timestamp: new Date().toISOString(),
      actor: agentId,
      decision,
      rulingId,
    });
    fs.writeFileSync(agreementFile, JSON.stringify(agreement, null, 2));
  }

  console.log(JSON.stringify({
    ...ruling,
    message: 'Ruling issued. Agreement is now closed.',
    publicRecord: {
      note: 'Reasoning hash can be posted to Moltbook for public record',
      hash: ruling.reasoningHash,
      suggestedPost: `⚖️ RULING: Arbitration ${arbitrationId} - Decision: ${decision}. Reasoning hash: ${reasoningHash.slice(0, 16)}...`,
    },
  }, null, 2));
}

function getDecisionDescription(decision, arbitration) {
  switch (decision) {
    case 'claimant':
      return `Ruled in favor of ${arbitration.claimant} (claimant)`;
    case 'respondent':
      return `Ruled in favor of ${arbitration.respondent} (respondent)`;
    case 'split':
      return 'Split decision - partial responsibility on both parties';
    default:
      return decision;
  }
}

// === TIMELINE COMMAND (LPR - Legal Provenance Review) ===
function handleTimeline(args) {
  const filters = parseFilters(args);
  const agreementId = filters.agreementId || filters.id;

  if (!agreementId) {
    console.error(JSON.stringify({
      error: 'Missing agreementId',
      usage: 'node capture.js timeline --agreementId=agr_xxx'
    }));
    process.exit(1);
  }

  const agreementFile = path.join(AGREEMENTS_DIR, `${agreementId}.json`);
  if (!fs.existsSync(agreementFile)) {
    console.error(JSON.stringify({ error: 'Agreement not found', agreementId }));
    process.exit(1);
  }

  const agreement = JSON.parse(fs.readFileSync(agreementFile, 'utf8'));

  // Build comprehensive timeline
  const timeline = {
    title: `Legal Provenance Review (LPR) - ${agreementId}`,
    generatedAt: new Date().toISOString(),
    agreement: {
      agreementId,
      termsHash: agreement.termsHash,
      parties: agreement.parties,
      arbiter: agreement.arbiter,
      status: agreement.status,
      deadline: agreement.deadline,
      value: agreement.value,
    },
    events: [...agreement.timeline],
    signatures: agreement.signatures,
  };

  // Add arbitration events if exists
  if (agreement.arbitrationId) {
    const arbitrationFile = path.join(ARBITRATIONS_DIR, `${agreement.arbitrationId}.json`);
    if (fs.existsSync(arbitrationFile)) {
      const arbitration = JSON.parse(fs.readFileSync(arbitrationFile, 'utf8'));

      timeline.arbitration = {
        arbitrationId: arbitration.arbitrationId,
        reason: arbitration.reason,
        claimant: arbitration.claimant,
        respondent: arbitration.respondent,
        status: arbitration.status,
      };

      // Add evidence submissions to timeline
      for (const ev of arbitration.evidence.claimant) {
        timeline.events.push({
          event: 'evidence_submitted',
          timestamp: ev.submittedAt,
          actor: arbitration.claimant,
          party: 'claimant',
          evidenceHash: ev.hash,
          type: ev.type,
        });
      }

      for (const ev of arbitration.evidence.respondent) {
        timeline.events.push({
          event: 'evidence_submitted',
          timestamp: ev.submittedAt,
          actor: arbitration.respondent,
          party: 'respondent',
          evidenceHash: ev.hash,
          type: ev.type,
        });
      }

      // Add ruling if exists
      if (arbitration.ruling) {
        timeline.ruling = {
          rulingId: arbitration.ruling.rulingId,
          decision: arbitration.ruling.decision,
          reasoningHash: arbitration.ruling.reasoningHash,
          issuedAt: arbitration.ruling.issuedAt,
        };
      }
    }
  }

  // Sort events by timestamp
  timeline.events.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  // Generate visual representation
  timeline.visualTimeline = timeline.events.map((e, i) => {
    const date = new Date(e.timestamp).toISOString().split('T')[0];
    const time = new Date(e.timestamp).toISOString().split('T')[1].slice(0, 5);
    return `${i + 1}. [${date} ${time}] ${e.event.toUpperCase()} by ${e.actor}${e.evidence ? ' (with evidence)' : ''}`;
  });

  console.log(JSON.stringify(timeline, null, 2));
}

// =============================================================================
// v0.4.0 FEATURES
// =============================================================================

// === PROMISE COMMAND (Agent-to-Agent Agreements) ===
function handlePromise(args) {
  const filters = parseFilters(args);
  const positionalArgs = args.filter(a => !a.startsWith('--'));
  const [commitmentText, counterparty] = positionalArgs;

  if (!commitmentText || !counterparty) {
    console.error(JSON.stringify({
      error: 'Missing required arguments',
      usage: 'node capture.js promise "COMMITMENT_TEXT" "COUNTERPARTY" [--direction=outbound] [--channel=email]'
    }));
    process.exit(1);
  }

  const agentId = process.env.RECEIPTS_AGENT_ID || 'openclaw-agent';
  const direction = filters.direction || 'outbound';
  const channel = filters.channel || 'unknown';

  // Create commitment hash
  const commitmentHash = crypto
    .createHash('sha256')
    .update(`${commitmentText}|${counterparty}|${agentId}|${Date.now()}`)
    .digest('hex');

  // Analyze commitment for risk
  const riskFlags = detectCommitmentRisks(commitmentText);

  const promise = {
    promiseId: `promise_${commitmentHash.slice(0, 16)}`,
    type: 'agent_commitment',
    direction, // 'outbound' = I promised them, 'inbound' = they promised me
    commitmentText,
    counterparty,
    channel,
    agentId,
    timestamp: new Date().toISOString(),
    commitmentHash,
    riskFlags,
    riskLevel: riskFlags.length >= 2 ? 'high' : riskFlags.length === 1 ? 'medium' : 'low',
    version: VERSION,
    disclaimer: 'RECEIPTS captures commitments for evidence. Not a substitute for legal review.',
  };

  console.log(JSON.stringify(promise, null, 2));

  // Save locally
  savePromise(promise, commitmentText);
  updateIndex(promise);
}

function detectCommitmentRisks(text) {
  const flags = [];
  const patterns = [
    { pattern: /unconditional/i, flag: 'Unconditional commitment' },
    { pattern: /guarantee/i, flag: 'Guarantee language' },
    { pattern: /by (monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{1,2}\/\d{1,2})/i, flag: 'Time-bound commitment' },
    { pattern: /deliver/i, flag: 'Delivery commitment' },
    { pattern: /pay|payment|\$\d+/i, flag: 'Financial commitment' },
    { pattern: /exclusive/i, flag: 'Exclusivity commitment' },
    { pattern: /permanent|forever|perpetual/i, flag: 'Perpetual commitment' },
    { pattern: /no matter what|regardless/i, flag: 'Unconditional language' },
  ];

  for (const { pattern, flag } of patterns) {
    if (pattern.test(text) && !flags.includes(flag)) {
      flags.push(flag);
    }
  }
  return flags;
}

function savePromise(promise, fullText) {
  try {
    if (!fs.existsSync(RECEIPTS_DIR)) {
      fs.mkdirSync(RECEIPTS_DIR, { recursive: true });
    }
    const metaFile = path.join(RECEIPTS_DIR, `${promise.promiseId}.json`);
    fs.writeFileSync(metaFile, JSON.stringify(promise, null, 2));
    const textFile = path.join(RECEIPTS_DIR, `${promise.promiseId}.txt`);
    fs.writeFileSync(textFile, fullText);
  } catch (e) {}
}

// === WITNESS COMMAND (Decentralized Witnessing) ===
function handleWitness(args) {
  const filters = parseFilters(args);
  const captureId = filters.captureId || filters.id;
  const anchor = filters.anchor || 'moltbook';

  if (!captureId) {
    console.error(JSON.stringify({
      error: 'Missing captureId',
      usage: 'node capture.js witness --captureId=ID [--anchor=moltbook|bitcoin|both]'
    }));
    process.exit(1);
  }

  const index = loadIndex();
  const capture = index.find(r => r.captureId === captureId || r.promiseId === captureId);

  if (!capture) {
    console.error(JSON.stringify({ error: 'Capture not found' }));
    process.exit(1);
  }

  // Create witness record
  const witnessRecord = {
    witnessId: `witness_${crypto.randomBytes(8).toString('hex')}`,
    captureId: captureId,
    documentHash: capture.documentHash || capture.commitmentHash,
    timestamp: new Date().toISOString(),
    anchor,
    status: 'pending',
    anchors: {},
  };

  // Handle different anchor types
  if (anchor === 'moltbook' || anchor === 'both') {
    const moltbookKey = process.env.RECEIPTS_MOLTBOOK_KEY;
    if (moltbookKey) {
      witnessRecord.anchors.moltbook = {
        status: 'ready',
        postContent: `📜 WITNESS: Document hash ${capture.documentHash || capture.commitmentHash} captured at ${capture.timestamp}`,
        instructions: 'POST to Moltbook API to anchor this hash publicly',
        apiEndpoint: 'https://www.moltbook.com/api/v1/posts',
      };
    } else {
      witnessRecord.anchors.moltbook = {
        status: 'missing_key',
        instructions: 'Set RECEIPTS_MOLTBOOK_KEY environment variable to enable Moltbook witnessing',
      };
    }
  }

  if (anchor === 'bitcoin' || anchor === 'both') {
    witnessRecord.anchors.bitcoin = {
      status: 'ready',
      opReturnData: `RECEIPTS:${(capture.documentHash || capture.commitmentHash).slice(0, 40)}`,
      instructions: 'Use any Bitcoin wallet to create an OP_RETURN transaction with this data',
      estimatedFee: '~$0.50-2.00 depending on network',
    };
  }

  // Save witness record
  saveWitness(witnessRecord);

  console.log(JSON.stringify(witnessRecord, null, 2));
}

function saveWitness(witness) {
  try {
    if (!fs.existsSync(WITNESS_DIR)) {
      fs.mkdirSync(WITNESS_DIR, { recursive: true });
    }
    const witnessFile = path.join(WITNESS_DIR, `${witness.witnessId}.json`);
    fs.writeFileSync(witnessFile, JSON.stringify(witness, null, 2));
  } catch (e) {}
}

// === RULES COMMAND (Custom Rulesets) ===
function handleRules(args) {
  const filters = parseFilters(args);

  if (args.includes('--list') || args.length === 0) {
    // List all rules (built-in + custom)
    const customRules = loadCustomRules();
    console.log(JSON.stringify({
      builtInRules: getBuiltInRules().length,
      customRules: customRules.length,
      rules: {
        builtIn: getBuiltInRules(),
        custom: customRules,
      }
    }, null, 2));
    return;
  }

  if (filters.add && filters.flag) {
    // Add a new custom rule
    addCustomRule(filters.add, filters.flag, filters.category || 'custom');
    console.log(JSON.stringify({
      success: true,
      message: `Added custom rule: "${filters.flag}"`,
      pattern: filters.add,
    }));
    return;
  }

  if (filters.import) {
    // Import rules from file
    try {
      const imported = JSON.parse(fs.readFileSync(filters.import, 'utf8'));
      const customRules = loadCustomRules();
      const merged = [...customRules, ...imported];
      fs.writeFileSync(CUSTOM_RULES_FILE, JSON.stringify(merged, null, 2));
      console.log(JSON.stringify({
        success: true,
        message: `Imported ${imported.length} rules`,
      }));
    } catch (e) {
      console.error(JSON.stringify({ error: 'Failed to import rules', details: e.message }));
    }
    return;
  }

  if (filters.remove) {
    // Remove a custom rule by flag name
    const customRules = loadCustomRules();
    const filtered = customRules.filter(r => r.flag !== filters.remove);
    fs.writeFileSync(CUSTOM_RULES_FILE, JSON.stringify(filtered, null, 2));
    console.log(JSON.stringify({
      success: true,
      message: `Removed rule: "${filters.remove}"`,
    }));
    return;
  }

  console.error(JSON.stringify({
    error: 'Invalid rules command',
    usage: 'node capture.js rules --list | --add="PATTERN" --flag="FLAG" | --import=FILE | --remove="FLAG"'
  }));
}

function getBuiltInRules() {
  return [
    { pattern: 'binding arbitration', flag: 'Binding arbitration clause', category: 'legal' },
    { pattern: 'class action waiver', flag: 'Class action waiver', category: 'legal' },
    { pattern: 'no refund', flag: 'No refund policy', category: 'financial' },
    { pattern: 'auto-renew', flag: 'Auto-renewal clause', category: 'financial' },
    { pattern: 'perpetual license', flag: 'Perpetual license grant', category: 'ip' },
    { pattern: 'sell.*data', flag: 'Data selling clause', category: 'privacy' },
    { pattern: 'share.*third part', flag: 'Third-party data sharing', category: 'privacy' },
    { pattern: 'limit.*liability', flag: 'Limited liability clause', category: 'legal' },
    { pattern: 'indemnif', flag: 'Indemnification clause', category: 'legal' },
    { pattern: 'terminate.*without.*notice', flag: 'Termination without notice', category: 'terms' },
  ];
}

function loadCustomRules() {
  try {
    if (fs.existsSync(CUSTOM_RULES_FILE)) {
      return JSON.parse(fs.readFileSync(CUSTOM_RULES_FILE, 'utf8'));
    }
  } catch (e) {}
  return [];
}

function addCustomRule(pattern, flag, category) {
  const customRules = loadCustomRules();
  customRules.push({ pattern, flag, category, addedAt: new Date().toISOString() });

  if (!fs.existsSync(RECEIPTS_DIR)) {
    fs.mkdirSync(RECEIPTS_DIR, { recursive: true });
  }
  fs.writeFileSync(CUSTOM_RULES_FILE, JSON.stringify(customRules, null, 2));
}

// Enhanced risk detection with custom rules
function detectRiskFlagsWithCustom(text) {
  const flags = detectRiskFlags(text); // Built-in
  const customRules = loadCustomRules();

  for (const rule of customRules) {
    try {
      const regex = new RegExp(rule.pattern, 'i');
      if (regex.test(text) && !flags.includes(rule.flag)) {
        flags.push(rule.flag);
      }
    } catch (e) {}
  }

  return flags;
}

// === PDF EXPORT (Enhanced Export) ===
// Note: Generates a structured format that can be converted to PDF by external tools
function generatePDFContent(capture, documentText) {
  const index = loadIndex();
  const meta = index.find(r => r.captureId === capture.captureId);

  return {
    format: 'receipts-evidence-v1',
    title: `Evidence Package: ${capture.merchantName || capture.counterparty}`,
    generatedAt: new Date().toISOString(),
    generatedBy: `RECEIPTS Guard v${VERSION}`,

    header: {
      caseReference: capture.captureId,
      documentType: capture.type === 'agent_commitment' ? 'Agent Commitment Record' : 'Terms of Service Capture',
      captureDate: capture.timestamp,
    },

    parties: {
      agent: capture.agentId,
      counterparty: capture.merchantName || capture.counterparty,
      direction: capture.direction || 'inbound',
    },

    documentEvidence: {
      hash: capture.documentHash || capture.commitmentHash,
      hashAlgorithm: 'SHA-256',
      length: documentText?.length || capture.documentLength,
      preview: documentText?.substring(0, 500) || '[Document text not available]',
    },

    consentEvidence: capture.consentProof ? {
      type: capture.consentProof.type,
      capturedAt: capture.consentProof.capturedAt,
      method: capture.consentProof.agentAction,
      elementSelector: capture.consentProof.elementSelector,
      hasScreenshot: !!capture.consentProof.screenshotHash,
    } : null,

    riskAnalysis: {
      trustScore: capture.trustScore,
      recommendation: capture.recommendation,
      flags: capture.riskFlags?.map(flag => ({
        flag,
        implication: getRiskImplication(flag),
      })) || [],
    },

    changeHistory: capture.changeDetected ? {
      detected: true,
      previousCapture: capture.previousCapture,
      note: capture.changeNote,
    } : { detected: false },

    legalDisclaimer: `This document was generated by RECEIPTS Guard v${VERSION}, an automated agreement capture tool. ` +
      'It records what terms existed at the time of capture and how consent was documented. ' +
      'This is NOT legal advice. The patterns flagged are based on automated detection and may not capture all relevant clauses. ' +
      'Consult with a qualified attorney for legal interpretation and dispute resolution.',

    exportInstructions: {
      toPDF: 'Use a JSON-to-PDF converter or import into your document system',
      forCourt: 'Print this document and have it notarized alongside the full agreement text',
      forMediation: 'Share this structured data with the mediator as evidence of agreement terms',
    },
  };
}

// === FRAMEWORK INTEGRATION API ===

/**
 * Register a beforeConsent hook
 * Called before any agreement is captured, can block or modify
 *
 * Usage:
 *   const receipts = require('./capture.js');
 *   receipts.beforeConsent(async (element, ctx) => {
 *     const capture = await receipts.capture({ text: element.innerText, ... });
 *     if (capture.recommendation === 'block') {
 *       return { proceed: false, reason: capture.summary };
 *     }
 *     return { proceed: true };
 *   });
 */
function beforeConsent(handler) {
  hooks.beforeConsent.push(handler);
}

/**
 * Register an afterCapture hook
 * Called after every successful capture
 */
function afterCapture(handler) {
  hooks.afterCapture.push(handler);
}

/**
 * Register an onRiskDetected hook
 * Called when high-risk patterns are found
 */
function onRiskDetected(handler) {
  hooks.onRiskDetected.push(handler);
}

/**
 * Programmatic capture (for framework integration)
 */
async function captureAgreement(options) {
  const { text, url, merchant, consentType, element, screenshot, action } = options;

  // Run beforeConsent hooks
  for (const hook of hooks.beforeConsent) {
    try {
      const result = await hook({ text, url, merchant }, { element });
      if (result && result.proceed === false) {
        return { blocked: true, reason: result.reason };
      }
    } catch (e) {}
  }

  const agentId = process.env.RECEIPTS_AGENT_ID || 'openclaw-agent';
  const documentHash = crypto.createHash('sha256').update(text).digest('hex');

  // Check for duplicates
  const duplicate = checkDuplicate(documentHash);
  if (duplicate) {
    return { ...duplicate, isDuplicate: true };
  }

  // Analyze
  const riskFlags = detectRiskFlagsWithCustom(text);
  const consentFlags = detectConsentType(text);
  const allFlags = [...riskFlags, ...consentFlags];
  const trustScore = Math.max(0, 100 - (allFlags.length * 15));
  const recommendation = getRecommendation(allFlags, consentFlags);

  const capture = {
    captureId: `local_${documentHash.slice(0, 16)}`,
    recommendation,
    trustScore,
    riskFlags: allFlags,
    summary: generateSummary(allFlags, trustScore, consentType || detectImplicitConsentType(text)),
    documentHash,
    sourceUrl: url || 'unknown',
    merchantName: merchant || 'Unknown Merchant',
    agentId,
    timestamp: new Date().toISOString(),
    documentLength: text.length,
    version: VERSION,
    consentProof: {
      type: consentType || detectImplicitConsentType(text),
      capturedAt: new Date().toISOString(),
      elementSelector: element || null,
      screenshotHash: screenshot ? crypto.createHash('sha256').update(screenshot).digest('hex') : null,
      agentAction: action || 'programmatic_capture',
    },
    disclaimer: 'RECEIPTS flags known problematic patterns only. Not a substitute for legal review.',
  };

  // Save
  saveLocalReceipt(capture, text);
  updateIndex(capture);

  // Run afterCapture hooks
  for (const hook of hooks.afterCapture) {
    try { await hook(capture); } catch (e) {}
  }

  // Run onRiskDetected hooks if high risk
  if (recommendation === 'block' || allFlags.length >= 2) {
    for (const hook of hooks.onRiskDetected) {
      try { await hook(capture, allFlags); } catch (e) {}
    }
  }

  return capture;
}

/**
 * Programmatic promise capture (for agent-to-agent)
 */
async function capturePromise(options) {
  const { text, counterparty, direction, channel } = options;
  const agentId = process.env.RECEIPTS_AGENT_ID || 'openclaw-agent';

  const commitmentHash = crypto
    .createHash('sha256')
    .update(`${text}|${counterparty}|${agentId}|${Date.now()}`)
    .digest('hex');

  const riskFlags = detectCommitmentRisks(text);

  const promise = {
    promiseId: `promise_${commitmentHash.slice(0, 16)}`,
    type: 'agent_commitment',
    direction: direction || 'outbound',
    commitmentText: text,
    counterparty,
    channel: channel || 'api',
    agentId,
    timestamp: new Date().toISOString(),
    commitmentHash,
    riskFlags,
    riskLevel: riskFlags.length >= 2 ? 'high' : riskFlags.length === 1 ? 'medium' : 'low',
    version: VERSION,
  };

  savePromise(promise, text);
  updateIndex(promise);

  return promise;
}

// === IDENTITY MODULE v0.6.0 ===
// Self-Sovereign Agent Identity with Ed25519 signatures

/**
 * Encode buffer to base58btc
 */
function base58btcEncode(buffer) {
  if (buffer.length === 0) return '';

  // Convert to BigInt
  let num = BigInt('0x' + buffer.toString('hex'));
  let encoded = '';

  while (num > 0n) {
    encoded = BASE58_ALPHABET[Number(num % 58n)] + encoded;
    num = num / 58n;
  }

  // Handle leading zeros
  for (let i = 0; i < buffer.length && buffer[i] === 0; i++) {
    encoded = '1' + encoded;
  }

  return encoded;
}

/**
 * Decode base58btc to buffer
 */
function base58btcDecode(str) {
  if (str.length === 0) return Buffer.alloc(0);

  let num = 0n;
  for (const char of str) {
    const index = BASE58_ALPHABET.indexOf(char);
    if (index === -1) throw new Error(`Invalid base58 character: ${char}`);
    num = num * 58n + BigInt(index);
  }

  // Convert to hex and then buffer
  let hex = num.toString(16);
  if (hex.length % 2) hex = '0' + hex;

  // Handle leading zeros (leading '1's in base58)
  let leadingZeros = 0;
  for (const char of str) {
    if (char === '1') leadingZeros++;
    else break;
  }

  const buffer = Buffer.from(hex, 'hex');
  if (leadingZeros > 0) {
    return Buffer.concat([Buffer.alloc(leadingZeros), buffer]);
  }
  return buffer;
}

/**
 * Generate Ed25519 keypair
 */
function generateEd25519Keypair() {
  const { publicKey, privateKey } = crypto.generateKeyPairSync('ed25519', {
    publicKeyEncoding: { type: 'spki', format: 'der' },
    privateKeyEncoding: { type: 'pkcs8', format: 'der' }
  });

  // Multibase format: z prefix = base58btc
  const publicKeyMultibase = 'z' + base58btcEncode(publicKey);
  const keyId = `#key-${Date.now()}`;

  return {
    publicKey,
    privateKey,
    publicKeyMultibase,
    keyId,
    createdAt: new Date().toISOString()
  };
}

/**
 * Generate DID document with fresh keypair
 */
function generateDIDDocument(namespace, identifier, controllerConfig) {
  const keypair = generateEd25519Keypair();
  const did = `did:${DID_METHOD}:${namespace}:${identifier}`;

  const document = {
    "@context": [
      "https://www.w3.org/ns/did/v1",
      "https://receipts.remaster.xyz/did/v1"
    ],
    id: did,

    verificationMethod: [{
      id: `${did}${keypair.keyId}`,
      type: "Ed25519VerificationKey2020",
      controller: did,
      publicKeyMultibase: keypair.publicKeyMultibase
    }],

    authentication: [`${did}${keypair.keyId}`],
    assertionMethod: [`${did}${keypair.keyId}`],

    keyHistory: [{
      keyId: keypair.keyId,
      activatedAt: keypair.createdAt,
      rotatedAt: null,
      rotationProof: null,
      publicKeyMultibase: keypair.publicKeyMultibase
    }],

    controller: controllerConfig || null,

    service: [{
      id: `${did}#receipts`,
      type: "RECEIPTSGuard",
      serviceEndpoint: `local://${RECEIPTS_DIR}`,
      version: VERSION
    }],

    created: keypair.createdAt,
    updated: keypair.createdAt
  };

  return { document, keypair };
}

/**
 * Load local DID document
 */
function loadLocalDID() {
  if (!fs.existsSync(DID_FILE)) return null;
  try {
    return JSON.parse(fs.readFileSync(DID_FILE, 'utf8'));
  } catch (e) {
    return null;
  }
}

/**
 * Load current private key
 */
function loadPrivateKey() {
  const keyFile = path.join(PRIVATE_KEY_DIR, 'key-current.json');
  if (!fs.existsSync(keyFile)) return null;
  try {
    return JSON.parse(fs.readFileSync(keyFile, 'utf8'));
  } catch (e) {
    return null;
  }
}

/**
 * Sign terms with Ed25519 private key
 */
function signTermsWithDID(termsHash, privateKeyDer) {
  const timestamp = Date.now();
  const message = Buffer.from(`${termsHash}|${timestamp}`);

  const privateKey = crypto.createPrivateKey({
    key: privateKeyDer,
    format: 'der',
    type: 'pkcs8'
  });

  const signature = crypto.sign(null, message, privateKey);
  const signatureBase64 = signature.toString('base64url');

  return `ed25519:${signatureBase64}:${timestamp}`;
}

/**
 * Verify Ed25519 signature against DID document
 */
function verifySignatureWithDID(termsHash, signature, didDocument) {
  if (!signature || !didDocument) {
    return { valid: false, error: 'Missing signature or DID document' };
  }

  // Parse signature
  const parts = signature.split(':');
  if (parts.length !== 3 || parts[0] !== 'ed25519') {
    return { valid: false, error: 'Invalid Ed25519 signature format' };
  }

  const [, signatureBase64, timestamp] = parts;
  const message = Buffer.from(`${termsHash}|${timestamp}`);
  const signatureBuffer = Buffer.from(signatureBase64, 'base64url');

  // Get public key from DID document (try current key first)
  const verificationMethod = didDocument.verificationMethod[0];
  if (!verificationMethod) {
    return { valid: false, error: 'No verification method in DID document' };
  }

  try {
    const publicKeyDer = base58btcDecode(
      verificationMethod.publicKeyMultibase.slice(1) // Remove 'z' prefix
    );

    const publicKey = crypto.createPublicKey({
      key: publicKeyDer,
      format: 'der',
      type: 'spki'
    });

    const valid = crypto.verify(null, message, publicKey, signatureBuffer);
    return {
      valid,
      timestamp: parseInt(timestamp),
      keyId: verificationMethod.id
    };
  } catch (e) {
    return { valid: false, error: e.message };
  }
}

/**
 * Verify signature with key history (for old signatures after rotation)
 */
function verifySignatureWithHistory(termsHash, signature, didDocument, signatureTimestamp) {
  // First try current key
  const result = verifySignatureWithDID(termsHash, signature, didDocument);
  if (result.valid) return result;

  // Find key that was active at signature time
  const sigTime = new Date(signatureTimestamp);

  for (const keyEntry of didDocument.keyHistory) {
    const activatedAt = new Date(keyEntry.activatedAt);
    const rotatedAt = keyEntry.rotatedAt ? new Date(keyEntry.rotatedAt) : null;

    // Check if this key was active at signature time
    if (sigTime >= activatedAt && (!rotatedAt || sigTime < rotatedAt)) {
      // Find verification method for this key
      const vm = didDocument.verificationMethod.find(
        v => v.id.endsWith(keyEntry.keyId)
      );

      if (vm) {
        try {
          const publicKeyDer = base58btcDecode(vm.publicKeyMultibase.slice(1));
          const publicKey = crypto.createPublicKey({
            key: publicKeyDer,
            format: 'der',
            type: 'spki'
          });

          const parts = signature.split(':');
          const signatureBuffer = Buffer.from(parts[1], 'base64url');
          const message = Buffer.from(`${termsHash}|${parts[2]}`);

          const valid = crypto.verify(null, message, publicKey, signatureBuffer);
          if (valid) {
            return { valid: true, timestamp: parseInt(parts[2]), keyId: vm.id, historical: true };
          }
        } catch (e) {
          // Continue to next key
        }
      }
    }
  }

  return { valid: false, error: 'No valid key found for signature timestamp' };
}

/**
 * Resolve DID (local only for now)
 */
function resolveDID(didId) {
  // For local DIDs, check if it matches our identity
  const localDID = loadLocalDID();
  if (localDID && localDID.id === didId) {
    return localDID;
  }

  // Future: resolve from network/registry
  return null;
}

// === IDENTITY CLI COMMANDS ===

/**
 * Identity command router
 */
function handleIdentity(args) {
  const subCommand = args[0];

  switch (subCommand) {
    case 'init':
      handleIdentityInit(args.slice(1));
      break;
    case 'show':
      handleIdentityShow(args.slice(1));
      break;
    case 'rotate':
      handleIdentityRotate(args.slice(1));
      break;
    case 'verify':
      handleIdentityVerify(args.slice(1));
      break;
    case 'set-controller':
      handleIdentitySetController(args.slice(1));
      break;
    case 'verify-controller':
      handleIdentityVerifyController(args.slice(1));
      break;
    case 'recover':
      handleIdentityRecover(args.slice(1));
      break;
    case 'publish':
      handleIdentityPublish(args.slice(1));
      break;
    case 'export':
      handleIdentityExport(args.slice(1));
      break;
    case 'resolve':
      handleIdentityResolve(args.slice(1));
      break;
    case 'anchor':
      handleIdentityAnchor(args.slice(1));
      break;
    default:
      showIdentityHelp();
  }
}

/**
 * Initialize identity
 */
function handleIdentityInit(args) {
  const filters = parseFilters(args);

  // Check if identity already exists
  if (fs.existsSync(DID_FILE)) {
    const existingDID = loadLocalDID();
    console.log(JSON.stringify({
      error: 'Identity already exists',
      did: existingDID?.id,
      hint: 'Use "identity rotate" to rotate keys or "identity show" to view',
    }, null, 2));
    process.exit(1);
  }

  // Get configuration
  const namespace = filters.namespace ||
    process.env.RECEIPTS_NAMESPACE ||
    'local';
  const identifier = filters.name ||
    process.env.RECEIPTS_AGENT_ID ||
    `agent-${crypto.randomBytes(4).toString('hex')}`;

  // Controller configuration
  let controllerConfig = null;
  if (filters['controller-twitter']) {
    controllerConfig = {
      type: 'human',
      platform: 'twitter',
      handle: filters['controller-twitter'],
      verificationUrl: null,
      linkedAt: new Date().toISOString()
    };
  }

  // Generate DID document and keypair
  const { document, keypair } = generateDIDDocument(
    namespace,
    identifier,
    controllerConfig
  );

  // Create directory structure with restricted permissions for sensitive dirs
  ensureDir(IDENTITY_DIR);
  ensureDir(PRIVATE_KEY_DIR, true);    // Restricted: 700
  ensureDir(KEY_ARCHIVE_DIR, true);    // Restricted: 700
  ensureDir(RECOVERY_DIR, true);       // Restricted: 700

  // Save DID document (public)
  fs.writeFileSync(DID_FILE, JSON.stringify(document, null, 2));

  // Save private key with restricted permissions
  const privateKeyData = {
    keyId: keypair.keyId,
    privateKey: keypair.privateKey.toString('base64'),
    publicKeyMultibase: keypair.publicKeyMultibase,
    createdAt: keypair.createdAt,
    encrypted: false
  };

  const keyFilePath = path.join(PRIVATE_KEY_DIR, 'key-current.json');
  fs.writeFileSync(keyFilePath, JSON.stringify(privateKeyData, null, 2));
  try {
    fs.chmodSync(keyFilePath, 0o600); // Owner read/write only
  } catch (e) {
    // Windows doesn't support chmod, continue anyway
  }

  // Initialize key history
  fs.writeFileSync(KEY_HISTORY_FILE, JSON.stringify({
    did: document.id,
    keys: document.keyHistory,
    rotations: []
  }, null, 2));

  // Save controller config
  if (controllerConfig) {
    fs.writeFileSync(CONTROLLER_FILE, JSON.stringify(controllerConfig, null, 2));
  }

  console.log(JSON.stringify({
    success: true,
    did: document.id,
    keyId: keypair.keyId,
    publicKeyMultibase: keypair.publicKeyMultibase,
    controller: controllerConfig,
    message: 'Identity initialized successfully',
    nextSteps: controllerConfig
      ? [
          `Verify controller: Post your DID to ${controllerConfig.platform}`,
          `Publish identity: node capture.js identity publish`
        ]
      : [
          'Add a human controller: node capture.js identity set-controller --twitter=@handle',
          'Publish identity: node capture.js identity publish'
        ],
    version: VERSION
  }, null, 2));
}

/**
 * Show identity
 */
function handleIdentityShow(args) {
  const filters = parseFilters(args);
  const full = filters.full === true || filters.full === 'true';

  const didDocument = loadLocalDID();
  if (!didDocument) {
    console.log(JSON.stringify({
      error: 'No identity found',
      hint: 'Run "identity init" to create one'
    }, null, 2));
    process.exit(1);
  }

  if (full) {
    // Show full DID document
    console.log(JSON.stringify(didDocument, null, 2));
  } else {
    // Show summary
    const keyHistory = didDocument.keyHistory || [];
    const currentKeyId = didDocument.authentication?.[0]?.split('#')[1] || keyHistory[0]?.keyId;

    console.log(JSON.stringify({
      did: didDocument.id,
      currentKeyId: currentKeyId,
      publicKeyMultibase: didDocument.verificationMethod?.[0]?.publicKeyMultibase?.slice(0, 30) + '...',
      controller: didDocument.controller,
      keyRotations: keyHistory.filter(k => k.rotatedAt).length,
      created: didDocument.created,
      updated: didDocument.updated,
      version: VERSION
    }, null, 2));
  }
}

/**
 * Rotate keys
 */
function handleIdentityRotate(args) {
  const filters = parseFilters(args);
  const reason = filters.reason || 'scheduled_rotation';

  // Load current identity
  const didDocument = loadLocalDID();
  if (!didDocument) {
    console.error(JSON.stringify({
      error: 'No identity found',
      hint: 'Run "identity init" first'
    }));
    process.exit(1);
  }

  const currentKeyData = loadPrivateKey();
  if (!currentKeyData) {
    console.error(JSON.stringify({
      error: 'No private key found',
      hint: 'Identity may be corrupted. Consider recovery.'
    }));
    process.exit(1);
  }

  // Generate new keypair
  const newKeypair = generateEd25519Keypair();

  // Create rotation proof (old key signs new key)
  const rotationData = {
    previousKeyId: currentKeyData.keyId,
    newKeyId: newKeypair.keyId,
    newPublicKeyMultibase: newKeypair.publicKeyMultibase,
    reason,
    rotatedAt: new Date().toISOString()
  };

  const rotationMessage = Buffer.from(JSON.stringify(rotationData));
  const oldPrivateKey = crypto.createPrivateKey({
    key: Buffer.from(currentKeyData.privateKey, 'base64'),
    format: 'der',
    type: 'pkcs8'
  });

  const rotationSignature = crypto.sign(null, rotationMessage, oldPrivateKey);
  const rotationProof = {
    ...rotationData,
    proof: {
      type: 'Ed25519Signature2020',
      created: rotationData.rotatedAt,
      verificationMethod: `${didDocument.id}${currentKeyData.keyId}`,
      proofValue: rotationSignature.toString('base64url')
    }
  };

  // Archive old key with restricted permissions
  const archiveFilePath = path.join(KEY_ARCHIVE_DIR, `${currentKeyData.keyId.replace('#', '')}.json`);
  fs.writeFileSync(
    archiveFilePath,
    JSON.stringify({
      ...currentKeyData,
      archivedAt: rotationData.rotatedAt,
      rotatedTo: newKeypair.keyId
    }, null, 2)
  );
  try {
    fs.chmodSync(archiveFilePath, 0o600); // Owner read/write only
  } catch (e) {}

  // Update DID document
  const newVerificationMethod = {
    id: `${didDocument.id}${newKeypair.keyId}`,
    type: "Ed25519VerificationKey2020",
    controller: didDocument.id,
    publicKeyMultibase: newKeypair.publicKeyMultibase
  };

  // Keep old keys for signature verification, prepend new key
  didDocument.verificationMethod.unshift(newVerificationMethod);
  didDocument.authentication = [`${didDocument.id}${newKeypair.keyId}`];
  didDocument.assertionMethod = [`${didDocument.id}${newKeypair.keyId}`];

  // Update key history
  const oldKeyEntry = didDocument.keyHistory.find(k => k.keyId === currentKeyData.keyId);
  if (oldKeyEntry) {
    oldKeyEntry.rotatedAt = rotationData.rotatedAt;
    oldKeyEntry.rotationProof = rotationProof.proof.proofValue;
  }

  didDocument.keyHistory.unshift({
    keyId: newKeypair.keyId,
    activatedAt: rotationData.rotatedAt,
    rotatedAt: null,
    rotationProof: null,
    publicKeyMultibase: newKeypair.publicKeyMultibase,
    previousKeyId: currentKeyData.keyId
  });

  didDocument.updated = rotationData.rotatedAt;

  // Save updates
  fs.writeFileSync(DID_FILE, JSON.stringify(didDocument, null, 2));

  const newKeyData = {
    keyId: newKeypair.keyId,
    privateKey: newKeypair.privateKey.toString('base64'),
    publicKeyMultibase: newKeypair.publicKeyMultibase,
    createdAt: newKeypair.createdAt,
    encrypted: false
  };

  const keyFilePath = path.join(PRIVATE_KEY_DIR, 'key-current.json');
  fs.writeFileSync(keyFilePath, JSON.stringify(newKeyData, null, 2));
  try {
    fs.chmodSync(keyFilePath, 0o600);
  } catch (e) {}

  // Update key history file
  const keyHistoryFile = fs.existsSync(KEY_HISTORY_FILE)
    ? JSON.parse(fs.readFileSync(KEY_HISTORY_FILE, 'utf8'))
    : { did: didDocument.id, keys: [], rotations: [] };
  keyHistoryFile.keys = didDocument.keyHistory;
  keyHistoryFile.rotations.push(rotationProof);
  fs.writeFileSync(KEY_HISTORY_FILE, JSON.stringify(keyHistoryFile, null, 2));

  console.log(JSON.stringify({
    success: true,
    did: didDocument.id,
    previousKeyId: currentKeyData.keyId,
    newKeyId: newKeypair.keyId,
    reason,
    rotationProof: rotationProof.proof,
    message: 'Key rotated successfully. Old key archived for signature verification.',
    chainIntegrity: 'verified',
    version: VERSION
  }, null, 2));
}

/**
 * Verify identity or signature
 */
function handleIdentityVerify(args) {
  const filters = parseFilters(args);

  // Signature verification takes priority if provided
  if (filters.signature && filters.termsHash) {
    // Verify a signature
    const termsHash = filters.termsHash.replace('sha256:', '');
    const didId = filters.did;

    let didDocument;
    if (didId) {
      didDocument = resolveDID(didId);
    } else {
      didDocument = loadLocalDID();
    }

    if (!didDocument) {
      console.error(JSON.stringify({ error: 'Could not resolve DID document' }));
      process.exit(1);
    }

    // Check signature format
    if (filters.signature.startsWith('ed25519:')) {
      const result = verifySignatureWithDID(termsHash, filters.signature, didDocument);
      console.log(JSON.stringify({
        ...result,
        did: didDocument.id,
        termsHash: filters.termsHash,
        signatureType: 'ed25519'
      }, null, 2));
    } else if (filters.signature.startsWith('sig:')) {
      // Legacy signature
      const legacyId = didDocument.id.split(':').pop();
      const valid = verifySignature(termsHash, filters.signature, legacyId);
      console.log(JSON.stringify({
        valid,
        did: didDocument.id,
        termsHash: filters.termsHash,
        signatureType: 'legacy_hmac'
      }, null, 2));
    } else {
      console.error(JSON.stringify({ error: 'Unknown signature format' }));
      process.exit(1);
    }
    return;
  }

  // DID verification (when no signature provided)
  if (filters.did) {
    const didDocument = resolveDID(filters.did);
    if (!didDocument) {
      console.log(JSON.stringify({
        valid: false,
        did: filters.did,
        error: 'Could not resolve DID'
      }, null, 2));
      return;
    }

    // Verify key chain integrity
    const keyHistory = didDocument.keyHistory || [];
    const issues = [];

    for (let i = 0; i < keyHistory.length - 1; i++) {
      const current = keyHistory[i];
      const previous = keyHistory[i + 1];

      if (current.previousKeyId && current.previousKeyId !== previous.keyId) {
        issues.push({
          type: 'chain_break',
          at: current.keyId,
          expected: current.previousKeyId,
          found: previous.keyId
        });
      }
    }

    console.log(JSON.stringify({
      valid: issues.length === 0,
      did: filters.did,
      keyCount: didDocument.verificationMethod?.length || 0,
      rotationCount: keyHistory.filter(k => k.rotatedAt).length,
      currentKeyId: didDocument.authentication?.[0],
      controller: didDocument.controller,
      issues: issues.length > 0 ? issues : undefined
    }, null, 2));
    return;
  }

  console.error(JSON.stringify({
    error: 'Missing required parameters',
    usage: [
      'node capture.js identity verify --did=did:agent:...',
      'node capture.js identity verify --signature=ed25519:... --termsHash=sha256:...'
    ]
  }));
  process.exit(1);
}

/**
 * Set human controller
 */
function handleIdentitySetController(args) {
  const filters = parseFilters(args);

  if (!filters.twitter && !filters.github && !filters.farcaster) {
    console.error(JSON.stringify({
      error: 'Controller platform required',
      usage: 'node capture.js identity set-controller --twitter=@handle'
    }));
    process.exit(1);
  }

  const didDocument = loadLocalDID();
  if (!didDocument) {
    console.error(JSON.stringify({ error: 'No local identity found' }));
    process.exit(1);
  }

  // Determine platform and handle
  let platform, handle;
  if (filters.twitter) {
    platform = 'twitter';
    handle = filters.twitter;
  } else if (filters.github) {
    platform = 'github';
    handle = filters.github;
  } else if (filters.farcaster) {
    platform = 'farcaster';
    handle = filters.farcaster;
  }

  const controllerConfig = {
    type: 'human',
    platform,
    handle,
    verificationUrl: null,
    linkedAt: new Date().toISOString()
  };

  // Update DID document
  didDocument.controller = controllerConfig;
  didDocument.updated = new Date().toISOString();
  fs.writeFileSync(DID_FILE, JSON.stringify(didDocument, null, 2));

  // Save controller config
  fs.writeFileSync(CONTROLLER_FILE, JSON.stringify(controllerConfig, null, 2));

  // Generate verification challenge
  const challenge = crypto.randomBytes(16).toString('hex');
  const verificationMessage = `I am the human controller of ${didDocument.id}\n\nChallenge: ${challenge}\n\n#RECEIPTS #AgentIdentity`;

  console.log(JSON.stringify({
    success: true,
    controller: controllerConfig,
    verificationRequired: true,
    verificationInstructions: {
      step1: `Post this message to your ${platform} account:`,
      message: verificationMessage,
      step2: `Then run: node capture.js identity verify-controller --url=<POST_URL>`,
      challenge
    }
  }, null, 2));
}

/**
 * Verify controller post
 */
function handleIdentityVerifyController(args) {
  const filters = parseFilters(args);

  if (!filters.url) {
    console.error(JSON.stringify({
      error: 'Verification URL required',
      usage: 'node capture.js identity verify-controller --url=https://twitter.com/...'
    }));
    process.exit(1);
  }

  const didDocument = loadLocalDID();
  if (!didDocument || !didDocument.controller) {
    console.error(JSON.stringify({
      error: 'No controller configured',
      hint: 'Run "identity set-controller" first'
    }));
    process.exit(1);
  }

  // Update controller with verification URL
  didDocument.controller.verificationUrl = filters.url;
  didDocument.controller.verifiedAt = new Date().toISOString();
  didDocument.updated = new Date().toISOString();

  fs.writeFileSync(DID_FILE, JSON.stringify(didDocument, null, 2));
  fs.writeFileSync(CONTROLLER_FILE, JSON.stringify(didDocument.controller, null, 2));

  console.log(JSON.stringify({
    success: true,
    controller: didDocument.controller,
    message: 'Controller verification recorded. Manual verification recommended.',
    note: 'In production, this would verify the post content automatically.'
  }, null, 2));
}

/**
 * Recover identity using controller
 */
function handleIdentityRecover(args) {
  const filters = parseFilters(args);

  if (!filters['controller-proof']) {
    console.error(JSON.stringify({
      error: 'Recovery proof required',
      usage: 'node capture.js identity recover --controller-proof=<TWITTER_URL>',
      note: 'Human controller must post recovery authorization'
    }));
    process.exit(1);
  }

  const didDocument = loadLocalDID();
  if (!didDocument || !didDocument.controller) {
    console.error(JSON.stringify({
      error: 'No identity with controller found',
      hint: 'Recovery requires a previously configured human controller'
    }));
    process.exit(1);
  }

  if (!filters.confirm) {
    console.log(JSON.stringify({
      status: 'recovery_pending',
      controller: didDocument.controller,
      proofUrl: filters['controller-proof'],
      warning: 'This will generate new keys and revoke all existing keys',
      nextStep: 'Confirm recovery: node capture.js identity recover --controller-proof=<URL> --confirm'
    }, null, 2));
    return;
  }

  // Generate new keypair for recovery
  const newKeypair = generateEd25519Keypair();

  // Create recovery record
  const recoveryRecord = {
    type: 'controller_recovery',
    did: didDocument.id,
    controller: didDocument.controller,
    proofUrl: filters['controller-proof'],
    previousKeyId: didDocument.authentication?.[0],
    newKeyId: newKeypair.keyId,
    recoveredAt: new Date().toISOString()
  };

  // Update DID document - replace all keys
  didDocument.verificationMethod = [{
    id: `${didDocument.id}${newKeypair.keyId}`,
    type: "Ed25519VerificationKey2020",
    controller: didDocument.id,
    publicKeyMultibase: newKeypair.publicKeyMultibase
  }];

  didDocument.authentication = [`${didDocument.id}${newKeypair.keyId}`];
  didDocument.assertionMethod = [`${didDocument.id}${newKeypair.keyId}`];

  // Mark all old keys as revoked
  const revokedKeys = [];
  for (const key of didDocument.keyHistory) {
    if (!key.revokedAt) {
      key.revokedAt = recoveryRecord.recoveredAt;
      key.revocationReason = 'controller_recovery';
      revokedKeys.push(key.keyId);
    }
  }

  // Add new key to history
  didDocument.keyHistory.unshift({
    keyId: newKeypair.keyId,
    activatedAt: recoveryRecord.recoveredAt,
    rotatedAt: null,
    rotationProof: null,
    publicKeyMultibase: newKeypair.publicKeyMultibase,
    activationMethod: 'controller_recovery'
  });

  didDocument.updated = recoveryRecord.recoveredAt;

  // Save everything
  fs.writeFileSync(DID_FILE, JSON.stringify(didDocument, null, 2));

  const newKeyData = {
    keyId: newKeypair.keyId,
    privateKey: newKeypair.privateKey.toString('base64'),
    publicKeyMultibase: newKeypair.publicKeyMultibase,
    createdAt: newKeypair.createdAt,
    encrypted: false
  };

  const keyFilePath = path.join(PRIVATE_KEY_DIR, 'key-current.json');
  fs.writeFileSync(keyFilePath, JSON.stringify(newKeyData, null, 2));
  try { fs.chmodSync(keyFilePath, 0o600); } catch (e) {}

  // Save recovery record
  fs.writeFileSync(
    path.join(RECOVERY_DIR, `recovery-${Date.now()}.json`),
    JSON.stringify(recoveryRecord, null, 2)
  );

  console.log(JSON.stringify({
    success: true,
    recoveryComplete: true,
    did: didDocument.id,
    newKeyId: newKeypair.keyId,
    revokedKeys,
    message: 'Identity recovered. All previous keys revoked. Publish updated DID document.',
    version: VERSION
  }, null, 2));
}

/**
 * Publish identity
 */
function handleIdentityPublish(args) {
  const filters = parseFilters(args);
  const platform = filters.platform || 'local';

  const didDocument = loadLocalDID();
  if (!didDocument) {
    console.error(JSON.stringify({ error: 'No local identity found' }));
    process.exit(1);
  }

  switch (platform) {
    case 'moltbook':
      const moltbookKey = process.env.RECEIPTS_MOLTBOOK_KEY;
      console.log(JSON.stringify({
        status: moltbookKey ? 'ready' : 'manual',
        platform: 'moltbook',
        did: didDocument.id,
        suggestedPost: `🪪 IDENTITY: ${didDocument.id}\n\nPublic Key: ${didDocument.verificationMethod[0].publicKeyMultibase.slice(0, 30)}...\nController: ${didDocument.controller?.handle || 'none'}\n\n#RECEIPTS #DID #AgentIdentity`,
        instructions: moltbookKey ? 'Will post automatically' : 'Set RECEIPTS_MOLTBOOK_KEY to auto-post'
      }, null, 2));
      break;

    case 'ipfs':
      // Future: pin to IPFS
      console.log(JSON.stringify({
        status: 'not_implemented',
        platform: 'ipfs',
        message: 'IPFS publishing coming in future version'
      }, null, 2));
      break;

    case 'local':
    default:
      console.log(JSON.stringify({
        platform: 'local',
        did: didDocument.id,
        document: didDocument,
        exportPath: DID_FILE,
        message: 'DID document ready. Host at well-known URL for remote resolution.'
      }, null, 2));
  }
}

/**
 * Export identity
 */
function handleIdentityExport(args) {
  const filters = parseFilters(args);

  const didDocument = loadLocalDID();
  if (!didDocument) {
    console.error(JSON.stringify({ error: 'No local identity found' }));
    process.exit(1);
  }

  // Export public DID document only (never private keys)
  console.log(JSON.stringify(didDocument, null, 2));
}

// === ERC-8004 CHAIN INTEGRATION (v0.7.0) ===

/**
 * Anchor identity to ERC-8004 registry on-chain
 */
async function handleIdentityAnchor(args) {
  const filters = parseFilters(args);
  const chain = filters.chain || 'sepolia'; // Default to testnet for safety

  const didDocument = loadLocalDID();
  if (!didDocument) {
    console.error(JSON.stringify({ error: 'No local identity found. Run "identity init" first.' }));
    process.exit(1);
  }

  const chainConfig = CHAIN_CONFIG[chain];
  if (!chainConfig) {
    console.error(JSON.stringify({
      error: 'Invalid chain',
      chain,
      validChains: Object.keys(CHAIN_CONFIG)
    }));
    process.exit(1);
  }

  if (!chainConfig.identityRegistry) {
    console.error(JSON.stringify({
      error: `ERC-8004 Identity Registry not deployed on ${chain} yet`,
      chain,
      suggestion: 'Use "sepolia" for testing or "ethereum" for mainnet'
    }));
    process.exit(1);
  }

  // Check for private key (required for signing transactions)
  const privateKey = process.env.RECEIPTS_WALLET_PRIVATE_KEY;
  if (!privateKey) {
    console.error(JSON.stringify({
      error: 'Wallet private key required for on-chain registration',
      hint: 'Set RECEIPTS_WALLET_PRIVATE_KEY environment variable',
      warning: 'Never commit private keys to code. Use environment variables or secrets manager.'
    }));
    process.exit(1);
  }

  try {
    // Connect to chain
    const provider = new ethers.JsonRpcProvider(chainConfig.rpc);
    const wallet = new ethers.Wallet(privateKey, provider);

    // Check balance
    const balance = await provider.getBalance(wallet.address);
    const balanceEth = ethers.formatEther(balance);

    if (balance === 0n) {
      console.error(JSON.stringify({
        error: 'Wallet has no funds',
        address: wallet.address,
        chain: chainConfig.name,
        hint: chain === 'sepolia' ? 'Get testnet ETH from a faucet' : 'Fund wallet with ETH for gas'
      }));
      process.exit(1);
    }

    // Create contract instance
    const identityRegistry = new ethers.Contract(
      chainConfig.identityRegistry,
      IDENTITY_REGISTRY_ABI,
      wallet
    );

    // Prepare agent URI (DID document location)
    // For now, use a local placeholder - in production this would be IPFS or hosted URL
    const agentURI = didDocument.service?.[0]?.serviceEndpoint ||
      `local://${DID_FILE}`;

    console.log(JSON.stringify({
      status: 'registering',
      chain: chainConfig.name,
      chainId: chainConfig.chainId,
      wallet: wallet.address,
      balance: `${balanceEth} ETH`,
      registry: chainConfig.identityRegistry,
      did: didDocument.id,
      agentURI
    }, null, 2));

    // Register agent
    const tx = await identityRegistry.register(agentURI);
    console.log(JSON.stringify({
      status: 'pending',
      transactionHash: tx.hash,
      explorer: `${chainConfig.explorer}/tx/${tx.hash}`
    }, null, 2));

    // Wait for confirmation
    const receipt = await tx.wait();

    // Extract agentId from Transfer event
    let agentNftId = null;
    for (const log of receipt.logs) {
      try {
        const parsed = identityRegistry.interface.parseLog(log);
        if (parsed?.name === 'Transfer') {
          agentNftId = parsed.args.tokenId.toString();
          break;
        }
      } catch (e) {
        // Not our event, continue
      }
    }

    // Update local DID document with anchor
    didDocument.anchors = didDocument.anchors || {};
    didDocument.anchors[chain] = {
      chainId: chainConfig.chainId,
      registryAddress: chainConfig.identityRegistry,
      transactionHash: receipt.hash,
      blockNumber: receipt.blockNumber,
      agentNftId,
      registeredAt: new Date().toISOString(),
      walletAddress: wallet.address
    };
    didDocument.updated = new Date().toISOString();

    // Save updated DID document
    fs.writeFileSync(DID_FILE, JSON.stringify(didDocument, null, 2));

    console.log(JSON.stringify({
      status: 'success',
      chain: chainConfig.name,
      did: didDocument.id,
      agentNftId,
      transactionHash: receipt.hash,
      blockNumber: receipt.blockNumber,
      explorer: `${chainConfig.explorer}/tx/${receipt.hash}`,
      gasUsed: receipt.gasUsed.toString(),
      message: `Identity anchored to ERC-8004 registry on ${chainConfig.name}`
    }, null, 2));

  } catch (error) {
    console.error(JSON.stringify({
      error: 'Chain registration failed',
      message: error.message,
      chain: chainConfig.name,
      hint: error.message.includes('insufficient funds')
        ? 'Fund wallet with ETH for gas'
        : 'Check RPC endpoint and contract address'
    }));
    process.exit(1);
  }
}

/**
 * Resolve DID from ERC-8004 registry or local
 */
async function handleIdentityResolve(args) {
  const filters = parseFilters(args);
  const didId = filters.did;
  const chain = filters.chain;

  if (!didId) {
    console.error(JSON.stringify({
      error: 'DID required',
      usage: 'identity resolve --did=did:agent:namespace:name [--chain=ethereum|base|sepolia]'
    }));
    process.exit(1);
  }

  // First, try local resolution
  const localDID = loadLocalDID();
  if (localDID && localDID.id === didId) {
    console.log(JSON.stringify({
      resolved: true,
      source: 'local',
      did: localDID.id,
      document: localDID,
      anchors: localDID.anchors || null
    }, null, 2));
    return;
  }

  // If chain specified, try on-chain resolution
  if (chain) {
    const chainConfig = CHAIN_CONFIG[chain];
    if (!chainConfig || !chainConfig.identityRegistry) {
      console.error(JSON.stringify({
        error: `Cannot resolve from ${chain}`,
        reason: chainConfig ? 'Registry not deployed' : 'Invalid chain'
      }));
      process.exit(1);
    }

    try {
      const provider = new ethers.JsonRpcProvider(chainConfig.rpc);
      const identityRegistry = new ethers.Contract(
        chainConfig.identityRegistry,
        IDENTITY_REGISTRY_ABI,
        provider
      );

      // For now, we can't resolve by DID directly - would need agentNftId
      // This is a limitation of the current ERC-8004 spec
      console.log(JSON.stringify({
        resolved: false,
        source: chain,
        did: didId,
        message: 'On-chain DID resolution requires agentNftId. Use --agent-id=N to resolve by NFT ID.',
        hint: 'Full DID resolution will be available when DID registries support reverse lookup'
      }, null, 2));

    } catch (error) {
      console.error(JSON.stringify({
        error: 'Chain resolution failed',
        message: error.message
      }));
      process.exit(1);
    }
  } else {
    // No local match, no chain specified
    console.log(JSON.stringify({
      resolved: false,
      did: didId,
      message: 'DID not found locally. Specify --chain to attempt on-chain resolution.',
      availableChains: Object.keys(CHAIN_CONFIG).filter(c => CHAIN_CONFIG[c].identityRegistry)
    }, null, 2));
  }
}

/**
 * Get chain status and configuration
 */
function getChainStatus() {
  const status = {};
  for (const [name, config] of Object.entries(CHAIN_CONFIG)) {
    status[name] = {
      chainId: config.chainId,
      identityRegistry: config.identityRegistry || 'not deployed',
      reputationRegistry: config.reputationRegistry || 'not deployed',
      rpcConfigured: !!config.rpc
    };
  }
  return status;
}

/**
 * Show identity help
 */
function showIdentityHelp() {
  console.log(JSON.stringify({
    command: 'identity',
    description: 'Self-sovereign agent identity management (v0.6.0)',
    subcommands: {
      init: {
        usage: 'identity init --namespace=X --name=Y [--controller-twitter=@handle]',
        description: 'Create new identity with Ed25519 keypair'
      },
      show: {
        usage: 'identity show [--full]',
        description: 'Display identity summary or full DID document'
      },
      rotate: {
        usage: 'identity rotate [--reason=scheduled|compromise|device_change]',
        description: 'Rotate keys with proof chain (old key signs new key)'
      },
      verify: {
        usage: 'identity verify --did=DID | --signature=SIG --termsHash=HASH',
        description: 'Verify identity or signature'
      },
      'set-controller': {
        usage: 'identity set-controller --twitter=@handle',
        description: 'Set human controller for recovery'
      },
      'verify-controller': {
        usage: 'identity verify-controller --url=URL',
        description: 'Verify controller post'
      },
      recover: {
        usage: 'identity recover --controller-proof=URL [--confirm]',
        description: 'Recover identity using human controller'
      },
      publish: {
        usage: 'identity publish [--platform=moltbook|ipfs|local]',
        description: 'Publish DID document'
      },
      export: {
        usage: 'identity export',
        description: 'Export public DID document'
      },
      anchor: {
        usage: 'identity anchor --chain=ethereum|base|sepolia',
        description: 'Anchor identity to ERC-8004 registry on-chain (v0.7.0)'
      },
      resolve: {
        usage: 'identity resolve --did=DID [--chain=CHAIN]',
        description: 'Resolve DID from local or on-chain registry (v0.7.0)'
      }
    },
    chains: getChainStatus(),
    version: VERSION
  }, null, 2));
}

/**
 * Migrate existing agreements to DID
 */
function handleMigrate(args) {
  const filters = parseFilters(args);

  if (!filters['to-did']) {
    console.error(JSON.stringify({
      error: 'Migration type required',
      usage: 'node capture.js migrate --to-did'
    }));
    process.exit(1);
  }

  const didDocument = loadLocalDID();
  if (!didDocument) {
    console.error(JSON.stringify({
      error: 'Initialize identity first',
      hint: 'Run "identity init" before migration'
    }));
    process.exit(1);
  }

  const agentId = process.env.RECEIPTS_AGENT_ID || 'openclaw-agent';
  const migrationResults = {
    agreements: { migrated: 0, skipped: 0, errors: 0 },
    proposals: { migrated: 0, skipped: 0, errors: 0 }
  };

  // Migrate agreements
  if (fs.existsSync(AGREEMENTS_DIR)) {
    const files = fs.readdirSync(AGREEMENTS_DIR).filter(f => f.endsWith('.json'));
    for (const file of files) {
      try {
        const filePath = path.join(AGREEMENTS_DIR, file);
        const agreement = JSON.parse(fs.readFileSync(filePath, 'utf8'));

        if (agreement.parties?.proposer?.did) {
          migrationResults.agreements.skipped++;
          continue;
        }

        // Add DID references
        const parties = agreement.parties || [];
        agreement.partiesLegacy = parties;
        agreement.parties = {
          proposer: parties[0] === agentId
            ? { did: didDocument.id, legacyId: agentId, keyId: didDocument.keyHistory[0]?.keyId }
            : { did: null, legacyId: parties[0], keyId: null },
          counterparty: parties[1] === agentId
            ? { did: didDocument.id, legacyId: agentId, keyId: didDocument.keyHistory[0]?.keyId }
            : { did: null, legacyId: parties[1], keyId: null }
        };

        agreement.signaturesLegacy = agreement.signatures;
        agreement.migratedToDID = true;
        agreement.migratedAt = new Date().toISOString();
        agreement.migrationVersion = VERSION;

        fs.writeFileSync(filePath, JSON.stringify(agreement, null, 2));
        migrationResults.agreements.migrated++;
      } catch (e) {
        migrationResults.agreements.errors++;
      }
    }
  }

  // Migrate proposals
  if (fs.existsSync(PROPOSALS_DIR)) {
    const files = fs.readdirSync(PROPOSALS_DIR).filter(f => f.endsWith('.json'));
    for (const file of files) {
      try {
        const filePath = path.join(PROPOSALS_DIR, file);
        const proposal = JSON.parse(fs.readFileSync(filePath, 'utf8'));

        if (proposal.proposer?.did) {
          migrationResults.proposals.skipped++;
          continue;
        }

        proposal.proposerLegacy = proposal.proposer;
        proposal.proposer = proposal.proposer === agentId
          ? { did: didDocument.id, legacyId: agentId, keyId: didDocument.keyHistory[0]?.keyId }
          : { did: null, legacyId: proposal.proposer, keyId: null };

        proposal.migratedToDID = true;
        proposal.migratedAt = new Date().toISOString();

        fs.writeFileSync(filePath, JSON.stringify(proposal, null, 2));
        migrationResults.proposals.migrated++;
      } catch (e) {
        migrationResults.proposals.errors++;
      }
    }
  }

  console.log(JSON.stringify({
    success: true,
    did: didDocument.id,
    migrationResults,
    message: 'Migration complete. Legacy data preserved for verification.',
    version: VERSION
  }, null, 2));
}

// === HTTP SERVER MODE (v0.7.0) ===
// === SECURITY HARDENING (v0.7.1) ===

// Rate limiting state
const rateLimits = new Map(); // IP -> { count, resetTime }
const RATE_LIMIT = parseInt(process.env.RECEIPTS_RATE_LIMIT) || 100; // requests per minute
const RATE_WINDOW = 60000; // 1 minute

/**
 * Check rate limit for IP
 */
function checkRateLimit(ip) {
  const now = Date.now();
  const entry = rateLimits.get(ip) || { count: 0, resetTime: now + RATE_WINDOW };

  if (now > entry.resetTime) {
    entry.count = 0;
    entry.resetTime = now + RATE_WINDOW;
  }

  entry.count++;
  rateLimits.set(ip, entry);

  return {
    allowed: entry.count <= RATE_LIMIT,
    remaining: Math.max(0, RATE_LIMIT - entry.count),
    resetAt: entry.resetTime
  };
}

/**
 * Get CORS headers based on allowed origins
 */
function getCorsHeaders(req) {
  const origin = req.headers.origin;
  const allowedOrigins = process.env.RECEIPTS_ALLOWED_ORIGINS?.split(',') || [];

  // If no allowed origins configured, block all cross-origin (secure default)
  // Unless '*' is explicitly set
  if (allowedOrigins.includes('*')) {
    return {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, X-API-Key, X-DID, X-DID-Signature, X-DID-Timestamp'
    };
  }

  if (origin && allowedOrigins.includes(origin)) {
    return {
      'Access-Control-Allow-Origin': origin,
      'Access-Control-Allow-Credentials': 'true',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, X-API-Key, X-DID, X-DID-Signature, X-DID-Timestamp'
    };
  }

  // No CORS headers = browser blocks cross-origin requests (secure default)
  return {};
}

/**
 * Authenticate HTTP request
 * Supports: API Key (X-API-Key) or DID Request Signing (X-DID-Signature)
 */
function authenticateRequest(req) {
  // Option 1: API Key header
  const apiKey = req.headers['x-api-key'];
  const configuredApiKey = process.env.RECEIPTS_API_KEY;

  if (apiKey && configuredApiKey && apiKey === configuredApiKey) {
    return { authenticated: true, method: 'api-key', did: null };
  }

  // Option 2: DID Request Signing
  const signature = req.headers['x-did-signature'];
  const timestamp = req.headers['x-did-timestamp'];
  const did = req.headers['x-did'];

  if (signature && timestamp && did) {
    // Verify timestamp is within 5 minutes (prevents replay attacks)
    const now = Date.now();
    const reqTime = parseInt(timestamp);
    if (isNaN(reqTime) || Math.abs(now - reqTime) > 300000) {
      return { authenticated: false, error: 'Request timestamp expired or invalid' };
    }

    // Build signed message: METHOD:PATH:TIMESTAMP
    const url = new URL(req.url, 'http://localhost');
    const message = `${req.method}:${url.pathname}:${timestamp}`;

    // Verify signature using our Ed25519 verification
    try {
      const verified = verifyDIDSignature(message, signature, did);
      if (verified) {
        return { authenticated: true, method: 'did-signature', did };
      }
    } catch (e) {
      return { authenticated: false, error: `Signature verification failed: ${e.message}` };
    }
  }

  // No valid authentication provided
  return { authenticated: false, error: 'Authentication required. Provide X-API-Key or X-DID-Signature headers.' };
}

/**
 * Verify DID signature for HTTP requests
 */
function verifyDIDSignature(message, signature, did) {
  // Try to resolve DID locally first
  const localDid = loadLocalDID();

  // If the DID matches our local identity, verify with our key
  if (localDid && localDid.id === did) {
    // Load public key from DID document
    const keyMethod = localDid.verificationMethod?.[0];
    if (!keyMethod?.publicKeyMultibase) {
      throw new Error('No public key in local DID document');
    }

    // Decode public key (remove 'z' prefix for base58btc)
    const publicKeyBase58 = keyMethod.publicKeyMultibase.slice(1);
    const publicKeyBytes = base58Decode(publicKeyBase58);

    // Parse signature: ed25519:BASE64URL:TIMESTAMP (we only need the base64url part)
    const sigParts = signature.split(':');
    if (sigParts[0] !== 'ed25519' || sigParts.length < 2) {
      throw new Error('Invalid signature format');
    }
    const signatureBytes = Buffer.from(sigParts[1], 'base64url');

    // Verify using nacl
    const nacl = require('tweetnacl');
    const messageBytes = Buffer.from(message, 'utf8');
    return nacl.sign.detached.verify(messageBytes, signatureBytes, publicKeyBytes);
  }

  // For external DIDs, we could resolve from chain or registry
  // For now, only allow local DID verification
  throw new Error('External DID verification not yet supported');
}

/**
 * Validate proposal input
 */
function validateProposalInput(body) {
  const errors = [];

  // Validate payment address (ERC-55 checksum if provided)
  if (body.paymentAddress) {
    if (typeof body.paymentAddress !== 'string' ||
        !/^0x[a-fA-F0-9]{40}$/.test(body.paymentAddress)) {
      errors.push('Invalid payment address format (must be 0x followed by 40 hex chars)');
    }
  }

  // Validate arbitration cost (positive number, reasonable range)
  if (body.arbitrationCost !== undefined && body.arbitrationCost !== null) {
    const cost = parseFloat(body.arbitrationCost);
    if (isNaN(cost) || cost < 0) {
      errors.push('Invalid arbitration cost (must be non-negative number)');
    } else if (cost > 1000000) {
      errors.push('Arbitration cost exceeds maximum (1000000)');
    }
  }

  // Validate deadline (must be ISO date string in the future)
  if (body.deadline) {
    const deadline = new Date(body.deadline);
    if (isNaN(deadline.getTime())) {
      errors.push('Invalid deadline format (must be ISO date string)');
    } else if (deadline < new Date()) {
      errors.push('Deadline must be in the future');
    }
  }

  // Validate payment token if specified
  if (body.paymentToken) {
    const validTokens = ['USDC', 'ETH', 'USDT', 'DAI'];
    if (!validTokens.includes(body.paymentToken.toUpperCase())) {
      errors.push(`Invalid payment token (must be one of: ${validTokens.join(', ')})`);
    }
  }

  // Validate payment chain if specified
  if (body.paymentChain) {
    const validChains = Object.keys(CHAIN_CONFIG);
    if (!validChains.includes(body.paymentChain)) {
      errors.push(`Invalid payment chain (must be one of: ${validChains.join(', ')})`);
    }
  }

  return errors;
}

/**
 * Check if endpoint requires authentication
 */
function requiresAuth(pathname, method) {
  // Public endpoints (no auth required)
  const publicEndpoints = [
    { path: '/', method: 'GET' },
    { path: '/health', method: 'GET' },
    { path: '/identity', method: 'GET' },
    { path: '/identity/chains', method: 'GET' }
  ];

  return !publicEndpoints.some(e => e.path === pathname && e.method === method);
}

/**
 * Start HTTP server for cloud deployment
 */
function startHttpServer(args) {
  const http = require('http');
  const filters = parseFilters(args);
  const port = filters.port || process.env.PORT || 3000;

  const server = http.createServer(async (req, res) => {
    // Get client IP for rate limiting
    const clientIp = req.headers['x-forwarded-for']?.split(',')[0] ||
                     req.socket.remoteAddress ||
                     'unknown';

    // Check rate limit
    const rateCheck = checkRateLimit(clientIp);
    res.setHeader('X-RateLimit-Limit', RATE_LIMIT);
    res.setHeader('X-RateLimit-Remaining', rateCheck.remaining);
    res.setHeader('X-RateLimit-Reset', rateCheck.resetAt);

    if (!rateCheck.allowed) {
      res.writeHead(429, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        error: 'Too many requests',
        retryAfter: Math.ceil((rateCheck.resetAt - Date.now()) / 1000)
      }));
      return;
    }

    // Set CORS headers (restrictive by default)
    const corsHeaders = getCorsHeaders(req);
    Object.entries(corsHeaders).forEach(([key, value]) => {
      res.setHeader(key, value);
    });
    res.setHeader('Content-Type', 'application/json');

    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
      if (Object.keys(corsHeaders).length > 0) {
        res.writeHead(200);
      } else {
        res.writeHead(403);
      }
      res.end();
      return;
    }

    const url = new URL(req.url, `http://localhost:${port}`);
    const pathname = url.pathname;

    try {
      // Check authentication for protected endpoints
      if (requiresAuth(pathname, req.method)) {
        const auth = authenticateRequest(req);
        if (!auth.authenticated) {
          res.writeHead(401);
          res.end(JSON.stringify({
            error: 'Unauthorized',
            message: auth.error || 'Authentication required',
            hint: 'Provide X-API-Key header or sign request with X-DID, X-DID-Signature, X-DID-Timestamp headers'
          }));
          return;
        }
        // Store auth info for use in handlers
        req.auth = auth;
      }

      // Parse body for POST requests
      let body = {};
      if (req.method === 'POST') {
        body = await parseRequestBody(req);
      }

      // Route handlers
      switch (pathname) {
        case '/':
        case '/health':
          res.writeHead(200);
          res.end(JSON.stringify({
            status: 'ok',
            service: 'receipts-guard',
            version: VERSION,
            uptime: process.uptime(),
            identity: loadLocalDID()?.id || null
          }));
          break;

        case '/identity':
          const didDoc = loadLocalDID();
          if (didDoc) {
            res.writeHead(200);
            res.end(JSON.stringify(didDoc, null, 2));
          } else {
            res.writeHead(404);
            res.end(JSON.stringify({ error: 'No identity configured' }));
          }
          break;

        case '/identity/chains':
          res.writeHead(200);
          res.end(JSON.stringify(getChainStatus(), null, 2));
          break;

        case '/propose':
          if (req.method !== 'POST') {
            res.writeHead(405);
            res.end(JSON.stringify({ error: 'Method not allowed. Use POST.' }));
            break;
          }
          // Input validation
          const proposeValidation = validateProposalInput(body);
          if (proposeValidation.length > 0) {
            res.writeHead(400);
            res.end(JSON.stringify({ error: 'Validation failed', details: proposeValidation }));
            break;
          }
          const proposeResult = handleProposeHttp(body, req.auth);
          res.writeHead(proposeResult.error ? 400 : 200);
          res.end(JSON.stringify(proposeResult, null, 2));
          break;

        case '/accept':
          if (req.method !== 'POST') {
            res.writeHead(405);
            res.end(JSON.stringify({ error: 'Method not allowed. Use POST.' }));
            break;
          }
          const acceptResult = handleAcceptHttp(body, req.auth);
          if (acceptResult.status === 403) {
            res.writeHead(403);
          } else {
            res.writeHead(acceptResult.error ? 400 : 200);
          }
          res.end(JSON.stringify(acceptResult, null, 2));
          break;

        case '/list':
          const listResult = handleListHttp(url.searchParams);
          res.writeHead(200);
          res.end(JSON.stringify(listResult, null, 2));
          break;

        case '/agreements':
          const agreementsResult = listAgreements();
          res.writeHead(200);
          res.end(JSON.stringify(agreementsResult, null, 2));
          break;

        case '/proposals':
          const proposalsResult = listProposals();
          res.writeHead(200);
          res.end(JSON.stringify(proposalsResult, null, 2));
          break;

        default:
          res.writeHead(404);
          res.end(JSON.stringify({
            error: 'Not found',
            availableEndpoints: [
              'GET /',
              'GET /health',
              'GET /identity',
              'GET /identity/chains',
              'GET /list',
              'GET /agreements',
              'GET /proposals',
              'POST /propose',
              'POST /accept'
            ]
          }));
      }
    } catch (error) {
      res.writeHead(500);
      res.end(JSON.stringify({
        error: 'Internal server error',
        message: error.message
      }));
    }
  });

  server.listen(port, () => {
    const apiKeyConfigured = !!process.env.RECEIPTS_API_KEY;
    const allowedOrigins = process.env.RECEIPTS_ALLOWED_ORIGINS?.split(',') || [];

    console.log(JSON.stringify({
      status: 'running',
      service: 'receipts-guard',
      version: VERSION,
      port,
      security: {
        authentication: apiKeyConfigured ? 'API Key + DID Signing' : 'DID Signing only (set RECEIPTS_API_KEY for API key auth)',
        cors: allowedOrigins.length > 0 ? `Restricted to: ${allowedOrigins.join(', ')}` : 'Blocked (set RECEIPTS_ALLOWED_ORIGINS)',
        rateLimit: `${RATE_LIMIT} requests/minute`
      },
      endpoints: {
        public: [
          'GET /',
          'GET /health',
          'GET /identity',
          'GET /identity/chains'
        ],
        protected: [
          'GET /list (auth required)',
          'GET /agreements (auth required)',
          'GET /proposals (auth required)',
          'POST /propose (auth required)',
          'POST /accept (auth required, counterparty only)'
        ]
      },
      message: 'RECEIPTS Guard HTTP server ready (v0.7.1 security hardened)'
    }, null, 2));
  });
}

/**
 * Parse request body as JSON
 */
function parseRequestBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (e) {
        reject(new Error('Invalid JSON body'));
      }
    });
    req.on('error', reject);
  });
}

/**
 * HTTP handler for propose
 */
function handleProposeHttp(body, auth) {
  const { terms, counterparty, arbiter, deadline, value, arbitrationCost, paymentAddress, paymentToken, paymentChain } = body;

  if (!terms || !counterparty) {
    return { error: 'Missing required fields: terms, counterparty' };
  }

  if (!arbiter) {
    return { error: 'Missing required field: arbiter' };
  }

  const agentId = process.env.RECEIPTS_AGENT_ID || 'openclaw-agent';
  const channel = 'http';

  // x402 Payment configuration
  let x402 = null;
  if (arbitrationCost) {
    x402 = {
      arbitrationCost,
      arbitrationToken: paymentToken || 'USDC',
      arbitrationChain: CHAIN_CONFIG[paymentChain || 'base']?.chainId || 8453,
      paymentAddress: paymentAddress || null,
      escrowRequired: false,
      paymentProtocol: 'x402',
      version: '1.0'
    };
  }

  // Generate PAO
  const parties = [agentId, counterparty];
  const termsHash = generateTermsHash(terms, parties, deadline);
  const proposerSignature = signTerms(termsHash, agentId);
  const proposalId = generateId('prop');
  const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();

  const proposal = {
    proposalId,
    termsHash: `sha256:${termsHash}`,
    terms: {
      text: terms,
      canonical: terms.trim().toLowerCase().replace(/\s+/g, ' '),
    },
    proposer: agentId,
    counterparty,
    proposedArbiter: arbiter,
    deadline: deadline || null,
    value: value || null,
    channel,
    proposerSignature,
    x402,
    status: 'pending_acceptance',
    createdAt: new Date().toISOString(),
    expiresAt,
    version: VERSION,
  };

  // Save proposal
  ensureDir(PROPOSALS_DIR);
  const proposalFile = path.join(PROPOSALS_DIR, `${proposalId}.json`);
  fs.writeFileSync(proposalFile, JSON.stringify(proposal, null, 2));

  const termsFile = path.join(PROPOSALS_DIR, `${proposalId}.txt`);
  fs.writeFileSync(termsFile, terms);

  return {
    ...proposal,
    message: `Proposal created. Share proposalId with ${counterparty} for acceptance.`
  };
}

/**
 * HTTP handler for accept
 */
function handleAcceptHttp(body, auth) {
  const { proposalId } = body;

  if (!proposalId) {
    return { error: 'Missing required field: proposalId' };
  }

  const proposalFile = path.join(PROPOSALS_DIR, `${proposalId}.json`);
  if (!fs.existsSync(proposalFile)) {
    return { error: 'Proposal not found', proposalId };
  }

  const proposal = JSON.parse(fs.readFileSync(proposalFile, 'utf8'));

  if (proposal.status !== 'pending_acceptance') {
    return { error: 'Proposal is not pending acceptance', currentStatus: proposal.status };
  }

  // Authorization check: If authenticated via DID, verify requester is the counterparty
  // For API key auth, we trust the server owner (they control the agent)
  if (auth?.method === 'did-signature' && auth.did) {
    // The accepting party's DID must match the proposal's counterparty
    // Note: counterparty could be a DID or agent ID
    if (auth.did !== proposal.counterparty && !proposal.counterparty.includes(auth.did)) {
      return {
        error: 'Forbidden',
        message: 'You are not authorized to accept this proposal. Only the counterparty can accept.',
        expectedCounterparty: proposal.counterparty,
        yourDid: auth.did,
        status: 403
      };
    }
  }

  const agentId = process.env.RECEIPTS_AGENT_ID || 'openclaw-agent';
  const counterpartySignature = signTerms(proposal.termsHash.replace('sha256:', ''), agentId);
  const agreementId = generateId('agr');

  const agreement = {
    agreementId,
    proposalId,
    termsHash: proposal.termsHash,
    terms: proposal.terms,
    parties: [proposal.proposer, proposal.counterparty],
    arbiter: proposal.proposedArbiter,
    deadline: proposal.deadline,
    value: proposal.value,
    signatures: {
      proposer: proposal.proposerSignature,
      counterparty: counterpartySignature,
    },
    x402: proposal.x402,
    status: 'active',
    acceptedAt: new Date().toISOString(),
    timeline: [
      { event: 'proposed', timestamp: proposal.createdAt, actor: proposal.proposer },
      { event: 'accepted', timestamp: new Date().toISOString(), actor: agentId },
    ],
    version: VERSION,
  };

  // Save agreement
  ensureDir(AGREEMENTS_DIR);
  const agreementFile = path.join(AGREEMENTS_DIR, `${agreementId}.json`);
  fs.writeFileSync(agreementFile, JSON.stringify(agreement, null, 2));

  // Update proposal status
  proposal.status = 'accepted';
  proposal.agreementId = agreementId;
  fs.writeFileSync(proposalFile, JSON.stringify(proposal, null, 2));

  return {
    ...agreement,
    message: 'Agreement created. Both parties have signed.'
  };
}

/**
 * HTTP handler for list
 */
function handleListHttp(params) {
  const type = params.get('type') || 'all';
  const status = params.get('status');

  const result = { generatedAt: new Date().toISOString() };

  if (type === 'all' || type === 'proposals') {
    result.proposals = listProposals();
  }
  if (type === 'all' || type === 'agreements') {
    result.agreements = listAgreements();
  }

  return result;
}

/**
 * List all proposals
 */
function listProposals() {
  if (!fs.existsSync(PROPOSALS_DIR)) return { count: 0, items: [] };

  const files = fs.readdirSync(PROPOSALS_DIR).filter(f => f.endsWith('.json'));
  const items = files.map(f => {
    const proposal = JSON.parse(fs.readFileSync(path.join(PROPOSALS_DIR, f), 'utf8'));
    return {
      proposalId: proposal.proposalId,
      status: proposal.status,
      counterparty: proposal.counterparty,
      arbiter: proposal.proposedArbiter,
      createdAt: proposal.createdAt
    };
  });

  return { count: items.length, items };
}

/**
 * List all agreements
 */
function listAgreements() {
  if (!fs.existsSync(AGREEMENTS_DIR)) return { count: 0, items: [] };

  const files = fs.readdirSync(AGREEMENTS_DIR).filter(f => f.endsWith('.json'));
  const items = files.map(f => {
    const agreement = JSON.parse(fs.readFileSync(path.join(AGREEMENTS_DIR, f), 'utf8'));
    return {
      agreementId: agreement.agreementId,
      status: agreement.status,
      parties: agreement.parties,
      arbiter: agreement.arbiter,
      acceptedAt: agreement.acceptedAt
    };
  });

  return { count: items.length, items };
}

// === EXPORT MODULE API ===
// When required as a module, export the programmatic API
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    // Hooks
    beforeConsent,
    afterCapture,
    onRiskDetected,

    // Programmatic capture
    capture: captureAgreement,
    capturePromise,

    // Arbitration Protocol (v0.5.0)
    generateTermsHash,
    signTerms,
    verifySignature,

    // Identity (v0.6.0 + v0.7.0)
    generateDIDDocument,
    loadLocalDID,
    resolveDID,
    signTermsWithDID,
    verifySignatureWithDID,
    verifySignatureWithHistory,
    generateEd25519Keypair,
    base58btcEncode,
    base58btcDecode,

    // Utilities
    detectRiskFlags: detectRiskFlagsWithCustom,
    detectConsentType,
    loadIndex,
    generatePDFContent,

    // Constants
    VERSION,
    RECEIPTS_DIR,
    PROPOSALS_DIR,
    AGREEMENTS_DIR,
    ARBITRATIONS_DIR,
    RULINGS_DIR,
    IDENTITY_DIR,
    DID_METHOD,
    VALID_ARBITRATION_REASONS,
  };
}
