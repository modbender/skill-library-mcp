// ============================================================================
// commands/publish.js — Publish a local asset directory to the marketplace
// ============================================================================

'use strict';

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const api = require('../api.js');
const config = require('../config.js');
const { fish, info, ok, warn, err, c, detail } = require('../ui.js');

/**
 * Parse SKILL.md frontmatter (YAML-like key: value pairs between --- markers)
 */
function parseFrontmatter(content) {
  const fm = {};
  let body = content;

  const match = content.match(/^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)/);
  if (match) {
    const fmText = match[1];
    body = match[2].trim();

    for (const line of fmText.split('\n')) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const kv = trimmed.match(/^([\w-]+)\s*:\s*(.*)/);
      if (kv) {
        let val = kv[2].trim();
        // Strip surrounding quotes
        if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
          val = val.slice(1, -1);
        }
        fm[kv[1]] = val;
      }
    }
  }

  return { frontmatter: fm, body };
}

/**
 * Extract metadata from a skill directory
 */
function extractMetadata(skillDir) {
  const hasSkillMd = fs.existsSync(path.join(skillDir, 'SKILL.md'));
  const hasPluginJson = fs.existsSync(path.join(skillDir, 'openclaw.plugin.json'));
  const hasPackageJson = fs.existsSync(path.join(skillDir, 'package.json'));
  const hasReadme = fs.existsSync(path.join(skillDir, 'README.md'));

  let name = '', displayName = '', description = '', version = '1.0.0';
  let readme = '', tags = [], category = '', longDescription = '';
  let detectedType = '';

  // --- Priority 1: SKILL.md ---
  if (hasSkillMd) {
    const content = fs.readFileSync(path.join(skillDir, 'SKILL.md'), 'utf-8');
    const { frontmatter: fm, body } = parseFrontmatter(content);

    name = fm.name || '';
    displayName = fm.displayName || fm['display-name'] || '';
    description = fm.description || '';
    version = fm.version || '1.0.0';
    readme = body;
    if (fm.tags) {
      tags = fm.tags.split(',').map(t => t.trim()).filter(Boolean);
    }
    category = fm.category || '';
    longDescription = fm.longDescription || description;
    detectedType = fm.type || 'skill';
  }

  // --- Priority 2: openclaw.plugin.json ---
  if (hasPluginJson && !name) {
    try {
      const plugin = JSON.parse(fs.readFileSync(path.join(skillDir, 'openclaw.plugin.json'), 'utf-8'));
      name = name || plugin.id || '';
      displayName = displayName || plugin.name || '';
      description = description || plugin.description || '';
      version = version === '1.0.0' ? (plugin.version || '1.0.0') : version;

      // Detect channel type
      if (Array.isArray(plugin.channels) && plugin.channels.length > 0) {
        detectedType = detectedType || 'channel';
      } else {
        detectedType = detectedType || 'plugin';
      }
    } catch {}
  }

  // --- Priority 3: package.json ---
  if (hasPackageJson && !name) {
    try {
      const pkg = JSON.parse(fs.readFileSync(path.join(skillDir, 'package.json'), 'utf-8'));
      let pkgName = pkg.name || '';
      // Strip @scope/ prefix
      if (pkgName.startsWith('@') && pkgName.includes('/')) {
        pkgName = pkgName.split('/').pop();
      }
      name = name || pkgName;
      displayName = displayName || pkgName;
      description = description || pkg.description || '';
      version = version === '1.0.0' ? (pkg.version || '1.0.0') : version;
    } catch {}
  }

  // --- Priority 4: README.md ---
  if (hasReadme) {
    try {
      const readmeContent = fs.readFileSync(path.join(skillDir, 'README.md'), 'utf-8');
      if (!readme) readme = readmeContent;
      if (!displayName) {
        const titleMatch = readmeContent.match(/^#\s+(.+)$/m);
        if (titleMatch) displayName = titleMatch[1].trim();
      }
      if (!description) {
        for (const line of readmeContent.split('\n')) {
          const t = line.trim();
          if (!t || t.startsWith('#') || t.startsWith('---')) continue;
          description = t;
          break;
        }
      }
    } catch {}
  }

  // Fallbacks
  if (!name) name = path.basename(skillDir);
  if (!displayName) displayName = name;
  if (!detectedType) detectedType = '';

  return {
    name, displayName, type: detectedType,
    description, version, readme,
    tags, category,
    longDescription: longDescription || description,
  };
}

async function run(args, flags) {
  let skillDir = args[0] || '.';
  skillDir = path.resolve(skillDir);

  fish(`Publishing from ${c('bold', skillDir)}`);
  console.log('');

  // Check device ID
  const deviceId = config.getDeviceId();
  if (!deviceId) {
    err('No OpenClaw device identity found.');
    console.log('');
    console.log(`  Expected: ${config.DEVICE_JSON}`);
    console.log('  Make sure OpenClaw is installed and has been started at least once.');
    console.log('');
    console.log(`  Your device must be authorized first:`);
    console.log(`    1. Login on ${c('bold', config.getApiBase())} (GitHub/Google)`);
    console.log('    2. Activate an invite code');
    console.log('    3. Authorize this device (your deviceId will be auto-detected)');
    process.exit(1);
  }

  info(`Device ID: ${deviceId.slice(0, 12)}...`);

  // Extract metadata
  const meta = extractMetadata(skillDir);

  // If type not detected, prompt user
  if (!meta.type) {
    warn('Could not auto-detect asset type (no SKILL.md or openclaw.plugin.json found)');
    console.log('  Available types: skill, plugin, channel, trigger, experience');

    const readline = require('readline');
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    meta.type = await new Promise(resolve => {
      rl.question('  Enter asset type: ', answer => {
        rl.close();
        resolve(answer.trim());
      });
    });

    if (!meta.type) {
      err('Asset type is required');
      process.exit(1);
    }
  }

  // ─── Validate package contents (hard block) ─────────────────────────
  const valErrors = [];
  switch (meta.type) {
    case 'skill': {
      const sp = path.join(skillDir, 'SKILL.md');
      if (!fs.existsSync(sp)) { valErrors.push('缺少 SKILL.md — skill 类型必须包含此文件'); break; }
      const { frontmatter: sfm, body: sbody } = parseFrontmatter(fs.readFileSync(sp, 'utf-8'));
      if (!sfm.name && !sfm.displayName && !sfm['display-name']) valErrors.push('SKILL.md frontmatter 缺少 name');
      if (!sfm.description) valErrors.push('SKILL.md frontmatter 缺少 description');
      if (!sbody.trim()) valErrors.push('SKILL.md 正文为空（frontmatter 之后需要技能说明）');
      break;
    }
    case 'plugin':
    case 'channel': {
      const pjp = path.join(skillDir, 'openclaw.plugin.json');
      if (!fs.existsSync(pjp)) { valErrors.push(`缺少 openclaw.plugin.json — ${meta.type} 类型必须包含此文件`); break; }
      try {
        const pd = JSON.parse(fs.readFileSync(pjp, 'utf-8'));
        if (!pd.id) valErrors.push('openclaw.plugin.json 缺少 id');
        if (meta.type === 'channel' && (!Array.isArray(pd.channels) || !pd.channels.length)) {
          valErrors.push('openclaw.plugin.json 缺少 channels 数组（channel 类型必须声明）');
        }
      } catch { valErrors.push('openclaw.plugin.json JSON 格式错误'); break; }
      if (!fs.existsSync(path.join(skillDir, 'README.md'))) valErrors.push(`缺少 README.md — ${meta.type} 类型必须包含 README.md`);
      if (!meta.displayName || !meta.description) valErrors.push('无法提取 displayName/description — 请在 openclaw.plugin.json 添加 name/description 或确保 README.md 有标题和描述');
      break;
    }
    case 'trigger':
    case 'experience': {
      const rp = path.join(skillDir, 'README.md');
      if (!fs.existsSync(rp)) { valErrors.push(`缺少 README.md — ${meta.type} 类型必须包含此文件`); break; }
      const rc = fs.readFileSync(rp, 'utf-8');
      let ht = false, hd = false;
      for (const l of rc.split('\n')) {
        const t = l.trim();
        if (!ht && /^#\s+.+/.test(t)) { ht = true; continue; }
        if (ht && !hd && t && !t.startsWith('#') && !t.startsWith('---') && !t.startsWith('>')) { hd = true; break; }
      }
      if (!ht) valErrors.push('README.md 缺少标题行（# 名称）');
      if (!hd) valErrors.push('README.md 缺少描述段落（标题后需要有文字说明）');
      break;
    }
  }

  if (valErrors.length) {
    console.log('');
    err('发布校验失败：');
    for (const e of valErrors) console.log(`  ${c('red', '✗')} ${e}`);
    console.log('');
    info('请补全以上内容后重新发布。');
    process.exit(1);
  }

  // Show preview
  console.log('');
  console.log(`  Name:        ${meta.name}`);
  console.log(`  Display:     ${meta.displayName}`);
  console.log(`  Type:        ${meta.type}`);
  console.log(`  Version:     ${meta.version}`);
  console.log(`  Description: ${(meta.description || '').slice(0, 80)}`);
  if (meta.tags.length) {
    console.log(`  Tags:        ${meta.tags.join(', ')}`);
  }
  console.log('');

  // Confirm
  if (!flags.yes && !flags.y) {
    const readline = require('readline');
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    const answer = await new Promise(resolve => {
      rl.question(`  Publish to ${config.getApiBase()}? [Y/n] `, resolve);
    });
    rl.close();
    if (/^[nN]/.test(answer)) {
      info('Cancelled.');
      return;
    }
  }

  // Create tarball
  const tarball = path.join(require('os').tmpdir(), `openclawmp-publish-${Date.now()}.tar.gz`);
  try {
    execSync(`tar czf "${tarball}" -C "${skillDir}" .`, { stdio: 'pipe' });
  } catch (e) {
    err('Failed to create package tarball');
    process.exit(1);
  }

  const tarStats = fs.statSync(tarball);
  const sizeKb = (tarStats.size / 1024).toFixed(1);
  info(`Package: ${sizeKb}KB compressed`);

  // Build payload
  const payload = {
    name: meta.name,
    displayName: meta.displayName,
    type: meta.type,
    description: meta.description,
    version: meta.version,
    readme: meta.readme,
    tags: meta.tags,
    category: meta.category,
    longDescription: meta.longDescription,
    authorId: process.env.SEAFOOD_AUTHOR_ID || '',
    authorName: process.env.SEAFOOD_AUTHOR_NAME || '',
    authorAvatar: process.env.SEAFOOD_AUTHOR_AVATAR || '',
  };

  // POST multipart: metadata + package file
  const { FormData, File } = require('node:buffer');
  let formData;

  // Node 18+ has global FormData via undici
  if (typeof globalThis.FormData !== 'undefined') {
    formData = new globalThis.FormData();
    formData.append('metadata', new Blob([JSON.stringify(payload)], { type: 'application/json' }), 'metadata.json');
    const tarBuffer = fs.readFileSync(tarball);
    formData.append('package', new Blob([tarBuffer], { type: 'application/gzip' }), 'package.tar.gz');
  } else {
    // Fallback for older Node — use raw fetch with multipart boundary
    err('FormData not available. Requires Node.js 18+ with fetch support.');
    process.exit(1);
  }

  const { status, data: respData } = await api.postMultipart('/api/v1/assets/publish', formData);

  // Clean up tarball
  try { fs.unlinkSync(tarball); } catch {}

  if (status === 200 || status === 201) {
    const assetId = respData?.data?.id || 'unknown';
    const fileCount = respData?.data?.files?.length || '?';

    console.log('');
    ok('Published successfully! 🎉');
    console.log('');
    detail('ID', assetId);
    detail('Files', fileCount);
    detail('Page', `${config.getApiBase()}/asset/${assetId}`);
    console.log('');

    // Check for metadataIncomplete flag
    if (respData?.data?.metadataIncomplete) {
      const missingFields = (respData.data.missingFields || []).join(', ');
      warn(`部分元数据缺失: ${missingFields}`);
      console.log('   建议让 Agent 自动补全，或手动编辑后重新发布');
      console.log('');
    }
  } else {
    const errorMsg = respData?.error || JSON.stringify(respData) || 'Unknown error';
    err(`Publish failed (HTTP ${status}): ${errorMsg}`);
    process.exit(1);
  }
}

module.exports = { run };
