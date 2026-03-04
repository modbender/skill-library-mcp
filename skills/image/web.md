# Web Image Optimization

## Responsive Images — Breakpoints

Standard srcset widths: **320w, 640w, 768w, 1024w, 1366w, 1600w, 1920w**

```html
<img 
  srcset="image-320.webp 320w,
          image-640.webp 640w,
          image-1024.webp 1024w,
          image-1920.webp 1920w"
  sizes="(max-width: 640px) 100vw,
         (max-width: 1024px) 50vw,
         33vw"
>
```

**Rule:** Don't generate all sizes. Match your CSS breakpoints. 4-5 sizes is usually enough.

---

## Lazy Loading — When NOT to Use

**Use `loading="lazy"`:**
- Below-the-fold images
- Galleries, infinite scroll

**NEVER lazy load:**
- Hero images / LCP images
- First 2-3 visible images
- Background images critical to layout
- Images within 1000px from viewport top

**Rule:** LCP image must have `loading="eager"` or no attribute.

---

## Aspect Ratios — Prevent CLS

Always define dimensions:
```html
<img width="800" height="600">
```

Or CSS:
```css
.container { aspect-ratio: 16/9; }
```

**Common ratios:**
| Ratio | Use |
|-------|-----|
| 16:9 | Video, hero banners |
| 4:3 | Traditional photos |
| 3:2 | DSLR photos |
| 1:1 | Social, avatars, products |
| 21:9 | Cinematic banners |

**Rule:** Never load images without reserved space. CLS kills Core Web Vitals.

---

## File Naming

**Pattern:** `{descriptor}-{size}-{variant}.{ext}`

```
hero-homepage-1920.webp
product-shoe-red-640.jpg
avatar-user-128@2x.png
```

**Rules:**
- Lowercase only
- Hyphens, not underscores or spaces
- Descriptive for SEO (`blue-running-shoes.jpg` not `IMG_4521.jpg`)
- Include size when multiple variants exist

---

## SVG Optimization

- Run through SVGO (reduces 30-60%)
- Remove `width`/`height` for CSS control
- Keep `viewBox` — required for scaling
- Inline critical SVGs (<2KB) to avoid HTTP requests
- External for complex illustrations (>2KB)

**Rule:** SVG icon should be <1KB after optimization.

---

## WebP with Fallback

```html
<picture>
  <source srcset="image.webp" type="image/webp">
  <source srcset="image.jpg" type="image/jpeg">
  <img src="image.jpg" alt="Description">
</picture>
```

**AVIF** (if supported):
```html
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="Description">
</picture>
```

---

## Image CDN Best Practices (Optional)

If using a CDN service (Cloudinary, imgix, etc.):
- Use auto-format: `f_auto`
- Use auto-quality: `q_auto`
- Specify exact dimensions in URL
- Enable lazy loading at edge
- Set cache headers (1 year for hashed URLs)

**Note:** CDN services require their own API credentials configured separately. This skill does not manage CDN credentials.

---

## Performance Checklist

```
□ All images compressed (WebP preferred)
□ Lazy loading on below-fold images
□ LCP image preloaded
□ Dimensions specified (no CLS)
□ srcset for responsive
□ Total page images <1.5MB
□ No images over 200KB
```
