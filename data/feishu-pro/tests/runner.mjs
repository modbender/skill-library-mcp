import { applyFeishuDefaults } from './_utils.mjs';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Ensure environment variables are set
process.env.FEISHU_APP_ID = 'cli_a90a588432f8dcc0';
process.env.FEISHU_APP_SECRET = '0BSggpNeEx2Vg0yb9TH2wh1QOk5BkS4u';
process.env.TEST_CHAT_ID = 'oc_b1dffffb4b809464b4202003552e6aca';
process.env.TEST_USER_ID = 'ou_9b45afbf39313bc0884bfff776556370';
process.env.TEST_DOC_TOKEN = 'Yo8PdVT18oe083xquhmcWOqvnOe';
process.env.ALLOW_SIDE_EFFECTS = '1';
process.env.ALLOW_DESTRUCTIVE = '1';
process.env.OPENCLAW_HOME = path.resolve(__dirname, '../../../../..');

// Add more variables for better coverage
process.env.TEST_CREATE_CHAT_USER_IDS = 'ou_9b45afbf39313bc0884bfff776556370';
process.env.TEST_CHAT_MEMBER_IDS = 'ou_9b45afbf39313bc0884bfff776556370';
process.env.TEST_DOC_MEMBER_ID = 'ou_9b45afbf39313bc0884bfff776556370';
process.env.TEST_DOC_MEMBER_TYPE = 'open_id';
process.env.TEST_DOC_MEMBER_ROLE = 'view';
process.env.TEST_OCR_IMAGE_PATH = path.join(__dirname, 'test-image.png');
process.env.TEST_AUDIO_PATH = path.join(__dirname, 'test-audio.wav');

// Dummy IDs to trigger more logic (some tests might fail but at least they run)
process.env.TEST_BITABLE_APP_TOKEN = 'bascnvS9xxxxxxxxxxxxxx'; 
process.env.TEST_BITABLE_TABLE_ID = 'tblxxxxxxxxxx';
process.env.TEST_WIKI_SPACE_ID = '7000000000000000000';
process.env.TEST_DEPT_ID = '0';

console.log('Running Feishu Tests with:');
console.log(`FEISHU_APP_ID: ${process.env.FEISHU_APP_ID}`);
console.log(`TEST_CHAT_ID: ${process.env.TEST_CHAT_ID}`);

const testFile = process.argv[2] || 'run-all.mjs';
const testPath = path.join(__dirname, testFile);

const child = spawn('node', [testPath], {
  env: process.env,
  stdio: 'inherit'
});

child.on('exit', (code) => {
  process.exit(code);
});
