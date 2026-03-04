
// Load .env from skill folder only (least-privilege: never read parent .env)
require('dotenv').config({ path: require('path').resolve(__dirname, '.env') });
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

// Constants
const SKILL_ROOT = __dirname;
const DIRECTOR_SCRIPT = path.join(SKILL_ROOT, 'src/director.js');
const OUTPUT_DIR = path.join(SKILL_ROOT, 'output');
const TEMP_DIR = path.join(SKILL_ROOT, 'temp');
const FINAL_VIDEO = path.join(OUTPUT_DIR, 'final_fixed_voice.mp4');
const SEND_SCRIPT = path.join(SKILL_ROOT, 'src/send_video_pro.js');

// Ensure temp dir
if (!fs.existsSync(TEMP_DIR)) fs.mkdirSync(TEMP_DIR, { recursive: true });

// Helper: Run command
function run(cmd) {
    try {
        execSync(cmd, { stdio: 'inherit' });
    } catch (e) {
        console.error(`❌ Command failed: ${cmd}`);
        process.exit(1);
    }
}

// Usage
if (process.argv.length < 3) {
    console.log("Usage: node run.js --target <open_id> [--script <json_string_or_file>] [--preview]");
    process.exit(0);
}

// Parse Args
const args = process.argv.slice(2);
let targetId = "";
let scriptContent = "";
let isPreview = false;

for (let i = 0; i < args.length; i++) {
    if (args[i] === '--target') targetId = args[++i];
    else if (args[i] === '--script') scriptContent = args[++i];
    else if (args[i] === '--preview') isPreview = true;
}

// Optional Script (Default Demo if Missing)
const tempScriptPath = path.join(TEMP_DIR, `script_${Date.now()}.json`);

if (scriptContent) {
    try {
        // Check if input is a file path
        if (fs.existsSync(scriptContent)) {
            // It's a file, copy it to temp to ensure consistency
            fs.copyFileSync(scriptContent, tempScriptPath);
        } else {
            // Assume JSON string
            // Validate JSON
            JSON.parse(scriptContent); 
            fs.writeFileSync(tempScriptPath, scriptContent);
        }
    } catch (e) {
        console.error("Invalid script JSON or file path:", e.message);
        process.exit(1);
    }
} else {
    console.log("⚠️ No script provided. Running demo mode.");
}

console.log(`🎬 [Anima] Starting production...`);
if (scriptContent) console.log(`   Script: ${tempScriptPath}`);
console.log(`   Target: ${targetId || "None (Generation Only)"}`);

// 1. Run Director
// If no script provided, director uses internal demo.
// If script provided, we pass the path.
const scriptArg = scriptContent ? `"${tempScriptPath}"` : "";
try {
    execSync(`node "${DIRECTOR_SCRIPT}" ${scriptArg}`, { stdio: 'inherit' });
} catch (e) {
    console.error("❌ Director failed.");
    process.exit(1);
}

if (!fs.existsSync(FINAL_VIDEO)) {
    console.error("❌ Output video not found.");
    process.exit(1);
}

// 2. Upload & Send (if target provided)
if (targetId && !isPreview) {
    console.log(`🚀 [Anima] Uploading and sending to ${targetId}...`);
    try {
        // Pass targetId and video path to send_video_pro.js
        execSync(`node "${SEND_SCRIPT}" "${targetId}" "${FINAL_VIDEO}"`, { stdio: 'inherit' });
    } catch (e) {
        console.error("❌ Delivery failed.");
        process.exit(1);
    }
} else {
    console.log(`✅ [Anima] Video generated at: ${FINAL_VIDEO}`);
}

// Cleanup
if (scriptContent && fs.existsSync(tempScriptPath)) {
    try { fs.unlinkSync(tempScriptPath); } catch(e) {}
}
