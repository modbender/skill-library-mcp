#!/usr/bin/env node
/**
 * BrainDB Execution Awareness Encoder
 * 
 * Introspects the OpenClaw environment and encodes tool/capability memories
 * into the procedural shard. Gives AI agents awareness of what they can do.
 * 
 * Three memory categories:
 *   1. Tool Catalog — what tools exist and when to use them
 *   2. Execution Patterns — proven workflows and tool chains
 *   3. Failure Memory — what doesn't work and why
 * 
 * Usage:
 *   node execution-awareness.js                    # Full introspection + encode
 *   node execution-awareness.js --scan             # Preview what would be encoded
 *   node execution-awareness.js --braindb URL      # Custom gateway URL
 *   node execution-awareness.js --workspace PATH   # Custom workspace
 */

import { readFileSync, existsSync, readdirSync, statSync } from 'fs';
import { join, basename, dirname } from 'path';
import { execSync } from 'child_process';

const args = process.argv.slice(2);
const SCAN_ONLY = args.includes('--scan');
const BRAINDB_URL = args[args.indexOf('--braindb') + 1] || 'http://localhost:3333';
const WORKSPACE = args[args.indexOf('--workspace') + 1] || process.env.OPENCLAW_WORKSPACE || process.cwd();

// ─── Environment Introspection ──────────────────────────

