/**
 * guard-scanner v3.0.0 — Type Definitions
 * TypeScript rewrite with full type safety
 */

// ── Severity & Verdict ──────────────────────────────────────────────────────

export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export type VerdictLabel = 'MALICIOUS' | 'SUSPICIOUS' | 'LOW RISK' | 'CLEAN';
export type VerdictStat = 'malicious' | 'suspicious' | 'low' | 'clean';

export interface Verdict {
    icon: string;
    label: VerdictLabel;
    stat: VerdictStat;
}

// ── File Types ──────────────────────────────────────────────────────────────

export type FileType = 'code' | 'doc' | 'data' | 'skill-doc' | 'other';

// ── Findings ────────────────────────────────────────────────────────────────

export interface Finding {
    severity: Severity;
    id: string;
    cat: string;
    desc: string;
    file: string;
    line?: number;
    matchCount?: number;
    sample?: string;
}

export interface SkillResult {
    skill: string;
    risk: number;
    verdict: VerdictLabel;
    findings: Finding[];
}

// ── Patterns ────────────────────────────────────────────────────────────────

export interface PatternRule {
    id: string;
    cat: string;
    regex: RegExp;
    severity: Severity;
    desc: string;
    codeOnly?: boolean;
    docOnly?: boolean;
    all?: boolean;
    /** OWASP LLM Top 10 2025 mapping (e.g. 'LLM01', 'LLM06') */
    owasp?: string;
}

export interface CustomRuleInput {
    id: string;
    pattern: string;
    flags?: string;
    severity: Severity;
    cat: string;
    desc: string;
    codeOnly?: boolean;
    docOnly?: boolean;
}

// ── IoC Database ────────────────────────────────────────────────────────────

export interface IoC_Database {
    ips: string[];
    domains: string[];
    urls: string[];
    usernames: string[];
    filenames: string[];
    typosquats: string[];
}

// ── Signature Database (hbg-scan compatible) ────────────────────────────────

export interface ThreatSignature {
    id: string;
    name: string;
    severity: Severity;
    description: string;
    hash?: string;          // SHA-256 content hash match
    patterns?: string[];    // String patterns to match
    domains?: string[];     // Suspicious domains
}

export interface SignatureDatabase {
    version: string;
    updated: string;
    signatures: ThreatSignature[];
}

// ── Scanner Options ─────────────────────────────────────────────────────────

export interface ScannerOptions {
    verbose?: boolean;
    selfExclude?: boolean;
    strict?: boolean;
    summaryOnly?: boolean;
    /** Suppress all console.log output (v3.2.0: for --format stdout piping) */
    quiet?: boolean;
    checkDeps?: boolean;
    rulesFile?: string;
    plugins?: string[];
}

// ── Scanner Stats ───────────────────────────────────────────────────────────

export interface ScanStats {
    scanned: number;
    clean: number;
    low: number;
    suspicious: number;
    malicious: number;
}

// ── Thresholds ──────────────────────────────────────────────────────────────

export interface Thresholds {
    suspicious: number;
    malicious: number;
}

// ── Reports ─────────────────────────────────────────────────────────────────

export interface JSONReport {
    timestamp: string;
    scanner: string;
    mode: 'strict' | 'normal';
    stats: ScanStats;
    thresholds: Thresholds;
    findings: SkillResult[];
    recommendations: Recommendation[];
    iocVersion: string;
    signaturesVersion?: string;
}

export interface Recommendation {
    skill: string;
    actions: string[];
}

// ── SARIF ───────────────────────────────────────────────────────────────────

export interface SARIFReport {
    version: string;
    $schema: string;
    runs: SARIFRun[];
}

export interface SARIFRun {
    tool: {
        driver: {
            name: string;
            version: string;
            informationUri: string;
            rules: SARIFRule[];
        };
    };
    results: SARIFResult[];
    invocations: Array<{ executionSuccessful: boolean; endTimeUtc: string }>;
}

export interface SARIFRule {
    id: string;
    name: string;
    shortDescription: { text: string };
    defaultConfiguration: { level: string };
    properties: { tags: string[]; 'security-severity': string };
}

export interface SARIFResult {
    ruleId: string;
    ruleIndex: number;
    level: string;
    message: { text: string };
    partialFingerprints: { primaryLocationLineHash: string };
    locations: Array<{
        physicalLocation: {
            artifactLocation: { uri: string; uriBaseId: string };
            region?: { startLine: number };
        };
    }>;
}
