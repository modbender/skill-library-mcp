# Neo-M3 Hybrid (Industrial Modernism)

A high-density design language blending the raw structure of Neo-Brutalism with the fluid geometry of Material You 3. Inspired by tech journalism and high-end engineering interfaces.

---

## Design DNA

| Property | Value |
|---|---|
| **Border Radius** | Large: 24px – 32px (rounded-3xl) |
| **Borders** | Bold: 3px – 4px Solid Black. Use dashed for experimental states |
| **Shadows** | Hard Offset: 6px – 10px (No blur) |
| **Typography** | Plus Jakarta Sans (Headers), JetBrains Mono (Metadata/Stats) |

---

## The Verge-inspired Palette

| Name | Hex Code | Usage |
|---|---|---|
| **Canvas** | #F8FAFC | Main background |
| **Ink** | #000000 | Borders and inverted labels |
| **M3 Lavender** | #E9D5FF | Hero cards, primary actions |
| **M3 Sky** | #DBEAFE | Secondary info, data viz |

---

## Component Logic

### 1. The Wired Article Card
```html
<article class="bg-white border-[3px] border-black rounded-[32px] p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
    <div class="flex gap-2 mb-6">
        <span class="bg-black text-white text-[10px] font-black uppercase px-3 py-1 rounded-full">Intelligence</span>
    </div>
    <h2 class="text-3xl font-extrabold tracking-tighter leading-none mb-4">Project Prism.</h2>
    <p class="text-zinc-600 mb-8">Engineering the future through Neo-M3 architecture.</p>
</article>
```

### 2. System Status Marquee
```html
<div class="bg-black text-white py-2 overflow-hidden whitespace-nowrap">
    <div class="animate-marquee inline-block font-mono text-xs uppercase tracking-widest">
        System Operational • Memory Cache Synced • Welcome Master Azzar • 
    </div>
</div>
```

## Anti-Patterns

- Subtle Borders: Anything less than 2px is too weak.
- Low Contrast: Black on white is mandatory.
- Traditional Icons: Use geometric/minimal icons.
- Rounded Corners < 16px: Keep it bold.
