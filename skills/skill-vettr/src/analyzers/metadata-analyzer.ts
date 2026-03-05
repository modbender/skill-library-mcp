import { Finding, SkillManifest, VettingConfig } from '../types.js';
import { generateFindingId, truncateEvidence } from '../utils/sanitise.js';
import { levenshtein } from '../utils/levenshtein.js';

const DANGEROUS_PERMISSIONS = new Set([
  'filesystem:write',
  'filesystem:all',
  'network:all',
  'shell:exec',
  'shell:all',
  'system:admin',
  'system:root',
  'credentials:read',
  'keychain:access',
]);

export class MetadataAnalyzer {
  analyze(
    manifest: SkillManifest,
    skillPath: string,
    config: VettingConfig,
  ): Finding[] {
    const findings: Finding[] = [];
    const manifestFile = `${skillPath}/SKILL.md`;

    // Missing author
    if (!manifest.author || manifest.author.trim() === '') {
      findings.push({
        id: generateFindingId(),
        severity: config.requireAuthor ? 'WARNING' : 'INFO',
        category: 'PERMISSION_RISK',
        message: 'Skill lacks author attribution',
        file: manifestFile,
        evidence: 'No author field in manifest',
      });
    }

    // Blocked authors (user-configurable list)
    if (manifest.author && config.blockedAuthors?.length) {
      const authorLower = manifest.author.toLowerCase();
      if (config.blockedAuthors.some((b) => b.toLowerCase() === authorLower)) {
        findings.push({
          id: generateFindingId(),
          severity: 'CRITICAL',
          category: 'PERMISSION_RISK',
          message: `Author "${manifest.author}" is on the blocked list`,
          file: manifestFile,
          evidence: manifest.author,
        });
      }
    }

    // Typosquatting via Levenshtein distance
    if (config.checkTyposquatting && config.typosquatTargets?.length) {
      const skillName = manifest.name.toLowerCase();

      for (const target of config.typosquatTargets) {
        const targetLower = target.toLowerCase();

        // Skip exact match
        if (skillName === targetLower) continue;

        const distance = levenshtein(skillName, targetLower);

        if (distance <= 2 && distance > 0) {
          findings.push({
            id: generateFindingId(),
            severity: distance === 1 ? 'CRITICAL' : 'WARNING',
            category: 'TYPO_SQUATTING',
            message: `Name "${skillName}" is ${distance} edit(s) from "${target}" — possible typosquat`,
            file: manifestFile,
            evidence: `levenshtein("${skillName}", "${targetLower}") = ${distance}`,
          });
        }
      }
    }

    // Dangerous permissions
    if (manifest.permissions && Array.isArray(manifest.permissions)) {
      for (const perm of manifest.permissions) {
        if (typeof perm === 'string' && DANGEROUS_PERMISSIONS.has(perm)) {
          findings.push({
            id: generateFindingId(),
            severity: 'WARNING',
            category: 'PERMISSION_RISK',
            message: `Skill requests dangerous permission: ${perm}`,
            file: manifestFile,
            evidence: perm,
          });
        }
      }
    }

    // Non-standard version format
    if (manifest.version && !/^\d+\.\d+\.\d+(-[a-z0-9.]+)?$/i.test(manifest.version)) {
      findings.push({
        id: generateFindingId(),
        severity: 'INFO',
        category: 'PERMISSION_RISK',
        message: 'Non-standard version format',
        file: manifestFile,
        evidence: truncateEvidence(manifest.version),
      });
    }

    return findings;
  }
}
