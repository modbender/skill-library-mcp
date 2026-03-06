/**
 * wip-release/core.mjs
 * Local release tool. Bumps version, updates changelog + SKILL.md,
 * commits, tags, publishes to npm + GitHub Packages, creates GitHub release.
 * Zero dependencies.
 */

import { execSync, execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, basename } from 'node:path';

// ── Version ─────────────────────────────────────────────────────────

/**
 * Read current version from package.json.
 */
export function detectCurrentVersion(repoPath) {
  const pkgPath = join(repoPath, 'package.json');
  if (!existsSync(pkgPath)) throw new Error(`No package.json found at ${repoPath}`);
  const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
  return pkg.version;
}

/**
 * Bump a semver string by level.
 */
export function bumpSemver(version, level) {
  const [major, minor, patch] = version.split('.').map(Number);
  switch (level) {
    case 'major': return `${major + 1}.0.0`;
    case 'minor': return `${major}.${minor + 1}.0`;
    case 'patch': return `${major}.${minor}.${patch + 1}`;
    default: throw new Error(`Invalid level: ${level}. Use major, minor, or patch.`);
  }
}

/**
 * Write new version to package.json.
 */
function writePackageVersion(repoPath, newVersion) {
  const pkgPath = join(repoPath, 'package.json');
  const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
  pkg.version = newVersion;
  writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + '\n');
}

// ── SKILL.md ────────────────────────────────────────────────────────

/**
 * Update version in SKILL.md YAML frontmatter.
 */
export function syncSkillVersion(repoPath, newVersion) {
  const skillPath = join(repoPath, 'SKILL.md');
  if (!existsSync(skillPath)) return false;

  let content = readFileSync(skillPath, 'utf8');
  // Match version: X.Y.Z in YAML frontmatter (between --- markers)
  const updated = content.replace(
    /^(---[\s\S]*?)(version:\s*)\S+([\s\S]*?---)/,
    `$1$2${newVersion}$3`
  );

  if (updated === content) return false;
  writeFileSync(skillPath, updated);
  return true;
}

// ── CHANGELOG.md ────────────────────────────────────────────────────

/**
 * Prepend a new version entry to CHANGELOG.md.
 */
