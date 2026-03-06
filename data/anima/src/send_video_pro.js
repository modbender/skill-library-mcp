// Load .env from skill folder only (least-privilege: never read parent .env)
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });
const fs = require('fs');
const { execSync } = require('child_process');

const APP_ID = process.env.FEISHU_APP_ID;
const APP_SECRET = process.env.FEISHU_APP_SECRET;
const TARGET_ID = process.argv[2];
if (!TARGET_ID) {
  console.error("❌ Usage: node send_video_pro.js <target_open_id> [video_path]");
  process.exit(1);
}
const VIDEO_PATH = process.argv[3] ? path.resolve(process.argv[3]) : path.resolve(__dirname, '../output/final_fixed_voice.mp4');
const COVER_PATH = path.resolve(__dirname, '../output/cover_extracted.jpg');

// Helper: Run curl
function runCurl(cmd) {
  try {
    const res = execSync(cmd, { maxBuffer: 10 * 1024 * 1024 }).toString();
    return JSON.parse(res);
  } catch (e) {
    console.error('Curl error:', e);
    return null;
  }
}

async function main() {
  console.log('1. Getting Token...');
  const tokenCmd = `curl -s -X POST -H "Content-Type: application/json; charset=utf-8" -d '{"app_id":"${APP_ID}","app_secret":"${APP_SECRET}"}' https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal`;
  const tokenRes = runCurl(tokenCmd);
  const token = tokenRes.tenant_access_token;
  
  if (!token) throw new Error('Failed to get token');

  // 1.5 Get Duration & Extract Cover
  const durationCmd = `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${VIDEO_PATH}"`;
  const durationSec = parseFloat(execSync(durationCmd).toString().trim());
  const durationMs = Math.round(durationSec * 1000);
  console.log(`Video Duration: ${durationMs}ms`);

  console.log('2. Extracting Cover (First Frame)...');
  // Extract frame at 0.5s to ensure content visibility (avoid black start)
  execSync(`ffmpeg -y -i "${VIDEO_PATH}" -ss 00:00:00.500 -vframes 1 "${COVER_PATH}"`, { stdio: 'ignore' });
  if (!fs.existsSync(COVER_PATH)) throw new Error('Cover extraction failed');

  // file_type must be 'mp4' for msg_type="media" to work correctly with duration metadata
  const stat = fs.statSync(VIDEO_PATH);
  const size = stat.size;
  // Changed file_type from stream to mp4
  const uploadVideoCmd = `curl -s -X POST -H "Authorization: Bearer ${token}" -H "Content-Type: multipart/form-data" -F "file_name=anima_demo.mp4" -F "file_type=mp4" -F "duration=${durationMs}" -F "file=@${VIDEO_PATH}" -F "size=${size}" https://open.feishu.cn/open-apis/im/v1/files`;
  
  const videoRes = runCurl(uploadVideoCmd);
  const fileKey = videoRes.data?.file_key;
  if (!fileKey) throw new Error('Failed to upload video: ' + JSON.stringify(videoRes));
  console.log('Video Key:', fileKey);

  console.log('3. Uploading Cover Image...');
  const uploadImgCmd = `curl -s -X POST -H "Authorization: Bearer ${token}" -H "Content-Type: multipart/form-data" -F "image_type=message" -F "image=@${COVER_PATH}" https://open.feishu.cn/open-apis/im/v1/images`;
  
  const imgRes = runCurl(uploadImgCmd);
  const imageKey = imgRes.data?.image_key;
  if (!imageKey) throw new Error('Failed to upload cover: ' + JSON.stringify(imgRes));
  console.log('Image Key:', imageKey);

  console.log('4. Sending Media Message...');
  const content = JSON.stringify({
    file_key: fileKey,
    image_key: imageKey,
    file_name: "anima_demo.mp4",
    duration: durationMs // Also pass here for compatibility
  }).replace(/"/g, '\\"');

  const sendCmd = `curl -s -X POST -H "Authorization: Bearer ${token}" -H "Content-Type: application/json; charset=utf-8" -d '{"receive_id": "${TARGET_ID}", "msg_type": "media", "content": "${content}"}' "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"`;
  
  const sendRes = runCurl(sendCmd);
  console.log('Send Result:', JSON.stringify(sendRes));
}

main().catch(console.error);
