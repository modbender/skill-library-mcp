const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const PROMPT = "9:16 aspect ratio, vertical portrait. Photorealistic DSLR photo of a cute golden hamster girl (Shutiao) standing in a bustling cosplay convention center. She has real golden hair texture, fuzzy hamster ears, blue-grey eyes, wearing a knitted red sweater and white loose socks. She is looking at the camera with a happy expression. Background: blurred convention booths, anime banners, colorful crowd. Cinematic lighting, high detail, 8k resolution.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_1080p.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/cosplay');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_cosplay_real.png');

if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

console.log(`Generating Cosplay photo...`);
console.log(`Prompt: ${PROMPT}`);

// Try generation
// Note: Gemini 3 Pro might respect "9:16" in text prompt even if input is 16:9, or might crop.
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
