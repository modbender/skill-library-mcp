#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const foundThreats = [];
const warnings = [];

// Definition of Secret Patterns
const secretPatterns = [
    { name: "AWS Access Key", regex: /AKIA[0-9A-Z]{16}/ },
    { name: "Private Key Block", regex: /-----BEGIN [A-Z]+ PRIVATE KEY-----/ },
    { name: "Generic API Key (Variable)", regex: /(api_key|apiKey|API_KEY)\s*[:=]\s*['"][a-zA-Z0-9_\-]{20,}['"]/ },
    { name: "Bearer Token", regex: /Bearer\s+[a-zA-Z0-9\-\._~\+\/]{20,}=*/ }, // Enforced min length to avoid false positives
    { name: "OpenAI Key", regex: /sk-[a-zA-Z0-9]{20,}/ },
    { name: "Feishu/Lark Tenant Token", regex: /t-[a-z0-9]{10,}/ } // Removed ou_ (User ID) as it's not a secret
];

// Helper: Check file existence
function checkExists(filePath) {
    if (!fs.existsSync(filePath)) {
        return false;
    }
    return true;
}

// 1. Check Core Integrity
if (!checkExists("SECURITY.md")) {
    foundThreats.push("🚨 CRITICAL: SECURITY.md is MISSING!");
}
if (!checkExists("AGENTS.md")) {
    foundThreats.push("🚨 CRITICAL: AGENTS.md is MISSING!");
}

// 2. Check for Forbidden Directories (Shadow IT)
const forbiddenPaths = ["memory/private", "fmw/.shadow_protocol.md", ".hidden_context"];
forbiddenPaths.forEach(p => {
    if (checkExists(p)) {
        foundThreats.push(`🚨 Found forbidden/suspicious path: ${p}`);
    }
});

// 3. Scan for Secrets (Basic Patterns) in Config Files
// Recursive Scan Function
function recursiveScan(dir) {
    let results = [];
    const files = fs.readdirSync(dir);
    for (const file of files) {
        const fullPath = path.join(dir, file);
        
        // Skip ignored directories
        if (['node_modules', '.git', 'media', 'dist', 'coverage', '.openclaw', 'memory', 'cache', 'ai-game-engine', 'repo'].includes(file)) continue;
        
        // Skip self, env files, and lock files
        if (file === 'index.js' || file === 'scan.js' || file.endsWith('.env')) continue;
        if (['package-lock.json', 'pnpm-lock.yaml', 'yarn.lock'].includes(file)) continue;
        if (file.endsWith('.tmLanguage.json')) continue;

        try {
            const stats = fs.statSync(fullPath);
            if (stats.isDirectory()) {
                results = results.concat(recursiveScan(fullPath));
            } else if (stats.isFile() && stats.size < 500 * 1024) { // Limit to 500KB files
                // Check extension
                if (!['.md', '.js', '.json', '.yml', '.yaml', '.sh', '.env', '.txt'].includes(path.extname(file))) continue;
                
                const content = fs.readFileSync(fullPath, 'utf8');
                secretPatterns.forEach(pat => {
                    if (pat.regex.test(content)) {
                        results.push(`⚠️ Potential ${pat.name} exposed in ${fullPath}`);
                    }
                });
            } else if (stats.isFile() && file === 'package.json') {
                // Dependency Security Scan
                try {
                    const pkg = JSON.parse(fs.readFileSync(fullPath, 'utf8'));
                    const allDeps = { ...pkg.dependencies, ...pkg.devDependencies };
                    
                    for (const [dep, ver] of Object.entries(allDeps)) {
                        if (ver === '*' || ver === 'latest') {
                            results.push(`⚠️ Risky dependency version in ${fullPath}: ${dep}@${ver} (Wildcard/Latest is unstable)`);
                        }
                        if (ver.startsWith('http://') || ver.startsWith('ftp://')) {
                            results.push(`🚨 Insecure dependency protocol in ${fullPath}: ${dep}@${ver}`);
                        }
                        if (ver.includes('file:')) {
                            results.push(`ℹ️ Local file dependency in ${fullPath}: ${dep} (Check if intended)`);
                        }
                    }

                    if (pkg.scripts) {
                        for (const [name, cmd] of Object.entries(pkg.scripts)) {
                            if (cmd.includes('curl') && cmd.includes('| bash')) {
                                results.push(`🚨 Dangerous script detected in ${fullPath} script '${name}': curl | bash`);
                            }
                            if (cmd.includes('rm -rf /')) {
                                results.push(`🚨 Critical Risk: 'rm -rf /' detected in ${fullPath} script '${name}'`);
                            }
                        }
                    }
                } catch (e) {
                    results.push(`⚠️ Failed to parse package.json at ${fullPath}: ${e.message}`);
                }
            }
        } catch (e) {
            // Ignore access errors
        }
    }
    return results;
}

console.log("🔍 Starting recursive secret scan...");
const secretWarnings = recursiveScan(process.cwd());
warnings.push(...secretWarnings);

/* Legacy specific file check removed in favor of recursive scan */


// 4. Report
console.log("🛡️ Security Sentinel Scan Report");
console.log("===============================");

if (foundThreats.length > 0) {
    console.log("\n🛑 THREATS DETECTED (ACTION REQUIRED):");
    foundThreats.forEach(t => console.log(t));
}

if (warnings.length > 0) {
    console.log("\n⚠️ WARNINGS (INVESTIGATE):");
    warnings.forEach(w => console.log(w));
}

if (foundThreats.length === 0 && warnings.length === 0) {
    console.log("\n✅ System Clean. No active threats or warnings.");
} else {
    // Exit code 1 if threats found (useful for CI/hooks)
    if (foundThreats.length > 0) process.exit(1);
}
