const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// "Roger Rabbit" Style - 2D Living in 3D
const PROMPT = "16:9 aspect ratio. 70mm lens photography. A scene where a 2D cel-shaded anime character lives in the real world (Space Jam style). The character is a cute golden hamster girl (Shutiao) with golden hair, hamster ears, red sweater. She is sitting comfortably on a real office chair at a modern desk. She is looking at a real Apple Studio Display showing the Weibo website. Her hands are on the real keyboard. The lighting from the real window (snowy mountain view) casts accurate shadows on her 2D body. High integration, photorealistic background, cinematic.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_original.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/daily');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_learning_dimension_break.png');

console.log(`Generating Dimensional Break image...`);
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
