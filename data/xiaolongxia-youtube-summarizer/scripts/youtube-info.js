#!/usr/bin/env node

/**
 * YouTube Video Info & Transcript Fetcher
 * 获取 YouTube 视频信息和字幕
 * 
 * Usage:
 *   node youtube-info.js <video_url_or_id> [--transcript] [--lang zh]
 */

const https = require('https');
const http = require('http');

// 从 URL 中提取视频 ID
function extractVideoId(input) {
  if (!input) return null;
  
  // 如果已经是 11 位 ID
  if (/^[a-zA-Z0-9_-]{11}$/.test(input)) {
    return input;
  }
  
  // 各种 URL 格式
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|m\.youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})/,
    /youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})/
  ];
  
  for (const pattern of patterns) {
    const match = input.match(pattern);
    if (match) return match[1];
  }
  
  return null;
}

// 获取视频页面内容
async function fetchVideoPage(videoId) {
  return new Promise((resolve, reject) => {
    const url = `https://www.youtube.com/watch?v=${videoId}`;
    
    https.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

// 从页面中提取视频信息
function parseVideoInfo(html) {
  const info = {
    title: '',
    channel: '',
    publishDate: '',
    description: '',
    duration: '',
    viewCount: '',
    transcript: null
  };
  
  // 提取标题
  const titleMatch = html.match(/<title>([^<]+)<\/title>/);
  if (titleMatch) {
    info.title = titleMatch[1].replace(' - YouTube', '').trim();
  }
  
  // 提取频道名称
  const channelMatch = html.match(/"author":"([^"]+)"/);
  if (channelMatch) {
    info.channel = channelMatch[1];
  }
  
  // 提取描述
  const descMatch = html.match(/"shortDescription":"([^"]*)"/);
  if (descMatch) {
    info.description = descMatch[1].replace(/\\n/g, '\n');
  }
  
  // 提取时长
  const durationMatch = html.match(/"lengthSeconds":"(\d+)"/);
  if (durationMatch) {
    const seconds = parseInt(durationMatch[1]);
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    info.duration = `${mins}:${secs.toString().padStart(2, '0')}`;
  }
  
  // 提取观看数
  const viewMatch = html.match(/"viewCount":"(\d+)"/);
  if (viewMatch) {
    info.viewCount = parseInt(viewMatch[1]).toLocaleString();
  }
  
  return info;
}

// 从页面中提取字幕轨道
function extractCaptionTracks(html) {
  const captionMatch = html.match(/"captionTracks":(\[[^\]]+\])/);
  if (!captionMatch) return [];
  
  try {
    // 解析 JSON
    const tracks = JSON.parse(captionMatch[1].replace(/\\"/g, '"').replace(/\\\\/g, '\\'));
    return tracks.map(track => ({
      baseUrl: track.baseUrl,
      languageCode: track.languageCode,
      name: track.name?.simpleText || track.languageCode,
      isTranslatable: track.isTranslatable
    }));
  } catch (e) {
    return [];
  }
}

// 获取字幕内容
async function fetchTranscript(trackUrl) {
  return new Promise((resolve, reject) => {
    https.get(trackUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        // 解析 XML 字幕
        const textMatches = data.match(/<text start="([^"]+)" dur="([^"]+)"[^>]*>([^<]+)<\/text>/g);
        if (textMatches) {
          const transcript = textMatches.map(match => {
            const [, start, dur, text] = match.match(/start="([^"]+)" dur="([^"]+)"[^>]*>([^<]+)<\/text>/);
            return {
              start: parseFloat(start),
              duration: parseFloat(dur),
              text: decodeHTMLEntities(text)
            };
          });
          resolve(transcript);
        } else {
          resolve([]);
        }
      });
    }).on('error', reject);
  });
}

function decodeHTMLEntities(text) {
  return text
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\n/g, ' ');
}

// 格式化字幕为纯文本
function formatTranscriptText(transcript) {
  return transcript.map(item => item.text).join(' ');
}

