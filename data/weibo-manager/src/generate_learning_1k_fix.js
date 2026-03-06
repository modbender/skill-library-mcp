const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Refine Prompt - Explicitly move Mac Studio (same as 2k_fix but resolution 1K)
const PROMPT = "16:9 aspect ratio. Mixed Reality. High quality refinement. A 2D cel-shaded anime golden hamster girl (Shutiao) sitting at a modern wooden desk. She is wearing a red sweater and white loose socks. Full body side profile view: her legs and bare thighs are clearly visible under the desk. She is typing on a SILVER APPLE MAGIC KEYBOARD. On the desk: A silver Mac Studio computer placed distinctly TO THE LEFT or RIGHT of the Apple Studio Display. The Mac Studio is NOT under the monitor stand. It is a separate box on the desk surface. The monitor shows the Weibo website. Background: LARGE GLASS WINDOW looking out at snow mountains. Photorealistic background, sharp details, cinematic lighting.";

// Use the image provided by user
const REF_IMG = '/Users/runchen/.openclaw/media/inbound/61e90d48-a941-464f-a8b7-f1ee6208cd58.jpg';
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/daily');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_learning_1k_fix.png');

console.log(`Generating 1K Fix...`);
console.log(`Ref Image: ${REF_IMG}`);
console.log(`Prompt: ${PROMPT}`);

// Resolution 1K
const cmd = `uv run skills/nano-banana-ultra/scripts/generate_image.py --prompt "${PROMPT}" --filename "${FILENAME}" -i "${REF_IMG}" --resolution 1K`;

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
