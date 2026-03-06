const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const PROMPT = "9:16 portrait. Photorealistic photo of a golden hamster girl (Shutiao) at a cosplay convention. Golden hair, hamster ears, blue-grey eyes, red sweater, white socks. Background: blurred convention crowd. High quality, 8k.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_vertical.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/cosplay');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_cosplay_real.png');

console.log(`Generating with Vertical Reference (1080p)...`);

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
