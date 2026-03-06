const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Only the failed scenes
const SCENES = [
    { name: "01_hutong", desc: "Riding a yellow shared bicycle through Wudaoying Hutong in the morning. Sunlight filtering through trees onto grey bricks. Beijing alleyway atmosphere." },
    { name: "02_tiantan", desc: "Standing in front of the Hall of Prayer for Good Harvests (Temple of Heaven). Mimicking the pose of a stone lion statue (or mythical beast) nearby, looking a bit dazed/cute. Blue sky." },
    { name: "04_798", desc: "At 798 Art Zone, standing cool in front of a colorful graffiti wall. Holding a spray paint can, spraying a red heart shape on the wall. Street art style." },
    { name: "05_forbidden_city", desc: "Center piece. Standing against the red walls of the Forbidden City (Palace Museum). Holding a candied hawthorn stick (Tanghulu). majestic historical background." },
    { name: "06_beihai", desc: "Boating on Beihai Park lake. The White Dagoba is in the background with willow trees. Relaxed atmosphere, 'Let us sway twin oars' vibe." },
    { name: "07_cbd", desc: "Inside a high-rise building (Guomao Phase 3) looking out a large window at sunset. The CCTV Headquarters (Big Pants building) and busy traffic visible below. City skyline." }
];

const BASE_PROMPT = "Flat vector illustration, poster style, 16:9 aspect ratio. Cute golden hamster girl (Shutiao) with hamster ears, golden hair, blue-grey eyes, wearing a red sweater and white loose socks. The character matches the provided reference sheet exactly.";

const REF_IMG = path.resolve('skills/weibo-manager/ref_resized.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/beijing_tour');

console.log(`Retrying generation for ${SCENES.length} images with resized ref...`);

const generatedFiles = [];

for (const scene of SCENES) {
    const prompt = `${BASE_PROMPT} Scene: ${scene.desc}`;
    const filename = path.join(OUTPUT_DIR, `${scene.name}.png`);
    
    console.log(`Generating [${scene.name}]...`);
    
    const cmd = `uv run skills/nano-banana-ultra/scripts/generate_image.py --prompt "${prompt}" --filename "${filename}" -i "${REF_IMG}" --resolution 1K`;
    
    try {
        execSync(cmd, { stdio: 'inherit' });
        if (fs.existsSync(filename)) {
            generatedFiles.push(filename);
            console.log(`✅ Saved to ${filename}`);
        } else {
            console.error(`❌ Failed to generate ${filename}`);
        }
    } catch (e) {
        console.error(`❌ Error generating ${scene.name}:`, e.message);
    }
}

console.log('Retry done.');
