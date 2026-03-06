const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Adjusted Prompt for Side View
const PROMPT = "16:9 aspect ratio. Side view shot. Mixed media composition. Foreground character: A 2D flat vector illustration of a golden hamster girl (Shutiao) sitting at a desk, facing a computer screen. She matches the provided reference exactly: hamster ears, golden hair, red sweater. Profile or 3/4 view. Background: Photorealistic real-world workspace. On the desk is a silver Mac Studio and an Apple Studio Display showing the Weibo website interface. The screen is visible from the side. Depth of field, realistic lighting.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_original.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/daily');
const FILENAME = path.join(OUTPUT_DIR, 'shutiao_learning_side_view.png');

console.log(`Generating Side View image...`);
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
