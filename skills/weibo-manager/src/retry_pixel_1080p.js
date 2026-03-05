const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Simplified Prompts for stability
const BASE_PROMPT = "Pixel art style, 16-bit, 16:9. Cute golden hamster girl (Shutiao), hamster ears, golden hair, blue-grey eyes, red sweater, white loose socks. Matching reference exactly.";

const SCENES = [
    { name: "01_hutong", desc: "Riding yellow bike in Hutong morning. Sunlight on grey bricks." },
    { name: "03_duck", desc: "Eating Peking Duck at restaurant table. Holding pancake. Happy expression." },
    { name: "05_forbidden_city", desc: "Standing against Forbidden City red walls. Holding Tanghulu. Historical background." },
    { name: "06_beihai", desc: "Boating on Beihai Park lake. White Dagoba background. Willow trees." },
    { name: "07_cbd", desc: "Inside high-rise looking at sunset city skyline. CCTV building visible." },
    { name: "08_sanlitun", desc: "Night at Sanlitun. Neon lights, holding bubble tea. 3D screen background." },
    { name: "09_birdnest", desc: "Sitting on Bird's Nest steel beams at night. Starry sky." }
];

const REF_IMG = path.resolve('skills/weibo-manager/ref_1080p.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/beijing_tour_pixel');

console.log(`Retrying 7 images with simplified prompts and 1080p ref...`);

for (const scene of SCENES) {
    const prompt = `${BASE_PROMPT} Scene: ${scene.desc}`;
    const filename = path.join(OUTPUT_DIR, `${scene.name}.png`);
    
    console.log(`Generating [${scene.name}]...`);
    
    // Retry loop
    let retries = 3;
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
            console.error(`⚠️ Attempt failed for ${scene.name}. Retries left: ${retries - 1}`);
            retries--;
            if (retries === 0) console.error(`❌ Finally failed: ${scene.name}`);
            // Wait 5s before retry
            execSync('sleep 5');
        }
    }
}

console.log('Retry batch done.');
