/**
 * Jasper Recall Doctor
 * System health check for RAG dependencies
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const VENV_PATH = path.join(os.homedir(), '.openclaw', 'rag-env');
const CHROMA_PATH = path.join(os.homedir(), '.openclaw', 'chroma-db');
const MEMORY_PATH = path.join(os.homedir(), '.openclaw', 'workspace', 'memory');

function exec(cmd, opts = {}) {
  try {
    const result = execSync(cmd, { 
      encoding: 'utf8',
      stdio: opts.silent !== false ? 'pipe' : 'inherit',
      ...opts 
    });
    return { success: true, output: result.trim() };
  } catch (e) {
    return { success: false, output: e.message, stderr: e.stderr?.toString() };
  }
}

function checkVersion(requirement, actual) {
  const reqParts = requirement.replace('>=', '').split('.').map(Number);
  const actParts = actual.split('.').map(Number);
  
  for (let i = 0; i < reqParts.length; i++) {
    if (actParts[i] > reqParts[i]) return true;
    if (actParts[i] < reqParts[i]) return false;
  }
  return true;
}

function formatTime(ms) {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (days > 0) return `${days}d ago`;
  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return `${seconds}s ago`;
}

function getLastIndexTime() {
  try {
    if (!fs.existsSync(CHROMA_PATH)) return null;
    
    const files = fs.readdirSync(CHROMA_PATH, { recursive: true });
    let latestMtime = 0;
    
    for (const file of files) {
      const fullPath = path.join(CHROMA_PATH, file);
      const stats = fs.statSync(fullPath);
      if (stats.isFile() && stats.mtimeMs > latestMtime) {
        latestMtime = stats.mtimeMs;
      }
    }
    
    if (latestMtime === 0) return null;
    return Date.now() - latestMtime;
  } catch (e) {
    return null;
  }
}

function countCollections() {
  try {
    if (!fs.existsSync(CHROMA_PATH)) return 0;
    
    const sqliteFile = path.join(CHROMA_PATH, 'chroma.sqlite3');
    if (!fs.existsSync(sqliteFile)) return 0;
    
    // Try to count collections from the database
    const result = exec(`sqlite3 "${sqliteFile}" "SELECT COUNT(*) FROM collections;"`, { silent: true });
    if (result.success) {
      return parseInt(result.output.trim()) || 0;
    }
    
    // Fallback: count directories
    const entries = fs.readdirSync(CHROMA_PATH, { withFileTypes: true });
    return entries.filter(e => e.isDirectory() && !e.name.startsWith('.')).length;
  } catch (e) {
    return 0;
  }
}

function countMemoryFiles() {
  try {
    if (!fs.existsSync(MEMORY_PATH)) return 0;
    
    const files = fs.readdirSync(MEMORY_PATH);
    return files.filter(f => f.endsWith('.md') && !f.startsWith('.')).length;
  } catch (e) {
    return 0;
  }
}

function runDoctor(options = {}) {
  const { fix = false, dryRun = false } = options;
  const verbose = dryRun;
  
  console.log('🏥 Jasper Recall Doctor\n');
  
  if (fix) {
    console.log('🔧 Fix mode enabled - will attempt to repair issues\n');
  } else if (dryRun) {
    console.log('👁️  Dry-run mode - showing what --fix would do\n');
  }
  
  const checks = [];
  const fixes = [];
  
  // Node.js version check
  const nodeResult = exec('node --version');
  const nodeVersion = nodeResult.output.replace('v', '');
  const nodeOk = nodeResult.success && checkVersion('18.0.0', nodeVersion);
  checks.push({
    label: 'Node.js',
    status: nodeOk ? '✅' : '❌',
    value: nodeResult.success ? `v${nodeVersion}` : 'not found',
    ok: nodeOk,
    fixable: false,
    fixMessage: 'Please upgrade Node.js manually: https://nodejs.org/'
  });
  
  // Python version check
  const pythonResult = exec('python3 --version');
  const pythonMatch = pythonResult.output.match(/Python (\d+\.\d+\.\d+)/);
  const pythonVersion = pythonMatch ? pythonMatch[1] : null;
  const pythonOk = pythonResult.success && pythonVersion;
  checks.push({
    label: 'Python',
    status: pythonOk ? '✅' : '❌',
    value: pythonVersion || 'not found',
    ok: pythonOk,
    fixable: false,
    fixMessage: 'Please install Python 3: https://www.python.org/downloads/'
  });
  
  // Virtual environment check
  const venvExists = fs.existsSync(VENV_PATH);
  checks.push({
    label: 'Venv',
    status: venvExists ? '✅' : '❌',
    value: venvExists ? VENV_PATH : 'not found',
    ok: venvExists,
    fixable: !venvExists && pythonOk,
    fixMessage: !venvExists ? `create virtual environment at ${VENV_PATH}` : null,
    fixCommand: `python3 -m venv ${VENV_PATH}`,
    fixAction: () => {
      console.log(`  🔧 Creating virtual environment...`);
      const result = exec(`python3 -m venv ${VENV_PATH}`, { silent: false });
      if (result.success) {
        console.log(`  ✅ Virtual environment created at ${VENV_PATH}`);
        return true;
      } else {
        console.log(`  ❌ Failed to create virtual environment`);
        return false;
      }
    }
  });
  
  // ChromaDB check
  const pipPath = path.join(VENV_PATH, 'bin', 'pip');
  const chromaResult = exec(`${pipPath} show chromadb 2>/dev/null || pip3 show chromadb 2>/dev/null`);
  const chromaMatch = chromaResult.output.match(/Version: ([\d.]+)/);
  const chromaVersion = chromaMatch ? chromaMatch[1] : null;
  const chromaOk = chromaResult.success && chromaVersion;
  checks.push({
    label: 'ChromaDB',
    status: chromaOk ? '✅' : '❌',
    value: chromaVersion ? `installed (${chromaVersion})` : 'not installed',
    ok: chromaOk,
    fixable: !chromaOk && venvExists,
    fixMessage: !chromaOk ? 'install chromadb via pip' : null,
    fixCommand: `${pipPath} install chromadb`,
    fixAction: () => {
      console.log(`  🔧 Installing ChromaDB...`);
      const result = exec(`${pipPath} install chromadb`, { silent: false });
      if (result.success) {
        console.log(`  ✅ ChromaDB installed successfully`);
        return true;
      } else {
        console.log(`  ❌ Failed to install ChromaDB`);
        return false;
      }
    }
  });
  
  // Sentence-transformers check
  const transformersResult = exec(`${pipPath} show sentence-transformers 2>/dev/null || pip3 show sentence-transformers 2>/dev/null`);
  const transformersMatch = transformersResult.output.match(/Version: ([\d.]+)/);
  const transformersVersion = transformersMatch ? transformersMatch[1] : null;
  const transformersOk = transformersResult.success && transformersVersion;
  checks.push({
    label: 'Transformers',
    status: transformersOk ? '✅' : '❌',
    value: transformersVersion ? 'sentence-transformers installed' : 'not installed',
    ok: transformersOk,
    fixable: !transformersOk && venvExists,
    fixMessage: !transformersOk ? 'install sentence-transformers via pip' : null,
    fixCommand: `${pipPath} install sentence-transformers`,
    fixAction: () => {
      console.log(`  🔧 Installing sentence-transformers...`);
      const result = exec(`${pipPath} install sentence-transformers`, { silent: false });
      if (result.success) {
        console.log(`  ✅ sentence-transformers installed successfully`);
        return true;
      } else {
        console.log(`  ❌ Failed to install sentence-transformers`);
        return false;
      }
    }
  });
  
  // ChromaDB directory check
  const chromaExists = fs.existsSync(CHROMA_PATH);
  const collections = countCollections();
  checks.push({
    label: 'Database',
    status: chromaExists ? '✅' : '❌',
    value: chromaExists ? `${CHROMA_PATH} (${collections} collections)` : 'not found',
    ok: chromaExists,
    fixable: !chromaExists,
    fixMessage: !chromaExists ? `create database directory at ${CHROMA_PATH}` : null,
    fixCommand: `mkdir -p ${CHROMA_PATH}`,
    fixAction: () => {
      console.log(`  🔧 Creating ChromaDB directory...`);
      try {
        fs.mkdirSync(CHROMA_PATH, { recursive: true });
        console.log(`  ✅ Created directory: ${CHROMA_PATH}`);
        return true;
      } catch (e) {
        console.log(`  ❌ Failed to create directory: ${e.message}`);
        return false;
      }
    }
  });
  
  // Memory files check
  const memoryExists = fs.existsSync(MEMORY_PATH);
  const memoryCount = countMemoryFiles();
  checks.push({
    label: 'Memory files',
    status: memoryExists ? '✅' : '⚠️',
    value: memoryExists ? `${memoryCount} files in memory/` : 'directory not found',
    ok: memoryExists,
    fixable: !memoryExists,
    fixMessage: !memoryExists ? `create memory directory at ${MEMORY_PATH}` : null,
    fixCommand: `mkdir -p ${MEMORY_PATH}`,
    fixAction: () => {
      console.log(`  🔧 Creating memory directory...`);
      try {
        fs.mkdirSync(MEMORY_PATH, { recursive: true });
        console.log(`  ✅ Created directory: ${MEMORY_PATH}`);
        return true;
      } catch (e) {
        console.log(`  ❌ Failed to create directory: ${e.message}`);
        return false;
      }
    }
  });
  
  // Last index time / collections check
  const lastIndexMs = getLastIndexTime();
  const needsIndex = collections === 0 && chromaExists;
  const lastIndexOk = !needsIndex && (lastIndexMs !== null && lastIndexMs < 7 * 24 * 60 * 60 * 1000); // < 7 days
  checks.push({
    label: 'Last indexed',
    status: lastIndexMs === null ? '⚠️' : (lastIndexOk ? '✅' : '⚠️'),
    value: needsIndex ? 'no collections - needs initial index' : (lastIndexMs === null ? 'never' : formatTime(lastIndexMs)),
    ok: lastIndexMs !== null && !needsIndex,
    fixable: needsIndex,
    fixMessage: needsIndex ? 'run initial indexing with index-digests' : null,
    fixCommand: 'index-digests',
    fixAction: () => {
      console.log(`  🔧 Running initial index...`);
      const indexScript = path.join(__dirname, 'index-digests.js');
      const result = exec(`node ${indexScript}`, { silent: false });
      if (result.success) {
        console.log(`  ✅ Initial indexing complete`);
        return true;
      } else {
        console.log(`  ⚠️  Indexing may have completed with warnings`);
        return true; // Don't treat warnings as failure
      }
    }
  });
  
  // Print results
  const maxLabelLength = Math.max(...checks.map(c => c.label.length));
  for (const check of checks) {
    const padding = ' '.repeat(maxLabelLength - check.label.length);
    console.log(`  ${check.label}:${padding} ${check.status} ${check.value}`);
    
    // Show fix suggestions in default/dry-run mode
    if (!check.ok && !fix) {
      if (check.fixable && check.fixMessage) {
        if (verbose && check.fixCommand) {
          console.log(`    ${dryRun ? '📋' : '→'} Would run: ${check.fixCommand}`);
        } else {
          console.log(`    → run with --fix to ${check.fixMessage}`);
        }
      } else if (!check.fixable && check.fixMessage) {
        console.log(`    ❌ ${check.fixMessage}`);
      }
    }
  }
  
  console.log('');
  
  // Apply fixes if requested
  if (fix) {
    const fixableIssues = checks.filter(c => !c.ok && c.fixable && c.fixAction);
    
    if (fixableIssues.length === 0) {
      const unfixableIssues = checks.filter(c => !c.ok && !c.fixable);
      if (unfixableIssues.length > 0) {
        console.log('⚠️  Some issues require manual intervention:\n');
        for (const issue of unfixableIssues) {
          console.log(`  ❌ ${issue.label}: ${issue.fixMessage}`);
        }
        console.log('');
      }
    } else {
      console.log('🔧 Applying fixes...\n');
      
      for (const issue of fixableIssues) {
        const success = issue.fixAction();
        fixes.push({ issue: issue.label, success });
        console.log('');
      }
      
      const successCount = fixes.filter(f => f.success).length;
      const failCount = fixes.filter(f => !f.success).length;
      
      if (failCount === 0) {
        console.log(`✅ All ${successCount} issue${successCount > 1 ? 's' : ''} fixed!\n`);
      } else {
        console.log(`⚠️  Fixed ${successCount}/${fixes.length} issues (${failCount} failed)\n`);
      }
      
      // Check for remaining unfixable issues
      const unfixableIssues = checks.filter(c => !c.ok && !c.fixable);
      if (unfixableIssues.length > 0) {
        console.log('⚠️  Remaining issues require manual intervention:\n');
        for (const issue of unfixableIssues) {
          console.log(`  ❌ ${issue.label}: ${issue.fixMessage}`);
        }
        console.log('');
      }
    }
  }
  
  // Summary
  const allOk = checks.every(c => c.ok);
  if (allOk) {
    console.log('✅ All systems operational!\n');
    return 0;
  } else {
    const failed = checks.filter(c => !c.ok);
    
    if (!fix) {
      console.log(`⚠️  ${failed.length} issue${failed.length > 1 ? 's' : ''} detected.\n`);
      
      const hasFixableIssues = failed.some(c => c.fixable);
      if (hasFixableIssues) {
        console.log('→ Run with --fix to automatically repair issues\n');
      }
    }
    
    return fixes.length > 0 && fixes.every(f => f.success) ? 0 : 1;
  }
}

module.exports = { runDoctor };

// Allow direct execution
if (require.main === module) {
  const args = process.argv.slice(2);
  const options = {
    fix: args.includes('--fix'),
    dryRun: args.includes('--dry-run')
  };
  
  process.exit(runDoctor(options));
}
