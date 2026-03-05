'use client'
import { useState, useCallback } from 'react'
import Script from 'next/script'

type StickerResult = { image: string; text: string }

function createAnimatedSticker(
  horseFrames: HTMLImageElement[],
  stickerText: string,
  onComplete: (gifDataUrl: string) => void
) {
  const size = 240  // WeChat sticker max recommended size
  const frames = 18  // 6 horse frames × 3 cycles
  const canvas = document.createElement('canvas')
  canvas.width = size
  canvas.height = size
  const ctx = canvas.getContext('2d')!

  // @ts-ignore
  const gif = new GIF({
    workers: 2,
    quality: 8,
    width: size,
    height: size,
    workerScript: '/gif.worker.js',
  })

  // Pre-calculate sparkle positions
  const sparkles = Array.from({ length: 30 }, () => ({
    x: Math.random() * size,
    y: Math.random() * size,
    r: Math.random() * 2 + 0.5,
    phase: Math.random() * Math.PI * 2,
  }))

  for (let f = 0; f < frames; f++) {
    const t = f / frames

    // === RED GRADIENT BACKGROUND ===
    const grad = ctx.createRadialGradient(size * 0.4, size * 0.3, 30, size / 2, size / 2, size * 0.8)
    grad.addColorStop(0, '#FF1A1A')
    grad.addColorStop(0.5, '#CC0000')
    grad.addColorStop(1, '#8B0000')
    ctx.fillStyle = grad
    ctx.fillRect(0, 0, size, size)

    // === GOLD SPARKLES ===
    for (const sp of sparkles) {
      const alpha = 0.15 + 0.85 * Math.abs(Math.sin(t * Math.PI * 2 + sp.phase))
      ctx.beginPath()
      ctx.arc(sp.x, sp.y, sp.r * (0.8 + 0.4 * alpha), 0, Math.PI * 2)
      ctx.fillStyle = `rgba(255, 215, 0, ${alpha})`
      ctx.fill()
    }

    // === TOP: USER INPUT TEXT — big gold calligraphy ===
    const mainFontSize = stickerText.length <= 2 ? 48 : stickerText.length <= 4 ? 38 : 28
    ctx.save()
    ctx.shadowColor = 'rgba(255, 180, 0, 0.8)'
    ctx.shadowBlur = 12 + 6 * Math.sin(t * Math.PI * 2)
    ctx.font = `bold ${mainFontSize}px "PingFang SC", "Microsoft YaHei", "STHeiti", sans-serif`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.strokeStyle = '#8B4513'
    ctx.lineWidth = 3
    ctx.lineJoin = 'round'
    ctx.strokeText(stickerText, size / 2, 30)
    const textGrad = ctx.createLinearGradient(size * 0.2, 10, size * 0.8, 50)
    textGrad.addColorStop(0, '#FFD700')
    textGrad.addColorStop(0.4, '#FFF8DC')
    textGrad.addColorStop(0.7, '#FFA500')
    textGrad.addColorStop(1, '#FFD700')
    ctx.fillStyle = textGrad
    ctx.fillText(stickerText, size / 2, 30)
    ctx.restore()

    // === CENTER: BIG RUNNING HORSE — 6-frame real animation ===
    const horseW = 160
    const horseH = 160
    const frameIdx = f % horseFrames.length
    const currentHorse = horseFrames[frameIdx]
    const gallopBounce = Math.sin(t * Math.PI * 4) * 3
    const horseX = (size - horseW) / 2
    const horseY = 50 + gallopBounce
    const tilt = Math.sin(t * Math.PI * 4) * 0.02

    ctx.save()
    ctx.shadowColor = 'rgba(255, 180, 0, 0.6)'
    ctx.shadowBlur = 18
    ctx.translate(horseX + horseW / 2, horseY + horseH / 2)
    ctx.rotate(tilt)
    ctx.drawImage(currentHorse, -horseW / 2, -horseH / 2, horseW, horseH)
    ctx.restore()

    // === BOTTOM: "立马加薪" — centered, big, gold ===
    ctx.save()
    ctx.shadowColor = 'rgba(255, 180, 0, 0.7)'
    ctx.shadowBlur = 10 + 5 * Math.sin(t * Math.PI * 2)
    ctx.font = 'bold 28px "PingFang SC", "Microsoft YaHei", sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.strokeStyle = '#5C1010'
    ctx.lineWidth = 3
    ctx.lineJoin = 'round'
    ctx.strokeText('立马加薪', size / 2, size - 18)
    const goldColors = ['#FFD700', '#FFA500', '#FFEC8B', '#FFD700', '#FF8C00', '#FFD700']
    ctx.fillStyle = goldColors[f % goldColors.length]
    ctx.fillText('立马加薪', size / 2, size - 18)
    ctx.restore()

    gif.addFrame(ctx, { copy: true, delay: 85 })
  }

  gif.on('finished', (blob: Blob) => {
    const reader = new FileReader()
    reader.onload = () => onComplete(reader.result as string)
    reader.readAsDataURL(blob)
  })

  gif.render()
}

