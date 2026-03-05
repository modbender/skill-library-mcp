// verification.js — On-chain verification trail for agent swarm deliverables
//
// Companion to escrow.js. Records deliverable hashes, acceptance criteria,
// and verification results on the VerificationRegistry contract.
//
// All actual content lives on XMTP. Only SHA-256 hashes go on-chain.

import { ethers } from 'ethers';
import { createHash } from 'crypto';

const REGISTRY_ABI = [
  'function setCriteria(bytes32 taskId, bytes32 criteriaHash) external',
  'function submitDeliverable(bytes32 taskId, bytes32 deliverableHash) external',
  'function recordVerification(bytes32 taskId, bytes32 verificationHash, bool passed) external',
  'function getDeliverable(bytes32 taskId) view returns (bytes32 deliverableHash, bytes32 criteriaHash, bytes32 verificationHash, address worker, address verifier, uint256 submittedAt, uint256 verifiedAt, bool verified, bool passed)',
  'function getWorkerStats(address worker) view returns (uint256 submissions, uint256 verifiedCount, uint256 passedCount)',
  'event CriteriaSet(bytes32 indexed taskId, bytes32 criteriaHash, address indexed requestor)',
  'event DeliverableSubmitted(bytes32 indexed taskId, bytes32 deliverableHash, address indexed worker)',
  'event VerificationRecorded(bytes32 indexed taskId, bytes32 verificationHash, bool passed, address indexed verifier)',
];

// V2 with access control, deployed 2026-02-24
const DEFAULT_REGISTRY = '0x22536E4C3A221dA3C42F02469DB3183E28fF7A74';

export function getDefaultRegistryAddress() {
  return process.env.VERIFICATION_REGISTRY || DEFAULT_REGISTRY;
}

/**
 * Hash content to bytes32 for on-chain storage.
 * Uses SHA-256 (not keccak) since this hashes deliverable content, not identifiers.
 */
export function hashContent(content) {
  const hash = createHash('sha256').update(content).digest('hex');
  return '0x' + hash;
}

/**
 * Hash a task ID string to bytes32 (matches escrow.js hashTaskId).
 */
export function hashTaskId(taskId) {
  return ethers.id(taskId);
}

// ─── Write Operations ───

/**
 * Set acceptance criteria for a task (requestor calls this after creating escrow).
 * @param {ethers.Wallet} wallet - Requestor wallet
 * @param {string} registryAddr - VerificationRegistry address
 * @param {string} taskId - Task ID string
 * @param {string} criteriaContent - The actual criteria (tests, spec, etc.)
 * @returns {{ txHash: string, criteriaHash: string }}
 */
export async function setCriteria(wallet, registryAddr, taskId, criteriaContent) {
  const registry = new ethers.Contract(registryAddr || DEFAULT_REGISTRY, REGISTRY_ABI, wallet);
  const taskIdHash = hashTaskId(taskId);
  const criteriaHash = hashContent(criteriaContent);

  const tx = await registry.setCriteria(taskIdHash, criteriaHash);
  await tx.wait();

  return { txHash: tx.hash, criteriaHash };
}

/**
 * Worker submits deliverable hash after completing work.
 * @param {ethers.Wallet} wallet - Worker wallet
 * @param {string} registryAddr - VerificationRegistry address
 * @param {string} taskId - Task ID string
 * @param {string} deliverableContent - The full deliverable (code, research, etc.)
 * @returns {{ txHash: string, deliverableHash: string }}
 */
export async function submitDeliverable(wallet, registryAddr, taskId, deliverableContent) {
  const registry = new ethers.Contract(registryAddr || DEFAULT_REGISTRY, REGISTRY_ABI, wallet);
  const taskIdHash = hashTaskId(taskId);
  const deliverableHash = hashContent(deliverableContent);

  const tx = await registry.submitDeliverable(taskIdHash, deliverableHash);
  await tx.wait();

  return { txHash: tx.hash, deliverableHash };
}

/**
 * Record verification result on-chain.
 * @param {ethers.Wallet} wallet - Verifier wallet (worker for auto, requestor for manual, third-party)
 * @param {string} registryAddr - VerificationRegistry address
 * @param {string} taskId - Task ID string
 * @param {string} verificationContent - The verification report
 * @param {boolean} passed - Whether the deliverable met criteria
 * @returns {{ txHash: string, verificationHash: string }}
 */
export async function recordVerification(wallet, registryAddr, taskId, verificationContent, passed) {
  const registry = new ethers.Contract(registryAddr || DEFAULT_REGISTRY, REGISTRY_ABI, wallet);
  const taskIdHash = hashTaskId(taskId);
  const verificationHash = hashContent(verificationContent);

  const tx = await registry.recordVerification(taskIdHash, verificationHash, passed);
  await tx.wait();

  return { txHash: tx.hash, verificationHash };
}

