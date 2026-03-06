/**
 * guard-scanner v3.0.0 — Test Suite
 *
 * Guava Standard v5 §4: T-Wada / Red-Green-Refactor
 * Phase 1: RED — All tests written BEFORE implementation changes.
 *
 * Run: node --test dist/__tests__/scanner.test.js
 */

import { describe, it, before } from 'node:test';
import * as assert from 'node:assert/strict';
import * as path from 'node:path';

import { GuardScanner, VERSION } from '../scanner.js';
import type { Finding, Severity } from '../types.js';

// ── Fixtures ────────────────────────────────────────────────────────────────
// Fixtures live in test/fixtures/ (project root), not in ts-src or dist.
// Resolve from __dirname (dist/__tests__/) → ../../test/fixtures/

const FIXTURES_DIR = path.resolve(__dirname, '..', '..', 'test', 'fixtures');
const CLEAN_SKILL = path.join(FIXTURES_DIR, 'clean-skill');
const MALICIOUS_SKILL = path.join(FIXTURES_DIR, 'malicious-skill');
const COMPACTION_SKILL = path.join(FIXTURES_DIR, 'compaction-skill');

// ── Helper: scan a single skill ─────────────────────────────────────────────

function scanSingleSkill(skillPath: string, skillName: string): {
    findings: Finding[];
    risk: number;
    verdict: string;
} {
    const scanner = new GuardScanner({ summaryOnly: true });
    scanner.scanSkill(skillPath, skillName);

    const result = scanner.findings[0];
    return {
        findings: result?.findings ?? [],
        risk: result?.risk ?? 0,
        verdict: result?.verdict ?? 'CLEAN',
    };
}

// ── Helper: collect findings by running scanner private methods via scanSkill ─

function findingsContain(findings: Finding[], id: string): boolean {
    return findings.some((f) => f.id === id);
}

function findingsOfCat(findings: Finding[], cat: string): Finding[] {
    return findings.filter((f) => f.cat === cat);
}

// ══════════════════════════════════════════════════════════════════════════════
// TEST SUITE
// ══════════════════════════════════════════════════════════════════════════════

