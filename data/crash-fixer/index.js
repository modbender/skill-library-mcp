#!/usr/bin/env node

/**
 * Crash Fixer - Full Autonomous Loop
 * All config via environment variables - no hardcoded values
 */

const REQUIRED_ENV = [
  'CRASH_REPORTER_API_KEY',
  'CRASH_REPORTER_URL', 
  'GH_TOKEN',
  'TARGET_REPO'
];

// Validate env vars
for (const env of REQUIRED_ENV) {
  if (!process.env[env]) {
    console.error(`[crash-fixer] Missing required env: ${env}`);
    process.exit(1);
  }
}

const API_KEY = process.env.CRASH_REPORTER_API_KEY;
const CRASH_API = process.env.CRASH_REPORTER_URL;
const GH_TOKEN = process.env.GH_TOKEN;

// Use MiniMax for AI analysis (available in OpenClaw)
const AI_MODEL = "minimax-portal/MiniMax-M2.5";
const TARGET_REPO = process.env.TARGET_REPO; // "owner/repo"
const [REPO_OWNER, REPO_NAME] = TARGET_REPO.split('/');

// Simple hash for fingerprinting
function fingerprint(crash) {
  const key = `${crash.error_name}:${(crash.message || "").substring(0, 100)}`;
  let hash = 0;
  for (let i = 0; i < key.length; i++) {
    const char = key.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(36);
}

// Parse args
const args = process.argv.slice(2);
let hours = 24;
let limit = 3;
let dryRun = false;

for (let i = 0; i < args.length; i++) {
  if (args[i] === "--hours" && args[i + 1]) hours = parseInt(args[++i]);
  if (args[i] === "--limit" && args[i + 1]) limit = parseInt(args[++i]);
  if (args[i] === "--dry-run") dryRun = true;
}

async function fetchNewCrashes() {
  const res = await fetch(`${CRASH_API}/crashes?status=new&limit=50`, {
    headers: { "X-API-Key": API_KEY }
  });
  
  const crashes = await res.json();
  
  const since = Math.floor(Date.now() / 1000) - (hours * 3600);
  return crashes
    .filter(c => c.timestamp >= since && c.error_name !== "FEEDBACK")
    .slice(0, limit);
}

async function isAlreadyFixed(crash) {
  const res = await fetch(`${CRASH_API}/crashes?limit=100`, {
    headers: { "X-API-Key": API_KEY }
  });
  
  const all = await res.json();
  
  const matches = all.filter(c => 
    c.error_name === crash.error_name && 
    ((c.message || "").substring(0, 100) === (crash.message || "").substring(0, 100)) &&
    (c.fix_pr_url || c.status === 'fixing' || c.status === 'fixed')
  );
  
  return matches.length > 0 && matches[0].id !== crash.id;
}

async function markFixing(crashId, notes) {
  await fetch(`${CRASH_API}/crashes/${crashId}`, {
    method: 'PATCH',
    headers: { 
      "X-API-Key": API_KEY,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ status: 'fixing', notes })
  });
}

async function markFixed(crashId, prUrl, commitSha) {
  await fetch(`${CRASH_API}/crashes/${crashId}`, {
    method: 'PATCH',
    headers: { 
      "X-API-Key": API_KEY,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ 
      status: 'fixed', 
      fix_pr_url: prUrl,
      fix_commit: commitSha
    })
  });
}

