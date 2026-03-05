import * as fs from 'fs';
import { createClient } from '@openclaw-feishu/feishu-client';

function getAuth() {
  const appId = process.env.FEISHU_APP_ID;
  const appSecret = process.env.FEISHU_APP_SECRET;
  if (!appId || !appSecret) throw new Error('Missing FEISHU_APP_ID or FEISHU_APP_SECRET');
  return { appId, appSecret };
}

/**
 * 翻译文本
 */
export async function translateText(text: string, sourceLang: string, targetLang: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().translation.text.translate({
    data: {
      text: text,
      source_language: sourceLang,
      target_language: targetLang,
    }
  }));
}

/**
 * 检测语种
 */
export async function detectLanguage(text: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().translation.text.detect({
    data: {
      text: text,
    }
  }));
}

/**
 * 基础图片 OCR 识别
 */
export async function ocrImage(filePath: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  if (!fs.existsSync(filePath)) {
    return { ok: false, error: `文件不存在: ${filePath}` };
  }

  return await client.call(() => (client.getClient() as any).optical_char_recognition.image.basicRecognize({
    data: {
      image: fs.createReadStream(filePath),
    }
  }));
}

/**
 * 语音文件识别 (STT)
 * @param filePath - 语音文件路径
 * @param format - 格式 (pcm, adpcm, wav, opus, amr, m4a)
 */
export async function speechToText(filePath: string, format: string = 'opus') {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  if (!fs.existsSync(filePath)) {
    return { ok: false, error: `文件不存在: ${filePath}` };
  }

  // 语音识别通常需要上传到临时存储或者是直接流式。这里使用 fileRecognize
  return await client.call(() => (client.getClient() as any).speech_to_text.speech.fileRecognize({
    data: {
      speech: {
        speech: fs.readFileSync(filePath).toString('base64'),
      },
      config: {
        file_id: `upload_${Date.now()}`,
        format: format,
        engine_type: '16k_auto',
      }
    }
  }));
}
