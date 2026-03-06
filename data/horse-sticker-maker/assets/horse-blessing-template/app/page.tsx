'use client'
import { useState, useRef, useCallback } from 'react'
import html2canvas from 'html2canvas-pro'

type Result = { poem: string; blessing: string; fortune: string; image: string | null }

export default function Home() {
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<Result | null>(null)
  const [savedImage, setSavedImage] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const cardRef = useRef<HTMLDivElement>(null)

  const saveAsImage = useCallback(async () => {
    if (!cardRef.current || saving) return
    setSaving(true)
    try {
      const canvas = await html2canvas(cardRef.current, {
        scale: 3,
        useCORS: true,
        backgroundColor: '#7f1d1d',
        logging: false,
      })
      const dataUrl = canvas.toDataURL('image/png')
      setSavedImage(dataUrl)
    } catch (e) {
      alert('图片生成失败，请长按截图保存')
    } finally {
      setSaving(false)
    }
  }, [saving])

  async function generate() {
    if (!name.trim() || loading) return
    setLoading(true)
    setResult(null)
    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim() }),
      })
      const data = await res.json()
      if (data.error) throw new Error(data.error)
      setResult(data)
    } catch (e: any) {
      alert('生成失败: ' + e.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-6">
        <div className="text-7xl animate-bounce mb-6">🐴</div>
        <p className="text-white text-xl font-medium">
          AI 正在为 <span className="text-yellow-300 font-bold">{name}</span> 专属创作...
        </p>
        <div className="flex gap-2 mt-4">
          <span className="text-white/60 text-sm">✍️ 写藏头诗</span>
          <span className="text-white/40">→</span>
          <span className="text-white/60 text-sm">🎨 画骏马</span>
          <span className="text-white/40">→</span>
          <span className="text-white/60 text-sm">🎁 生成祝福卡</span>
        </div>
      </div>
    )
  }

  if (result) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-4 py-8">
        {/* 祝福卡 */}
        <div ref={cardRef} className="blessing-card rounded-2xl overflow-hidden max-w-sm w-full mx-auto shadow-2xl">
          {/* AI 生成的马图 */}
          {result.image && (
            <div className="relative">
              <img src={result.image} alt="AI生成骏马图" className="w-full h-48 object-cover" />
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-red-900/80 to-transparent h-16" />
            </div>
          )}
          
          <div className="p-6 text-center bg-gradient-to-b from-red-800 to-red-900">
            {/* 运势标签 */}
            <div className="inline-block bg-yellow-400 text-red-900 text-xs font-bold px-3 py-1 rounded-full mb-3">
              🐴 {result.fortune}
            </div>
            
            <h2 className="text-yellow-300 text-2xl font-bold mb-4">{name} 的马年祝福</h2>
            
            {/* 藏头诗 */}
            <div className="bg-red-950/50 rounded-xl p-5 mb-4 border border-yellow-400/20">
              {result.poem.split('\n').map((line, i) => (
                <p key={i} className="text-yellow-100 text-lg leading-relaxed font-serif">
                  <span className="text-yellow-400 font-bold">{line[0]}</span>
                  {line.slice(1)}
                </p>
              ))}
            </div>
            
            {/* 祝福语 */}
            <p className="text-yellow-100/90 text-sm leading-relaxed mb-4">{result.blessing}</p>
            
            <div className="border-t border-yellow-400/20 pt-3 mt-3">
              <p className="text-xs text-yellow-200/50">🐴 马上有福 · AI 专属祝福 · 2026马年</p>
            </div>
          </div>
        </div>

        {/* 生成的图片预览 */}
        {savedImage && (
          <div className="mt-4 max-w-sm w-full mx-auto">
            <p className="text-yellow-300 text-sm text-center mb-2">✅ 图片已生成！长按下方图片保存</p>
            <img src={savedImage} alt="祝福卡" className="w-full rounded-xl shadow-lg" />
          </div>
        )}

        <div className="flex gap-3 mt-4">
          {!savedImage ? (
            <button
              onClick={saveAsImage}
              disabled={saving}
              className="bg-yellow-500 hover:bg-yellow-400 disabled:opacity-50 text-red-900 font-bold px-6 py-3 rounded-full shadow-lg transition active:scale-95"
            >
              {saving ? '⏳ 生成中...' : '📸 生成图片保存'}
            </button>
          ) : (
            <a
              href={savedImage}
              download={`${name}-马年祝福.png`}
              className="bg-green-500 hover:bg-green-400 text-white font-bold px-6 py-3 rounded-full shadow-lg transition active:scale-95"
            >
              💾 下载图片
            </a>
          )}
          
          <button
            onClick={() => { setResult(null); setName(''); setSavedImage(null) }}
            className="bg-white/20 hover:bg-white/30 text-white px-6 py-3 rounded-full backdrop-blur transition"
          >
            🐴 再来一个
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6">
      <div className="text-center mb-8">
        <div className="text-8xl mb-4">🐴</div>
        <h1 className="text-white text-4xl font-bold mb-2">马上有福</h1>
        <p className="text-white/80 text-lg">AI 为你写一首专属马年藏头诗</p>
        <p className="text-yellow-300/70 text-sm mt-1">每个人的祝福都独一无二 ✨</p>
      </div>

      <div className="w-full max-w-xs">
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && generate()}
          placeholder="输入你的名字"
          maxLength={10}
          className="w-full px-5 py-4 rounded-2xl text-center text-xl bg-white/95 text-gray-800 placeholder-gray-400 outline-none shadow-lg focus:ring-2 focus:ring-yellow-400"
        />
        
        <button
          onClick={generate}
          disabled={!name.trim()}
          className="w-full mt-4 bg-yellow-500 hover:bg-yellow-400 disabled:opacity-50 text-red-900 font-bold text-lg px-6 py-4 rounded-2xl shadow-lg transition active:scale-95"
        >
          ✨ 生成我的马年祝福
        </button>
      </div>

      <a href="/sticker" className="text-yellow-300/70 text-sm mt-6 hover:text-yellow-300 transition">
        🤪 去做马年表情包 →
      </a>
      <p className="text-white/40 text-xs mt-4">AI 藏头诗 + AI 骏马图 · 千人千面</p>
    </div>
  )
}
