const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Ultra-simplified Prompts
// Removing detailed descriptions, keeping only essential style and subject.
const BASE_PROMPT = "Pixel art style, 16:9. Cute golden hamster girl (Shutiao). Matching reference exactly.";

const SCENES = [
    { name: "01_hutong", desc: "Riding yellow bike in Beijing Hutong." },
    { name: "06_beihai", desc: "Boating on a lake with white tower background." },
    { name: "07_cbd", desc: "Watching city sunset from high window." },
    { name: "08_sanlitun", desc: "Holding bubble tea in neon city night." },
    { name: "09_birdnest", desc: "Sitting on steel beam under starry night." }
];

const REF_IMG = path.resolve('skills/weibo-manager/ref_1080p.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/beijing_tour_pixel');

console.log(`Final retry for 5 images with ultra-short prompts...`);

for (const scene of SCENES) {
    const prompt = `${BASE_PROMPT} Action: ${scene.desc}`;
    const filename = path.join(OUTPUT_DIR, `${scene.name}.png`);
    
    console.log(`Generating [${scene.name}]... Prompt: ${prompt}`);
    
    let retries = 2;
    while (retries > 0) {
        try {
            const cmd = `uv run skills/nano-banana-ultra/scripts/generate_image.py --prompt "${prompt}" --filename "${filename}" -i "${REF_IMG}" --resolution 1K`;
            execSync(cmd, { stdio: 'inherit' });
            
            if (fs.existsSync(filename)) {
                console.log(`✅ Saved to ${filename}`);
                break;
            } else {
                throw new Error("File not created");
            }
        } catch (e) {
            console.error(`⚠️ Attempt failed for ${scene.name}.`);
            retries--;
            if (retries > 0) execSync('sleep 3');
        }
    }
}

console.log('Final retry sequence finished.');