export default function StickerPage() {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<StickerResult[]>([])
  const [gifReady, setGifReady] = useState(false)

  async function generate() {
    if (loading || !gifReady) return
    const trimmed = text.trim()
    if (!trimmed || trimmed.length > 8) {
      alert('请输入1-8个字')
      return
    }
    setLoading(true)

    // Load 6 horse frames
    const frameCount = 6
    const frames: HTMLImageElement[] = []
    let loaded = 0
    let errored = false
    for (let i = 1; i <= frameCount; i++) {
      const img = new Image()
      img.crossOrigin = 'anonymous'
      img.onload = () => {
        loaded++
        if (loaded === frameCount && !errored) {
          createAnimatedSticker(frames, trimmed, (gifDataUrl) => {
            setResults(prev => [{ image: gifDataUrl, text: trimmed }, ...prev])
            setLoading(false)
          })
        }
      }
      img.onerror = () => {
        if (!errored) { errored = true; alert('素材加载失败'); setLoading(false) }
      }
      img.src = `/horse-frame-${i}.png`
      frames.push(img)
    }
  }

  const saveSticker = useCallback((dataUrl: string, stickerText: string) => {
    const link = document.createElement('a')
    link.download = `马年祝福-${stickerText}.gif`
    link.href = dataUrl
    link.click()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-6">
        <div className="text-7xl animate-bounce mb-6">🐴</div>
        <p className="text-white text-xl font-medium">✨ 动态表情包生成中...</p>
        <p className="text-white/60 text-sm mt-2">合成 GIF 动画，稍等几秒</p>
      </div>
    )
  }

  return (
    <>
      <Script
        src="https://cdn.jsdelivr.net/npm/gif.js@0.2.0/dist/gif.js"
        onLoad={() => setGifReady(true)}
      />
      <div className="min-h-screen px-4 py-8">
        <div className="max-w-md mx-auto">
          <div className="text-center mb-6">
            <div className="text-6xl mb-2">🐴🔥</div>
            <h1 className="text-white text-3xl font-bold">马年表情包工厂</h1>
            <p className="text-white/70 text-sm mt-1">输入祝福语 → 秒出动态 GIF 表情包</p>
          </div>

          <div className="mb-4">
            <label className="text-yellow-300 text-sm font-medium mb-1 block">祝福文字（1-8字）</label>
            <input
              type="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && generate()}
              placeholder="新年快乐、恭喜发财、马到成功..."
              maxLength={8}
              className="w-full px-4 py-3 rounded-xl text-center text-lg bg-white/95 text-gray-800 placeholder-gray-400 outline-none focus:ring-2 focus:ring-yellow-400"
            />
          </div>

          <button
            onClick={generate}
            disabled={!text.trim() || !gifReady}
            className="w-full bg-yellow-500 hover:bg-yellow-400 disabled:opacity-50 text-red-900 font-bold text-lg px-6 py-4 rounded-2xl shadow-lg transition active:scale-95 mb-6"
          >
            {gifReady ? '✨ 生成动态表情包' : '⏳ 加载中...'}
          </button>

          {results.length > 0 && (
            <div>
              <h2 className="text-yellow-300 font-bold mb-3">📦 我的表情包</h2>
              <div className="grid grid-cols-2 gap-3">
                {results.map((r, i) => (
                  <div key={i} className="bg-white/10 rounded-xl p-2 text-center">
                    <img src={r.image} alt={r.text} className="w-full rounded-lg mb-2" />
                    <button
                      onClick={() => saveSticker(r.image, r.text)}
                      className="text-xs bg-green-500 hover:bg-green-400 text-white px-3 py-1 rounded-full"
                    >
                      💾 下载GIF
                    </button>
                  </div>
                ))}
              </div>
              <p className="text-white/50 text-xs text-center mt-3">💡 保存后添加到微信自定义表情即可使用</p>
            </div>
          )}

          <div className="text-center mt-6">
            <a href="/" className="text-white/50 text-sm hover:text-white/80 transition">← 回到藏头诗祝福</a>
          </div>
        </div>
      </div>
    </>
  )
}
