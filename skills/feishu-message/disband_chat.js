const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });

// Try to load Lark SDK
let Lark;
try {
    Lark = require('@larksuiteoapi/node-sdk');
} catch (e) {
    try {
        Lark = require('../feishu-calendar/node_modules/@larksuiteoapi/node-sdk');
    } catch (e2) {
        console.error('Error: Could not load @larksuiteoapi/node-sdk');
        process.exit(1);
    }
}

const APP_ID = process.env.FEISHU_APP_ID;
const APP_SECRET = process.env.FEISHU_APP_SECRET;
const client = new Lark.Client({ appId: APP_ID, appSecret: APP_SECRET });

async function disbandChat(chatId) {
    try {
        console.log(`Attempting to disband chat: ${chatId}`);
        const res = await client.im.chat.delete({
            path: { chat_id: chatId }
        });

        if (res.code !== 0) {
            console.error(`Error: [${res.code}] ${res.msg}`);
            if (res.code === 403001) console.error("Permission denied (Not owner?)");
            process.exit(1);
        }

        console.log(`Success: Chat ${chatId} disbanded.`);
        console.log(JSON.stringify(res.data, null, 2));
    } catch (e) {
        console.error(`Exception: ${e.message}`);
        process.exit(1);
    }
}

const chatId = process.argv[2];
if (!chatId) {
    console.error("Usage: node disband_chat.js <chat_id>");
    process.exit(1);
}

disbandChat(chatId);
