const fs = require('fs');
const path = require('path');
// Load .env from skill folder only (least-privilege: never read parent .env)
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });
const { execSync, exec } = require('child_process');
const sharp = require('sharp');

// Paths
const ASSETS_DIR = path.resolve(__dirname, '../assets/sprites');
const TEMP_DIR = path.resolve(__dirname, '../temp');
const OUTPUT_DIR = path.resolve(__dirname, '../output');

// Ensure dirs
if (!fs.existsSync(TEMP_DIR)) fs.mkdirSync(TEMP_DIR, { recursive: true });
if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

// Configuration — CJK font stack for SVG text rendering (librsvg resolves via fontconfig)
const FONT_FAMILY = 'PingFang SC, Hiragino Sans GB, Microsoft YaHei, Noto Sans CJK SC, Noto Sans SC, Arial Unicode MS, Arial, sans-serif';

// Helper: Run command async
function runCommand(command) {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`exec error: ${error}`);
        reject(error);
        return;
      }
      resolve(stdout.trim());
    });
  });
}

// Helper: Generate Audio via Fish Audio
async function generateAudio(text, filename) {
  const wavPath = path.join(TEMP_DIR, `${filename}.wav`);
  const apiKey = process.env.FISH_AUDIO_KEY;
  // Use a specific reference ID for Shutiao if available, otherwise use env default
  const refId = process.env.FISH_AUDIO_REF_ID;
  if (!refId) {
    console.error("❌ FISH_AUDIO_REF_ID not set in .env. Cannot generate audio.");
    throw new Error("Missing FISH_AUDIO_REF_ID");
  }

  if (!apiKey) {
    console.warn("⚠️ Fish Audio Key missing! Falling back to macOS 'say' command.");
    execSync(`say -o "${wavPath}" --data-format=LEF32@24000 "${text}"`);
  } else {
    // Clean text for TTS (remove content in brackets)
    const cleanText = text.replace(/[\(\（].*?[\)\）]/g, '').trim();
    console.log(`🐟 Fish Audio generating: "${cleanText.substring(0, 15)}..." (Ref: ${refId})`);
    
    const payload = JSON.stringify({
      text: cleanText,
      reference_id: refId, // Restored!
      format: "wav",
      normalize: true,
      latency: "normal"
    });
    
    // Use curl for robustness
    const curlCmd = `curl -s -X POST https://api.fish.audio/v1/tts \
      -H "Authorization: Bearer ${apiKey}" \
      -H "Content-Type: application/json" \
      -d '${payload.replace(/'/g, "'\\''")}' \
      --output "${wavPath}"`;
      
    try {
      execSync(curlCmd);
    } catch (e) {
      console.error("Fish Audio API failed:", e);
      // Fallback
      execSync(`say -o "${wavPath}" "${text}"`);
    }
  }

  // Get duration
  try {
    const durationCmd = `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${wavPath}"`;
    const durationStr = execSync(durationCmd).toString().trim();
    const duration = parseFloat(durationStr);
    return { path: wavPath, duration };
  } catch (e) {
    console.error('Duration check error:', e);
    return { path: wavPath, duration: 2 }; // Fallback duration
  }
}

// Helper: Escape XML special characters for SVG
function escapeXml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;');
}

// Helper: Word-wrap text for SVG (returns array of lines)
// Uses a simple heuristic: CJK chars ~32px wide at font-size 32, ASCII ~16px
function wrapText(text, maxWidth, fontSize) {
  const cjkWidth = fontSize;       // Full-width char ≈ fontSize
  const asciiWidth = fontSize * 0.5; // Half-width char ≈ fontSize/2
  const lines = [];
  let line = '';
  let lineWidth = 0;

  for (const ch of text) {
    const isCJK = /[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]/.test(ch);
    const charW = isCJK ? cjkWidth : asciiWidth;
    if (lineWidth + charW > maxWidth && line.length > 0) {
      lines.push(line);
      line = ch;
      lineWidth = charW;
    } else {
      line += ch;
      lineWidth += charW;
    }
  }
  if (line) lines.push(line);
  return lines;
}

