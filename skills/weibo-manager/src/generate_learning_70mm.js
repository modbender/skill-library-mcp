const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Adjusted Prompt for 70mm Portrait
const PROMPT = "16:9 aspect ratio. 70mm lens portrait photography. Side profile close-up. A 2D flat vector illustration of a golden hamster girl (Shutiao) sitting at a desk. We clearly see her left side face, hamster ears, golden hair, red sweater. She is looking at an Apple Studio Display on the desk. The screen shows the Weibo social media interface. The desk is clean, minimalist, with some green indoor plants. Through the window behind, there is a realistic view of majestic snowy mountains. Natural light, photorealistic environment, depth of field.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_original.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/daily');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_learning_70mm.png');

console.log(`Generating 70mm Portrait...`);
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
