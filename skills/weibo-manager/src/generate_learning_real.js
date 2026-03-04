const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Ultimate Prompt for Realism
const PROMPT = "16:9 aspect ratio. 70mm lens. A highly photorealistic, real-world photography of a clean, modern workspace. On the desk is a silver Mac Studio and an Apple Studio Display. The screen clearly shows the Weibo website. Next to the monitor is a cute, 2D anime-style paper cutout or AR projection of a golden hamster girl (Shutiao) standing on the desk. She has hamster ears, golden hair, red sweater. The background is a real floor-to-ceiling window with white curtains, looking out at a majestic real snow mountain range. Natural daylight, realistic textures, reflections, depth of field. 8k, raw photo quality.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_original.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/daily');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_learning_real_v4.png');

console.log(`Generating Real World + AR Character...`);
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
