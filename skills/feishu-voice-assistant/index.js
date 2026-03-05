#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { program } = require('commander');
const { getToken, fetchWithRetry } = require('../feishu-common/index.js');
const duby = require('../duby/index.js');
const { Blob } = require('buffer'); // Use native Blob for FormData

// Ensure .env is loaded
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });

async function uploadAudio(token, filePath) {
    const fileName = path.basename(filePath);
    const fileBuffer = fs.readFileSync(filePath);
    const blob = new Blob([fileBuffer]);
    
    const formData = new FormData();
    formData.append('file_type', 'stream'); // Generic stream for audio files
    formData.append('file_name', fileName);
    formData.append('file', blob, fileName);
    formData.append('duration', '10000'); // Optional duration in ms

    try {
        const response = await fetchWithRetry('https://open.feishu.cn/open-apis/im/v1/files', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        const data = await response.json();
        if (data.code !== 0) {
            throw new Error(`Upload failed: ${data.msg} (Code: ${data.code})`);
        }
        return data.data.file_key;
    } catch (error) {
        throw new Error(`Upload error: ${error.message}`);
    }
}

async function sendAudioMessage(target, fileKey) {
    const token = await getToken();
    
    // Determine receive_id_type
    const receiveIdType = target.startsWith('oc_') ? 'chat_id' : 'open_id';
    
    const body = {
        receive_id: target,
        msg_type: 'audio',
        content: JSON.stringify({ file_key: fileKey })
    };

    try {
        const response = await fetchWithRetry(
            `https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=${receiveIdType}`,
            {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(body)
            }
        );

        const data = await response.json();
        if (data.code !== 0) {
            throw new Error(`Send failed: ${data.msg} (Code: ${data.code})`);
        }
        return data.data;
    } catch (error) {
        throw new Error(`Send error: ${error.message}`);
    }
}

async function main() {
    program
        .option('--text <text>', 'Text to speak')
        .option('--target <id>', 'Target User ID or Chat ID')
        .option('--voice <id>', 'Voice ID (optional)')
        .parse(process.argv);

    const options = program.opts();

    if (!options.text || !options.target) {
        console.error('Usage: node index.js --text "Hello" --target "ou_xxx" [--voice "id"]');
        process.exit(1);
    }

    try {
        console.log(`🎤 Generating audio for: "${options.text}"...`);
        
        // Step 1: Generate TTS
        // duby.duby_tts returns "MEDIA:/path/to/file.mp3" string
        // We need to parse this string to get the actual path.
        const mediaPath = await duby.duby_tts({ 
            text: options.text, 
            voice_id: options.voice 
        });

        if (!mediaPath || !mediaPath.startsWith('MEDIA:')) {
            throw new Error(`Invalid TTS response: ${mediaPath}`);
        }

        const filePath = mediaPath.replace('MEDIA:', '').trim();
        const absolutePath = path.resolve(process.cwd(), filePath);

        if (!fs.existsSync(absolutePath)) {
            throw new Error(`Generated audio file not found at: ${absolutePath}`);
        }

        console.log(`📤 Uploading audio: ${filePath}...`);
        
        // Step 2: Upload to Feishu
        const token = await getToken();
        const fileKey = await uploadAudio(token, absolutePath);
        
        console.log(`📨 Sending audio message to ${options.target}...`);

        // Step 3: Send Message
        await sendAudioMessage(options.target, fileKey);

        console.log('✅ Voice message sent successfully!');
        
        // Cleanup temp file
        // fs.unlinkSync(absolutePath); // Optional: keep for cache or delete
    } catch (error) {
        console.error(`❌ Error: ${error.message}`);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { main };
