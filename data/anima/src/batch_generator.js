const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Load .env from skill folder only (least-privilege: never read parent .env)
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

// Simple CSV Parser/Writer
const CSV_PATH = path.resolve(__dirname, '../assets/production_plan.csv');
const BASE_IMG = path.resolve(__dirname, '../assets/sprites/shutiao_base_1k.png');

function readCSV() {
  const content = fs.readFileSync(CSV_PATH, 'utf8');
  const lines = content.trim().split('\n');
  const headers = lines[0].split(',');
  return lines.slice(1).map(line => {
    const values = line.split(',');
    return headers.reduce((obj, header, index) => {
      obj[header] = values[index] ? values[index].trim() : '';
      return obj;
    }, {});
  });
}

function writeCSV(data) {
  const headers = ['ID','Emotion','Variant','Description','Filename','Prompt','Status'];
  const content = [headers.join(',')].concat(data.map(row => headers.map(h => row[h]).join(','))).join('\n');
  fs.writeFileSync(CSV_PATH, content);
}

// Image generation via Gemini API (self-contained, no external skill dependency)
// Requires GEMINI_API_KEY in .env
// Falls back to a simple file-copy placeholder if no key is set.
function generate(row) {
  const output = path.resolve(__dirname, '../assets/sprites', row.Filename);
  const prompt = `Same image, change facial expression to ${row.Prompt}. Keep clothes and background exactly same.`;
  const apiKey = process.env.GEMINI_API_KEY;

  console.log(`Generating ${row.ID}: ${row.Description}...`);

  const outputDir = path.dirname(output);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  if (!apiKey) {
    console.error("❌ GEMINI_API_KEY not set in .env. Cannot generate sprites.");
    console.error("   Set GEMINI_API_KEY in your .env file to use Gemini image generation.");
    return false;
  }

  try {
    // Read base image and encode to base64
    const imgBuffer = fs.readFileSync(BASE_IMG);
    const imgBase64 = imgBuffer.toString('base64');

    // Build Gemini API request payload
    const payload = JSON.stringify({
      contents: [{
        parts: [
          { text: prompt },
          { inline_data: { mime_type: "image/png", data: imgBase64 } }
        ]
      }],
      generationConfig: {
        responseModalities: ["IMAGE", "TEXT"],
        imageSizes: "1024x1024"
      }
    });

    // Write payload to temp file to avoid shell escaping issues
    const payloadPath = path.resolve(__dirname, '../temp/_gen_payload.json');
    fs.writeFileSync(payloadPath, payload);

    const cmd = `curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${apiKey}" -H "Content-Type: application/json" -d @"${payloadPath}"`;
    const response = JSON.parse(execSync(cmd, { maxBuffer: 50 * 1024 * 1024 }).toString());

    // Clean up payload
    try { fs.unlinkSync(payloadPath); } catch(e) {}

    // Extract image from response
    const parts = response?.candidates?.[0]?.content?.parts || [];
    const imagePart = parts.find(p => p.inlineData || p.inline_data);
    if (imagePart) {
      const imageData = (imagePart.inlineData || imagePart.inline_data).data;
      fs.writeFileSync(output, Buffer.from(imageData, 'base64'));
      return true;
    } else {
      console.error(`No image in Gemini response for ${row.ID}`);
      return false;
    }
  } catch (e) {
    console.error(`Failed to generate ${row.ID}:`, e.message || e);
    return false;
  }
}

async function main() {
  if (!fs.existsSync(CSV_PATH)) {
    console.error(`CSV file not found at ${CSV_PATH}`);
    process.exit(1);
  }

  const data = readCSV();
  let pending = data.filter(r => r.Status === 'Pending');

  console.log(`Found ${pending.length} pending tasks.`);

  for (const row of pending) {
    const success = generate(row);
    if (success) {
      row.Status = 'Done';
      writeCSV(data);
      console.log(`${row.Filename} DONE! Waiting 10s...`);
      execSync('sleep 10');
    } else {
      console.log(`Skipping ${row.Filename} due to error. Waiting 20s...`);
      execSync('sleep 20');
    }
  }
  console.log('Batch run complete.');
}

main();
