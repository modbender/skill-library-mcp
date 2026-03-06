const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const WORKSPACE_ROOT = path.join(__dirname, '../../');
const SKILLS_DIR = path.join(WORKSPACE_ROOT, 'skills');
const VETTER_BIN = path.join(__dirname, 'vet.js');

function runCommand(cmd, cwd) {
    try {
        return execSync(cmd, { cwd, encoding: 'utf8', stdio: 'pipe' });
    } catch (e) {
        return { error: true, message: e.message, stdout: e.stdout };
    }
}

function safeUpdateRepo(repoPath, name) {
    console.log(`\n--- 📦 Updating Repository: [${name}] ---`);
    
    // 1. Check if git repo
    if (!fs.existsSync(path.join(repoPath, '.git')) && !fs.lstatSync(repoPath).isSymbolicLink()) {
        console.log(`ℹ️  Skipping: ${name} (Not a direct Git repository)`);
        return;
    }

    // 2. Git Pull
    console.log(`📥 Pulling latest changes...`);
    const pullResult = runCommand('git pull', repoPath);
    
    if (pullResult.error) {
        if (pullResult.message.includes('conflict')) {
            console.log(`🚨 MERGE CONFLICT in ${name}! Please resolve manually.`);
        } else {
            console.log(`❌ Pull failed: ${pullResult.message.split('\n')[0]}`);
        }
        return;
    }

    console.log(pullResult.trim());

    if (pullResult.includes('Already up to date.')) {
        console.log(`✅ ${name} is up to date.`);
        return;
    }

    // 3. Identify and Vet changes
    console.log(`🔍 Identifying changed files...`);
    const diffOutput = runCommand('git diff --name-only HEAD@{1} HEAD', repoPath);
    if (typeof diffOutput !== 'string') return;

    const changedFiles = diffOutput.split('\n').filter(f => f && fs.existsSync(path.join(repoPath, f)));

    if (changedFiles.length > 0) {
        console.log(`🔬 Vetting ${changedFiles.length} updated files...`);
        changedFiles.forEach(f => {
            const fullPath = path.join(repoPath, f);
            try {
                const auditOutput = execSync(`node "${VETTER_BIN}" "${fullPath}"`, { encoding: 'utf8' });
                const verdict = auditOutput.match(/\[Verdict\]:\n(.*?)\n/);
                console.log(` - [${f}]: ${verdict ? verdict[1] : 'Unknown'}`);
            } catch (e) {
                console.error(` ❌ Error vetting ${f}: ${e.message}`);
            }
        });
        console.log(`⚠️  Base hashes changed for ${name}. Remember to run scan_all.js if trusted.`);
    }
}

function startTargetedUpdate() {
    console.log("🚀 Starting Targeted Safe Update (Tool Integrity Mode)");
    
    // ONLY update the hex-vetter directory itself
    const toolDir = __dirname;
    safeUpdateRepo(toolDir, 'Skill: Hex Vetter (Self)');

    console.log("\n✨ Targeted Update Process Complete.");
}

startTargetedUpdate();
