import { NextRequest, NextResponse } from 'next/server'

const GEMINI_API_KEY = process.env.GEMINI_API_KEY!
const GEMINI_MODEL = 'gemini-3-pro-image-preview'

const STYLE_PROMPTS: Record<string, string> = {
  rich: '金色骏马被金币和红包环绕，富贵发财主题',
  epic: '威武霸气的骏马昂首嘶鸣，火焰鬃毛，英雄史诗风格',
  cute: '超萌Q版小马驹，大眼睛水汪汪，卡哇伊粉嫩风格',
  lucky: '骏马踏祥云，周围环绕吉祥如意符号，传统中国祝福风格',
  party: '欢乐的马在庆祝，周围有烟花彩带，派对狂欢风格',
  zen: '一匹马悠闲躺着冥想，旁边有香炉青烟，佛系搞笑风格',
}

async function geminiGenerateImage(prompt: string): Promise<string> {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}`
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: {
        responseModalities: ['TEXT', 'IMAGE'],
      },
    }),
  })
  const data = await res.json()
  if (data.error) throw new Error(data.error.message || 'Gemini API error')

  const parts = data.candidates?.[0]?.content?.parts || []
  for (const part of parts) {
    if (part.inlineData) {
      return `data:${part.inlineData.mimeType};base64,${part.inlineData.data}`
    }
  }
  throw new Error('未生成图片')
}

export async function POST(req: NextRequest) {
  try {
    const { text, styleId } = await req.json()
    if (!text || typeof text !== 'string' || text.trim().length === 0 || text.trim().length > 8) {
      return NextResponse.json({ error: '请输入1-8个字的表情文字' }, { status: 400 })
    }

    const trimmed = text.trim()
    const styleDesc = STYLE_PROMPTS[styleId] || STYLE_PROMPTS.rich

    const prompt = `生成一张正方形微信表情包图片：

- 纯红色喜庆背景，有金色光效和闪烁粒子（单一背景，不要图中图）
- 画面中心是一匹金色骏马，${styleDesc}
- 马头上戴着一个金色发箍，发箍正面清晰写着"${trimmed}"（金色醒目大字，必须在发箍上）
- 马的周围有飞舞旋转的金币和红包（要有动感，像在旋转飞舞的感觉）
- 画面底部用大号醒目金色艺术字写"2026，财源滚滚来"（字要大、要醒目、要有质感）
- 整体风格：喜庆、炫酷、大气，正方形构图

重要：发箍上只写"${trimmed}"，底部大字"2026，财源滚滚来"要非常醒目。金币红包要有旋转飞舞的动感效果。`

    const imageDataUrl = await geminiGenerateImage(prompt)

    return NextResponse.json({ image: imageDataUrl })
  } catch (e: any) {
    console.error('Sticker generate error:', e)
    return NextResponse.json({ error: '生成失败: ' + e.message }, { status: 500 })
  }
}
