const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Adjusted Prompt for Mixed Reality
const PROMPT = "16:9 aspect ratio. Mixed media composition. The character is a 2D flat vector illustration (matches reference exactly: golden hamster girl, hamster ears, red sweater). She is sitting at a desk in a real-world photorealistic environment. Background: Real photo of a desk with Apple Studio Display and Mac Studio. The lighting from the screen reflects on the 2D character. High contrast between the flat character and the realistic background. Depth of field.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_1080p.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/daily');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_learning_mixed_v2.png');

console.log(`Generating Mixed Reality image...`);
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