function discoverEnvironment() {
  const env = {
    platform: { os: process.platform, arch: process.arch, node: process.version },
    tools: { openclaw: [], cli: [], scripts: [], skills: [] },
    patterns: [],
    failures: [],
  };

  // 1. Discover CLI tools
  const cliTools = [
    { cmd: 'docker', desc: 'Container runtime for building and running Docker images/containers' },
    { cmd: 'docker compose', desc: 'Multi-container Docker orchestration' },
    { cmd: 'gh', desc: 'GitHub CLI for repos, PRs, issues, releases, and API calls' },
    { cmd: 'node', desc: 'Node.js runtime for JavaScript execution' },
    { cmd: 'npm', desc: 'Node.js package manager' },
    { cmd: 'python3', desc: 'Python runtime' },
    { cmd: 'curl', desc: 'HTTP client for API calls' },
    { cmd: 'jq', desc: 'JSON processor for parsing and transforming JSON data' },
    { cmd: 'git', desc: 'Version control' },
    { cmd: 'clawhub', desc: 'ClaWHub CLI for publishing and installing OpenClaw skills' },
    { cmd: 'swarm', desc: 'Parallel task execution on Gemini Flash workers (200x cheaper than Opus)' },
  ];

  for (const tool of cliTools) {
    try {
      const path = execSync(`which ${tool.cmd.split(' ')[0]} 2>/dev/null`, { encoding: 'utf8' }).trim();
      if (path) {
        let version = '';
        try {
          version = execSync(`${tool.cmd.split(' ')[0]} --version 2>/dev/null | head -1`, { encoding: 'utf8' }).trim();
        } catch {}
        env.tools.cli.push({ ...tool, path, version, available: true });
      }
    } catch {
      env.tools.cli.push({ ...tool, available: false });
    }
  }

  // 2. Discover custom scripts (~/bin/)
  const binDir = join(process.env.HOME, 'bin');
  if (existsSync(binDir)) {
    for (const file of readdirSync(binDir)) {
      const fullPath = join(binDir, file);
      if (statSync(fullPath).isFile()) {
        let desc = '';
        try {
          const content = readFileSync(fullPath, 'utf8');
          // Extract description from comments
          const descMatch = content.match(/^#\s*(.+?)$/m);
          if (descMatch) desc = descMatch[1].replace(/^[#!/]+\s*/, '');
        } catch {}
        env.tools.scripts.push({ name: file, path: fullPath, desc });
      }
    }
  }

  // 3. Discover workspace scripts
  const scriptsDir = join(WORKSPACE, 'scripts');
  if (existsSync(scriptsDir)) {
    for (const file of readdirSync(scriptsDir)) {
      if (file.endsWith('.sh') || file.endsWith('.js')) {
        const fullPath = join(scriptsDir, file);
        let desc = '';
        try {
          const content = readFileSync(fullPath, 'utf8');
          const descMatch = content.match(/^#\s*(.+?)$/m);
          if (descMatch) desc = descMatch[1].replace(/^[#!/]+\s*/, '');
        } catch {}
        env.tools.scripts.push({ name: file, path: fullPath, desc, workspace: true });
      }
    }
  }

  // 4. Discover skills
  const skillDirs = [
    join(WORKSPACE, 'skills'),
    join(process.env.HOME, '.openclaw', 'skills'),
  ];
  for (const dir of skillDirs) {
    if (!existsSync(dir)) continue;
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue;
      const skillMd = join(dir, entry.name, 'SKILL.md');
      if (existsSync(skillMd)) {
        const content = readFileSync(skillMd, 'utf8');
        const nameMatch = content.match(/^name:\s*(.+)$/m);
        const descMatch = content.match(/^description:\s*(.+)$/m);
        env.tools.skills.push({
          name: nameMatch?.[1] || entry.name,
          slug: entry.name,
          desc: descMatch?.[1] || '',
          path: join(dir, entry.name),
        });
      }
    }
  }

  // 5. Discover OpenClaw tools from system prompt context
  // These are the tools available via the OpenClaw runtime
  env.tools.openclaw = [
    { name: 'read', desc: 'Read file contents (text and images). Supports offset/limit for large files.' },
    { name: 'write', desc: 'Create or overwrite files. Auto-creates parent directories.' },
    { name: 'edit', desc: 'Surgical text replacement in files. oldText must match exactly.' },
    { name: 'exec', desc: 'Execute shell commands. Supports background, timeout, PTY mode. Use for any CLI operation.' },
    { name: 'process', desc: 'Manage background exec sessions: poll, log, write stdin, send keys, kill.' },
    { name: 'web_search', desc: 'Search the web via Brave Search API. Returns titles, URLs, snippets.' },
    { name: 'web_fetch', desc: 'Fetch and extract readable content from URLs (HTML to markdown).' },
    { name: 'browser', desc: 'Full browser automation: navigate, click, type, screenshot, snapshot DOM.' },
    { name: 'canvas', desc: 'Present HTML/UI to user, evaluate JS, take snapshots.' },
    { name: 'nodes', desc: 'Control paired nodes: run commands, camera, screen recording, location.' },
    { name: 'cron', desc: 'Schedule tasks: one-shot, recurring, or cron expressions. Supports isolated sessions.' },
    { name: 'message', desc: 'Send messages across channels: Discord, Telegram, WhatsApp, Signal, Slack, etc.' },
    { name: 'gateway', desc: 'Restart OpenClaw, apply config changes, run updates.' },
    { name: 'agents_list', desc: 'List available agent IDs for spawning sub-agents.' },
    { name: 'sessions_list', desc: 'List active sessions with optional filters.' },
    { name: 'sessions_history', desc: 'Fetch message history from another session.' },
    { name: 'sessions_send', desc: 'Send a message into another session.' },
    { name: 'sessions_spawn', desc: 'Spawn a background sub-agent in an isolated session.' },
    { name: 'session_status', desc: 'Show usage, cost, model info. Also set per-session model override.' },
    { name: 'image', desc: 'Analyze an image with vision model. Only use when image not already in message.' },
    { name: 'tts', desc: 'Convert text to speech. Returns MEDIA path for audio playback.' },
  ];

  // 6. Discover node fleet
  try {
    const nodeInfo = execSync('cat /tmp/fleet-nodes.json 2>/dev/null || echo "[]"', { encoding: 'utf8' });
    env.fleet = JSON.parse(nodeInfo);
  } catch {
    env.fleet = [];
  }

  return env;
}

// ─── Memory Generation ──────────────────────────────────

function generateMemories(env) {
  const memories = [];

  // === TOOL CATALOG ===

  // OpenClaw native tools
  for (const tool of env.tools.openclaw) {
    memories.push({
      event: `OpenClaw tool: ${tool.name}`,
      content: `The "${tool.name}" tool is available in this OpenClaw session. ${tool.desc}`,
      shard: 'procedural',
      category: 'tool-catalog',
    });
  }

  // CLI tools
  for (const tool of env.tools.cli) {
    if (tool.available) {
      memories.push({
        event: `CLI tool available: ${tool.cmd}`,
        content: `The "${tool.cmd}" CLI is installed at ${tool.path}${tool.version ? ` (${tool.version})` : ''}. ${tool.desc}`,
        shard: 'procedural',
        category: 'tool-catalog',
      });
    } else {
      memories.push({
        event: `CLI tool NOT available: ${tool.cmd}`,
        content: `The "${tool.cmd}" CLI is NOT installed in this environment. Do not attempt to use it. ${tool.desc ? 'It would be used for: ' + tool.desc : ''}`,
        shard: 'procedural',
        category: 'failure-memory',
      });
    }
  }

  // Custom scripts
  for (const script of env.tools.scripts) {
    memories.push({
      event: `Custom script: ${script.name}`,
      content: `Script "${script.name}" is available at ${script.path}.${script.desc ? ' ' + script.desc : ''}${script.workspace ? ' (workspace script)' : ' (~/bin/ utility)'}`,
      shard: 'procedural',
      category: 'tool-catalog',
    });
  }

  // Skills
  for (const skill of env.tools.skills) {
    memories.push({
      event: `Skill installed: ${skill.name}`,
      content: `The "${skill.name}" skill is installed at ${skill.path}. ${skill.desc} Read its SKILL.md before using.`,
      shard: 'procedural',
      category: 'tool-catalog',
    });
  }

  // === EXECUTION PATTERNS (high-value workflows) ===
  memories.push({
    event: 'Pattern: parallel research via swarm',
    content: 'For any research with 3+ independent queries, use swarm parallel instead of doing them sequentially. Command: swarm parallel "query1" "query2" "query3" --full. Uses Gemini Flash (200x cheaper than Opus). Add --context for BrainDB memory injection into workers.',
    shard: 'procedural',
    category: 'execution-pattern',
  });

  memories.push({
    event: 'Pattern: post alerts to Discord',
    content: 'To post alerts to Discord, use the message tool with action="send", channel="discord", and target=channelId. Security alerts go to #security-alerts (1465467780814995598). System alerts go to #system-alerts (1465467870677958798). Guild: 1427454483088019469.',
    shard: 'procedural',
    category: 'execution-pattern',
  });

  memories.push({
    event: 'Pattern: remote command execution on fleet',
    content: 'To run commands on remote nodes, use nodes(action="run", node="node-name", command=["bash","-c","command"]). The nodes tool handles authentication internally.',
    shard: 'procedural',
    category: 'execution-pattern',
  });

  memories.push({
    event: 'Pattern: schedule future tasks',
    content: 'To schedule a future task, use the cron tool. For reminders: action="add" with schedule kind="at" and payload kind="systemEvent". For recurring: kind="every" or kind="cron". Prefer sessionTarget="isolated" with payload kind="agentTurn" for autonomous work.',
    shard: 'procedural',
    category: 'execution-pattern',
  });

  memories.push({
    event: 'Pattern: GitHub workflow',
    content: 'GitHub operations use the "gh" CLI via exec tool. Create repos: gh repo create. Create releases: gh release create. Push code: git add/commit/push. Create PRs: gh pr create. Always work in feature branches, never push to main directly.',
    shard: 'procedural',
    category: 'execution-pattern',
  });

  memories.push({
    event: 'Pattern: file operations',
    content: 'For reading files use the read tool (supports offset/limit for large files). For writing use write tool. For precise edits use edit tool (oldText must match exactly including whitespace). For bulk operations use exec with shell commands. Prefer trash over rm for safety.',
    shard: 'procedural',
    category: 'execution-pattern',
  });

  memories.push({
    event: 'Pattern: web research',
    content: 'For web research: web_search for finding pages, web_fetch for extracting content from URLs. For interactive sites or JS-heavy pages, use the browser tool. web_fetch returns markdown by default, truncated to reasonable length.',
    shard: 'procedural',
    category: 'execution-pattern',
  });

  memories.push({
    event: 'Pattern: environment health checks',
    content: 'Workspace scripts for monitoring: fleet-health.sh (checks 4 Linux nodes), network-monitor-cron.sh (network device scan), gaming-server-monitor.sh (game server health). Check swarm status: swarm status. Check email: ~/bin/check-email. All run via exec tool.',
    shard: 'procedural',
    category: 'execution-pattern',
  });

  // === FAILURE MEMORIES ===
  memories.push({
    event: 'Failure: SSH to fleet nodes',
    content: 'If SSH fails to remote nodes, use nodes(action="run") instead — it handles authentication internally and avoids SSH key issues.',
    shard: 'procedural',
    category: 'failure-memory',
  });

  memories.push({
    event: 'Failure: todoist and icalBuddy CLIs',
    content: 'The todoist CLI and icalBuddy are NOT available on this machine. Do not attempt to use them. For calendar: use the calendar-today script in ~/bin/. For todos: would need API integration.',
    shard: 'procedural',
    category: 'failure-memory',
  });

  memories.push({
    event: 'Failure: Docker port conflicts',
    content: 'When testing Docker containers, always use non-default ports to avoid conflicts with production services. BrainDB production runs on port 3333 natively. Use GATEWAY_PORT=13333 or similar for Docker tests.',
    shard: 'procedural',
    category: 'failure-memory',
  });

  return memories;
}

// ─── Encoding ────────────────────────────────────────────

async function encode(memory) {
  const res = await fetch(`${BRAINDB_URL}/memory/encode`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      event: memory.event,
      content: memory.content,
      shard: memory.shard,
      context: { category: memory.category, source: 'execution-awareness', version: '1.0' },
      motivationDelta: { serve: 0.4, protect: 0.3 },
      dedupThreshold: 0.85, // Slightly lower threshold — tool descriptions can be similar
    }),
  });
  return res.json();
}

// ─── Main ────────────────────────────────────────────────

async function main() {
  console.log('🔍 BrainDB Execution Awareness Encoder');
  console.log('═'.repeat(50));

  // Introspect environment
  console.log('\n📡 Introspecting environment...');
  const env = discoverEnvironment();

  console.log(`   Platform: ${env.platform.os}/${env.platform.arch} (Node ${env.platform.node})`);
  console.log(`   CLI tools: ${env.tools.cli.filter(t => t.available).length}/${env.tools.cli.length} available`);
  console.log(`   Scripts: ${env.tools.scripts.length} discovered`);
  console.log(`   Skills: ${env.tools.skills.length} installed`);
  console.log(`   OpenClaw tools: ${env.tools.openclaw.length} in runtime`);

  // Generate memories
  const memories = generateMemories(env);
  console.log(`\n🧠 Generated ${memories.length} execution awareness memories:`);

  const byCat = {};
  for (const m of memories) {
    byCat[m.category] = (byCat[m.category] || 0) + 1;
  }
  for (const [cat, count] of Object.entries(byCat)) {
    console.log(`   ${cat}: ${count}`);
  }

  if (SCAN_ONLY) {
    console.log('\n📋 Memories that would be encoded:\n');
    for (const m of memories) {
      console.log(`  [${m.category}] ${m.event}`);
      console.log(`    ${m.content.slice(0, 100)}...`);
      console.log('');
    }
    return;
  }

  // Encode
  console.log(`\n📝 Encoding to ${BRAINDB_URL}...`);
  let encoded = 0, deduped = 0, errors = 0;
  for (const m of memories) {
    try {
      const result = await encode(m);
      if (result?.ok) {
        if (result.deduplicated) {
          deduped++;
        } else {
          encoded++;
          process.stdout.write('.');
        }
      } else {
        errors++;
        console.error(`\n  ❌ ${m.event}: ${result?.error || 'unknown error'}`);
      }
    } catch (e) {
      errors++;
      console.error(`\n  ❌ ${m.event}: ${e.message}`);
    }
  }

  console.log(`\n\n═${'═'.repeat(49)}`);
  console.log(`✅ Execution awareness encoded`);
  console.log(`   New: ${encoded} | Deduped: ${deduped} | Errors: ${errors}`);
  console.log(`═${'═'.repeat(49)}`);
}

main().catch(e => { console.error('Fatal:', e.message); process.exit(1); });
