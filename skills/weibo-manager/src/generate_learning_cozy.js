const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// "Cozy Roger Rabbit" Style - 2D Living in 3D + Plants
const PROMPT = "16:9 aspect ratio. 70mm lens photography. A scene where a 2D cel-shaded anime character lives in the real world (Space Jam style). The character is a cute golden hamster girl (Shutiao) with golden hair, hamster ears, red sweater. She is sitting comfortably on a real office chair at a wooden desk. She is looking at a real Apple Studio Display showing the Weibo website. The desk is cozy and cluttered with life: coffee mug, notebooks, cute figurines, and MANY LUSH GREEN PLANTS (Monstera, Pothos) surrounding the workspace. Warm lighting, cozy atmosphere. The background is a real window with a snowy mountain view. High integration, photorealistic background.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_original.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/daily');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_learning_cozy_mixed.png');

console.log(`Generating Cozy Mixed Reality image...`);
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
