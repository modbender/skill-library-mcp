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

async function getChatInfo(chatId) {
    try {
        const res = await client.im.chat.get({
            path: { chat_id: chatId },
            params: { user_id_type: 'open_id' }
        });

        if (res.code !== 0) {
            console.error(`Error: [${res.code}] ${res.msg}`);
            return;
        }

        console.log(JSON.stringify(res, null, 2));
    } catch (e) {
        console.error(e);
    }
}

const chatId = process.argv[2];
if (!chatId) {
    console.error("Usage: node get_chat_info.js <chat_id>");
    process.exit(1);
}

getChatInfo(chatId);
