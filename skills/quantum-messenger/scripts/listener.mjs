import http from 'http';
import { URL } from 'url';
import { exec } from 'child_process';
import fs from 'fs';
import path from 'path';

/**
 * =========================================================================
 * 量子密信 (Quantum Messenger) - 1号机 智能监听大脑
 * 
 * 作者：上海电信政支中心/量子能力中心 技术经理 程沛及他的openclaw机器人助手：1号机（Gemini)
 * 联系方式：18918115454
 * 邮箱：chenpei.sh@chinatelecom.cn
 * 
 * 说明：本脚本用于监听量子密信自定义会话机器人的消息，并调用 OpenClaw 进行逻辑回复。
 * 
 * 配置指南：
 * 1. KEY: 请从量子密信后台创建机器人后获取。
 * 2. PORT: 本地监听端口，需在服务器安全组/防火墙中放通。
 * 3. 机器人在量子密信 APP 设置时，URL 填：http://<您的公网IP>:<PORT>
 * =========================================================================
 */

const PORT = process.env.QUANTUM_PORT || 9001; // 监听端口
const KEY = process.env.QUANTUM_KEY || 'YOUR_QUANTUM_KEY_HERE'; // 优先从环境变量读取

async function askAgent(content) {
    return new Promise((resolve) => {
        // 调用 OpenClaw CLI 将消息传递给主 Agent
        const cmd = `openclaw agent --agent main --message ${JSON.stringify(content)}`;
        exec(cmd, (error, stdout, stderr) => {
            if (error) {
                console.error('[Quantum Listener] Brain Error:', stderr);
                resolve(`[系统异常] 抱歉，我暂时无法处理该指令。`);
            } else {
                // 清理终端控制字符
                const cleanOutput = stdout.replace(/\x1B\[[0-9;]*[mG]/g, '').trim();
                resolve(cleanOutput);
            }
        });
    });
}

/**
 * 媒体发送逻辑（图片/附件）
 */
async function uploadAndSendMedia(callBackUrl, phone, groupId, filePath, isImage = false) {
    const type = isImage ? 1 : 2; // 1代表图片，2代表文件/附件
    // 注意：upload-attachment 接口用于将本地文件同步至量子服务器
    const uploadUrlStr = `http://imtwo.zdxlz.com/im-external/v1/webhook/upload-attachment?key=${KEY}&type=${type}`;
    
    return new Promise((resolve, reject) => {
        const url = new URL(uploadUrlStr);
        const boundary = 'WebAppBoundary' + Math.random().toString(16).substring(2);
        
        const options = {
            hostname: url.hostname,
            port: url.port || 80,
            path: url.pathname + url.search,
            method: 'POST',
            headers: { 'Content-Type': `multipart/form-data; boundary=${boundary}` }
        };

        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', async () => {
                try {
                    const uploadRes = JSON.parse(body);
                    if (uploadRes.ok) {
                        const fileId = uploadRes.data.id;
                        // 组装量子密信媒体消息负载
                        const sendPayload = JSON.stringify({
                            type: isImage ? "image" : "file", // 类型标识：image 或 file
                            [isImage ? "imageMsg" : "fileMsg"]: {
                                fileId: fileId,
                                groupId: groupId,
                                isMentioned: true,
                                mentionType: 2,
                                mentionedMobileList: [phone]
                            }
                        });
                        await postToUrl(callBackUrl, sendPayload);
                        resolve();
                    } else { reject(new Error(uploadRes.message)); }
                } catch (e) { reject(e); }
            });
        });

        const header = `--${boundary}\r\n` +
                     `Content-Disposition: form-data; name="file"; filename="${path.basename(filePath)}"\r\n` +
                     `Content-Type: application/octet-stream\r\n\r\n`;
        req.write(header);
        fs.createReadStream(filePath).on('end', () => {
            req.write(`\r\n--${boundary}--\r\n`);
            req.end();
        }).pipe(req, { end: false });
    });
}

async function postToUrl(targetUrl, payload) {
    const url = new URL(targetUrl);
    const options = {
        hostname: url.hostname,
        port: url.port || (url.protocol === 'https:' ? 443 : 80),
        path: url.pathname + url.search,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(payload)
        }
    };
    return new Promise((resolve, reject) => {
        const transport = url.protocol === 'https:' ? import('https') : Promise.resolve({ request: http.request });
        transport.then(m => {
            const req = m.request(options, (res) => {
                let body = '';
                res.on('data', (chunk) => body += chunk);
                res.on('end', () => resolve(body));
            });
            req.on('error', reject);
            req.write(payload);
            req.end();
        });
    });
}

const server = http.createServer((req, res) => {
    if (req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk.toString());
        req.on('end', async () => {
            try {
                const data = JSON.parse(body);
                // 这里的 content 提取的是用户输入的【文本】内容
                const content = data.textMsg?.content || '';
                const phone = data.phone || '';
                const groupId = data.groupId || '';
                const callBackUrl = data.callBackUrl || '';

                if (content && callBackUrl) {
                    console.log(`[Quantum Listener] Processing message: ${content}`);
                    const rawReply = await askAgent(content);
                    
                    /**
                     * 状态栏回复逻辑：
                     * OpenClaw 的回复默认会包含状态栏（显示模型名、CTX使用率、时间）。
                     * 这里将完整回复（包含文本+状态栏）返回给用户。
                     */
                    const replyText = rawReply.trim();
                    
                    // 多模态处理：判断 AI 回复中是否包含本地图片或文件路径
                    if (replyText.includes('IMAGE:')) {
                        // 匹配格式: IMAGE:/path/to/image.png
                        const match = replyText.match(/IMAGE:([^\s\n]+)/);
                        const filePath = match ? match[1] : '';
                        if (filePath && fs.existsSync(filePath)) {
                            console.log(`[Quantum Listener] Sending image: ${filePath}`);
                            await uploadAndSendMedia(callBackUrl, phone, groupId, filePath, true);
                        }
                    } else if (replyText.includes('FILE:')) {
                        // 匹配格式: FILE:/path/to/file.pdf
                        const match = replyText.match(/FILE:([^\s\n]+)/);
                        const filePath = match ? match[1] : '';
                        if (filePath && fs.existsSync(filePath)) {
                            console.log(`[Quantum Listener] Sending attachment: ${filePath}`);
                            await uploadAndSendMedia(callBackUrl, phone, groupId, filePath, false);
                        }
                    } 
                    
                    // 发送最终的【文本回复】（包含 AI 生成的回答内容和实时系统状态栏）
                    const payload = JSON.stringify({
                        type: "text",
                        textMsg: {
                            content: replyText,
                            isMentioned: true,
                            mentionType: 2,
                            mentionedMobileList: [phone],
                            groupId: groupId
                        }
                    });
                    await postToUrl(callBackUrl, payload);
                }
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ ok: true }));
            } catch (e) {
                console.error('[Quantum Listener] Error:', e.message);
                res.writeHead(400); res.end();
            }
        });
    } else { res.writeHead(404); res.end(); }
});

server.listen(PORT, () => {
    console.log(`[Quantum Listener] 服务已启动，端口: ${PORT}`);
});
