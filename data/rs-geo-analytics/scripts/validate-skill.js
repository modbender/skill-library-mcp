#!/usr/bin/env node
/**
 * validate-skill.js
 * ClawhHub Skill Validation Script
 *
 * Validates the rs-geo-analytics skill against ClawhHub packaging
 * requirements. Exits 0 on success, 1 on failure.
 *
 * Usage:
 *   node scripts/validate-skill.js
 *   node scripts/validate-skill.js --verbose
 */

'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const verbose = process.argv.includes('--verbose');

let passed = 0;
let failed = 0;
const errors = [];
const warnings = [];

// ─── Helpers ─────────────────────────────────────────────
function check(label, condition, errorMsg, isWarning = false) {
  if (condition) {
    if (verbose) console.log(`  ✅ ${label}`);
    passed++;
  } else {
    const msg = `${label}: ${errorMsg}`;
    if (isWarning) {
      console.warn(`  ⚠️  ${label}: ${errorMsg}`);
      warnings.push(msg);
    } else {
      console.error(`  ❌ ${label}: ${errorMsg}`);
      errors.push(msg);
      failed++;
    }
  }
}

function fileExists(relPath) {
  return fs.existsSync(path.join(ROOT, relPath));
}

function fileContains(relPath, substring) {
  try {
    const content = fs.readFileSync(
      path.join(ROOT, relPath),
      'utf8'
    );
    return content.includes(substring);
  } catch {
    return false;
  }
}

function fileSize(relPath) {
  try {
    const stat = fs.statSync(path.join(ROOT, relPath));
    return stat.size;
  } catch {
    return 0;
  }
}

function parseJson(relPath) {
  try {
    const content = fs.readFileSync(
      path.join(ROOT, relPath),
      'utf8'
    );
    return JSON.parse(content);
  } catch {
    return null;
  }
}

function requireModule(relPath) {
  try {
    return require(path.join(ROOT, relPath));
  } catch (e) {
    return null;
  }
}

// ─── Validation Suites ────────────────────────────────────

function validateFileStructure() {
  console.log('\n📁 File Structure\n');

  const required = [
    'SKILL.md',
    'rankscale-skill.js',
    'references/api-integration.md',
    'references/geo-playbook.md',
    'assets/onboarding.md',
    'scripts/validate-skill.js',
    '.skill',
  ];

  required.forEach((f) => {
    check(
      `File exists: ${f}`,
      fileExists(f),
      `Missing required file: ${f}`
    );
  });
}

function validateSkillMd() {
  console.log('\n📋 SKILL.md\n');

  check(
    'SKILL.md exists',
    fileExists('SKILL.md'),
    'SKILL.md is required'
  );

  check(
    'SKILL.md has trigger patterns',
    fileContains('SKILL.md', 'Trigger Patterns') ||
      fileContains('SKILL.md', 'trigger'),
    'Must include trigger pattern documentation'
  );

  check(
    'SKILL.md has skill ID',
    fileContains('SKILL.md', 'rs-geo-analytics'),
    'Must include skill ID "rs-geo-analytics"'
  );

  check(
    'SKILL.md references credential setup',
    fileContains('SKILL.md', 'RANKSCALE_API_KEY'),
    'Must document required credentials'
  );

  check(
    'SKILL.md has output format',
    fileContains('SKILL.md', 'ASCII') ||
      fileContains('SKILL.md', 'output'),
    'Should document output format',
    true // warning only
  );

  check(
    'SKILL.md reasonable size (>1KB)',
    fileSize('SKILL.md') > 1000,
    'SKILL.md seems too small — check content'
  );
}

function validateDotSkill() {
  console.log('\n🏷️  .skill Metadata\n');

  check(
    '.skill file exists',
    fileExists('.skill'),
    '.skill metadata file is required'
  );

  const skill = parseJson('.skill');
  check(
    '.skill is valid JSON',
    skill !== null,
    '.skill must be valid JSON'
  );

  if (skill) {
    check(
      '.skill has id field',
      typeof skill.id === 'string' && skill.id.length > 0,
      'id field is required'
    );

    check(
      '.skill id matches rs-geo-analytics',
      skill.id === 'rs-geo-analytics',
      `Expected id "rs-geo-analytics", got "${skill.id}"`
    );

    check(
      '.skill has name field',
      typeof skill.name === 'string' && skill.name.length > 0,
      'name field is required'
    );

    check(
      '.skill has version field',
      typeof skill.version === 'string' &&
        /^\d+\.\d+\.\d+$/.test(skill.version),
      'version must be semver (e.g., 1.0.0)'
    );

    check(
      '.skill has description field',
      typeof skill.description === 'string' &&
        skill.description.length > 10,
      'description field is required'
    );

    check(
      '.skill has entrypoint',
      typeof skill.entrypoint === 'string' &&
        fileExists(skill.entrypoint),
      'entrypoint must exist'
    );

    check(
      '.skill has triggers array',
      Array.isArray(skill.triggers) && skill.triggers.length > 0,
      'triggers array with at least 1 pattern required'
    );

    check(
      '.skill has credentials spec',
      Array.isArray(skill.credentials) ||
        typeof skill.credentials === 'object',
      'credentials spec required',
      true // warning
    );

    check(
      '.skill has author field',
      typeof skill.author === 'string',
      'author field recommended',
      true // warning
    );
  }
}

