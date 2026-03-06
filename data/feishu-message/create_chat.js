#!/usr/bin/env node
const { program } = require('commander');
const path = require('path');
const fs = require('fs');

// Try to load Lark SDK from local or fallback
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

require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });

const APP_ID = process.env.FEISHU_APP_ID;
const APP_SECRET = process.env.FEISHU_APP_SECRET;
const client = new Lark.Client({ appId: APP_ID, appSecret: APP_SECRET });

async function createGroupChat(name, userIds, description) {
    try {
        console.log(`Creating group chat: "${name}" with users: ${userIds.join(', ')}`);
        
        const res = await client.im.chat.create({
            params: {
                user_id_type: 'open_id',
                set_bot_manager: true 
            },
            data: {
                name: name,
                description: description || "Created by OpenClaw Agent",
                user_id_list: userIds,
                chat_mode: 'group',
                group_type: 'private',
                external: false // Internal only by default
            }
        });

        if (res.code !== 0) {
            console.error(`Error creating chat: [${res.code}] ${res.msg}`);
            if (res.code === 403001) console.error("Tip: Check if bot has 'im:chat' scope and users are in visibility range.");
            return null;
        }

        console.log(JSON.stringify(res.data, null, 2));
        return res.data;
    } catch (e) {
        console.error(`API Exception: ${e.message}`);
        return null;
    }
}

program
    .version('1.0.0')
    .description('Create a Feishu group chat with specified users')
    .argument('<name>', 'Name of the group chat')
    .argument('<users...>', 'List of user OpenIDs (space separated)')
    .option('-d, --desc <description>', 'Group description')
    .option('--content <description>', 'Group description (alias)')
    .action(async (name, users, options) => {
        if (!process.env.FEISHU_APP_ID || !process.env.FEISHU_APP_SECRET) {
            console.error('Error: FEISHU_APP_ID or FEISHU_APP_SECRET not set in env');
            process.exit(1);
        }
        await createGroupChat(name, users, options.desc || options.content);
    });

program.parse(process.argv);