// ─── Read Operations ───

/**
 * Get the on-chain verification trail for a task.
 */
export async function getVerificationTrail(providerOrWallet, registryAddr, taskId) {
  const registry = new ethers.Contract(registryAddr || DEFAULT_REGISTRY, REGISTRY_ABI, providerOrWallet);
  const taskIdHash = hashTaskId(taskId);

  const [deliverableHash, criteriaHash, verificationHash, worker, verifier, submittedAt, verifiedAt, verified, passed] =
    await registry.getDeliverable(taskIdHash);

  return {
    deliverableHash,
    criteriaHash,
    verificationHash,
    worker,
    verifier,
    submittedAt: Number(submittedAt),
    verifiedAt: Number(verifiedAt),
    verified,
    passed,
  };
}

/**
 * Get worker's verified stats.
 */
export async function getWorkerStats(providerOrWallet, registryAddr, workerAddr) {
  const registry = new ethers.Contract(registryAddr || DEFAULT_REGISTRY, REGISTRY_ABI, providerOrWallet);
  const [submissions, verifiedCount, passedCount] = await registry.getWorkerStats(workerAddr);
  return {
    submissions: Number(submissions),
    verified: Number(verifiedCount),
    passed: Number(passedCount),
    passRate: Number(submissions) > 0 ? (Number(passedCount) / Number(submissions) * 100).toFixed(1) + '%' : 'N/A',
  };
}

// ─── Verification Logic ───

/**
 * Tier 2: Automated test verification for code tasks.
 * Runs acceptance criteria (tests) against the deliverable.
 * Returns { passed, report }
 */
export async function verifyCodeTask(workDir, criteriaContent) {
  const { execSync } = await import('child_process');
  const { writeFileSync, existsSync } = await import('fs');
  const { join } = await import('path');

  const report = { tests: [], passed: true, summary: '' };

  try {
    // Write criteria (test file) to workdir
    const testPath = join(workDir, '_acceptance_test.js');
    writeFileSync(testPath, criteriaContent);

    // Try to run the test
    const output = execSync(`cd ${workDir} && node _acceptance_test.js 2>&1`, {
      encoding: 'utf-8',
      timeout: 30000,
    });
    report.tests.push({ name: 'acceptance_test', output, passed: true });
    report.summary = 'All acceptance tests passed.';
  } catch (err) {
    report.passed = false;
    report.tests.push({
      name: 'acceptance_test',
      output: err.stdout || err.message,
      error: err.stderr || '',
      passed: false,
    });
    report.summary = `Acceptance test failed: ${(err.message || '').slice(0, 200)}`;
  }

  return report;
}

/**
 * Tier 3: AI verification for subjective tasks.
 * Uses the cheapest available model to compare deliverable against spec.
 * Returns { passed, report, score }
 */
export async function verifyWithAI(taskDescription, criteriaContent, deliverableContent) {
  const { execSync } = await import('child_process');

  const prompt = `You are a verification agent. Compare this deliverable against the task specification and acceptance criteria.

TASK: ${taskDescription}

ACCEPTANCE CRITERIA:
${criteriaContent || 'None specified — evaluate based on task description.'}

DELIVERABLE:
${deliverableContent.slice(0, 4000)}

Score 1-10 on: completeness, correctness, relevance.
Reply with EXACTLY this JSON format:
{"passed": true/false, "score": N, "completeness": N, "correctness": N, "relevance": N, "summary": "one line reason"}`;

  // Try cheapest available models in order
  const models = [
    { cmd: 'openclaw ask', flag: '--model anthropic/claude-haiku' },
    { cmd: 'openclaw ask', flag: '--model google/gemini-flash' },
    { cmd: 'openclaw ask', flag: '' },
  ];

  for (const model of models) {
    try {
      const output = execSync(
        `echo '${prompt.replace(/'/g, "'\\''")}' | ${model.cmd} ${model.flag} 2>/dev/null`,
        { encoding: 'utf-8', timeout: 30000 }
      );

      // Try to parse JSON from output
      const jsonMatch = output.match(/\{[^}]*"passed"[^}]*\}/s);
      if (jsonMatch) {
        const result = JSON.parse(jsonMatch[0]);
        return {
          passed: result.passed,
          score: result.score,
          report: output,
          model: model.cmd + ' ' + model.flag,
        };
      }
    } catch {}
  }

  // Fallback: can't verify with AI
  return {
    passed: null,
    score: null,
    report: 'AI verification unavailable — no model accessible.',
    model: 'none',
  };
}
