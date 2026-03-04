const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Refine Prompt - Focus on details using the previous successful composition as base
const PROMPT = "16:9 aspect ratio. 70mm lens photography. Mixed Reality. High quality refinement. A 2D cel-shaded anime golden hamster girl (Shutiao) sitting at a modern wooden desk. She is wearing a red sweater and white loose socks. Full body side profile view: her legs and bare thighs (Zettai Ryouiki) are clearly visible under the desk. She is typing on a SILVER APPLE MAGIC KEYBOARD. On the desk: A silver Mac Studio computer placed distinctly TO THE SIDE of the Apple Studio Display. The monitor shows the Weibo website. Background: LARGE GLASS WINDOW looking out at snow mountains. Photorealistic background, sharp details, cinematic lighting.";

// Use the previous output as the new reference
const REF_IMG = path.resolve('skills/weibo-manager/assets/daily/shutiao_learning_final_separated.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/daily');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_learning_final_refined.png');

console.log(`Refining Final image...`);
console.log(`Prompt: ${PROMPT}`);

// Using a lower resolution first to ensure structure is kept, then maybe upscale? 
// Or just 1K is fine. Gemini 3 Pro 1K is usually quite detailed.
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
