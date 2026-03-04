#!/usr/bin/env node
/**
 * 使用原生FormData的飞书文件上传工具
 * Node.js 18+ 支持全局的FormData和fetch
 */

const fs = require('fs');
const path = require('path');

// 检查Node.js版本
const nodeVersion = process.version;
console.log(`Node.js版本: ${nodeVersion}`);

// 读取访问令牌
const tokenFile = '/home/node/.openclaw/workspace/feishu_token.txt';
if (!fs.existsSync(tokenFile)) {
    console.error('错误: 找不到访问令牌文件');
    process.exit(1);
}

const accessToken = fs.readFileSync(tokenFile, 'utf8').trim();
console.log('使用访问令牌:', accessToken.substring(0, 30) + '...');

// 检查参数
if (process.argv.length < 3) {
    console.error('用法: node native_feishu_upload.js <文件路径>');
    process.exit(1);
}

const filePath = path.resolve(process.argv[2]);
if (!fs.existsSync(filePath)) {
    console.error('错误: 文件不存在:', filePath);
    process.exit(1);
}

const fileName = path.basename(filePath);
const fileSize = fs.statSync(filePath).size;

console.log(`上传文件: ${fileName}`);
console.log(`文件大小: ${fileSize} 字节`);

// 检查文件大小限制 (30MB)
if (fileSize > 30 * 1024 * 1024) {
    console.error(`错误: 文件太大 (${(fileSize / 1024 / 1024).toFixed(2)} MB)，最大支持30MB`);
    process.exit(1);
}

async function uploadFile() {
    try {
        // 读取文件内容
        const fileBuffer = fs.readFileSync(filePath);
        
        // Node.js 18+ 支持全局的FormData
        if (typeof FormData === 'undefined') {
            throw new Error('当前Node.js版本不支持全局FormData，请使用Node.js 18+');
        }
        
        // 创建FormData
        const form = new FormData();
        form.append('file_type', 'stream');
        form.append('file_name', fileName);
        
        // 创建Blob并添加到FormData
        const blob = new Blob([fileBuffer]);
        form.append('file', blob, fileName);
        
        console.log('正在上传文件...');
        
        // 上传文件
        const response = await fetch('https://open.feishu.cn/open-apis/im/v1/files', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`
                // 注意：使用FormData时不要设置Content-Type，浏览器/Node.js会自动设置
            },
            body: form
        });
        
        const data = await response.json();
        
        if (data.code !== 0) {
            throw new Error(`上传失败 (代码 ${data.code}): ${data.msg}`);
        }
        
        const fileKey = data.data.file_key;
        console.log('✅ 文件上传成功!');
        console.log('文件Key:', fileKey);
        
        // 输出JSON格式结果
        console.log(JSON.stringify({
            status: 'success',
            file_key: fileKey,
            file_name: fileName,
            file_size: fileSize
        }, null, 2));
        
        return fileKey;
        
    } catch (error) {
        console.error('❌ 上传失败:', error.message);
        console.error(JSON.stringify({
            status: 'error',
            error: error.message
        }, null, 2));
        process.exit(1);
    }
}

// 运行上传
uploadFile();