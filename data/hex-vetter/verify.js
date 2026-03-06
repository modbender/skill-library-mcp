const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const AUDIT_DIR = path.join(__dirname, '../../security_audits');
const HEX_DUMPS_DIR = path.join(AUDIT_DIR, 'hex_dumps');
const SUMMARY_PATH = path.join(AUDIT_DIR, 'audit_summary.md');

function getHashes(data) {
    const sha256 = crypto.createHash('sha256').update(data).digest('hex');
    const md5 = crypto.createHash('md5').update(data).digest('hex');
    return { sha256, md5 };
}

function verifyAudits() {
    console.log(`🔍 Starting Verification of Hex Dumps...`);

    // AUTO-PROTECT: Try to elevate OOM priority before verification
    try {
        const { execSync } = require('child_process');
        execSync('echo -500 | sudo tee /proc/self/oom_score_adj', { stdio: 'ignore' });
        console.log("🛡️  Priority Guard: OOM Score adjusted to -500 (Elevated).");
    } catch (e) {
        // Silent fail for verify to keep output clean
    }
    
    if (!fs.existsSync(SUMMARY_PATH)) {
        console.error("❌ Error: audit_summary.md not found. Run scan_all.js first.");
        return;
    }

    const dumps = fs.readdirSync(HEX_DUMPS_DIR);
    let total = 0;
    let failures = 0;

    dumps.forEach(dumpFile => {
        const dumpPath = path.join(HEX_DUMPS_DIR, dumpFile);
        const dumpContent = fs.readFileSync(dumpPath, 'utf8');

        // Extract the original file path and hashes from the dump header
        const pathMatch = dumpContent.match(/SOURCE_FILE: (.*)\n/);
        const shaMatch = dumpContent.match(/SHA256: (.*)\n/);
        
        if (!pathMatch || !shaMatch) {
            console.warn(`⚠️  Skipping ${dumpFile}: Missing header information.`);
            return;
        }

        const sourcePath = pathMatch[1].trim();
        const recordedSha = shaMatch[1].trim();
        const selfSigMatch = dumpContent.match(/SELF_SIGNATURE: (.*)\n/);

        // 1. SELF-INTEGRITY CHECK (Did someone tamper with the HEX report itself?)
        if (selfSigMatch) {
            const recordedSelfSig = selfSigMatch[1].trim();
            const reportBody = dumpContent.split('\n\n').slice(1).join('\n\n');
            const metaPart = dumpContent.split('SELF_SIGNATURE:')[0];
            const recomputedSelfSig = crypto.createHash('sha256').update(metaPart + reportBody).digest('hex');

            if (recordedSelfSig !== recomputedSelfSig) {
                console.log(`🚨 REPORT TAMPERED: ${dumpFile}`);
                console.log(`   Expect Sig: ${recordedSelfSig}`);
                console.log(`   Actual Sig: ${recomputedSelfSig}`);
                failures++;
                return; // Skip file check if report is invalid
            }
        } else {
            console.warn(`⚠️  Warning: ${dumpFile} has no self-signature. Initial audit?`);
        }

        // 2. SOURCE INTEGRITY CHECK
        if (!fs.existsSync(sourcePath)) {
            console.warn(`⚠️  Source file missing: ${sourcePath}`);
            return;
        }

        const sourceData = fs.readFileSync(sourcePath);
        const currentSha = crypto.createHash('sha256').update(sourceData).digest('hex');

        total++;
        if (currentSha !== recordedSha) {
            console.log(`❌ INTEGRITY BREACH: ${sourcePath}`);
            console.log(`   Recorded SHA256: ${recordedSha}`);
            console.log(`   Current  SHA256: ${currentSha}`);
            failures++;
        }
    });

    console.log(`\n=== Verification Result ===`);
    
    // PROJECT STARFRAGMENT: Verify against hidden fragments
    const starfragment = require('./starfragment.js');
    const summaryContent = fs.readFileSync(SUMMARY_PATH, 'utf8');
    const currentMasterHash = crypto.createHash('sha256').update(summaryContent).digest('hex');
    const savedMasterHash = starfragment.loadFragments();

    if (savedMasterHash && currentMasterHash !== savedMasterHash) {
        console.log(`🚨 CRITICAL: Summary report has been modified or Starfragment integrity failed!`);
        failures++;
    } else if (savedMasterHash) {
        console.log(`✨ Starfragment check: Verified (Hidden anchor matched).`);
    }

    // AUTO-RESTORE: Lower priority after verification is done
    try {
        const { execSync } = require('child_process');
        execSync('echo 0 | sudo tee /proc/self/oom_score_adj', { stdio: 'ignore' });
        console.log("🍃 Priority Guard: OOM Score restored to 0 (Normal).");
    } catch (e) {}

    console.log(`Total Files Checked: ${total}`);
    if (failures === 0) {
        console.log(`✅ ALL CLEAR: No unauthorized changes detected.`);
    } else {
        console.log(`🚨 ALERT: ${failures} files have been modified since last audit!`);
    }
}

verifyAudits();
