import { Finding, VettingConfig } from '../types.js';
import { generateFindingId, truncateEvidence } from '../utils/sanitise.js';

interface PackageJson {
  name?: string;
  version?: string;
  dependencies?: Record<string, string> | null;
  devDependencies?: Record<string, string> | null;
  scripts?: Record<string, string> | null;
}

// Only packages involved in real, documented supply-chain attacks.
const KNOWN_MALICIOUS_PACKAGES = new Set([
  'event-stream',    // 2018: injected flatmap-stream to steal Bitcoin
  'flatmap-stream',  // Payload delivered via event-stream
]);

const SUSPICIOUS_PREFIXES = ['@free-', '@hack-', '@crack-', '@keygen-'];

export class DependencyAnalyzer {
  analyze(packageJson: PackageJson, skillPath: string, config: VettingConfig): Finding[] {
    const findings: Finding[] = [];
    const pkgFile = `${skillPath}/package.json`;

    const deps: Record<string, string> = {
      ...(packageJson.dependencies ?? {}),
      ...(packageJson.devDependencies ?? {}),
    };

    // Merge user-configured blocked packages with known malicious ones
    const blockedPackages = new Set([
      ...KNOWN_MALICIOUS_PACKAGES,
      ...(config.blockedPackages ?? []),
    ]);

    for (const [name, version] of Object.entries(deps)) {
      if (typeof version !== 'string') continue;

      // Known malicious or user-blocked packages
      if (blockedPackages.has(name)) {
        findings.push({
          id: generateFindingId(),
          severity: 'CRITICAL',
          category: 'DEPENDENCY_RISK',
          message: `Blocked dependency: ${name}`,
          file: pkgFile,
          evidence: `${name}@${version}`,
          cwe: 'CWE-829',
        });
      }

      // Suspicious prefixes
      for (const prefix of SUSPICIOUS_PREFIXES) {
        if (name.startsWith(prefix)) {
          findings.push({
            id: generateFindingId(),
            severity: 'WARNING',
            category: 'DEPENDENCY_RISK',
            message: `Suspicious package prefix: ${prefix}`,
            file: pkgFile,
            evidence: name,
          });
        }
      }

      // Unversioned deps (git/http/github:)
      if (version.startsWith('git') || version.startsWith('http') || version.includes('github:')) {
        findings.push({
          id: generateFindingId(),
          severity: 'WARNING',
          category: 'DEPENDENCY_RISK',
          message: 'External/unversioned dependency — cannot verify integrity',
          file: pkgFile,
          evidence: `${name}@${truncateEvidence(version, 50)}`,
          cwe: 'CWE-829',
        });
      }

      // Local file: protocol
      if (version.startsWith('file:')) {
        findings.push({
          id: generateFindingId(),
          severity: 'WARNING',
          category: 'DEPENDENCY_RISK',
          message: 'Local file dependency — verify path safety',
          file: pkgFile,
          evidence: `${name}@${version}`,
        });
      }
    }

    // Lifecycle scripts
    const dangerousScripts = ['postinstall', 'preinstall', 'install', 'prepare'];
    if (packageJson.scripts) {
      for (const script of dangerousScripts) {
        const scriptContent = packageJson.scripts[script];
        if (scriptContent) {
          findings.push({
            id: generateFindingId(),
            severity: script === 'postinstall' ? 'CRITICAL' : 'WARNING',
            category: 'DEPENDENCY_RISK',
            message: `Package contains ${script} script — executes automatically`,
            file: pkgFile,
            evidence: truncateEvidence(scriptContent),
            cwe: 'CWE-829',
          });
        }
      }
    }

    return findings;
  }
}
