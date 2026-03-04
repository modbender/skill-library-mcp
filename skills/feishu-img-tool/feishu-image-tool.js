#!/usr/bin/env node
/**
 * Feishu Image Upload and Send Tool
 * 
 * Usage:
 *   node feishu-image-tool.js send --target <open_id> --file <path> [--message <text>]
 *   node feishu-image-tool.js upload --file <path>
 *   node feishu-image-tool.js send-with-key --target <open_id> --image-key <key>
 */

const fs = require('fs');
const path = require('path');

// Try to load Lark SDK from OpenClaw's node_modules
const LARK_SDK_PATH = path.join(
  process.env.HOME || '/root',
  '.local/share/pnpm/global/5/.pnpm/@larksuiteoapi+node-sdk@1.59.0/node_modules/@larksuiteoapi/node-sdk'
);

const Lark = require(LARK_SDK_PATH);

/**
 * Feishu app credentials configuration
 * 
 * Configure using one of these methods (in order of priority):
 * 1. Environment variables: FEISHU_APP_ID, FEISHU_APP_SECRET
 * 2. Config file: ~/.feishu-image/config.json
 * 3. Default: Will prompt error if not configured
 */
function getFeishuConfig() {
  // Method 1: Environment variables
  if (process.env.FEISHU_APP_ID && process.env.FEISHU_APP_SECRET) {
    return {
      appId: process.env.FEISHU_APP_ID,
      appSecret: process.env.FEISHU_APP_SECRET,
    };
  }

  // Method 2: Config file
  const configPath = path.join(
    process.env.HOME || '/root',
    '.feishu-image',
    'config.json'
  );
  try {
    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      if (config.appId && config.appSecret) {
        return config;
      }
    }
  } catch (e) {
    // Ignore config file errors
  }

  // Method 3: Error - not configured
  throw new Error(
    'Feishu credentials not configured. Please set:\n' +
    '  - Environment variables: FEISHU_APP_ID and FEISHU_APP_SECRET\n' +
    '  - Or create config file: ~/.feishu-image/config.json\n' +
    '    with { "appId": "xxx", "appSecret": "xxx" }'
  );
}

// Parse command line arguments
function parseArgs(args) {
  const result = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      result[key] = args[i + 1];
      i++;
    } else if (!result.action) {
      result.action = args[i];
    }
  }
  return result;
}

// Create Feishu client
let cachedClient = null;

function createClient() {
  if (cachedClient) return cachedClient;
  
  const config = getFeishuConfig();
  cachedClient = new Lark.Client({
    appId: config.appId,
    appSecret: config.appSecret,
    appType: Lark.AppType.SelfBuild,
  });
  return cachedClient;
}

// Upload image to Feishu
async function uploadImage(client, filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }

  const imageBuffer = fs.readFileSync(filePath);
  
  const result = await client.im.image.create({
    data: {
      image_type: 'message',
      image: imageBuffer,
    },
  });

  // image_key can be in result.data.image_key or directly in result
  const imageKey = result.data?.image_key || result.image_key;
  
  if (!imageKey) {
    throw new Error(`Upload failed: ${JSON.stringify(result)}`);
  }

  return imageKey;
}

// Send image message
async function sendImage(client, targetOpenId, imageKey, message) {
  const result = await client.im.message.create({
    params: {
      receive_id_type: 'open_id',
    },
    data: {
      receive_id: targetOpenId,
      msg_type: 'image',
      content: JSON.stringify({
        image_key: imageKey,
      }),
    },
  });

  if (result.code !== 0) {
    throw new Error(`Send failed: ${result.msg}`);
  }

  return result.data;
}

// Main function
async function main() {
  const args = parseArgs(process.argv.slice(2));
  const client = createClient();

  try {
    switch (args.action) {
      case 'send': {
        if (!args.file) {
          console.error('❌ Missing --file argument');
          process.exit(1);
        }

        console.log('📤 Uploading image...');
        const imageKey = await uploadImage(client, args.file);
        console.log('✅ Upload successful:', imageKey);

        // If target is provided, send the image
        if (args.target) {
          console.log('📨 Sending image message...');
          const result = await sendImage(client, args.target, imageKey, args.message);
          console.log('✅ Message sent:', result.message_id);
          
          // If message text is provided, send it separately
          if (args.message) {
            await client.im.message.create({
              params: { receive_id_type: 'open_id' },
              data: {
                receive_id: args.target,
                msg_type: 'text',
                content: JSON.stringify({ text: args.message }),
              },
            });
            console.log('✅ Caption sent');
          }
          
          console.log(JSON.stringify({
            success: true,
            image_key: imageKey,
            message_id: result.message_id,
          }));
        } else {
          // Just return the image key
          console.log(JSON.stringify({
            success: true,
            image_key: imageKey,
          }));
        }
        break;
      }

      case 'upload': {
        if (!args.file) {
          console.error('❌ Missing --file argument');
          process.exit(1);
        }

        console.log('📤 Uploading image...');
        const imageKey = await uploadImage(client, args.file);
        console.log('✅ Upload successful:', imageKey);
        console.log(JSON.stringify({
          success: true,
          image_key: imageKey,
        }));
        break;
      }

      case 'send-with-key': {
        if (!args.target || !args['image-key']) {
          console.error('❌ Missing --target or --image-key argument');
          process.exit(1);
        }

        console.log('📨 Sending image message...');
        const result = await sendImage(client, args.target, args['image-key']);
        console.log('✅ Message sent:', result.message_id);
        console.log(JSON.stringify({
          success: true,
          message_id: result.message_id,
        }));
        break;
      }

      default:
        console.error('❌ Unknown action. Use: send, upload, or send-with-key');
        console.error('Usage:');
        console.error('  send --target <open_id> --file <path> [--message <text>]');
        console.error('  upload --file <path>');
        console.error('  send-with-key --target <open_id> --image-key <key>');
        process.exit(1);
    }
  } catch (error) {
    console.error('❌ Error:', error.message);
    console.error(error);
    process.exit(1);
  }
}

main();
