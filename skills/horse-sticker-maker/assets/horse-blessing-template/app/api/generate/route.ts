import { NextRequest, NextResponse } from 'next/server'

const API_KEY = process.env.GOOGLE_API_KEY!
const BASE = process.env.GOOGLE_API_BASE || 'https://aiplatform.googleapis.com/v1/publishers/google/models'

async function geminiGenerate(prompt: string): Promise<string> {
  const res = await fetch(`${BASE}/gemini-2.5-flash:generateContent?key=${API_KEY}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{ role: 'user', parts: [{ text: prompt }] }],
      generationConfig: { temperature: 0.9, maxOutputTokens: 2048, thinkingConfig: { thinkingBudget: 0 } },
    }),
  })
  const data = await res.json()
  if (data.error) throw new Error(data.error.message || 'Gemini API error')
  // Handle streaming response (array) or single response
  const candidates = Array.isArray(data) ? data[data.length - 1]?.candidates : data.candidates
  return candidates?.[0]?.content?.parts?.map((p: any) => p.text).join('') || ''
}

async function imagenGenerate(prompt: string): Promise<string> {
  const res = await fetch(`${BASE}/imagen-4.0-generate-001:predict?key=${API_KEY}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      instances: [{ prompt }],
      parameters: { sampleCount: 1, aspectRatio: '9:16' },
    }),
  })
  const data = await res.json()
  if (data.error) throw new Error(data.error.message || 'Imagen API error')
  return data.predictions?.[0]?.bytesBase64Encoded || ''
}

export async function POST(req: NextRequest) {
  try {
    const { name } = await req.json()
    if (!name || typeof name !== 'string' || name.trim().length === 0 || name.trim().length > 10) {
      return NextResponse.json({ error: '请输入有效的名字（1-10个字）' }, { status: 400 })
    }

    const trimmed = name.trim()
    const chars = Array.from(trimmed)

    // 1. Generate poem + blessing via Gemini
    // Build acrostic constraint: pad to 4 chars for 七绝 (4 lines)
    const padded = chars.length >= 4 ? chars.slice(0, 4) : [...chars, ...['马', '到', '成', '功'].slice(0, 4 - chars.length)]

    const textPrompt = `你是一位精通格律的诗词大师+创意文案高手。请为"${trimmed}"创作2026马年专属祝福。

【藏头诗·七言绝句】严格要求（违反任何一条都不合格）：
1. 必须恰好四句，不能多不能少
2. 每句恰好7个汉字（不含标点），句末用中文逗号或句号
3. 四句的第一个字依次是：「${padded[0]}」「${padded[1]}」「${padded[2]}」「${padded[3]}」
4. 押韵：第一、二、四句的最后一个字必须押韵（韵母相同或相近）
5. 第三句最后一个字用仄声（不押韵），形成"AABA"韵律
6. 内容要有画面感：骏马奔腾、春风破晓、星辰大海等意象，避免空洞说教
7. 禁止使用以下俗套词组：宏图大展、前程似锦、鹏程万里、蒸蒸日上

自检清单（生成后逐条验证）：
- [ ] 共四句？每句数汉字=7？
- [ ] 第1/2/3/4句首字分别是${padded.join('/')}？
- [ ] 第1、2、4句尾字押韵？第3句尾字不押韵？

【创意祝福语】要求：
- 40字以内，必须含"${trimmed}"
- 风格：像好朋友发的微信，不是官方贺卡
- 可以幽默、可以温暖、可以谐音梗，要真诚有个性
- 参考风格："2026了，${trimmed}骑上快马冲就完了！你的好运配速：每秒一个小目标 🏇"

【运势标签】要求：
- 8字以内，必须含"马"字
- 要有趣味和记忆点，像社交媒体爆款标签
- 好的例子：一马平川躺赢版、桃花快马加鞭来、财运万马奔腾中
- 坏的例子：马到成功（太俗）、万事如意（没有马）

严格按JSON返回，不要用markdown代码块包裹：
{"poem":"四句七绝用\\n分隔","blessing":"创意祝福语","fortune":"运势标签"}`

    const textRaw = await geminiGenerate(textPrompt)
    
    // Extract JSON from response (handle potential markdown wrapping)
    const jsonMatch = textRaw.match(/\{[\s\S]*\}/)
    if (!jsonMatch) throw new Error('文本生成格式错误')
    const textResult = JSON.parse(jsonMatch[0])

    // 2. Generate horse image via Imagen
    const imagePrompt = `A magnificent golden horse galloping through auspicious red clouds, Chinese New Year celebration style, traditional Chinese art fusion with modern illustration, gold and red color scheme, festive lanterns and fireworks in background, lucky symbols, elegant and joyful atmosphere, high quality digital art`

    const imageBase64 = await imagenGenerate(imagePrompt)

    return NextResponse.json({
      poem: textResult.poem,
      blessing: textResult.blessing,
      fortune: textResult.fortune || '马到成功',
      image: imageBase64 ? `data:image/png;base64,${imageBase64}` : null,
    })
  } catch (e: any) {
    console.error('Generate error:', e)
    return NextResponse.json({ error: '生成失败，请重试: ' + e.message }, { status: 500 })
  }
}