// 格式化字幕为带时间戳的文本
function formatTranscriptWithTimestamps(transcript) {
  return transcript.map(item => {
    const mins = Math.floor(item.start / 60);
    const secs = Math.floor(item.start % 60);
    return `[${mins}:${secs.toString().padStart(2, '0')}] ${item.text}`;
  }).join('\n');
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(`
YouTube Video Info & Transcript Fetcher

Usage:
  node youtube-info.js <video_url_or_id> [options]

Options:
  --transcript         获取字幕
  --transcript-full    获取带时间戳的字幕
  --lang <code>        指定字幕语言 (默认: 优先中文，其次英文)
  --json               输出 JSON 格式

Examples:
  node youtube-info.js "https://www.youtube.com/watch?v=YZVpUeEvGxs"
  node youtube-info.js YZVpUeEvGxs --transcript
  node youtube-info.js "https://youtu.be/YZVpUeEvGxs" --transcript-full --lang en
`);
    process.exit(0);
  }
  
  const input = args.find(a => !a.startsWith('--'));
  const getTranscript = args.includes('--transcript') || args.includes('--transcript-full');
  const transcriptWithTimestamps = args.includes('--transcript-full');
  const outputJson = args.includes('--json');
  
  const langIndex = args.indexOf('--lang');
  const preferredLang = langIndex !== -1 ? args[langIndex + 1] : null;
  
  const videoId = extractVideoId(input);
  
  if (!videoId) {
    console.error('❌ 无法识别视频 ID，请检查 URL');
    process.exit(1);
  }
  
  try {
    console.error(`📹 获取视频信息: ${videoId}`);
    
    const html = await fetchVideoPage(videoId);
    const info = parseVideoInfo(html);
    info.videoId = videoId;
    info.url = `https://www.youtube.com/watch?v=${videoId}`;
    
    if (getTranscript) {
      console.error('📝 正在获取字幕...');
      const tracks = extractCaptionTracks(html);
      
      if (tracks.length === 0) {
        console.error('⚠️ 该视频没有字幕');
        info.transcript = null;
        info.transcriptAvailable = false;
      } else {
        // 选择字幕轨道
        let selectedTrack = null;
        
        if (preferredLang) {
          selectedTrack = tracks.find(t => t.languageCode === preferredLang);
        } else {
          // 优先选择中文字幕，其次英文，再次第一个可用
          selectedTrack = tracks.find(t => t.languageCode === 'zh' || t.languageCode === 'zh-CN' || t.languageCode === 'zh-Hans') ||
                         tracks.find(t => t.languageCode === 'en') ||
                         tracks[0];
        }
        
        if (selectedTrack) {
          console.error(`✅ 使用字幕: ${selectedTrack.name} (${selectedTrack.languageCode})`);
          const transcript = await fetchTranscript(selectedTrack.baseUrl);
          
          if (transcriptWithTimestamps) {
            info.transcript = formatTranscriptWithTimestamps(transcript);
          } else {
            info.transcript = formatTranscriptText(transcript);
          }
          info.transcriptLanguage = selectedTrack.languageCode;
          info.transcriptAvailable = true;
        }
      }
    }
    
    if (outputJson) {
      console.log(JSON.stringify(info, null, 2));
    } else {
      console.log('\n' + '='.repeat(60));
      console.log(`📺 ${info.title}`);
      console.log('='.repeat(60));
      console.log(`频道: ${info.channel}`);
      console.log(`时长: ${info.duration}`);
      console.log(`观看: ${info.viewCount}`);
      console.log(`链接: ${info.url}`);
      
      if (info.description) {
        console.log('\n📋 描述:');
        console.log(info.description.slice(0, 500) + (info.description.length > 500 ? '...' : ''));
      }
      
      if (info.transcript) {
        console.log('\n📝 字幕:');
        console.log('-'.repeat(60));
        console.log(info.transcript);
      }
      
      console.log('\n' + '='.repeat(60));
    }
    
  } catch (error) {
    console.error('❌ 获取视频信息失败:', error.message);
    process.exit(1);
  }
}

main();
