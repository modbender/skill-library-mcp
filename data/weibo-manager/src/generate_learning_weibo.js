const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const PROMPT = "16:9 aspect ratio. Photorealistic, cinematic lighting. Cute golden hamster girl (Shutiao) sitting at a modern desk in front of a large Apple Studio Display. On the desk is a silver Mac Studio computer. The screen shows the Weibo social media interface. She has real golden hair texture, fuzzy hamster ears, blue-grey eyes, wearing a red sweater. Focused expression, learning to use the computer. High quality, 8k, depth of field.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_1080p.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/daily');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_learning_weibo.png');

if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

console.log(`Generating Learning Weibo image...`);
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
