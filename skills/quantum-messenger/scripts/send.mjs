import http from 'http';
import { URL } from 'url';
import fs from 'fs';
import path from 'path';

/**
 * =========================================================================
 * 量子密信 (Quantum Messenger) - 主动发送工具
 * 
 * 作者：上海电信政支中心/量子能力中心 技术经理 程沛及他的openclaw机器人助手：1号机（Gemini)
 * 联系方式：18918115454
 * 邮箱：chenpei.sh@chinatelecom.cn
 * =========================================================================
 */

// 优先从环境变量读取，方便 ClawHub 部署
const KEY = process.env.QUANTUM_KEY || 'YOUR_QUANTUM_KEY_HERE'; 
const WEBHOOK_URL = `http://imtwo.zdxlz.com/im-external/v1/webhook/send?key=${KEY}`;

/**
 * 上传附件/图片逻辑
 */
async function uploadFile(filePath, type = 2) {
    const UPLOAD_URL = `http://imtwo.zdxlz.com/im-external/v1/webhook/upload-attachment?key=${KEY}&type=${type}`;
    return new Promise((resolve, reject) => {
        const url = new URL(UPLOAD_URL);
        const boundary = 'WebAppBoundary' + Math.random().toString(16).substring(2);
        
        const options = {
            hostname: url.hostname,
            port: url.port || 80,
            path: url.pathname + url.search,
            method: 'POST',
            headers: {
                'Content-Type': `multipart/form-data; boundary=${boundary}`
            }
        };

        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(body));
                } catch (e) {
                    reject(new Error('Failed to parse upload response: ' + body));
                }
            });
        });

        req.on('error', (e) => reject(e));

        const fileName = path.basename(filePath);
        const mimeType = type === 1 ? 'image/jpeg' : 'application/octet-stream';
        const header = `--${boundary}\r\n` +
                     `Content-Disposition: form-data; name="file"; filename="${fileName}"\r\n` +
                     `Content-Type: ${mimeType}\r\n\r\n`;
        const footer = `\r\n--${boundary}--\r\n`;

        req.write(header);
        const fileStream = fs.createReadStream(filePath);
        fileStream.on('end', () => {
            req.write(footer);
            req.end();
        });
        fileStream.pipe(req, { end: false });
    });
}

/**
 * 发送图片消息
 */
async function sendImage(fileId) {
    const payload = JSON.stringify({
        type: "image",
        imageMsg: { fileId: fileId }
    });

    const url = new URL(WEBHOOK_URL);
    const options = {
        hostname: url.hostname,
        port: url.port || 80,
        path: url.pathname + url.search,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(payload)
        }
    };

    return new Promise((resolve, reject) => {
        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => resolve(JSON.parse(body)));
        });
        req.on('error', (e) => reject(e));
        req.write(payload);
        req.end();
    });
}

/**
 * 发送文件/附件消息
 */
async function sendFile(fileId, fileName) {
    const payload = JSON.stringify({
        type: "file",
        fileMsg: { 
            fileId: fileId,
            fileName: fileName
        }
    });

    const url = new URL(WEBHOOK_URL);
    const options = {
        hostname: url.hostname,
        port: url.port || 80,
        path: url.pathname + url.search,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(payload)
        }
    };

    return new Promise((resolve, reject) => {
        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => resolve(JSON.parse(body)));
        });
        req.on('error', (e) => reject(e));
        req.write(payload);
        req.end();
    });
}

/**
 * 发送文本消息
 */
async function sendText(content) {
    const payload = JSON.stringify({
        type: "text",
        textMsg: { content: content }
    });

    const url = new URL(WEBHOOK_URL);
    const options = {
        hostname: url.hostname,
        port: url.port || 80,
        path: url.pathname + url.search,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(payload)
        }
    };

    return new Promise((resolve, reject) => {
        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => resolve(JSON.parse(body)));
        });
        req.on('error', (e) => reject(e));
        req.write(payload);
        req.end();
    });
}

// 命令行入口
const action = process.argv[2];
const param = process.argv[3];

if (action === 'image' && param) {
    uploadFile(param, 1).then(res => {
        if (res.ok) return sendImage(res.data.id);
        else throw new Error(res.message);
    }).then(res => console.log(JSON.stringify(res, null, 2)))
      .catch(err => console.error(err));
} else if (action === 'file' && param) {
    uploadFile(param, 2).then(res => {
        if (res.ok) return sendFile(res.data.id, path.basename(param));
        else throw new Error(res.message);
    }).then(res => console.log(JSON.stringify(res, null, 2)))
      .catch(err => console.error(err));
} else if (action === 'text' && param) {
    sendText(param).then(res => console.log(JSON.stringify(res, null, 2)))
      .catch(err => console.error(err));
}
