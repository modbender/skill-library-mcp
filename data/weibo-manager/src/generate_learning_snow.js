const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Adjusted Prompt for Snow Mountain View + Single Monitor
const PROMPT = "16:9 aspect ratio. Wide angle shot from the side-rear. A 2D flat vector illustration of a golden hamster girl (Shutiao) sitting at a modern glass desk. We see her left side profile (distinct french fry hair clip on left, golden hair, red sweater). She is looking at a SINGLE large Apple Studio Display on the desk. The screen shows the Weibo interface clearly. Next to the desk is a huge floor-to-ceiling glass window. Outside the window is a breathtaking view of majestic snowy mountains under a clear blue sky. Realistic lighting, reflection on the glass, high-end workspace aesthetic. Only ONE monitor.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_original.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/daily');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_learning_snow_mountain.png');

console.log(`Generating Snow Mountain Workspace image...`);
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