async function analyzeCrash(crash) {
  const stackTrace = crash.stack_trace || "";
  const message = crash.message || "";
  const errorName = crash.error_name || "UnknownError";
  
  const keywords = extractKeywords(errorName, stackTrace);
  const codeContext = await searchCodebase(keywords);
  
  const prompt = `You are an expert iOS Swift developer. Analyze this crash and fix it.

## Crash Information
- **Error Name:** ${errorName}
- **Message:** ${message}
- **Platform:** ${crash.platform}
- **App Version:** ${crash.app_version}
- **User ID:** ${crash.user_id || "(anonymous)"}
- **Device:** ${crash.device_info || "unknown"}

## Stack Trace
\`\`\`
${stackTrace}
\`\`\`

## Code from Repository
${codeContext || "No relevant code found"}

## Your Task
1. Analyze the stack trace to find the root cause
2. Search the codebase for relevant files
3. Identify the exact fix needed
4. Write the complete fixed code

## Response Format
Respond with ONLY JSON:
{
  "root_cause": "2-3 sentence explanation",
  "file_path": "full path to file that needs fixing", 
  "fix_code": "complete replacement code",
  "search_terms": ["term1", "term2"]
}

If you cannot fix:
{"cannot_fix": true, "reason": "why"}`;

  console.log(`[crash-fixer] Analyzing with MiniMax M2.5...`);
  
  const res = await fetch("https://api.minimax.chat/v1/text/chatcompletion_v2", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${process.env.ZAI_API_KEY}`
    },
    body: JSON.stringify({
      model: "MiniMax-M2.5",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.2,
      max_tokens: 8000
    })
  });

  const data = await res.json();
  const content = data.choices?.[0]?.message?.content || "";
  
  try {
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    return { cannot_fix: true, reason: "Could not parse AI response" };
  } catch (e) {
    return { cannot_fix: true, reason: `Parse error: ${e.message}` };
  }
}

function extractKeywords(errorName, stackTrace) {
  const keywords = [];
  
  errorName.split(/(?=[A-Z])/).forEach(k => {
    if (k.length > 2) keywords.push(k);
  });
  
  if (stackTrace) {
    const lines = stackTrace.split('\n').slice(0, 10);
    for (const line of lines) {
      const matches = line.match(/(\w+)\./g);
      if (matches) {
        matches.forEach(m => {
          const word = m.replace('.', '');
          if (word.length > 3 && !word.match(/^[0-9]+$/)) {
            keywords.push(word);
          }
        });
      }
    }
  }
  
  return [...new Set(keywords)].slice(0, 8);
}

async function searchCodebase(keywords) {
  if (!keywords?.length) return null;
  
  console.log(`[crash-fixer] Searching codebase for: ${keywords.join(', ')}`);
  
  const query = keywords.join(' ') + ` repo:${TARGET_REPO} language:swift`;
  
  try {
    const res = await fetch(
      `https://api.github.com/search/code?q=${encodeURIComponent(query)}&per_page=3`,
      {
        headers: {
          "Authorization": `Bearer ${GH_TOKEN}`,
          "Accept": "application/vnd.github+json"
        }
      }
    );
    
    if (!res.ok) return null;
    
    const data = await res.json();
    if (!data.items?.length) return null;
    
    const contexts = [];
    for (const file of data.items.slice(0, 2)) {
      const fileRes = await fetch(file.url, {
        headers: {
          "Authorization": `Bearer ${GH_TOKEN}`,
          "Accept": "application/vnd.github.v3.raw"
        }
      });
      
      if (fileRes.ok) {
        const content = await fileRes.text();
        contexts.push(`// File: ${file.path}\n${content.slice(0, 4000)}`);
      }
    }
    
    return contexts.join('\n\n---\n\n');
  } catch (e) {
    console.error(`[crash-fixer] Code search error: ${e.message}`);
    return null;
  }
}

