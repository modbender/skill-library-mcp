#!/usr/bin/env node
/**
 * 完整的飞书文件上传和发送工具
 * 1. 上传文件到飞书
 * 2. 发送文件消息到指定聊天
 */

const fs = require('fs');
const path = require('path');

// 读取访问令牌
function getAccessToken() {
    const tokenFile = '/home/node/.openclaw/workspace/feishu_token.txt';
    if (!fs.existsSync(tokenFile)) {
        throw new Error('找不到访问令牌文件');
    }
    return fs.readFileSync(tokenFile, 'utf8').trim();
}

// 上传文件到飞书
async function uploadFile(filePath) {
    const accessToken = getAccessToken();
    const fileName = path.basename(filePath);
    const fileSize = fs.statSync(filePath).size;
    
    console.log(`📤 上传文件: ${fileName}`);
    console.log(`   文件大小: ${fileSize} 字节`);
    
    // 检查文件大小限制 (30MB)
    if (fileSize > 30 * 1024 * 1024) {
        throw new Error(`文件太大 (${(fileSize / 1024 / 1024).toFixed(2)} MB)，最大支持30MB`);
    }
    
    // 读取文件内容
    const fileBuffer = fs.readFileSync(filePath);
    
    // 创建FormData
    const form = new FormData();
    form.append('file_type', 'stream');
    form.append('file_name', fileName);
    
    // 创建Blob并添加到FormData
    const blob = new Blob([fileBuffer]);
    form.append('file', blob, fileName);
    
    console.log('   正在上传...');
    
    // 上传文件
    const response = await fetch('https://open.feishu.cn/open-apis/im/v1/files', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`
        },
        body: form
    });
    
    const data = await response.json();
    
    if (data.code !== 0) {
        throw new Error(`上传失败 (代码 ${data.code}): ${data.msg}`);
    }
    
    const fileKey = data.data.file_key;
    console.log(`✅ 上传成功!`);
    console.log(`   文件Key: ${fileKey}`);
    
    return {
        file_key: fileKey,
        file_name: fileName,
        file_size: fileSize
    };
}

// 发送文件消息到聊天
async function sendFileMessage(chatId, fileKey, fileName) {
    const accessToken = getAccessToken();
    
    console.log(`📨 发送文件消息到聊天: ${chatId}`);
    console.log(`   文件: ${fileName}`);
    
    const receiveIdType = chatId.startsWith('oc_') ? 'chat_id' : 'open_id';
    
    const messageBody = {
        receive_id: chatId,
        msg_type: 'file',
        content: JSON.stringify({ file_key: fileKey })
    };
    
    const response = await fetch(
        `https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=${receiveIdType}`,
        {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(messageBody)
        }
    );
    
    const data = await response.json();
    
    if (data.code !== 0) {
        throw new Error(`发送失败 (代码 ${data.code}): ${data.msg}`);
    }
    
    console.log(`✅ 消息发送成功!`);
    console.log(`   消息ID: ${data.data.message_id}`);
    
    return data.data;
}

// 主函数
async function main() {
    console.log('🚀 飞书文件上传工具');
    console.log('=' .repeat(50));
    
    // 检查参数
    if (process.argv.length < 3) {
        console.error('用法:');
        console.error('  1. 仅上传文件: node feishu_complete_upload.js <文件路径>');
        console.error('  2. 上传并发送: node feishu_complete_upload.js <文件路径> <聊天ID>');
        console.error('');
        console.error('示例:');
        console.error('  node feishu_complete_upload.js test.txt');
        console.error('  node feishu_complete_upload.js test.txt oc_dd899cb1a7846915cdd2d6850bd1dafa');
        process.exit(1);
    }
    
    const filePath = path.resolve(process.argv[2]);
    const chatId = process.argv[3]; // 可选的聊天ID
    
    if (!fs.existsSync(filePath)) {
        console.error(`❌ 错误: 文件不存在: ${filePath}`);
        process.exit(1);
    }
    
    try {
        // 1. 上传文件
        const uploadResult = await uploadFile(filePath);
        
        // 2. 如果提供了聊天ID，发送文件消息
        if (chatId) {
            console.log('\n' + '-'.repeat(50));
            await sendFileMessage(chatId, uploadResult.file_key, uploadResult.file_name);
        }
        
        // 输出最终结果
        console.log('\n' + '='.repeat(50));
        console.log('🎉 操作完成!');
        
        const result = {
            status: 'success',
            upload: uploadResult,
            sent: !!chatId
        };
        
        if (chatId) {
            result.chat_id = chatId;
        }
        
        console.log(JSON.stringify(result, null, 2));
        
        // 保存结果到文件
        fs.writeFileSync(
            '/home/node/.openclaw/workspace/upload_result.json',
            JSON.stringify(result, null, 2)
        );
        console.log('\n结果已保存到: upload_result.json');
        
    } catch (error) {
        console.error(`\n❌ 错误: ${error.message}`);
        console.error(JSON.stringify({
            status: 'error',
            error: error.message
        }, null, 2));
        process.exit(1);
    }
}

// 运行主函数
main();