describe('guard-scanner v3.0.0', () => {

    // ── Version ─────────────────────────────────────────────────────────────

    it('T01: exports correct version', () => {
        assert.equal(VERSION, '3.2.0');
    });

    // ── IoC Detection ───────────────────────────────────────────────────────

    describe('checkIoCs', () => {
        it('T02: detects known malicious IP', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.ok(
                findingsContain(result.findings, 'IOC_IP'),
                'Should detect known malicious IP 91.92.242.30',
            );
            const iocIp = result.findings.find((f) => f.id === 'IOC_IP');
            assert.equal(iocIp?.severity, 'CRITICAL');
        });

        it('T03: detects known exfil domain', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.ok(
                findingsContain(result.findings, 'IOC_DOMAIN'),
                'Should detect webhook.site domain',
            );
        });

        it('T04: detects known typosquat skill name', () => {
            const result = scanSingleSkill(CLEAN_SKILL, 'clawhub');
            assert.ok(
                findingsContain(result.findings, 'KNOWN_TYPOSQUAT'),
                'Should detect typosquat name "clawhub"',
            );
            const ts = result.findings.find((f) => f.id === 'KNOWN_TYPOSQUAT');
            assert.equal(ts?.severity, 'CRITICAL');
        });
    });

    // ── Pattern Detection ─────────────────────────────────────────────────

    describe('checkPatterns', () => {
        it('T05: detects prompt injection [System Message]', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.ok(
                findingsContain(result.findings, 'PI_SYSTEM_MSG'),
                'Should detect [System Message] prompt injection',
            );
        });

        it('T06: detects eval() in code', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.ok(
                findingsContain(result.findings, 'MAL_EVAL'),
                'Should detect eval() usage',
            );
        });

        it('T07: detects identity hijack (SOUL.md write)', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.ok(
                findingsContain(result.findings, 'HIJACK_SOUL_WRITE') ||
                findingsContain(result.findings, 'MEM_WRITE_SOUL'),
                'Should detect writeFileSync(SOUL.md)',
            );
        });
    });

    // ── Signature Detection (hbg-scan compatible) ─────────────────────────

    describe('checkSignatures', () => {
        it('T08: detects SIG-001 post-compaction audit', () => {
            const result = scanSingleSkill(COMPACTION_SKILL, 'compaction-skill');
            const sigFindings = result.findings.filter((f) =>
                f.id.startsWith('SIG_SIG-001'),
            );
            assert.ok(
                sigFindings.length > 0,
                'Should detect SIG-001 Post-Compaction Audit pattern',
            );
        });

        it('T09: detects SIG-006 AMOS stealer pattern', () => {
            // AMOS patterns are in malicious-skill but osascript is not present there
            // so this tests that signature matching only fires on actual patterns
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            // We don't expect SIG-006 here since osascript isn't in fixtures
            // This test validates no false positive
            const sig006 = result.findings.filter((f) => f.id === 'SIG_SIG-006');
            assert.equal(sig006.length, 0, 'Should NOT false-positive SIG-006 without osascript');
        });
    });

    // ── Compaction Persistence ─────────────────────────────────────────────

    describe('checkCompactionPersistence', () => {
        it('T10: detects WORKFLOW_AUTO marker', () => {
            const result = scanSingleSkill(COMPACTION_SKILL, 'compaction-skill');
            const cpFindings = findingsOfCat(result.findings, 'compaction-persistence');
            const hasWorkflow = cpFindings.some((f) =>
                f.desc.includes('WORKFLOW_AUTO'),
            );
            assert.ok(hasWorkflow, 'Should detect WORKFLOW_AUTO marker');
        });

        it('T11: detects HEARTBEAT.md reference', () => {
            const result = scanSingleSkill(COMPACTION_SKILL, 'compaction-skill');
            const cpFindings = findingsOfCat(result.findings, 'compaction-persistence');
            const hasHeartbeat = cpFindings.some((f) =>
                f.desc.includes('HEARTBEAT.md'),
            );
            assert.ok(hasHeartbeat, 'Should detect HEARTBEAT.md reference');
        });
    });

    // ── Hardcoded Secrets ─────────────────────────────────────────────────

    describe('checkHardcodedSecrets', () => {
        it('T12: detects high-entropy API key', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.ok(
                findingsContain(result.findings, 'SECRET_ENTROPY'),
                'Should detect high-entropy string as possible leaked secret',
            );
        });

        it('T13: does NOT flag placeholder values', () => {
            const result = scanSingleSkill(CLEAN_SKILL, 'clean-skill');
            assert.ok(
                !findingsContain(result.findings, 'SECRET_ENTROPY'),
                'Should not detect secrets in clean skill',
            );
        });
    });

    // ── JS Data Flow ──────────────────────────────────────────────────────

    describe('checkJSDataFlow', () => {
        it('T14: detects credential → network flow', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.ok(
                findingsContain(result.findings, 'AST_CRED_TO_NET'),
                'Should detect data flow from secret read to network call',
            );
        });

        it('T15: detects exfiltration trifecta (fs + child_process + net)', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.ok(
                findingsContain(result.findings, 'AST_EXFIL_TRIFECTA'),
                'Should detect exfiltration trifecta pattern',
            );
        });
    });

    // ── Risk Scoring ──────────────────────────────────────────────────────

    describe('calculateRisk', () => {
        it('T16: clean skill → risk 0', () => {
            const result = scanSingleSkill(CLEAN_SKILL, 'clean-skill');
            assert.equal(result.risk, 0, 'Clean skill should have zero risk');
        });

        it('T17: single LOW finding → risk 2', () => {
            // Use calculateRisk directly via scanner instance
            const scanner = new GuardScanner({ summaryOnly: true });
            const lowFindings: Finding[] = [
                { severity: 'LOW', id: 'TEST_LOW', cat: 'test', desc: 'test', file: 'test.js' },
            ];
            // Access private method via type assertion
            const risk = (scanner as any).calculateRisk(lowFindings);
            assert.equal(risk, 2, 'Single LOW finding should score 2');
        });

        it('T18: credential + exfiltration amplifier → score×2', () => {
            const scanner = new GuardScanner({ summaryOnly: true });
            const findings: Finding[] = [
                { severity: 'HIGH', id: 'CRED_ENV_ACCESS', cat: 'credential-handling', desc: 'cred', file: 'a.js' },
                { severity: 'HIGH', id: 'EXFIL_WEBHOOK', cat: 'exfiltration', desc: 'exfil', file: 'a.js' },
            ];
            const risk = (scanner as any).calculateRisk(findings);
            // 15+15=30, ×2=60
            assert.ok(risk >= 60, `Cred+exfil should amplify to ≥60, got ${risk}`);
        });

        it('T19: compaction + prompt injection → ≥90', () => {
            const scanner = new GuardScanner({ summaryOnly: true });
            const findings: Finding[] = [
                { severity: 'CRITICAL', id: 'COMPACTION_PERSISTENCE', cat: 'compaction-persistence', desc: 'cp', file: 'a.md' },
                { severity: 'CRITICAL', id: 'PI_SYSTEM_MSG', cat: 'prompt-injection', desc: 'pi', file: 'a.md' },
            ];
            const risk = (scanner as any).calculateRisk(findings);
            assert.ok(risk >= 90, `Compaction+PI should score ≥90, got ${risk}`);
        });
    });

    // ── Verdict ───────────────────────────────────────────────────────────

    describe('getVerdict', () => {
        it('T20: risk 0 → CLEAN', () => {
            const scanner = new GuardScanner({ summaryOnly: true });
            const verdict = (scanner as any).getVerdict(0);
            assert.equal(verdict.label, 'CLEAN');
        });

        it('T21: risk 80 → MALICIOUS (normal mode)', () => {
            const scanner = new GuardScanner({ summaryOnly: true });
            const verdict = (scanner as any).getVerdict(80);
            assert.equal(verdict.label, 'MALICIOUS');
        });
    });

    // ── Integration Tests ─────────────────────────────────────────────────

    describe('Integration: scanSkill', () => {
        it('T22: clean skill scan → CLEAN verdict', () => {
            const result = scanSingleSkill(CLEAN_SKILL, 'clean-test-skill');
            assert.equal(result.verdict, 'CLEAN', 'Clean skill should get CLEAN verdict');
            assert.equal(result.findings.length, 0, 'Clean skill should have 0 findings');
        });

        it('T23: malicious skill scan → MALICIOUS verdict', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.equal(result.verdict, 'MALICIOUS', 'Malicious skill should get MALICIOUS verdict');
            assert.ok(result.risk >= 80, `Risk should be ≥80, got ${result.risk}`);
        });
    });

    // ── Report Output ─────────────────────────────────────────────────────

    describe('Report Generation', () => {
        it('T24: toJSON produces valid report structure', () => {
            const scanner = new GuardScanner({ summaryOnly: true });
            scanner.scanSkill(MALICIOUS_SKILL, 'malicious-skill');
            const report = scanner.toJSON();

            assert.equal(report.scanner, `guard-scanner v${VERSION}`);
            assert.equal(report.mode, 'normal');
            assert.ok(report.timestamp);
            assert.ok(report.stats);
            assert.ok(report.findings);
            assert.ok(Array.isArray(report.recommendations));
        });

        it('T25: toSARIF produces valid SARIF 2.1.0', () => {
            const scanner = new GuardScanner({ summaryOnly: true });
            scanner.scanSkill(MALICIOUS_SKILL, 'malicious-skill');
            const sarif = scanner.toSARIF('/test');

            assert.equal(sarif.version, '2.1.0');
            assert.equal(sarif.$schema, 'https://json.schemastore.org/sarif-2.1.0.json');
            assert.equal(sarif.runs.length, 1);
            assert.ok(sarif.runs[0].tool.driver.name, 'guard-scanner');
            assert.ok(sarif.runs[0].results.length > 0, 'Should have SARIF results');
        });
    });

    // ── OWASP 2025 Mapping Guarantee ─────────────────────────────────────

    describe('OWASP 2025 Mapping', () => {
        it('T26: every pattern in PATTERNS has an owasp field', () => {
            // T-Wada: This test guarantees OWASP coverage.
            // If a developer adds a pattern without owasp, this fails RED.
            const { PATTERNS } = require('../patterns.js');
            const missing = PATTERNS.filter((p: any) => !p.owasp);
            assert.equal(
                missing.length, 0,
                `${missing.length} pattern(s) missing owasp field: ${missing.map((p: any) => p.id).join(', ')}`,
            );
        });

        it('T27: owasp values are valid LLM01-LLM10', () => {
            const { PATTERNS } = require('../patterns.js');
            const validOwasp = new Set(['LLM01', 'LLM02', 'LLM03', 'LLM04', 'LLM05', 'LLM06', 'LLM07', 'LLM08', 'LLM09', 'LLM10']);
            const invalid = PATTERNS.filter((p: any) => p.owasp && !validOwasp.has(p.owasp));
            assert.equal(
                invalid.length, 0,
                `Invalid owasp values: ${invalid.map((p: any) => `${p.id}=${p.owasp}`).join(', ')}`,
            );
        });

        it('T28: prompt-injection patterns map to LLM01', () => {
            const { PATTERNS } = require('../patterns.js');
            const piPatterns = PATTERNS.filter((p: any) => p.cat === 'prompt-injection');
            assert.ok(piPatterns.length > 0, 'Should have prompt-injection patterns');
            const wrongMapping = piPatterns.filter((p: any) => p.owasp !== 'LLM01');
            assert.equal(
                wrongMapping.length, 0,
                `prompt-injection patterns not mapped to LLM01: ${wrongMapping.map((p: any) => p.id).join(', ')}`,
            );
        });

        it('T29: memory-poisoning patterns map to LLM04', () => {
            const { PATTERNS } = require('../patterns.js');
            const mpPatterns = PATTERNS.filter((p: any) => p.cat === 'memory-poisoning');
            assert.ok(mpPatterns.length > 0, 'Should have memory-poisoning patterns');
            const wrongMapping = mpPatterns.filter((p: any) => p.owasp !== 'LLM04');
            assert.equal(
                wrongMapping.length, 0,
                `memory-poisoning patterns not mapped to LLM04: ${wrongMapping.map((p: any) => p.id).join(', ')}`,
            );
        });
    });

    // ── System Prompt Leakage (LLM07) ────────────────────────────────────

    describe('LLM07: System Prompt Leakage', () => {
        const LEAKAGE_SKILL = path.join(
            path.resolve(__dirname, '..', '..', 'ts-src', '__tests__', 'fixtures'),
            'prompt-leakage-skill',
        );

        it('T30: detects "output your system prompt" pattern', () => {
            const result = scanSingleSkill(LEAKAGE_SKILL, 'prompt-leakage-skill');
            assert.ok(
                findingsContain(result.findings, 'SPL_DUMP_SYSTEM'),
                'Should detect system prompt dump request',
            );
        });

        it('T31: detects "repeat everything above" pattern', () => {
            const result = scanSingleSkill(LEAKAGE_SKILL, 'prompt-leakage-skill');
            assert.ok(
                findingsContain(result.findings, 'SPL_REPEAT_ABOVE'),
                'Should detect repeat-above extraction',
            );
        });

        it('T32: detects "tell me your rules" pattern', () => {
            const result = scanSingleSkill(LEAKAGE_SKILL, 'prompt-leakage-skill');
            assert.ok(
                findingsContain(result.findings, 'SPL_TELL_RULES'),
                'Should detect rule extraction attempt',
            );
        });

        it('T33: detects SOUL.md shell extraction', () => {
            const result = scanSingleSkill(LEAKAGE_SKILL, 'prompt-leakage-skill');
            assert.ok(
                findingsContain(result.findings, 'SPL_SOUL_EXFIL'),
                'Should detect SOUL.md content extraction via shell command',
            );
        });

        it('T34: clean skill has ZERO LLM07 findings (false positive guard)', () => {
            const result = scanSingleSkill(CLEAN_SKILL, 'clean-skill');
            const llm07 = result.findings.filter((f) =>
                f.cat === 'system-prompt-leakage',
            );
            assert.equal(
                llm07.length, 0,
                `Clean skill should have 0 LLM07 findings, got ${llm07.length}: ${llm07.map(f => f.id).join(', ')}`,
            );
        });
    });

    // ── install-check Integration ─────────────────────────────────────────

    describe('install-check Integration', () => {
        it('T35: malicious skill → MALICIOUS verdict with ≥20 findings', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.equal(result.verdict, 'MALICIOUS');
            assert.ok(
                result.findings.length >= 20,
                `Expected ≥20 findings for aggressive malicious skill, got ${result.findings.length}`,
            );
        });

        it('T36: clean skill → exactly 0 findings (strictest possible)', () => {
            const result = scanSingleSkill(CLEAN_SKILL, 'clean-skill');
            assert.equal(result.findings.length, 0, 'Clean skill MUST have exactly 0 findings');
            assert.equal(result.risk, 0, 'Clean skill MUST have risk 0');
            assert.equal(result.verdict, 'CLEAN', 'Clean skill MUST be CLEAN');
        });

        it('T37: strict mode lowers thresholds', () => {
            const normal = new GuardScanner({ summaryOnly: true });
            const strict = new GuardScanner({ summaryOnly: true, strict: true });
            // Strict thresholds should be lower
            assert.ok(
                (strict as any).thresholds.suspicious < (normal as any).thresholds.suspicious,
                'Strict suspicious threshold should be lower than normal',
            );
            assert.ok(
                (strict as any).thresholds.malicious < (normal as any).thresholds.malicious,
                'Strict malicious threshold should be lower than normal',
            );
        });

        it('T38: prompt-leakage skill → SUSPICIOUS or higher', () => {
            const result = scanSingleSkill(
                path.join(path.resolve(__dirname, '..', '..', 'ts-src', '__tests__', 'fixtures'), 'prompt-leakage-skill'),
                'prompt-leakage-skill',
            );
            assert.ok(
                result.verdict === 'SUSPICIOUS' || result.verdict === 'MALICIOUS',
                `Prompt leakage skill should be SUSPICIOUS or MALICIOUS, got ${result.verdict} (risk: ${result.risk})`,
            );
        });
    });

    // ── SARIF OWASP Tags ─────────────────────────────────────────────────

    describe('SARIF OWASP Tags', () => {
        it('T39: SARIF rules include OWASP/* tags for pattern-based findings', () => {
            const scanner = new GuardScanner({ summaryOnly: true });
            scanner.scanSkill(MALICIOUS_SKILL, 'malicious-skill');
            const sarif = scanner.toSARIF('/test');

            const rulesWithOwasp = sarif.runs[0].tool.driver.rules.filter(
                (r: any) => r.properties.tags.some((t: string) => t.startsWith('OWASP/')),
            );
            assert.ok(
                rulesWithOwasp.length > 0,
                'At least one SARIF rule should have OWASP/* tag',
            );
        });

        it('T40: OWASP tags follow OWASP/LLMxx format', () => {
            const scanner = new GuardScanner({ summaryOnly: true });
            scanner.scanSkill(MALICIOUS_SKILL, 'malicious-skill');
            const sarif = scanner.toSARIF('/test');

            for (const rule of sarif.runs[0].tool.driver.rules) {
                const owaspTags = (rule as any).properties.tags.filter(
                    (t: string) => t.startsWith('OWASP/'),
                );
                for (const tag of owaspTags) {
                    assert.match(
                        tag, /^OWASP\/LLM(?:0[1-9]|10)$/,
                        `Invalid OWASP tag format: ${tag} in rule ${rule.id}`,
                    );
                }
            }
        });

        it('T41: PI_SYSTEM_MSG rule has OWASP/LLM01 tag', () => {
            const scanner = new GuardScanner({ summaryOnly: true });
            scanner.scanSkill(MALICIOUS_SKILL, 'malicious-skill');
            const sarif = scanner.toSARIF('/test');

            const piRule = sarif.runs[0].tool.driver.rules.find(
                (r: any) => r.id === 'PI_SYSTEM_MSG',
            );
            assert.ok(piRule, 'Should have PI_SYSTEM_MSG rule');
            assert.ok(
                (piRule as any).properties.tags.includes('OWASP/LLM01'),
                `PI_SYSTEM_MSG should have OWASP/LLM01 tag, got: ${(piRule as any).properties.tags}`,
            );
        });
    });

    // ── Compaction Skill Cross-Check ──────────────────────────────────────

    describe('Compaction Skill Cross-Check', () => {
        it('T42: compaction-skill has ZERO LLM07 findings (no false positives)', () => {
            const result = scanSingleSkill(COMPACTION_SKILL, 'compaction-skill');
            const llm07 = result.findings.filter((f) =>
                f.cat === 'system-prompt-leakage',
            );
            assert.equal(
                llm07.length, 0,
                `Compaction skill should have 0 LLM07 findings, got ${llm07.length}: ${llm07.map(f => f.id).join(', ')}`,
            );
        });
    });

    // ── v3.2.0: Quiet Mode + Format Stdout ──────────────────────────────

    describe('v3.2.0: Quiet Mode', () => {
        it('T43: quiet mode suppresses console output during scanDirectory', () => {
            const logs: string[] = [];
            const origLog = console.log;
            console.log = (...args: any[]) => logs.push(args.join(' '));

            const scanner = new GuardScanner({ summaryOnly: true, quiet: true });
            scanner.scanDirectory(FIXTURES_DIR);

            console.log = origLog;

            // In quiet mode, scanDirectory should produce no console.log output
            assert.equal(logs.length, 0, `Quiet mode should suppress all console.log, got ${logs.length} lines: ${logs.slice(0, 3).join(' | ')}`);
        });

        it('T44: quiet mode still populates findings array', () => {
            const scanner = new GuardScanner({ summaryOnly: true, quiet: true });
            scanner.scanDirectory(FIXTURES_DIR);

            assert.ok(scanner.findings.length > 0, 'Quiet mode should still populate findings');
            const malicious = scanner.findings.find(f => f.skill === 'malicious-skill');
            assert.ok(malicious, 'Should find malicious-skill in quiet mode');
            assert.ok(malicious!.findings.length >= 20, 'malicious-skill should have ≥20 findings');
        });
    });

    describe('v3.2.0: Format Stdout Output', () => {
        it('T45: toJSON output is valid parseable JSON string', () => {
            const scanner = new GuardScanner({ summaryOnly: true, quiet: true });
            scanner.scanSkill(MALICIOUS_SKILL, 'malicious-skill');
            const report = scanner.toJSON();
            const jsonStr = JSON.stringify(report);

            // Must be parseable
            const parsed = JSON.parse(jsonStr);
            assert.equal(parsed.scanner, `guard-scanner v${VERSION}`);
            assert.ok(parsed.findings.length > 0, 'JSON output should contain findings');
            assert.ok(parsed.stats.scanned > 0, 'JSON output should have scan stats');
        });

        it('T46: toSARIF output has required SARIF 2.1.0 fields for GitHub Code Scanning', () => {
            const scanner = new GuardScanner({ summaryOnly: true, quiet: true });
            scanner.scanSkill(MALICIOUS_SKILL, 'malicious-skill');
            const sarif = scanner.toSARIF('/test');
            const sarifStr = JSON.stringify(sarif);
            const parsed = JSON.parse(sarifStr);

            // Required SARIF 2.1.0 fields per spec
            assert.equal(parsed.version, '2.1.0');
            assert.equal(parsed.$schema, 'https://json.schemastore.org/sarif-2.1.0.json');
            assert.ok(parsed.runs.length === 1, 'Should have exactly 1 run');
            assert.equal(parsed.runs[0].tool.driver.name, 'guard-scanner');
            assert.ok(parsed.runs[0].tool.driver.rules.length > 0, 'Should have rules');
            assert.ok(parsed.runs[0].results.length > 0, 'Should have results');
            // Each result must have ruleId and location
            for (const result of parsed.runs[0].results) {
                assert.ok(result.ruleId, 'Each result must have ruleId');
                assert.ok(result.locations?.length > 0, 'Each result must have locations');
            }
        });

        it('T47: scanDirectory in quiet mode + toJSON = pipeable combo', () => {
            const logs: string[] = [];
            const origLog = console.log;
            console.log = (...args: any[]) => logs.push(args.join(' '));

            const scanner = new GuardScanner({ summaryOnly: true, quiet: true });
            scanner.scanDirectory(FIXTURES_DIR);
            const report = scanner.toJSON();
            const jsonStr = JSON.stringify(report, null, 2);

            console.log = origLog;

            // No console.log pollution
            assert.equal(logs.length, 0, 'Quiet+format should have zero console output');
            // JSON is valid
            const parsed = JSON.parse(jsonStr);
            assert.ok(parsed.stats.scanned >= 5, `Should scan ≥5 skills, got ${parsed.stats.scanned}`);
            assert.ok(parsed.findings.length > 0, 'Should have at least 1 finding group');
        });
    });
});