function validateMainSkill() {
  console.log('\n⚙️  rankscale-skill.js\n');

  check(
    'rankscale-skill.js exists',
    fileExists('rankscale-skill.js'),
    'Main skill file missing'
  );

  const skill = requireModule('rankscale-skill.js');
  check(
    'Module loads without error',
    skill !== null,
    'Module threw an error on require'
  );

  if (skill) {
    // Required exports
    const requiredExports = [
      'run',
      'resolveCredentials',
      'GEO_RULES',
      'interpretGeoData',
      'normalizeSentiment',
      'normalizeCitations',
      'normalizeReport',
      'normalizeSearchTerms',
      'AuthError',
      'NotFoundError',
      'ApiError',
    ];

    requiredExports.forEach((exp) => {
      check(
        `Exports: ${exp}`,
        typeof skill[exp] !== 'undefined',
        `Missing export: ${exp}`
      );
    });

    // GEO_RULES validation
    if (Array.isArray(skill.GEO_RULES)) {
      check(
        'GEO_RULES has 10 rules',
        skill.GEO_RULES.length === 10,
        `Expected 10 rules, found ${skill.GEO_RULES.length}`
      );

      skill.GEO_RULES.forEach((rule, i) => {
        check(
          `Rule ${i + 1} has required fields`,
          rule.id && rule.severity && rule.check && rule.recommendation,
          `Rule ${i + 1} missing id/severity/check/recommendation`
        );

        check(
          `Rule ${i + 1} severity is valid`,
          ['CRIT', 'WARN', 'INFO'].includes(rule.severity),
          `Invalid severity "${rule.severity}"`
        );

        check(
          `Rule ${i + 1} check is a function`,
          typeof rule.check === 'function',
          'check must be a function'
        );
      });
    }

    // Test normalizeSentiment
    if (typeof skill.normalizeSentiment === 'function') {
      const formatA = skill.normalizeSentiment({
        positive: 0.61,
        negative: 0.10,
        neutral: 0.29,
      });
      check(
        'normalizeSentiment handles Format A (floats)',
        Math.abs(formatA.positive - 61) < 0.5 &&
          Math.abs(formatA.negative - 10) < 0.5,
        `Expected ~61/10, got ${formatA.positive}/${formatA.negative}`
      );

      const formatB = skill.normalizeSentiment({
        scores: { pos: 61, neg: 10, neu: 29 },
      });
      check(
        'normalizeSentiment handles Format B (nested scores)',
        Math.abs(formatB.positive - 61) < 0.5,
        `Expected ~61, got ${formatB.positive}`
      );

      const nullSentiment = skill.normalizeSentiment(null);
      check(
        'normalizeSentiment handles null input',
        nullSentiment.positive === 0,
        'Should return zero values for null'
      );
    }

    // Test normalizeReport
    if (typeof skill.normalizeReport === 'function') {
      const r = skill.normalizeReport({
        geoScore: 72,
        weeklyDelta: 3,
        rankPosition: 1,
      });
      check(
        'normalizeReport handles alternate field names',
        r.score === 72 && r.change === 3,
        `Expected score=72 change=3, got score=${r.score} change=${r.change}`
      );
    }

    // Test interpretGeoData
    if (typeof skill.interpretGeoData === 'function') {
      const mockData = {
        report: { score: 30, rank: 5, change: -8 },
        citations: { count: 100, rate: 15, sources: [] },
        sentiment: { positive: 40, neutral: 30, negative: 30 },
        searchTerms: [],
      };
      const insights = skill.interpretGeoData(mockData);
      check(
        'interpretGeoData returns array',
        Array.isArray(insights),
        'Must return an array'
      );
      check(
        'interpretGeoData returns max 5 insights',
        insights.length <= 5,
        `Returned ${insights.length} insights (max 5)`
      );
      check(
        'interpretGeoData fires CRIT for score<40',
        insights.some((i) => i.severity === 'CRIT'),
        'Should fire CRIT rules for low score data'
      );
    }

    // Test extractBrandIdFromKey indirectly
    if (typeof skill.resolveCredentials === 'function') {
      const creds = skill.resolveCredentials({
        apiKey: 'rk_test_faker_xxx_notreal',
      });
      check(
        'resolveCredentials extracts brandId from key',
        creds.brandId === 'notreal',
        `Expected "notreal", got "${creds.brandId}"`
      );
    }
  }

  // Source code checks
  const source = (() => {
    try {
      return fs.readFileSync(
        path.join(ROOT, 'rankscale-skill.js'),
        'utf8'
      );
    } catch {
      return '';
    }
  })();

  check(
    'Uses exponential backoff',
    source.includes('Math.pow') || source.includes('backoff'),
    'Must implement exponential backoff for rate limits'
  );

  check(
    'Handles 429 rate limit',
    source.includes('429'),
    'Must handle HTTP 429 rate limit'
  );

  check(
    'Has ASCII output (WIDTH constant)',
    source.includes('WIDTH') || source.includes('55'),
    'Must use fixed-width ASCII output'
  );

  check(
    'Has brand discovery',
    source.includes('discoverBrandId') ||
      source.includes('brands'),
    'Must implement brand discovery'
  );

  check(
    'Has onboarding flow',
    source.includes('onboarding') ||
      source.includes('SETUP'),
    'Must have onboarding prompt for missing credentials'
  );
}

