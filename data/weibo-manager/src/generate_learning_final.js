const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Final "Corrected" Style - Mac Studio visible, Window fix
const PROMPT = "16:9 aspect ratio. 70mm lens photography. Mixed Reality. A 2D cel-shaded anime golden hamster girl (Shutiao) sitting at a modern wooden desk. Golden hair, hamster ears, red sweater. She is typing on a SILVER APPLE MAGIC KEYBOARD (flat, minimalist). On the desk, clearly visible next to the monitor, is a SILVER MAC STUDIO computer (small metal box). The monitor is an Apple Studio Display showing the Weibo website. The desk has coffee and green plants. The background is a LARGE GLASS WINDOW (not a door) looking out from a high floor. Outside is a scenic view of snowy mountains in the distance (safe indoor perspective). Photorealistic background.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_original.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/daily');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_learning_final_corrected.png');

console.log(`Generating Final Corrected image...`);
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
