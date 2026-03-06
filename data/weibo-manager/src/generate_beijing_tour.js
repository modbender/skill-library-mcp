const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 9 Prompts based on the plan
const BASE_PROMPT = "Flat vector illustration, poster style, 16:9 aspect ratio. Cute golden hamster girl (Shutiao) with hamster ears, golden hair, blue-grey eyes, wearing a red sweater and white loose socks. The character matches the provided reference sheet exactly.";

const SCENES = [
    { name: "01_hutong", desc: "Riding a yellow shared bicycle through Wudaoying Hutong in the morning. Sunlight filtering through trees onto grey bricks. Beijing alleyway atmosphere." },
    { name: "02_tiantan", desc: "Standing in front of the Hall of Prayer for Good Harvests (Temple of Heaven). Mimicking the pose of a stone lion statue (or mythical beast) nearby, looking a bit dazed/cute. Blue sky." },
    { name: "03_duck", desc: "Sitting at a restaurant table with a huge Peking Duck. Holding a rolled pancake (chunbing) in hand, eyes sparkling with excitement. Foodie vibe." },
    { name: "04_798", desc: "At 798 Art Zone, standing cool in front of a colorful graffiti wall. Holding a spray paint can, spraying a red heart shape on the wall. Street art style." },
    { name: "05_forbidden_city", desc: "Center piece. Standing against the red walls of the Forbidden City (Palace Museum). Holding a candied hawthorn stick (Tanghulu). majestic historical background." },
    { name: "06_beihai", desc: "Boating on Beihai Park lake. The White Dagoba is in the background with willow trees. Relaxed atmosphere, 'Let us sway twin oars' vibe." },
    { name: "07_cbd", desc: "Inside a high-rise building (Guomao Phase 3) looking out a large window at sunset. The CCTV Headquarters (Big Pants building) and busy traffic visible below. City skyline." },
    { name: "08_sanlitun", desc: "Night time at Sanlitun Taikoo Li. Neon lights, holding a giant bubble tea cup. Background shows a cool 3D screen. Trendy fashion vibe." },
    { name: "09_birdnest", desc: "Sitting on the steel beams of the Bird's Nest (National Stadium) at night. Surreal perspective, watching stars and city lights. Dreamy atmosphere." }
];

const REF_IMG = path.resolve('avatars/shutiao_setting_sheet.png');
const OUTPUT_DIR = path.resolve('skills/weibo-manager/assets/beijing_tour');

if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

console.log(`Starting generation for ${SCENES.length} images...`);

const generatedFiles = [];

for (const scene of SCENES) {
    const prompt = `${BASE_PROMPT} Scene: ${scene.desc}`;
    const filename = path.join(OUTPUT_DIR, `${scene.name}.png`);
    
    console.log(`Generating [${scene.name}]...`);
    
    // Command structure: uv run scripts/generate_image.py --prompt "..." --filename "..." -i "ref.png"
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

console.log('All done.');
console.log(JSON.stringify(generatedFiles));