function validateReferences() {
  console.log('\n📚 References\n');

  check(
    'api-integration.md exists',
    fileExists('references/api-integration.md'),
    'Missing API reference'
  );

  check(
    'api-integration.md covers all 4 endpoints',
    fileContains(
      'references/api-integration.md',
      '/v1/metrics/report'
    ) &&
      fileContains(
        'references/api-integration.md',
        '/v1/metrics/citations'
      ) &&
      fileContains(
        'references/api-integration.md',
        '/v1/metrics/sentiment'
      ) &&
      fileContains(
        'references/api-integration.md',
        '/v1/metrics/search-terms-report'
      ),
    'Must document all 4 API endpoints'
  );

  check(
    'api-integration.md has response schemas',
    fileContains('references/api-integration.md', 'Response') &&
      fileContains('references/api-integration.md', '200'),
    'Must include response schemas'
  );

  check(
    'api-integration.md documents error codes',
    fileContains('references/api-integration.md', '429') &&
      fileContains('references/api-integration.md', '401'),
    'Must document error codes'
  );

  check(
    'geo-playbook.md exists',
    fileExists('references/geo-playbook.md'),
    'Missing GEO playbook'
  );

  check(
    'geo-playbook.md has all 10 rules',
    fileContains('references/geo-playbook.md', 'Rule R1') &&
      fileContains('references/geo-playbook.md', 'Rule R10'),
    'Must document all 10 interpretation rules (R1–R10)'
  );

  check(
    'geo-playbook.md has severity levels',
    fileContains('references/geo-playbook.md', 'CRIT') &&
      fileContains('references/geo-playbook.md', 'WARN') &&
      fileContains('references/geo-playbook.md', 'INFO'),
    'Must document all severity levels'
  );

  check(
    'geo-playbook.md has GEO score bands',
    fileContains('references/geo-playbook.md', '0–39') ||
      fileContains('references/geo-playbook.md', 'Critical'),
    'Should document GEO score bands'
  );
}

function validateAssets() {
  console.log('\n🎨 Assets\n');

  check(
    'onboarding.md exists',
    fileExists('assets/onboarding.md'),
    'Missing onboarding asset'
  );

  check(
    'onboarding.md has signup URL',
    fileContains('assets/onboarding.md', 'rankscale.ai'),
    'Must include Rankscale signup URL'
  );

  check(
    'onboarding.md has credential setup steps',
    fileContains('assets/onboarding.md', 'RANKSCALE_API_KEY') ||
      fileContains('assets/onboarding.md', 'API_KEY'),
    'Must include credential setup instructions'
  );

  check(
    'onboarding.md has step-by-step flow',
    fileContains('assets/onboarding.md', 'STEP 1') ||
      fileContains('assets/onboarding.md', 'Step 1'),
    'Should have numbered steps'
  );
}

// ─── Run All Validations ──────────────────────────────────
console.log('━'.repeat(55));
console.log('  ClawhHub Skill Validator — rs-geo-analytics');
console.log('  RS-126 Implementation Check');
console.log('━'.repeat(55));

validateFileStructure();
validateSkillMd();
validateDotSkill();
validateMainSkill();
validateReferences();
validateAssets();

// ─── Summary ──────────────────────────────────────────────
console.log('\n' + '━'.repeat(55));
console.log('  VALIDATION SUMMARY');
console.log('━'.repeat(55));
console.log(`  ✅ Passed:   ${passed}`);
console.log(`  ❌ Failed:   ${failed}`);
console.log(`  ⚠️  Warnings: ${warnings.length}`);

if (errors.length > 0) {
  console.log('\n  ERRORS:');
  errors.forEach((e) => console.error(`    • ${e}`));
}

if (warnings.length > 0 && verbose) {
  console.log('\n  WARNINGS:');
  warnings.forEach((w) => console.warn(`    • ${w}`));
}

console.log('━'.repeat(55));

if (failed === 0) {
  console.log(
    '\n  ✅ SKILL VALID — Ready for ClawhHub packaging\n'
  );
  process.exit(0);
} else {
  console.log(
    `\n  ❌ SKILL INVALID — ${failed} check(s) failed\n`
  );
  process.exit(1);
}
