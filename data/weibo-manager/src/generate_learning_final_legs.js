const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Final "Corrected" Style + Visible Legs/Socks
const PROMPT = "16:9 aspect ratio. 70mm lens photography. Mixed Reality. A 2D cel-shaded anime golden hamster girl (Shutiao) sitting at a modern wooden desk. She is wearing a red sweater and white loose socks. Full body side profile view: her legs and bare thighs (Zettai Ryouiki) are clearly visible under the desk. She is typing on a SILVER APPLE MAGIC KEYBOARD. On the desk: SILVER MAC STUDIO computer. The monitor is an Apple Studio Display showing the Weibo website. Cozy desk with plants. Background: LARGE GLASS WINDOW looking out at snow mountains. Photorealistic background.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_original.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/daily');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_learning_final_legs.png');

console.log(`Generating Final with Legs...`);
console.log(`Prompt: ${PROMPT}`);

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