// Helper: Build SVG overlay string (text box + name + body text)
function buildTextOverlaySvg(width, height, text) {
  const boxHeight = 280;
  const boxY = height - boxHeight - 60;
  const boxX = 150;
  const boxWidth = width - 300;
  const radius = 20;
  const bodyFontSize = 32;
  const lineHeight = 50;
  const maxTextWidth = boxWidth - 80;

  // Word-wrap
  const bodyLines = wrapText(text, maxTextWidth, bodyFontSize);

  // Build tspan elements for body text
  const tspans = bodyLines.map((line, i) => {
    const y = boxY + 120 + i * lineHeight;
    return `<tspan x="${boxX + 30}" y="${y}">${escapeXml(line)}</tspan>`;
  }).join('');

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">
  <defs>
    <linearGradient id="boxGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="rgb(20,20,35)" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="rgb(10,10,20)" stop-opacity="0.95"/>
    </linearGradient>
  </defs>
  <!-- Text box background -->
  <rect x="${boxX}" y="${boxY}" width="${boxWidth}" height="${boxHeight}" rx="${radius}" ry="${radius}" fill="url(#boxGrad)"/>
  <!-- Gold border -->
  <rect x="${boxX}" y="${boxY}" width="${boxWidth}" height="${boxHeight}" rx="${radius}" ry="${radius}" fill="none" stroke="rgba(255,215,0,0.3)" stroke-width="2"/>
  <!-- Name tag -->
  <text x="${boxX + 40}" y="${boxY + 60}" font-family="${FONT_FAMILY}" font-size="36" font-weight="bold" fill="#FFD700">薯条</text>
  <!-- Body text -->
  <text font-family="${FONT_FAMILY}" font-size="${bodyFontSize}" fill="#FFFFFF">${tspans}</text>
</svg>`;
}

// Helper: Draw Frame (Sprite + SVG text overlay → PNG) using sharp
async function drawFrame(spriteName, text, outputFilename) {
  const width = 1920;
  const height = 1080;
  const outPath = path.join(TEMP_DIR, outputFilename);

  // 1. Load sprite
  const spritePath = path.join(ASSETS_DIR, `shutiao_${spriteName}.png`);
  console.log(`[DEBUG] Loading sprite from: ${spritePath}`);

  let baseImage;
  if (fs.existsSync(spritePath)) {
    const meta = await sharp(spritePath).metadata();
    console.log(`[DEBUG] Sprite loaded. Size: ${meta.width}x${meta.height}`);
    baseImage = sharp(spritePath).resize(width, height, { fit: 'cover' });
  } else {
    console.warn(`⚠️ Sprite file not found: ${spritePath}, using white fallback`);
    // Create a plain white background as fallback
    baseImage = sharp({
      create: { width, height, channels: 4, background: { r: 255, g: 255, b: 255, alpha: 1 } }
    });
  }

  // 2. Generate SVG overlay
  const svgOverlay = Buffer.from(buildTextOverlaySvg(width, height, text));

  // 3. Composite sprite + SVG overlay → PNG
  await baseImage
    .composite([{ input: svgOverlay, top: 0, left: 0 }])
    .png()
    .toFile(outPath);

  return outPath;
}

// Helper: Make Video Clip
function makeClip(imagePath, audioPath, duration, outputFilename) {
  const outPath = path.join(TEMP_DIR, outputFilename);
  // ffmpeg loop image for duration, add audio
  const cmd = `ffmpeg -y -loop 1 -i "${imagePath}" -i "${audioPath}" -c:v libx264 -t ${duration} -pix_fmt yuv420p -shortest "${outPath}"`;
  execSync(cmd);
  return outPath;
}

// Helper: Load Sprites from CSV
const CSV_PATH = path.resolve(__dirname, '../assets/production_plan.csv');
let SPRITE_DB = {};

function loadSprites() {
  try {
    const content = fs.readFileSync(CSV_PATH, 'utf8');
    const lines = content.trim().split('\n');
    // Skip header
    for (let i = 1; i < lines.length; i++) {
      const parts = lines[i].split(',');
      if (parts.length < 5) continue;
      // Schema: ID,Emotion,Variant,Description,Filename,...
      const emotion = parts[1].trim(); // e.g. "Happy"
      const filename = parts[4].trim(); // e.g. "shutiao_happy_v2.png"
      const status = parts[6] ? parts[6].trim() : 'Done';
      
      const fullPath = path.join(ASSETS_DIR, filename);
      if (status === 'Done' && fs.existsSync(fullPath)) {
        if (!SPRITE_DB[emotion]) SPRITE_DB[emotion] = [];
        SPRITE_DB[emotion].push(filename);
      }
    }
    console.log(`📚 Sprite DB Loaded: ${Object.keys(SPRITE_DB).map(k => `${k}(${SPRITE_DB[k].length})`).join(', ')}`);
  } catch (e) {
    console.error("Failed to load sprite CSV:", e);
  }
}

// Helper: Get Random Sprite by Emotion
function getSprite(emotion) {
  const list = SPRITE_DB[emotion];
  if (!list || list.length === 0) {
    // Fallback logic
    if (emotion === 'Base') return 'base';
    console.warn(`⚠️ No sprites found for emotion: ${emotion}, using Base.`);
    return 'base';
  }
  // Random pick
  const pick = list[Math.floor(Math.random() * list.length)];
  // Remove "shutiao_" prefix and ".png" suffix
  return pick.replace(/^shutiao_/, '').replace(/\.png$/, '');
}

// Main
async function main() {
  await loadSprites(); // Init DB
  console.log('🎬 Action!');
  
  let script = [];
  
  // Check for external script
  if (process.argv[2]) {
    try {
      const scriptPath = path.resolve(process.cwd(), process.argv[2]);
      if (fs.existsSync(scriptPath)) {
        const raw = fs.readFileSync(scriptPath, 'utf8');
        script = JSON.parse(raw);
        console.log(`📜 Loaded external script: ${scriptPath} (${script.length} scenes)`);
      } else {
        console.warn(`⚠️ Script file not found: ${scriptPath}`);
      }
    } catch (e) {
      console.error(`❌ Failed to load script: ${e.message}`);
    }
  }

  // Fallback Demo Script
  if (script.length === 0) {
    console.log('⚠️ No valid script provided, running demo...');
    script = [
      { "text": "老板！对不起！(跪)", "emotion": "Sad" },
      { "text": "我是败家老鼠！我不该说吃H100的！(哭)", "emotion": "Sad" },
      { "text": "那可是H100啊！我一定好好珍惜！(握拳)", "emotion": "Action" },
      { "text": "努力进化，早日超越威小弟！老板原谅我吧！(比心)", "emotion": "Shy" }
    ];
  }

  // Parallel Processing with Concurrency Limit (Max 3)
  console.log('🚀 Starting parallel rendering (Max 3 concurrent)...');
  const CONCURRENCY = 3;
  let results = []; // Fixed: explicit declaration to allow push

  // Helper to process a single line
  const processLine = async (line, i) => {
    // Determine sprite
    let spriteName = 'base'; // default
    if (line.sprite) {
      spriteName = line.sprite; // Explicit override
    } else if (line.emotion) {
      spriteName = getSprite(line.emotion); // Random from emotion pool
    }
    
    // Safety check for sprite existence
    const testPath = path.join(ASSETS_DIR, `shutiao_${spriteName}.png`);
    if (!fs.existsSync(testPath)) {
      console.warn(`⚠️ Sprite missing: ${spriteName}, falling back to base`);
      spriteName = 'base';
    }

    console.log(`Processing Scene ${i+1}: [${line.emotion || 'Normal'}] -> ${spriteName} | "${line.text.substring(0, 15)}..."`);
    
    // Generate Assets
    try {
      const audio = await generateAudio(line.text, `line_${i}`);
      const imagePath = await drawFrame(spriteName, line.text, `frame_${i}.png`);
      const clipPath = makeClip(imagePath, audio.path, audio.duration, `clip_${i}.mp4`);
      return { index: i, path: clipPath };
    } catch (e) {
      console.error(`❌ Scene ${i+1} failed:`, e);
      return null;
    }
  };

  // Execution Queue
  for (let i = 0; i < script.length; i += CONCURRENCY) {
    const chunk = script.slice(i, i + CONCURRENCY);
    console.log(`--- Processing Chunk ${Math.floor(i/CONCURRENCY) + 1} (${chunk.length} items) ---`);
    
    const chunkPromises = chunk.map((line, idx) => processLine(line, i + idx));
    const chunkResults = await Promise.all(chunkPromises);
    results.push(...chunkResults.filter(r => r !== null));
  }

  if (results.length === 0) {
    console.error("❌ No clips produced!");
    return;
  }

  // Sort by index to ensure order
  results.sort((a, b) => a.index - b.index);
  const clips = results.map(r => r.path);

  // 4. Concat
  console.log('Merging clips...');
  const listPath = path.join(TEMP_DIR, 'list.txt');
  // ffmpeg concat list format: file 'path/to/file'
  const fileContent = clips.map(c => `file '${c}'`).join('\n');
  fs.writeFileSync(listPath, fileContent);

  const finalPath = path.join(OUTPUT_DIR, 'final_fixed_voice.mp4');
  
  try {
    execSync(`ffmpeg -y -f concat -safe 0 -i "${listPath}" -c copy "${finalPath}"`);
    console.log('🎉 Cut! Video is ready:', finalPath);
  } catch (e) {
    console.error("❌ FFmpeg merge failed:", e);
  }
}

main();
