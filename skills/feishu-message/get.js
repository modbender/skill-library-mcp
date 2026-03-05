#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { program } = require('commander');
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });

const APP_ID = process.env.FEISHU_APP_ID;
const APP_SECRET = process.env.FEISHU_APP_SECRET;
const TOKEN_CACHE_FILE = path.resolve(__dirname, '../../memory/feishu_token.json');

async function getToken() {
    try {
        if (fs.existsSync(TOKEN_CACHE_FILE)) {
            const cached = JSON.parse(fs.readFileSync(TOKEN_CACHE_FILE, 'utf8'));
            const now = Math.floor(Date.now() / 1000);
            if (cached.expire > now + 60) return cached.token;
        }
    } catch (e) {}

    try {
        const res = await fetch('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ app_id: APP_ID, app_secret: APP_SECRET })
        });
        const data = await res.json();
        if (data.code !== 0) throw new Error(`Auth failed: ${JSON.stringify(data)}`);
        
        try {
            fs.writeFileSync(TOKEN_CACHE_FILE, JSON.stringify({
                token: data.tenant_access_token,
                expire: Math.floor(Date.now() / 1000) + data.expire
            }));
        } catch(e) {}
        
        return data.tenant_access_token;
    } catch (e) {
        console.error(e);
        process.exit(1);
    }
}

async function fetchMessage(messageId) {
    const token = await getToken();
    const url = `https://open.feishu.cn/open-apis/im/v1/messages/${messageId}`;
    const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
    const json = await res.json();
    
    if (json.code !== 0) {
        // If message not found, maybe it's a merge forward item?
        // But we can't fetch merge forward items directly via this API usually.
        throw new Error(`API Error ${json.code}: ${json.msg}`);
    }
    return json.data;
}

function parseContent(msgBody) {
    try {
        const content = JSON.parse(msgBody.content);
        if (content.text) return content.text;
        if (content.title && content.content) {
            // Post type
            return `[Post] ${content.title}\n` + content.content.map(p => p.map(e => e.text).join('')).join('\n');
        }
        if (content.image_key) return `[Image key=${content.image_key}]`;
        return JSON.stringify(content);
    } catch (e) {
        return msgBody.content;
    }
}

async function formatMessage(msg, depth = 0, recursive = false) {
    const indent = '  '.repeat(depth);
    let output = '';
    
    const sender = msg.sender && msg.sender.sender_type === 'user' ? (msg.sender.id || 'User') : 'App';
    const time = new Date(parseInt(msg.create_time)).toISOString().replace('T', ' ').substring(0, 19);
    
    if (msg.msg_type === 'merge_forward') {
        output += `${indent}📂 [Merged Forward] (${time})\n`;
        // If recursive is true, we should try to fetch the merged content if it's not present
        // But standard message API doesn't return merged content unless specific params are used?
        // Actually for merge_forward, the content is usually just a placeholder or list of IDs.
        // We might need a separate API call to get merged content? 
        // For now, let's just print what we have.
        
        // If items are present (e.g. from a specialized fetch), print them
        if (msg.items && Array.isArray(msg.items)) {
            for (const item of msg.items) {
                output += await formatMessage(item, depth + 1, recursive);
            }
        } else {
             output += `${indent}  (No items found or not expanded)\n`;
        }
    } else {
        const content = parseContent(msg.body);
        output += `${indent}💬 [${sender}] ${time}: ${content}\n`;
    }
    
    return output;
}

program
    .argument('[message_id]', 'Message ID to read (positional)') // Make optional to allow --message-id usage
    .option('-m, --message-id <id>', 'Message ID to read (alternative)')
    .option('-r, --raw', 'Output raw JSON')
    .option('-R, --recursive', 'Recursively fetch merged messages (dummy for now)')
    .action(async (posMessageId, options) => {
        try {
            const messageId = posMessageId || options.messageId;
            if (!messageId) {
                console.error("Error: Message ID is required (argument or --message-id)");
                process.exit(1);
            }

            const data = await fetchMessage(messageId);
            
            if (options.raw) {
                console.log(JSON.stringify(data, null, 2));
            } else {
                if (data.items && data.items.length > 0) {
                    console.log(`📦 Merged Message Container (${data.items.length} items):\n`);
                    for (const item of data.items) {
                        if (item.message_id === messageId && data.items.length > 1) continue; 
                        console.log(await formatMessage(item, 0, options.recursive));
                    }
                } else {
                    // Single message
                    console.log(await formatMessage(data.items ? data.items[0] : data, 0, options.recursive));
                }
            }
        } catch (e) {
            console.error('Error:', e.message);
            process.exit(1);
        }
    });

program.parse();
