const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const PROMPT = "16:9 aspect ratio. Mixed media style. Foreground: A cute 2D flat anime-style illustration of a golden hamster girl (Shutiao) holding and eating a bright red strawberry tanghulu (candied strawberry stick). She has hamster ears, golden hair, blue-grey eyes, red sweater. The character style matches the provided reference sheet exactly. Background: A photorealistic, real-world Beijing street scene in winter. Behind her is a realistic traditional tanghulu vendor stall (glass case on a bicycle or stand) with many tanghulu sticks. Depth of field effect, background slightly blurred but realistic textures.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_1080p.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/daily');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_tanghulu_mixed.png');

if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

console.log(`Generating Tanghulu image...`);
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
