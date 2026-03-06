#!/usr/bin/env node

/**
 * 抖音无水印视频下载和文案提取工具 (Node.js 版本)
 * 
 * 功能:
 * 1. 从抖音分享链接获取无水印视频下载链接
 * 2. 下载视频并提取音频
 * 3. 使用硅基流动 API 从音频中提取文本
 * 4. 使用 MiniMax 模型进行语义分段（可选）
 * 5. 自动保存文案到文件
 * 
 * 环境变量:
 * - SILI_FLOW_API_KEY: 硅基流动 API 密钥 (用于文案提取功能)
 * - MINIMAX_API_KEY: MiniMax API 密钥 (用于语义分段功能)
 * 
 * 使用示例:
 *   node douyin.js info "抖音分享链接"
 *   node douyin.js download "抖音分享链接" -o /tmp/douyin-download
 *   node douyin.js extract "抖音分享链接" -o /tmp/douyin-download
 *   node douyin.js extract "抖音链接" --segment     # 带语义分段
 *   node douyin.js extract "抖音链接" --no-segment  # 不分段
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const https = require('https');
const http = require('http');
const { URL } = require('url');

// 配置
const HEADERS = {
  'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/121.0.2277.107 Version/17.0 Mobile/15E148 Safari/604.1',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'zh-CN,zh;q=0.9',
};

const SILI_FLOW_BASE_URL = 'https://api.siliconflow.cn/v1/audio/transcriptions';
const SILI_FLOW_MODEL = 'FunAudioLLM/SenseVoiceSmall';
const MINIMAX_BASE_URL = 'https://api.minimaxi.com';
const DEFAULT_DOWNLOAD_PATH = '/tmp/douyin-download/';

// 工具函数：Promise 版本的 http 请求
function httpRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const client = parsedUrl.protocol === 'https:' ? https : http;
    
    const opts = {
      method: options.method || 'GET',
      headers: { ...HEADERS, ...options.headers }
    };
    
    const req = client.request(url, opts, (res) => {
      // 处理重定向
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        httpRequest(res.headers.location, options)
          .then(resolve)
          .catch(reject);
        return;
      }
      
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        resolve({ 
          statusCode: res.statusCode, 
          headers: res.headers,
          body: data,
          url: url 
        });
      });
    });
    
    req.on('error', reject);
    req.setTimeout(30000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
    
    if (options.body) {
      req.write(options.body);
    }
    req.end();
  });
}

// 工具函数：下载文件
async function downloadFile(url, filepath, showProgress = true) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const client = parsedUrl.protocol === 'https:' ? https : http;
    
    const req = client.get(url, { headers: HEADERS }, (res) => {
      // 处理重定向
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        downloadFile(res.headers.location, filepath, showProgress)
          .then(resolve)
          .catch(reject);
        return;
      }
      
      if (res.statusCode !== 200) {
        reject(new Error(`HTTP ${res.statusCode}`));
        return;
      }
      
      const totalSize = parseInt(res.headers['content-length'] || '0', 10);
      let downloaded = 0;
      
      const writer = fs.createWriteStream(filepath);
      
      res.on('data', (chunk) => {
        downloaded += chunk.length;
        if (showProgress && totalSize > 0) {
          const progress = (downloaded / totalSize * 100).toFixed(1);
          process.stdout.write(`\r下载进度: ${progress}%`);
        }
      });
      
      res.pipe(writer);
      
      writer.on('finish', () => {
        if (showProgress) console.log(`\n文件已保存: ${filepath}`);
        resolve(filepath);
      });
      
      writer.on('error', reject);
    });
    
    req.on('error', reject);
    req.setTimeout(120000, () => {
      req.destroy();
      reject(new Error('Download timeout'));
    });
  });
}

// 工具函数：运行 ffmpeg
function runFfmpeg(args) {
  return new Promise((resolve, reject) => {
    const proc = spawn('ffmpeg', args);
    
    let stderr = '';
    proc.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    proc.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`ffmpeg exited with code ${code}: ${stderr.slice(-500)}`));
      }
    });
    
    proc.on('error', reject);
  });
}

// 解析抖音分享链接或 modal_id
async function parseShareUrl(shareText) {
  // 首先检查是否是 modal_id（16+位数字或 modal_id=xxx 格式）
  const modalIdMatch = shareText.match(/(?:modal_id[=:])?(\d{16,})/);
  if (modalIdMatch) {
    const modalId = modalIdMatch[1];
    return await getVideoInfoByModalId(modalId);
  }
  
  // 提取 URL
  const urlMatch = shareText.match(/https?:\/\/[^\s]+/);
  if (!urlMatch) {
    throw new Error('未找到有效的分享链接');
  }
  
  const shareUrl = urlMatch[0];
  
  // 第一步：访问分享链接，获取重定向后的 URL 和 video_id
  const response1 = await httpRequest(shareUrl);
  const finalUrl = response1.url;
  
  // 从 URL 中提取 video_id
  const videoIdMatch = finalUrl.match(/\/video\/(\d+)/);
  if (!videoIdMatch) {
    throw new Error('无法从URL中提取视频ID');
  }
  const videoId = videoIdMatch[1];
  
  return await getVideoInfoByModalId(videoId);
}

// 通过 modal_id 获取视频信息
async function getVideoInfoByModalId(modalId) {
  // 访问 iesdouyin.com 页面
  const pageUrl = `https://www.iesdouyin.com/share/video/${modalId}/`;
  const response = await httpRequest(pageUrl);
  
  // 从 HTML 中提取 window._ROUTER_DATA
  const match = response.body.match(/window\._ROUTER_DATA\s*=\s*(.*?)<\/script>/);
  if (!match || !match[1]) {
    throw new Error('从HTML中解析视频信息失败');
  }
  
  // 解析 JSON
  const jsonData = JSON.parse(match[1].trim());
  const loaderData = jsonData.loaderData || jsonData;
  
  let videoData;
  if (loaderData['video_(id)/page']) {
    videoData = loaderData['video_(id)/page'].videoInfoRes?.item_list?.[0];
  } else if (loaderData['note_(id)/page']) {
    videoData = loaderData['note_(id)/page'].videoInfoRes?.item_list?.[0];
  }
  
  if (!videoData) {
    throw new Error('无法从JSON中解析视频信息');
  }
  
  const videoUrl = videoData.video?.play_addr?.url_list?.[0]?.replace('playwm', 'play') ||
                   videoData.video?.download_addr?.url_list?.[0];
  const desc = videoData.desc || `douyin_${modalId}`;
  
  return {
    url: videoUrl,
    title: desc.replace(/[\\/:*?"<>|]/g, '_'),
    video_id: modalId
  };
}

// 下载视频
async function downloadVideo(videoInfo, outputDir, showProgress = true) {
  const outputPath = path.join(outputDir, `${videoInfo.video_id}.mp4`);
  
  if (showProgress) {
    console.log(`正在下载视频: ${videoInfo.title}`);
  }
  
  await downloadFile(videoInfo.url, outputPath, showProgress);
  
  return outputPath;
}

// 提取音频
async function extractAudio(videoPath, showProgress = true) {
  const audioPath = videoPath.replace(/\.mp4$/, '.mp3');
  
  if (showProgress) {
    console.log('正在提取音频...');
  }
  
  await runFfmpeg([
    '-i', videoPath,
    '-vn',
    '-acodec', 'libmp3lame',
    '-q:a', '0',
    '-y',
    audioPath
  ]);
  
  if (showProgress) {
    console.log(`音频已保存: ${audioPath}`);
  }
  
  return audioPath;
}

// 语音转文字 - 使用 curl
async function transcribeAudio(audioPath, apiKey, showProgress = true) {
  if (showProgress) {
    console.log('正在识别语音...');
  }
  
  return new Promise((resolve, reject) => {
    const { spawn } = require('child_process');
    const proc = spawn('curl', [
      '-X', 'POST',
      SILI_FLOW_BASE_URL,
      '-H', `Authorization: Bearer ${apiKey}`,
      '-F', `file=@${audioPath}`,
      '-F', `model=${SILI_FLOW_MODEL}`
    ]);
    
    let stdout = '';
    let stderr = '';
    
    proc.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    proc.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    proc.on('close', (code) => {
      if (code === 0) {
        try {
          const json = JSON.parse(stdout);
          resolve(json.text || JSON.stringify(json));
        } catch {
          resolve(stdout);
        }
      } else {
        reject(new Error(`curl failed: ${stderr}`));
      }
    });
    
    proc.on('error', reject);
  });
}

// 语义分段 - 使用 MiniMax API
async function semanticSegment(text, apiKey, showProgress = true) {
  if (!apiKey) {
    apiKey = process.env.MINIMAX_API_KEY;
  }
  
  if (!apiKey) {
    if (showProgress) {
      console.log('Warning: MINIMAX_API_KEY 未设置，跳过语义分段');
    }
    return text;
  }
  
  if (showProgress) {
    console.log('正在语义分段...');
  }
  
  const url = `${MINIMAX_BASE_URL}/v1/text/chatcompletion_v2`;
  
  const prompt = `你是专业语音转写文本分段助手。
请对下面这段语音转写文本进行**自然语义分段**。

要求：
1. 根据语义完整性和内容逻辑进行分段
2. 每段应该是内容相对完整的句子或论述
3. 保持原文内容不变，只添加合理的段落分隔
4. 保留原文的语气词和表达特点
5. 适当添加##小标题概括每段主旨（如果内容足够长）

请直接返回分段后的文本，用markdown格式，小标题用##开头。不要添加其他说明。`;

  const data = {
    model: "MiniMax-M2.5",
    messages: [
      { role: "system", content: prompt },
      { role: "user", content: text }
    ],
    max_tokens: 4096,
    temperature: 0.3
  };

  return new Promise((resolve, reject) => {
    const { spawn } = require('child_process');
    const proc = spawn('curl', [
      '-X', 'POST',
      url,
      '-H', `Authorization: Bearer ${apiKey}`,
      '-H', 'Content-Type: application/json',
      '-d', JSON.stringify(data)
    ]);

    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (chunk) => { stdout += chunk.toString(); });
    proc.stderr.on('data', (chunk) => { stderr += chunk.toString(); });

    proc.on('close', (code) => {
      if (code === 0) {
        try {
          const json = JSON.parse(stdout);
          if (json.choices && json.choices[0]) {
            resolve(json.choices[0].message.content);
          } else {
            console.error('分段失败:', stdout);
            resolve(text);
          }
        } catch (e) {
          console.error('解析失败:', e);
          resolve(text);
        }
      } else {
        reject(new Error(`curl failed: ${stderr}`));
      }
    });
    proc.on('error', reject);
  });
}

// 提取文案主函数
async function extractText(shareLink, apiKey, outputDir, saveVideo = false, showProgress = true, doSegment = true) {
  if (!apiKey) {
    apiKey = process.env.SILI_FLOW_API_KEY;
  }
  
  if (!apiKey) {
    throw new Error('未设置 API 密钥，请设置 SILI_FLOW_API_KEY 环境变量');
  }
  
  if (showProgress) {
    console.log('正在解析抖音分享链接...');
  }
  
  const videoInfo = await parseShareUrl(shareLink);
  
  if (showProgress) {
    console.log('正在下载视频...');
  }
  
  const videoPath = await downloadVideo(videoInfo, outputDir, showProgress);
  
  if (showProgress) {
    console.log('正在提取音频...');
  }
  
  const audioPath = await extractAudio(videoPath, showProgress);
  
  if (showProgress) {
    console.log('正在从音频中提取文本...');
  }
  
  let textContent = await transcribeAudio(audioPath, apiKey, showProgress);
  
  // 语义分段
  if (doSegment) {
    textContent = await semanticSegment(textContent, null, showProgress);
  }
  
  // 保存文案
  const outputPath = path.join(outputDir, videoInfo.video_id, 'transcript.md');
  const outputFolder = path.dirname(outputPath);
  
  fs.mkdirSync(outputFolder, { recursive: true });
  
  const markdown = `# ${videoInfo.title}

| 属性 | 值 |
|------|-----|
| 视频ID | \`${videoInfo.video_id}\` |
| 提取时间 | ${new Date().toLocaleString('zh-CN')} |
| 下载链接 | [点击下载](${videoInfo.url}) |

---

## 文案内容

${textContent}
`;
  
  fs.writeFileSync(outputPath, markdown, 'utf-8');
  
  if (showProgress) {
    console.log(`文案已保存到: ${outputPath}`);
  }
  
  // 清理临时文件
  if (!saveVideo) {
    try { fs.unlinkSync(videoPath); } catch {}
  }
  try { fs.unlinkSync(audioPath); } catch {}
  
  return {
    video_info: videoInfo,
    text: textContent,
    output_path: outputPath
  };
}

// 主入口
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const shareLink = args[1];
  
  if (!command || !shareLink) {
    console.log(`
抖音无水印视频下载和文案提取工具

用法:
  node douyin.js info <分享链接|modal_id>         - 获取视频信息
  node douyin.js download <链接|modal_id> -o <目录>  - 下载视频（默认: /tmp/douyin-download/）
  node douyin.js extract <链接|modal_id> -o <目录>   - 提取文案（默认: /tmp/douyin-download/）
  node douyin.js extract <链接> --no-segment        - 提取文案（不语义分段）
  
支持输入:
  - 抖音分享链接: https://v.douyin.com/xxxxx
  - modal_id: 7597329042169220398
  - modal_id=xxx 格式

`);
    process.exit(1);
  }
  
  // 解析参数
  let outputDir = DEFAULT_DOWNLOAD_PATH;
  let saveVideo = false;
  let doSegment = true;
  
  for (let i = 2; i < args.length; i++) {
    if (args[i] === '-o' && args[i + 1]) {
      outputDir = args[i + 1];
      i++;
    } else if (args[i] === '-v' || args[i] === '--save-video') {
      saveVideo = true;
    } else if (args[i] === '--segment') {
      doSegment = true;
    } else if (args[i] === '--no-segment') {
      doSegment = false;
    }
  }
  
  try {
    if (command === 'info') {
      const info = await parseShareUrl(shareLink);
      console.log('\n' + '='.repeat(50));
      console.log('视频信息:');
      console.log('='.repeat(50));
      console.log(`视频ID: ${info.video_id}`);
      console.log(`标题: ${info.title}`);
      console.log(`下载链接: ${info.url}`);
      console.log('='.repeat(50));
      
    } else if (command === 'download') {
      const videoInfo = await parseShareUrl(shareLink);
      const videoPath = await downloadVideo(videoInfo, outputDir);
      console.log(`\n视频已保存到: ${videoPath}`);
      
    } else if (command === 'extract') {
      const result = await extractText(shareLink, null, outputDir, saveVideo, true, doSegment);
      console.log('\n' + '='.repeat(50));
      console.log('提取完成!');
      console.log('='.repeat(50));
      console.log(`视频ID: ${result.video_info.video_id}`);
      console.log(`标题: ${result.video_info.title}`);
      console.log(`保存位置: ${result.output_path}`);
      console.log('='.repeat(50));
      console.log('\n文案内容:\n');
      console.log(result.text.slice(0, 500) + '...' || result.text);
      console.log('\n' + '='.repeat(50));
    }
    
  } catch (error) {
    console.error(`错误: ${error.message}`);
    process.exit(1);
  }
}

main();