export function updateChangelog(repoPath, newVersion, notes) {
  const changelogPath = join(repoPath, 'CHANGELOG.md');
  const date = new Date().toISOString().split('T')[0];
  const entry = `## ${newVersion} (${date})\n\n${notes || 'Release.'}\n`;

  if (!existsSync(changelogPath)) {
    writeFileSync(changelogPath, `# Changelog\n\n${entry}\n`);
    return;
  }

  let content = readFileSync(changelogPath, 'utf8');
  // Insert after the # Changelog header
  const headerMatch = content.match(/^# Changelog\s*\n/);
  if (headerMatch) {
    const insertPoint = headerMatch[0].length;
    content = content.slice(0, insertPoint) + '\n' + entry + '\n' + content.slice(insertPoint);
  } else {
    content = `# Changelog\n\n${entry}\n${content}`;
  }

  writeFileSync(changelogPath, content);
}

// ── Git ─────────────────────────────────────────────────────────────

function gitCommitAndTag(repoPath, newVersion, notes) {
  const msg = `v${newVersion}: ${notes || 'Release'}`;
  // Stage known files (ignore missing ones)
  for (const f of ['package.json', 'CHANGELOG.md', 'SKILL.md']) {
    if (existsSync(join(repoPath, f))) {
      execFileSync('git', ['add', f], { cwd: repoPath, stdio: 'pipe' });
    }
  }
  // Use execFileSync to avoid shell injection via notes
  execFileSync('git', ['commit', '-m', msg], { cwd: repoPath, stdio: 'pipe' });
  execFileSync('git', ['tag', `v${newVersion}`], { cwd: repoPath, stdio: 'pipe' });
}

// ── Publish ─────────────────────────────────────────────────────────

/**
 * Publish to npm via 1Password for auth.
 */
export function publishNpm(repoPath) {
  const token = getNpmToken();
  execFileSync('npm', [
    'publish', '--access', 'public',
    `--//registry.npmjs.org/:_authToken=${token}`
  ], { cwd: repoPath, stdio: 'inherit' });
}

/**
 * Publish to GitHub Packages.
 */
export function publishGitHubPackages(repoPath) {
  const ghToken = execSync('gh auth token', { encoding: 'utf8' }).trim();
  execFileSync('npm', [
    'publish',
    '--registry', 'https://npm.pkg.github.com',
    `--//npm.pkg.github.com/:_authToken=${ghToken}`
  ], { cwd: repoPath, stdio: 'inherit' });
}

/**
 * Build detailed release notes from git history and repo metadata.
 */
export function buildReleaseNotes(repoPath, currentVersion, newVersion, notes) {
  const slug = detectRepoSlug(repoPath);
  const pkg = JSON.parse(readFileSync(join(repoPath, 'package.json'), 'utf8'));
  const lines = [];

  // What changed section
  lines.push('## What changed\n');
  if (notes) {
    lines.push(notes);
    lines.push('');
  }

  // Commits since last tag
  const prevTag = `v${currentVersion}`;
  let commits = '';
  try {
    commits = execFileSync('git', [
      'log', `${prevTag}..HEAD`, '--pretty=format:- %s (%h)'
    ], { cwd: repoPath, encoding: 'utf8' }).trim();
  } catch {
    // No previous tag ... show all commits on branch
    try {
      commits = execFileSync('git', [
        'log', '--pretty=format:- %s (%h)', '-20'
      ], { cwd: repoPath, encoding: 'utf8' }).trim();
    } catch {}
  }

  if (commits) {
    lines.push('### Commits\n');
    lines.push(commits);
    lines.push('');
  }

  // Files changed
  let filesChanged = '';
  try {
    filesChanged = execFileSync('git', [
      'diff', `${prevTag}..HEAD`, '--stat'
    ], { cwd: repoPath, encoding: 'utf8' }).trim();
  } catch {}

  if (filesChanged) {
    lines.push('### Files changed\n');
    lines.push('```');
    lines.push(filesChanged);
    lines.push('```');
    lines.push('');
  }

  // Install section
  lines.push('### Install\n');
  lines.push('```bash');
  lines.push(`npm install -g ${pkg.name}@${newVersion}`);
  lines.push('```');
  lines.push('');
  lines.push('Or update your local clone:');
  lines.push('```bash');
  lines.push('git pull origin main');
  lines.push('```');
  lines.push('');

  // Compare URL
  if (slug) {
    lines.push('---');
    lines.push('');
    lines.push(`Full changelog: https://github.com/${slug}/compare/v${currentVersion}...v${newVersion}`);
  }

  return lines.join('\n');
}

/**
 * Create a GitHub release with detailed notes.
 */
export function createGitHubRelease(repoPath, newVersion, notes, currentVersion) {
  const repoSlug = detectRepoSlug(repoPath);
  const body = buildReleaseNotes(repoPath, currentVersion, newVersion, notes);

  // Write notes to a temp file to avoid shell escaping issues
  const tmpFile = join(repoPath, '.release-notes-tmp.md');
  writeFileSync(tmpFile, body);

  try {
    execFileSync('gh', [
      'release', 'create', `v${newVersion}`,
      '--title', `v${newVersion}`,
      '--notes-file', '.release-notes-tmp.md',
      '--repo', repoSlug
    ], { cwd: repoPath, stdio: 'inherit' });
  } finally {
    try { execFileSync('rm', ['-f', tmpFile]); } catch {}
  }
}

/**
 * Publish skill to ClawHub.
 */
export function publishClawHub(repoPath, newVersion, notes) {
  const skillPath = join(repoPath, 'SKILL.md');
  if (!existsSync(skillPath)) return false;

  const slug = detectSkillSlug(repoPath);
  const changelog = notes || 'Release.';

  execFileSync('clawhub', [
    'publish', repoPath,
    '--slug', slug,
    '--version', newVersion,
    '--changelog', changelog
  ], { cwd: repoPath, stdio: 'inherit' });
  return true;
}

// ── Helpers ──────────────────────────────────────────────────────────

function getNpmToken() {
  try {
    return execSync(
      `OP_SERVICE_ACCOUNT_TOKEN=$(cat ~/.openclaw/secrets/op-sa-token) op item get "npm Token" --vault "Agent Secrets" --fields label=password --reveal 2>/dev/null`,
      { encoding: 'utf8' }
    ).trim();
  } catch {
    throw new Error('Could not fetch npm token from 1Password. Check op CLI and SA token.');
  }
}

function detectSkillSlug(repoPath) {
  // Slug must be lowercase and url-safe. Use directory name, not SKILL.md name
  // (SKILL.md name can be display-formatted like "WIP.release").
  return basename(repoPath).toLowerCase();
}

function detectRepoSlug(repoPath) {
  try {
    const url = execSync('git remote get-url origin', { cwd: repoPath, encoding: 'utf8' }).trim();
    // git@github.com:wipcomputer/wip-grok.git or https://github.com/wipcomputer/wip-grok.git
    const match = url.match(/github\.com[:/](.+?)(?:\.git)?$/);
    return match ? match[1] : null;
  } catch {
    return null;
  }
}

// ── Main ────────────────────────────────────────────────────────────

/**
 * Run the full release pipeline.
 */
export async function release({ repoPath, level, notes, dryRun, noPublish }) {
  repoPath = repoPath || process.cwd();
  const currentVersion = detectCurrentVersion(repoPath);
  const newVersion = bumpSemver(currentVersion, level);
  const repoName = basename(repoPath);

  console.log('');
  console.log(`  ${repoName}: ${currentVersion} -> ${newVersion} (${level})`);
  console.log(`  ${'─'.repeat(40)}`);

  if (dryRun) {
    const hasSkill = existsSync(join(repoPath, 'SKILL.md'));
    console.log(`  [dry run] Would bump package.json to ${newVersion}`);
    if (hasSkill) console.log(`  [dry run] Would update SKILL.md version`);
    console.log(`  [dry run] Would update CHANGELOG.md`);
    console.log(`  [dry run] Would commit and tag v${newVersion}`);
    if (!noPublish) {
      console.log(`  [dry run] Would publish to npm (@wipcomputer scope)`);
      console.log(`  [dry run] Would publish to GitHub Packages`);
      console.log(`  [dry run] Would create GitHub release v${newVersion}`);
      if (hasSkill) console.log(`  [dry run] Would publish to ClawHub`);
    }
    console.log('');
    console.log(`  Dry run complete. No changes made.`);
    console.log('');
    return { currentVersion, newVersion, dryRun: true };
  }

  // 1. Bump package.json
  writePackageVersion(repoPath, newVersion);
  console.log(`  ✓ package.json -> ${newVersion}`);

  // 2. Sync SKILL.md
  if (syncSkillVersion(repoPath, newVersion)) {
    console.log(`  ✓ SKILL.md -> ${newVersion}`);
  }

  // 3. Update CHANGELOG.md
  updateChangelog(repoPath, newVersion, notes);
  console.log(`  ✓ CHANGELOG.md updated`);

  // 4. Git commit + tag
  gitCommitAndTag(repoPath, newVersion, notes);
  console.log(`  ✓ Committed and tagged v${newVersion}`);

  // 5. Push commit + tag
  try {
    execSync('git push && git push --tags', { cwd: repoPath, stdio: 'pipe' });
    console.log(`  ✓ Pushed to remote`);
  } catch {
    console.log(`  ! Push failed (maybe branch protection). Push manually.`);
  }

  if (!noPublish) {
    // 6. npm publish
    try {
      publishNpm(repoPath);
      console.log(`  ✓ Published to npm`);
    } catch (e) {
      console.log(`  ✗ npm publish failed: ${e.message}`);
    }

    // 7. GitHub Packages
    try {
      publishGitHubPackages(repoPath);
      console.log(`  ✓ Published to GitHub Packages`);
    } catch (e) {
      console.log(`  ✗ GitHub Packages publish failed: ${e.message}`);
    }

    // 8. GitHub release
    try {
      createGitHubRelease(repoPath, newVersion, notes, currentVersion);
      console.log(`  ✓ GitHub release v${newVersion} created`);
    } catch (e) {
      console.log(`  ✗ GitHub release failed: ${e.message}`);
    }

    // 9. ClawHub skill publish
    const skillPath = join(repoPath, 'SKILL.md');
    if (existsSync(skillPath)) {
      try {
        publishClawHub(repoPath, newVersion, notes);
        console.log(`  ✓ Published to ClawHub`);
      } catch (e) {
        console.log(`  ✗ ClawHub publish failed: ${e.message}`);
      }
    }
  }

  console.log('');
  console.log(`  Done. ${repoName} v${newVersion} released.`);
  console.log('');

  return { currentVersion, newVersion, dryRun: false };
}
