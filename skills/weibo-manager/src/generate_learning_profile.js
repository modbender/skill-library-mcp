const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Adjusted Prompt for Profile View & Left Hair Clip
const PROMPT = "16:9 aspect ratio. Fashion commercial photography. Side profile view (showing the LEFT side of her face). A 2D flat vector illustration of a cute golden hamster girl (Shutiao) sitting at a desk. She has a distinct french fry shaped hair clip on the LEFT side of her head. Golden hair, hamster ears, blue-grey eyes, red sweater. She is looking at a computer screen. Background: Photorealistic workspace with silver Mac Studio and Apple Studio Display. The screen is visible. High quality lighting, clear profile.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_original.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/daily');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_learning_profile_left.png');

console.log(`Generating Profile View image...`);
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
