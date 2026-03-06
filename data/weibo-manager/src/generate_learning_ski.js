const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Adjusted Prompt for Ski Resort View + Minimalist
const PROMPT = "16:9 aspect ratio. Wide angle shot from the side-rear. A 2D flat vector illustration of a golden hamster girl (Shutiao) sitting at a modern minimalist desk. We see her left side profile (distinct french fry hair clip on left, golden hair, red sweater). She is looking at a SINGLE large Apple Studio Display on the desk. The screen shows the Weibo interface. Interior is very clean and empty, no clutter. Next to the desk is a huge floor-to-ceiling glass window with white curtains on the sides. Outside the window is a view of a ski resort (snowy slopes, ski lifts). Realistic lighting, high-end hotel room aesthetic. Only ONE monitor.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_original.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/daily');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_learning_ski_resort.png');

console.log(`Generating Ski Resort Workspace image...`);
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