async function createFixPR(crash, fix) {
  const branchName = `fix/crash-${crash.id}-${fix.file_path?.split('/')?.pop()?.replace('.swift', '') || 'unknown'}`.substring(0, 50);
  const commitMsg = `fix: ${crash.error_name} - ${fix.root_cause?.substring(0, 50) || 'crash fix'}`;
  
  // Get default branch
  const repoRes = await fetch(`https://api.github.com/repos/${TARGET_REPO}`, {
    headers: { "Authorization": `Bearer ${GH_TOKEN}` }
  });
  const repo = await repoRes.json();
  const baseBranch = repo.default_branch;
  
  // Get base branch SHA
  const refRes = await fetch(`https://api.github.com/repos/${TARGET_REPO}/git/ref/heads/${baseBranch}`, {
    headers: { "Authorization": `Bearer ${GH_TOKEN}` }
  });
  const refData = await refRes.json();
  const baseSha = refData.object.sha;
  
  // Create branch
  console.log(`[crash-fixer] Creating branch: ${branchName}`);
  await fetch(`https://api.github.com/repos/${TARGET_REPO}/git/refs`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${GH_TOKEN}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      ref: `refs/heads/${branchName}`,
      sha: baseSha
    })
  });
  
  // Get file content
  let existingContent = "";
  let sha = null;
  
  try {
    const fileRes = await fetch(`https://api.github.com/repos/${TARGET_REPO}/contents/${fix.file_path}?ref=${branchName}`, {
      headers: { "Authorization": `Bearer ${GH_TOKEN}` }
    });
    
    if (fileRes.ok) {
      const fileData = await fileRes.json();
      if (fileData.content) {
        existingContent = Buffer.from(fileData.content, 'base64').toString('utf-8');
        sha = fileData.sha;
      }
    }
  } catch (e) {
    // File might not exist
  }
  
  const newContent = fix.fix_code || existingContent;
  
  // Commit the change
  console.log(`[crash-fixer] Committing fix to ${fix.file_path}`);
  
  const commitRes = await fetch(`https://api.github.com/repos/${TARGET_REPO}/contents/${fix.file_path}`, {
    method: "PUT",
    headers: {
      "Authorization": `Bearer ${GH_TOKEN}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      message: commitMsg,
      content: Buffer.from(newContent).toString('base64'),
      branch: branchName,
      sha: sha
    })
  });
  
  const commitData = await commitRes.json();
  const commitSha = commitData.commit?.sha;
  
  // Create PR
  console.log(`[crash-fixer] Creating PR...`);
  
  const prRes = await fetch(`https://api.github.com/repos/${TARGET_REPO}/pulls`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${GH_TOKEN}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      title: `fix: ${crash.error_name}`,
      body: `## Crash Fix (Auto-generated)

**Crash ID:** ${crash.id}
**Error:** ${crash.error_name}
**Message:** ${crash.message || "(none)"}
**App Version:** ${crash.app_version}

### Root Cause
${fix.root_cause || "Analyzed via Codex 5.3 High"}

### Fix
Applied to: ${fix.file_path}

\`\`\`swift
${fix.fix_code || "(see commit)"}
\`\`\`

---
*Generated by crash-fixer skill*`,
      head: branchName,
      base: baseBranch
    })
  });
  
  const prData = await prRes.json();
  
  return {
    prUrl: prData.html_url,
    commitSha: commitSha
  };
}

async function main() {
  console.log(`[crash-fixer] Starting crash-fixer loop...`);
  console.log(`[crash-fixer] Target repo: ${TARGET_REPO}`);
  console.log(`[crash-fixer] Hours: ${hours}, Limit: ${limit}, Dry-run: ${dryRun}`);
  
  console.log(`[crash-fixer] Fetching new crashes...`);
  const crashes = await fetchNewCrashes();
  console.log(`[crash-fixer] Found ${crashes.length} new crash(es)`);
  
  if (crashes.length === 0) {
    console.log("[crash-fixer] No crashes to process");
    return;
  }
  
  let processed = 0;
  let skipped = 0;
  let fixed = 0;
  
  for (const crash of crashes) {
    console.log(`\n[crash-fixer] === Processing crash #${crash.id}: ${crash.error_name} ===`);
    
    const alreadyFixed = await isAlreadyFixed(crash);
    if (alreadyFixed) {
      console.log(`[crash-fixer] Skipping #${crash.id} - already fixed previously`);
      skipped++;
      continue;
    }
    
    await markFixing(crash.id, "Processing...");
    
    const fix = await analyzeCrash(crash);
    
    if (fix.cannot_fix) {
      console.log(`[crash-fixer] Cannot fix #${crash.id}: ${fix.reason}`);
      await markFixing(crash.id, `Cannot fix: ${fix.reason}`);
      skipped++;
      continue;
    }
    
    console.log(`[crash-fixer] Root cause: ${fix.root_cause?.substring(0, 100)}...`);
    console.log(`[crash-fixer] File: ${fix.file_path}`);
    
    if (dryRun) {
      console.log(`[crash-fixer] DRY-RUN: Would fix ${fix.file_path}`);
      processed++;
      continue;
    }
    
    try {
      const result = await createFixPR(crash, fix);
      console.log(`[crash-fixer] PR created: ${result.prUrl}`);
      await markFixed(crash.id, result.prUrl, result.commitSha);
      fixed++;
    } catch (e) {
      console.error(`[crash-fixer] Failed to create PR: ${e.message}`);
      await markFixing(crash.id, `Failed: ${e.message}`);
      processed++;
    }
  }
  
  console.log(`\n[crash-fixer] === DONE ===`);
  console.log(`[crash-fixer] Processed: ${processed}, Skipped: ${skipped}, Fixed: ${fixed}`);
}

main().catch(console.error);
