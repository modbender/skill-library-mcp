const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Refine Prompt - Explicitly move Mac Studio
const PROMPT = "16:9 aspect ratio. 2K resolution. Mixed Reality. High quality refinement. A 2D cel-shaded anime golden hamster girl (Shutiao) sitting at a modern wooden desk. She is wearing a red sweater and white loose socks. Full body side profile view: her legs and bare thighs are clearly visible under the desk. She is typing on a SILVER APPLE MAGIC KEYBOARD. On the desk: A silver Mac Studio computer placed distinctly TO THE LEFT or RIGHT of the Apple Studio Display. The Mac Studio is NOT under the monitor stand. It is a separate box on the desk surface. The monitor shows the Weibo website. Background: LARGE GLASS WINDOW looking out at snow mountains. Photorealistic background, sharp details, cinematic lighting.";

// Use the downloaded image
const REF_IMG = path.resolve('skills/weibo-manager/user_ref_correct.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/daily');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_learning_2k_fix_v2.png');

console.log(`Generating 2K Fix V2...`);
console.log(`Ref Image: ${REF_IMG}`);
console.log(`Prompt: ${PROMPT}`);

// Try 2K first
const cmd = `uv run skills/nano-banana-ultra/scripts/generate_image.py --prompt "${PROMPT}" --filename "${FILENAME}" -i "${REF_IMG}" --resolution 2K`;

try {
    execSync(cmd, { stdio: 'inherit' });
    if (fs.existsSync(FILENAME)) {
        console.log(`✅ Saved to ${FILENAME}`);
    } else {
        console.error(`❌ Failed to generate`);
    }
} catch (e) {
    console.error(`❌ Error:`, e.message);
}
