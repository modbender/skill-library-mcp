---
name: horse-sticker-maker
description: Create and deploy a festive Chinese New Year (Year of the Horse 2026) animated GIF sticker maker web app. Use when the user wants to generate custom horse-themed blessing stickers, deploy a sticker generator H5 page, or create WeChat-compatible animated GIF stickers with gold horse animation on red background. Supports custom text input, 6-frame gold horse galloping animation, Canvas-based client-side GIF rendering via gif.js, and Vercel deployment.
---

# Horse Sticker Maker

Generate a web app that creates custom animated GIF stickers for Chinese New Year (Year of the Horse 2026).

## What It Does

- Users input custom blessing text (1-8 chars)
- Client-side Canvas renders a 240px animated GIF with:
  - Red gradient background with gold sparkle particles
  - 6-frame gold horse galloping animation (transparent PNG)
  - User's custom text in gold calligraphy at top
  - "立马加薪" bottom text with color-cycling effect
- Output is WeChat sticker compatible (≤500KB, 240px)

## Quick Start

1. Copy the template project:
   ```bash
   cp -r <skill_dir>/assets/horse-blessing-template ./horse-blessing
   cd horse-blessing
   npm install
   ```

2. Run locally:
   ```bash
   npm run dev
   # Open http://localhost:3000/sticker
   ```

3. Deploy to Vercel:
   ```bash
   vercel --prod --yes
   ```

## Project Structure

```
horse-blessing/
├── app/
│   ├── page.tsx          # Main page (AI-generated blessing with poem)
│   ├── sticker/page.tsx  # Sticker maker (Canvas GIF generator)
│   ├── api/generate/     # AI poem + image generation API
│   ├── api/sticker/      # Sticker API
│   └── layout.tsx        # Root layout (red theme)
├── public/
│   ├── horse-frame-[1-6].png  # 6-frame transparent gold horse
│   ├── horse-transparent.png  # Static horse fallback
│   └── gif.worker.js          # gif.js web worker
├── package.json
└── tailwind.config.ts
```

## Key Technical Details

### GIF Generation (Client-Side)
- Uses `gif.js` loaded via CDN (`Script` from next/script)
- 18 frames (6 horse frames × 3 cycles), 85ms delay per frame
- Canvas size: 240×240px for WeChat sticker compatibility
- Horse frames loaded as `Image` elements, drawn via `drawImage`

### Horse Frame Assets
- 6 transparent PNG frames in `public/horse-frame-[1-6].png`
- Generated via AI image model, backgrounds removed with `sharp`
- Removal technique: pixels with R>210, G>210, B>210 → alpha=0

### Customization Points
- **Bottom text**: Edit `'立马加薪'` in `sticker/page.tsx`
- **GIF size**: Change `const size = 240` (keep ≤240 for WeChat)
- **Frame count**: Change `const frames = 18`
- **Horse images**: Replace `public/horse-frame-*.png`
- **Background**: Modify the radial gradient colors
- **Sparkle count**: Adjust sparkle array size (default 30)

### WeChat Sticker Compatibility
- Max 500KB file size
- Max 240px recommended dimension
- GIF format required
- Save → WeChat chat → emoji panel → "+" → select from gallery

## Dependencies

```json
{
  "next": "^14.0.0",
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "sharp": "latest",
  "gif-encoder-2": "^1.0.5",
  "html2canvas-pro": "^1.6.7"
}
```

External CDN: `gif.js@0.2.0` (loaded at runtime for client-side GIF encoding)
