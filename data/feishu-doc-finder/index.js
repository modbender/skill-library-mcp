#!/usr/bin/env node
const { Command } = require('commander');
const { Client } = require('@larksuiteoapi/node-sdk');
const fs = require('fs');
const path = require('path');

const program = new Command();

program
  .name('feishu-file-finder')
  .description('Find and download files from Feishu chat by filename')
  .requiredOption('-c, --chat <chat_id>', 'Target Chat ID')
  .requiredOption('-f, --file <filename>', 'Filename to search for')
  .option('-o, --output <path>', 'Output directory', '.')
  .option('-h, --hours <hours>', 'Search history lookback in hours', '24')
  .parse(process.argv);

const options = program.opts();

const client = new Client({
    appId: process.env.FEISHU_APP_ID,
    appSecret: process.env.FEISHU_APP_SECRET,
});

async function main() {
    if (!process.env.FEISHU_APP_ID || !process.env.FEISHU_APP_SECRET) {
        console.error('Error: FEISHU_APP_ID and FEISHU_APP_SECRET env vars must be set.');
        process.exit(1);
    }

    console.log(`Searching for "${options.file}" in chat ${options.chat} (last ${options.hours}h)...`);

    const startTime = String(Math.floor(Date.now() / 1000) - (options.hours * 3600));

    try {
        const resp = await client.im.message.list({
            params: {
                container_id_type: 'chat',
                container_id: options.chat,
                page_size: 50,
                start_time: startTime
            }
        });

        if (resp.code !== 0) {
            console.error('API Error:', resp);
            return;
        }

        const items = resp.data.items || [];
        // Look for file messages
        const targetMsg = items.find(m => {
            if (m.msg_type === 'file' || m.msg_type === 'media' || m.msg_type === 'audio') {
                try {
                    const content = JSON.parse(m.body.content);
                    return (content.file_name && content.file_name.includes(options.file));
                } catch (e) { return false; }
            }
            return false;
        });

        if (!targetMsg) {
            console.log('❌ File not found in recent messages.');
            // console.log('Checked messages:', items.length);
            return;
        }

        // Found
        const content = JSON.parse(targetMsg.body.content);
        const fileKey = content.file_key;
        const msgId = targetMsg.message_id;
        const fileName = content.file_name;
        
        console.log(`✅ Found: ${fileName}`);
        console.log(`   MsgID: ${msgId}`);
        console.log(`   Key:   ${fileKey}`);

        // Download
        console.log('Downloading...');
        const downResp = await client.im.messageResource.get({
            path: { message_id: msgId, file_key: fileKey },
            params: { type: 'file' }
        });

        // Handle binary response (Buffer or Stream or Wrapper)
        const outputPath = path.join(options.output, fileName);
        
        let dataToWrite = downResp;
        if (downResp && downResp.code === 0 && downResp.data) {
             dataToWrite = downResp.data;
        } else if (downResp && downResp.writeFile) {
             // SDK file helper if available
             await downResp.writeFile(outputPath);
             console.log(`💾 Saved to ${outputPath}`);
             return;
        }

        if (Buffer.isBuffer(dataToWrite)) {
            await fs.promises.writeFile(outputPath, dataToWrite);
            console.log(`💾 Saved to ${outputPath}`);
        } else if (dataToWrite && typeof dataToWrite.pipe === 'function') {
            const dest = fs.createWriteStream(outputPath);
            dataToWrite.pipe(dest);
            console.log(`💾 Savings via stream to ${outputPath}...`);
        } else {
            console.error('❌ Failed to save: Unknown response format.');
            console.error('Keys:', Object.keys(downResp));
        }

    } catch (e) {
        console.error('Runtime Error:', e);
    }
}

main();
