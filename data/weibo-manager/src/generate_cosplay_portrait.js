const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const PROMPT = "Photorealistic DSLR photo of a cute golden hamster girl (Shutiao) at a cosplay convention. Standing pose, looking at camera, happy smile. Real golden hair, fuzzy hamster ears, blue-grey eyes, red sweater, white loose socks. Background: blurred convention crowd, anime posters. High quality, 8k, cinematic lighting.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_9_16.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/cosplay');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_cosplay_portrait.png');

console.log(`Generating Portrait Cosplay photo...`);

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
