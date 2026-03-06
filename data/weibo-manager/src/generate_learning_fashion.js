const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Adjusted Prompt for Fashion/Ad Style + Over-the-shoulder
const PROMPT = "16:9 aspect ratio. High-end fashion commercial photography style. Over-the-shoulder view from behind. A 2D flat vector illustration of a golden hamster girl (Shutiao) sitting at a minimalist designer desk. We see her back/side profile (hamster ears, golden hair, red sweater) and she is looking at the computer screen. On the desk is a silver Mac Studio and an Apple Studio Display. The screen clearly shows the Weibo social media interface. Lighting is dramatic, studio quality, cool tones, very clean and modern. Apple advertisement aesthetic. Mixed media: 2D character in 3D photorealistic environment.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_original.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/daily');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_learning_fashion.png');

console.log(`Generating Fashion Ad Style image...`);
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
