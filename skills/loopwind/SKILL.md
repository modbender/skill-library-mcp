---
name: loopwind
description: Generate images and videos from React + Tailwind CSS templates using the loopwind CLI.
metadata:
  version: "0.25.11"
---

# loopwind

A CLI tool for generating images and videos from JSX templates using Tailwind CSS and Satori. Templates live in a `.loopwind/` directory alongside your codebase.

## Quick Start

Loopwind is a CLI tool for generating images and videos with React and Tailwind CSS. It's designed to be used with AI Agents and Cursor.

### Installation

```bash
curl -fsSL https://loopwind.dev/install.sh | bash
```

This installs loopwind to `~/.loopwind/` and adds the `loopwind` command to your PATH. Requires Node.js 18+.

### Initialize in Your Project

Navigate to any project folder and run:

```bash
loopwind init
```

This creates `.loopwind/loopwind.json` — a configuration file with your project's theme colors.

### Install AI Skill

Give your AI agent expertise in loopwind:

```bash
npx skills add https://loopwind.dev/skill.md
```

This installs a skill that teaches Claude Code (or other AI agents) how to create templates, use animation classes, and render images/videos.

### Use with Claude Code

With the loopwind skill installed, Claude has deep knowledge of template structure, animation classes, and Tailwind CSS patterns for Satori. Just ask:

```
Create an OG image for my blog post about TypeScript tips
```

```
Create an animated intro video for my YouTube channel
```

Claude will create optimized templates and render the final output automatically.

### Install a Template

#### 1. Official Templates

```bash
loopwind add image-template
loopwind add video-template
```

Templates are installed to: `.loopwind/<template>/`

**Benefits:**
- Templates are local to your project
- Version controlled with your project
- Easy to share within your team

### Render a Template

```bash
loopwind render template-name '{"title":"Hello World","subtitle":"Built with loopwind"}'
```
or use a local props file:

```bash
loopwind render template-name props.json
```
## Commands

### `loopwind add <source>`

Install a template from various sources:

```bash
# Official templates
loopwind add image-template
loopwind add video-template
```
These will be downloaded to `.loopwind/<template>/`

### `loopwind list`

List all installed templates:

```bash
loopwind list
```

### `loopwind render <template> <props> [options]`

Render an image or video:

```bash
# Image with inline props
loopwind render banner-hero '{"title":"Hello World"}'

# Video with inline props
loopwind render video-intro '{"title":"Welcome"}'

# Using a props file
loopwind render banner-hero props.json

# Custom output
loopwind render banner-hero '{"title":"Hello"}' --out custom-name.png

# Different format
loopwind render banner-hero '{"title":"Hello"}' --format jpeg
```

Options:
- `--out, -o` - Output filename (default: `<template>.<ext>` in current directory)
- `--format` - Output format: `png`, `jpeg`, `svg` (images only)
- `--quality` - JPEG quality 1-100 (default: 92)

### `loopwind validate <template>`

Validate a template:

```bash
loopwind validate banner-hero
```

Checks:
- Template file exists and is valid React
- `export const meta` exists and is valid
- Required props are defined
- Fonts exist (if specified)

### `loopwind init`

Initialize loopwind in a project:

```bash
loopwind init
```

Creates `.loopwind/loopwind.json` configuration file with your project's design tokens.

## Animation Classes (Video Only)

Use Tailwind-style animation classes - no manual calculations needed:

```tsx
// Fade in: starts at 0ms, lasts 500ms
<h1 style={tw('enter-fade-in/0/500')}>Hello</h1>

// Loop: ping effect every 500ms
<div style={tw('loop-ping/500')} />

// Combined with easing
<h1 style={tw('ease-out enter-bounce-in-up/0/600')}>Title</h1>
```

See [Animation](/animation) for the complete reference.

## Next Steps

- [Templates](/templates)
- [Embedding Images](/images)
- [Animation](/animation)
- [Helpers (QR, Template Composition)](/helpers)
- [Styling with Tailwind & shadcn/ui](/styling)
- [Custom Fonts](/fonts)
- [AI Agent Integration](/agents)



# Templates

Templates are React components that define your images and videos. They use Tailwind CSS for styling and export metadata that loopwind uses for rendering.

## Installing Templates

### Official Templates

```bash
loopwind add image-template
loopwind add video-template
```

Templates are installed to `.loopwind/<template-name>/`.

### Direct URLs

```bash
loopwind add https://example.com/templates/my-template.json
```

### Local Filesystem

```bash
loopwind add ./my-templates/banner-hero
loopwind add /Users/you/templates/social-card
```

---

## Image Templates

### Basic Structure

```tsx
// .loopwind/banner-hero/template.tsx
export const meta = {
  name: "banner-hero",
  type: "image",
  description: "Hero banner with gradient background",
  size: { width: 1600, height: 900 },
  props: { title: "string", subtitle: "string" }
};

export default function BannerHero({ title, subtitle, tw }) {
  return (
    <div style={tw('flex flex-col justify-center items-center w-full h-full bg-gradient-to-br from-purple-600 to-blue-500 p-12')}>
      <h1 style={tw('text-7xl font-bold text-white mb-4')}>
        {title}
      </h1>
      <p style={tw('text-2xl text-white/80')}>
        {subtitle}
      </p>
    </div>
  );
}
```

### Rendering Images

```bash
# Render with inline props
loopwind render banner-hero '{"title":"Hello World","subtitle":"Welcome"}'

# Custom output name
loopwind render banner-hero '{"title":"Hello"}' --out custom-name.png

# Different format
loopwind render banner-hero '{"title":"Hello"}' --format jpeg --quality 95

# Use a props file
loopwind render banner-hero props.json
```

### Output Formats

| Format | Best For |
|--------|----------|
| **PNG** (default) | Transparency, sharp text, logos |
| **JPEG** | Photographs, gradients, smaller files |
| **SVG** | Vector graphics, scalable designs |

---

## Video Templates

### Basic Structure

```tsx
// .loopwind/video-intro/template.tsx
export const meta = {
  name: "video-intro",
  type: "video",
  description: "Animated intro with bounce-in title",
  size: { width: 1920, height: 1080 },
  video: { fps: 30, duration: 3 },
  props: { title: "string" }
};

export default function VideoIntro({ tw, title }) {
  return (
    <div style={tw('flex items-center justify-center w-full h-full bg-gradient-to-br from-blue-600 to-purple-700')}>
      <h1 style={tw('text-8xl font-bold text-white ease-out enter-bounce-in-up/0/600')}>
        {title}
      </h1>
    </div>
  );
}
```

### Rendering Videos

```bash
# Render with inline props
loopwind render video-intro '{"title":"Welcome!"}' --out intro.mp4

# Faster encoding with FFmpeg
loopwind render video-intro '{"title":"Welcome!"}' --ffmpeg

# Higher quality (lower CRF = better)
loopwind render video-intro '{"title":"Welcome!"}' --crf 18
```

### FPS and Duration

```tsx
video: { fps: 30, duration: 3 }  // 90 frames total
```

| FPS | Use Case |
|-----|----------|
| **24** | Cinematic look, smaller files |
| **30** | Standard web video |
| **60** | Smooth animations |

### Video-Specific Props

Templates receive these additional props:

- **`frame`** - Current frame number (0 to totalFrames - 1)
- **`progress`** - Animation progress from 0 to 1

```tsx
export default function MyVideo({ frame, progress }) {
  // frame: 0, 1, 2, ... 89 (for 3s @ 30fps)
  // progress: 0.0 at start, 0.5 at middle, 1.0 at end
}
```

### Encoding Options

| Encoder | Command | Use Case |
|---------|---------|----------|
| **WASM** (default) | `loopwind render ...` | CI/CD, no dependencies |
| **FFmpeg** | `loopwind render ... --ffmpeg` | Faster, smaller files |

Install FFmpeg: `brew install ffmpeg` (macOS)

---

## Animation Classes

Use Tailwind-style animation classes for videos:

```tsx
// Enter animations: enter-{type}/{delay}/{duration}
<h1 style={tw('enter-fade-in/0/500')}>Fade in at start</h1>
<h1 style={tw('enter-bounce-in-up/300/400')}>Bounce in after 300ms</h1>

// Exit animations: exit-{type}/{start}/{duration}
<div style={tw('exit-fade-out/2500/500')}>Fade out at 2.5s</div>

// Loop animations: loop-{type}/{duration}
<div style={tw('loop-float/1000')}>Continuous floating</div>
<div style={tw('loop-spin/1000')}>Spinning</div>

// Easing
<h1 style={tw('ease-out enter-slide-left/0/500')}>Smooth slide</h1>
```

See the full [Animation documentation](/animation) for all classes.

---

## Common Sizes

### Social Media
- **Twitter/X Card**: 1200x675
- **Facebook/OG**: 1200x630
- **Instagram Post**: 1080x1080
- **LinkedIn Post**: 1200x627

### Web Graphics
- **Hero Banner**: 1920x1080
- **Blog Header**: 1600x900
- **Thumbnail**: 640x360

---

## Example Templates

### Open Graph Image

```tsx
export const meta = {
  name: "og-image",
  type: "image",
  size: { width: 1200, height: 630 },
  props: { title: "string", description: "string" }
};

export default function OGImage({ tw, image, title, description }) {
  return (
    <div style={tw('flex w-full h-full bg-white')}>
      <div style={tw('flex-1 flex flex-col justify-between p-12')}>
        <img src={image('logo.svg')} style={tw('h-12 w-auto')} />
        <div>
          <h1 style={tw('text-5xl font-bold text-gray-900 mb-4')}>{title}</h1>
          <p style={tw('text-xl text-gray-600')}>{description}</p>
        </div>
        <p style={tw('text-gray-400')}>yoursite.com</p>
      </div>
    </div>
  );
}
```

### Animated Intro

```tsx
export const meta = {
  name: "animated-intro",
  type: "video",
  size: { width: 1920, height: 1080 },
  video: { fps: 60, duration: 3 },
  props: { title: "string", subtitle: "string" }
};

export default function AnimatedIntro({ tw, title, subtitle }) {
  return (
    <div style={tw('flex flex-col items-center justify-center w-full h-full bg-background')}>
      <h1 style={tw('text-8xl font-bold text-foreground ease-out enter-bounce-in-up/0/400')}>
        {title}
      </h1>
      <p style={tw('text-2xl text-muted-foreground mt-4 ease-out enter-fade-in-up/300/400')}>
        {subtitle}
      </p>
    </div>
  );
}
```

---

## Next Steps

- [Layouts](/layouts) - Wrap templates with reusable layouts
- [Embedding Images](/images) - Using the `image()` helper
- [Animation](/animation) - Full animation reference
- [Styling](/styling) - Tailwind & shadcn/ui integration
- [Fonts](/fonts) - Custom fonts


# Layouts

Layouts let you wrap templates with consistent headers, footers, and styling. A child template specifies a layout in its meta, and the layout receives the child content as a `children` prop.

## Basic Usage

### Layout Template

Create a layout template that receives `children`:

```tsx
// .loopwind/base-layout/template.tsx
export const meta = {
  name: 'base-layout',
  type: 'image',
  size: { width: 1200, height: 630 },
  props: {},
};

export default function BaseLayout({ tw, children }) {
  return (
    <div style={tw('flex flex-col w-full h-full bg-background')}>
      {/* Header */}
      <div style={tw('flex items-center px-8 py-4 border-b border-border')}>
        <span style={tw('text-2xl font-bold text-primary')}>loopwind</span>
      </div>

      {/* Content slot */}
      <div style={tw('flex flex-1')}>
        {children}
      </div>

      {/* Footer */}
      <div style={tw('flex items-center justify-between px-8 py-4 border-t border-border')}>
        <span style={tw('text-muted-foreground')}>loopwind.dev</span>
      </div>
    </div>
  );
}
```

### Usage in Templates

Reference the layout using a relative path:

```tsx
// .loopwind/blog-post/template.tsx
export const meta = {
  name: 'blog-post',
  type: 'image',
  layout: '../base-layout', // Layout controls size
  props: {
    title: 'string',
    excerpt: 'string',
  },
};

export default function BlogPost({ tw, title, excerpt }) {
  return (
    <div style={tw('flex flex-col justify-center p-12')}>
      <h1 style={tw('text-5xl font-bold text-foreground mb-4 text-balance')}>
        {title}
      </h1>
      <p style={tw('text-xl text-muted-foreground leading-relaxed')}>
        {excerpt}
      </p>
    </div>
  );
}
```

### Render

```bash
loopwind render blog-post '{"title":"Hello World","excerpt":"My first post"}'
```

The output uses the layout's size (1200x630) with the child content inside.

---

## Key Concepts

### Size

When using a layout, the **layout's size** controls the final output dimensions. The child template doesn't need a `size` property.

### Path Resolution

Use relative paths to reference layouts:

```tsx
layout: '../base-layout'      // Sibling directory
layout: './shared/layout'     // Subdirectory
layout: '../../layouts/main'  // Parent's sibling
```

### Props Flow

The layout receives:
- All standard helpers (`tw`, `image`, `qr`, `template`, etc.)
- `children` prop containing the rendered child content
- Animation context (`frame`, `progress`) for video layouts

```tsx
export default function Layout({ tw, children, frame, progress }) {
  // tw, image, qr, template, path, textPath all available
  return (
    <div style={tw('flex w-full h-full')}>
      {children}
    </div>
  );
}
```

---

## Video Layouts

Layouts work with video templates. Both the layout and child can use animations:

```tsx
// .loopwind/video-layout/template.tsx
export const meta = {
  name: 'video-layout',
  type: 'video',
  size: { width: 1920, height: 1080 },
  video: { fps: 60, duration: 4 },
  props: {},
};

export default function VideoLayout({ tw, children }) {
  return (
    <div style={tw('flex flex-col w-full h-full bg-background')}>
      {/* Animated header */}
      <div style={tw('flex items-center px-12 py-6 ease-out enter-slide-down/0/500')}>
        <span style={tw('text-3xl font-bold text-primary')}>loopwind</span>
      </div>

      {/* Content */}
      <div style={tw('flex flex-1')}>
        {children}
      </div>

      {/* Animated footer */}
      <div style={tw('flex px-12 py-6 ease-out enter-fade-in/500/400')}>
        <span style={tw('text-muted-foreground')}>loopwind.dev</span>
      </div>
    </div>
  );
}
```

---

## Example: Consistent OG Images

Create a layout for all your OG images:

```tsx
// .loopwind/og-layout/template.tsx
export const meta = {
  name: 'og-layout',
  type: 'image',
  size: { width: 1200, height: 630 },
  props: {},
};

export default function OGLayout({ tw, image, children }) {
  return (
    <div style={tw('flex w-full h-full bg-background')}>
      {/* Content area */}
      <div style={tw('flex flex-col flex-1 p-12')}>
        {/* Logo */}
        <div style={tw('flex items-center gap-3 mb-auto')}>
          <img src={image('logo.svg')} style={tw('h-10 w-auto')} />
          <span style={tw('text-2xl font-bold')}>MyBrand</span>
        </div>

        {/* Slot for page-specific content */}
        <div style={tw('flex flex-1 items-center')}>
          {children}
        </div>

        {/* Domain */}
        <span style={tw('text-muted-foreground mt-auto')}>mybrand.com</span>
      </div>
    </div>
  );
}
```

Then create page-specific templates:

```tsx
// .loopwind/og-blog/template.tsx
export const meta = {
  name: 'og-blog',
  type: 'image',
  layout: '../og-layout',
  props: {
    title: 'string',
    author: 'string',
  },
};

export default function OGBlog({ tw, title, author }) {
  return (
    <div style={tw('flex flex-col')}>
      <span style={tw('text-sm text-muted-foreground uppercase tracking-wider mb-2')}>
        Blog Post
      </span>
      <h1 style={tw('text-4xl font-bold text-foreground mb-4 text-balance')}>
        {title}
      </h1>
      <span style={tw('text-muted-foreground')}>By {author}</span>
    </div>
  );
}
```

---

## Next Steps

- [Templates](/templates) - Template structure and metadata
- [Animation](/animation) - Animation classes for video layouts
- [Helpers](/helpers) - Using image(), qr(), and template()


# Embedding Images

Use the `image()` helper to embed images in your templates. It supports loading from props, template directories, and URLs.

## Prop-based Images

Pass the prop name to load an image path from props:

```tsx
export const meta = {
  name: "product-card",
  type: "image",
  size: { width: 1200, height: 630 },
  props: {
    title: "string",
    background: "string?"
  }
};

export default function ProductCard({ tw, image, title, background }) {
  // Use fallback if no background prop provided
  const bgSrc = background
    ? image('background')
    : 'https://images.unsplash.com/photo-1557682250-33bd709cbe85?w=1200';

  return (
    <div style={tw('relative w-full h-full')}>
      <img
        src={bgSrc}
        style={tw('absolute inset-0 w-full h-full object-cover')}
      />
      <div style={tw('relative z-10 p-12')}>
        <h1 style={tw('text-6xl font-bold text-white')}>{title}</h1>
      </div>
    </div>
  );
}
```

The `image('background')` helper loads from the `background` prop value (file path or URL).

## Direct File Images

Load images directly from your template directory by including the file extension:

```tsx
export default function ChangelogItem({ tw, image, text }) {
  return (
    <div style={tw('flex items-center gap-4')}>
      {/* Load check.svg from template directory */}
      <img
        src={image('check.svg')}
        style={tw('w-6 h-6')}
      />
      <span style={tw('text-lg')}>{text}</span>
    </div>
  );
}
```

You can also use subdirectories:

```tsx
<img src={image('assets/icons/star.svg')} />
<img src={image('shared/logo.png')} />
```

**Template directory structure:**
```
.loopwind/my-template/
├── template.tsx
├── check.svg           ← image('check.svg')
└── assets/
    └── icons/
        └── star.svg    ← image('assets/icons/star.svg')
```

## URLs

The `image()` helper also supports loading images from URLs:

```json
{
  "background": "https://example.com/image.jpg"
}
```

## Supported Formats

- **JPEG** (`.jpg`, `.jpeg`)
- **PNG** (`.png`)
- **GIF** (`.gif`)
- **WebP** (`.webp`)
- **SVG** (`.svg`)

## Image Positioning

Use Tailwind's object-fit utilities:

```tsx
export default function ImageGrid({ tw, image, img1, img2, img3 }) {
  return (
    <div style={tw('flex gap-4 w-full h-full p-8 bg-gray-100')}>
      {/* Cover - fills entire area, may crop */}
      <img
        src={image('img1')}
        style={tw('w-full h-full object-cover rounded-lg')}
      />

      {/* Contain - fits within area, may letterbox */}
      <img
        src={image('img2')}
        style={tw('w-full h-full object-contain')}
      />

      {/* Fill - stretches to fill */}
      <img
        src={image('img3')}
        style={tw('w-full h-full object-fill')}
      />
    </div>
  );
}
```

## Troubleshooting

### Images Not Loading

Check file paths are relative to the props file:

```json
{
  "background": "./images/bg.jpg"
}
```

Absolute paths won't work.

### Optimize Image Sizes

Use appropriately sized images before embedding:

```bash
convert large-image.jpg -resize 1600x900 optimized.jpg
```

---

## Next Steps

- [Templates](/templates) - Creating image and video templates
- [Animation](/animation) - Animation classes for videos
- [Styling](/styling) - Tailwind & shadcn/ui integration


# Animation

loopwind provides **Tailwind-style animation classes** that work with time to create smooth video animations without writing custom code.

> **Note:** Animation classes only work with **video templates** and **GIFs**. For static images, animations will have no effect since there's no time context.

## Quick Start

```tsx
export default function MyVideo({ tw, title, subtitle }) {
  return (
    <div style={tw('flex flex-col items-center justify-center w-full h-full bg-black')}>
      {/* Bounce in from below: starts at 0, lasts 400ms */}
      <h1 style={tw('text-8xl font-bold text-white ease-out enter-bounce-in-up/0/400')}>
        {title}
      </h1>

      {/* Fade in with upward motion: starts at 300ms, lasts 400ms */}
      <p style={tw('text-2xl text-white/80 mt-4 ease-out enter-fade-in-up/300/400')}>
        {subtitle}
      </p>

      {/* Continuous floating animation: repeats every 1s (1000ms) */}
      <div style={tw('mt-8 text-4xl loop-float/1000')}>
        ⬇️
      </div>
    </div>
  );
}
```

## Animation Format

loopwind uses three types of animations with **millisecond timing**:

| Type | Format | Description |
|------|--------|-------------|
| Enter | `enter-{type}/{start}/{duration}` | Animations that play when entering |
| Exit | `exit-{type}/{start}/{duration}` | Animations that play when exiting |
| Loop | `loop-{type}/{duration}` | Continuous looping animations |

All timing values are in **milliseconds** (1000ms = 1 second).

## Utility-Based Animations

In addition to predefined animations, loopwind supports **Tailwind utility-based animations** that let you animate any transform or opacity property directly:

```tsx
// Slide in 20px from the left
<div style={tw('enter-translate-x-5/0/1000')}>Content</div>

// Rotate 90 degrees on entrance
<div style={tw('enter-rotate-90/0/500')}>Spinning</div>

// Fade to 50% opacity in a loop
<div style={tw('loop-opacity-50/1000')}>Pulsing</div>

// Scale down with negative value
<div style={tw('enter--scale-50/0/800')}>Shrinking</div>
```

### Supported Utilities

| Utility | Format | Description | Example |
|---------|--------|-------------|---------|
| **translate-x** | `enter-translate-x-{value}` | Translate horizontally | `enter-translate-x-5` = 20px<br/>`enter-translate-x-full` = 100%<br/>`enter-translate-x-[20px]` = 20px |
| **translate-y** | `enter-translate-y-{value}` | Translate vertically | `loop-translate-y-10` = 40px<br/>`enter-translate-y-1/2` = 50%<br/>`enter-translate-y-[5rem]` = 80px |
| **opacity** | `enter-opacity-{n}` | Set opacity (0-100) | `enter-opacity-50` = 50% |
| **scale** | `enter-scale-{n}` | Scale element (0-200) | `enter-scale-100` = 1.0x |
| **rotate** | `enter-rotate-{n}` | Rotate in degrees | `enter-rotate-45` = 45° |
| **skew-x** | `enter-skew-x-{n}` | Skew on X axis in degrees | `enter-skew-x-12` = 12° |
| **skew-y** | `enter-skew-y-{n}` | Skew on Y axis in degrees | `exit-skew-y-6` = 6° |

**Translate value formats:**
- **Numeric**: `5` = 20px (Tailwind spacing scale: 1 unit = 4px)
- **Keywords**: `full` = 100%
- **Fractions**: `1/2` = 50%, `1/3` = 33.333%, `2/3` = 66.666%, etc.
- **Arbitrary values**: `[20px]`, `[5rem]`, `[10%]` (rem converts to px: 1rem = 16px)

All utilities work with:
- **All prefixes**: `enter-`, `exit-`, `loop-`, `animate-`
- **Negative values**: Prefix with `-` (e.g., `-translate-x-5`, `-rotate-45`)
- **Timing syntax**: Add `/start/duration` (e.g., `enter-translate-x-5/0/800`)

### Translate Animations

```tsx
// Numeric (Tailwind spacing): 20px (5 * 4px)
<div style={tw('enter-translate-x-5/0/500')}>Content</div>

// Keyword: Full width (100%)
<div style={tw('enter-translate-y-full/0/800')}>Dropping full height</div>

// Fraction: Half width (50%)
<div style={tw('enter-translate-x-1/2/0/600')}>Slide in halfway</div>

// Arbitrary values: Exact px or rem
<div style={tw('enter-translate-y-[20px]/0/500')}>Slide 20px</div>
<div style={tw('enter-translate-x-[5rem]/0/800')}>Slide 5rem (80px)</div>

// Loop with fractions
<div style={tw('loop-translate-y-1/4/1000')}>Oscillate 25%</div>

// Negative values
<div style={tw('exit--translate-y-8/2000/500')}>Rising</div>
```

### Opacity Animations

```tsx
// Fade to 100% opacity
<div style={tw('enter-opacity-100/0/500')}>Fading In</div>

// Fade to 50% opacity
<div style={tw('enter-opacity-50/0/800')}>Half Opacity</div>

// Pulse between 50% and 100%
<div style={tw('loop-opacity-50/1000')}>Pulsing</div>

// Fade out to 0%
<div style={tw('exit-opacity-0/2500/500')}>Vanishing</div>
```

### Scale Animations

```tsx
// Scale from 0 to 100% (1.0x)
<div style={tw('enter-scale-100/0/500')}>Growing</div>

// Scale to 150% (1.5x)
<div style={tw('enter-scale-150/0/800')}>Enlarging</div>

// Pulse scale in a loop
<div style={tw('loop-scale-110/1000')}>Breathing</div>

// Scale down to 50%
<div style={tw('exit-scale-50/2000/500')}>Shrinking</div>
```

### Rotate Animations

```tsx
// Rotate 90 degrees
<div style={tw('enter-rotate-90/0/500')}>Quarter Turn</div>

// Rotate 180 degrees
<div style={tw('enter-rotate-180/0/1000')}>Half Turn</div>

// Continuous rotation in loop (360 degrees per cycle)
<div style={tw('loop-rotate-360/2000')}>Spinning</div>

// Rotate backwards with negative value
<div style={tw('enter--rotate-45/0/500')}>Counter Rotation</div>
```

### Skew Animations

```tsx
// Skew on X axis
<div style={tw('enter-skew-x-12/0/500')}>Slanted</div>

// Skew on Y axis
<div style={tw('enter-skew-y-6/0/800')}>Tilted</div>

// Oscillating skew in loop
<div style={tw('loop-skew-x-6/1000')}>Wobbling</div>

// Negative skew
<div style={tw('exit--skew-x-12/2000/500')}>Reverse Slant</div>
```

### Combining Utilities

You can combine multiple utility animations on the same element:

```tsx
// Translate and rotate together
<div style={tw('enter-translate-y-10/0/500 enter-rotate-45/0/500')}>
  Flying In
</div>

// Fade and scale
<div style={tw('enter-opacity-100/0/800 enter-scale-100/0/800')}>
  Appearing
</div>

// Enter with translate, exit with rotation
<div style={tw('enter-translate-x-5/0/500 exit-rotate-180/2500/500')}>
  Slide and Spin
</div>
```

### Bracket Notation

For more CSS-like syntax, you can use brackets with units:

```tsx
// Using bracket notation with seconds
<h1 style={tw('enter-slide-up/[0.6s]/[1.5s]')}>Hello</h1>

// Using bracket notation with milliseconds
<h1 style={tw('enter-fade-in/[300ms]/[800ms]')}>World</h1>

// Mix and match - plain numbers are milliseconds
<h1 style={tw('enter-bounce-in/0/[1.2s]')}>Mixed</h1>
```

## Enter Animations

Format: `enter-{type}/{startMs}/{durationMs}`

- `startMs` - when the animation begins (milliseconds from start)
- `durationMs` - how long the animation lasts

When values are omitted (`enter-fade-in`), it uses the full video duration.

### Fade Animations

Simple opacity transitions with optional direction.

```tsx
// Fade in from 0ms to 500ms
<h1 style={tw('enter-fade-in/0/500')}>Hello</h1>

// Fade in with upward motion
<h1 style={tw('enter-fade-in-up/0/600')}>Hello</h1>
```

| Class | Description |
|-------|-------------|
| `enter-fade-in/0/500` | Fade in (opacity 0 → 1) |
| `enter-fade-in-up/0/500` | Fade in + slide up (30px) |
| `enter-fade-in-down/0/500` | Fade in + slide down (30px) |
| `enter-fade-in-left/0/500` | Fade in + slide from left (30px) |
| `enter-fade-in-right/0/500` | Fade in + slide from right (30px) |

### Slide Animations

Larger movement (100px) with fade.

```tsx
// Slide in from left: starts at 0, lasts 500ms
<div style={tw('enter-slide-left/0/500')}>Content</div>

// Slide up from bottom: starts at 200ms, lasts 600ms
<div style={tw('enter-slide-up/200/600')}>Content</div>
```

| Class | Description |
|-------|-------------|
| `enter-slide-left/0/500` | Slide in from left (100px) |
| `enter-slide-right/0/500` | Slide in from right (100px) |
| `enter-slide-up/0/500` | Slide in from bottom (100px) |
| `enter-slide-down/0/500` | Slide in from top (100px) |

### Bounce Animations

Playful entrance with overshoot effect.

```tsx
// Bounce in with scale overshoot
<h1 style={tw('enter-bounce-in/0/500')}>Bouncy!</h1>

// Bounce in from below
<div style={tw('enter-bounce-in-up/0/600')}>Pop!</div>
```

| Class | Description |
|-------|-------------|
| `enter-bounce-in/0/500` | Bounce in with scale overshoot |
| `enter-bounce-in-up/0/500` | Bounce in from below |
| `enter-bounce-in-down/0/500` | Bounce in from above |
| `enter-bounce-in-left/0/500` | Bounce in from left |
| `enter-bounce-in-right/0/500` | Bounce in from right |

### Scale & Zoom Animations

Size-based transitions.

```tsx
// Scale in from 50%
<div style={tw('enter-scale-in/0/500')}>Growing</div>

// Zoom in from 0%
<div style={tw('enter-zoom-in/0/1000')}>Zooming</div>
```

| Class | Description |
|-------|-------------|
| `enter-scale-in/0/500` | Scale up from 50% to 100% |
| `enter-zoom-in/0/500` | Zoom in from 0% to 100% |

### Rotate & Flip Animations

Rotation-based transitions.

```tsx
// Rotate in 180 degrees
<div style={tw('enter-rotate-in/0/500')}>Spinning</div>

// 3D flip on X axis
<div style={tw('enter-flip-in-x/0/500')}>Flipping</div>
```

| Class | Description |
|-------|-------------|
| `enter-rotate-in/0/500` | Rotate in from -180° |
| `enter-flip-in-x/0/500` | 3D flip on horizontal axis |
| `enter-flip-in-y/0/500` | 3D flip on vertical axis |

## Exit Animations

Format: `exit-{type}/{startMs}/{durationMs}`

- `startMs` - when the exit animation begins
- `durationMs` - how long the exit animation lasts

Exit animations use the same timing system but animate elements out.

```tsx
// Fade out starting at 2500ms, lasting 500ms (ends at 3000ms)
<h1 style={tw('exit-fade-out/2500/500')}>Goodbye</h1>

// Combined enter and exit on same element
<h1 style={tw('enter-fade-in/0/500 exit-fade-out/2500/500')}>
  Hello and Goodbye
</h1>
```

| Class | Description |
|-------|-------------|
| `exit-fade-out/2500/500` | Fade out (opacity 1 → 0) |
| `exit-fade-out-up/2500/500` | Fade out + slide up |
| `exit-fade-out-down/2500/500` | Fade out + slide down |
| `exit-fade-out-left/2500/500` | Fade out + slide left |
| `exit-fade-out-right/2500/500` | Fade out + slide right |
| `exit-slide-up/2500/500` | Slide out upward (100px) |
| `exit-slide-down/2500/500` | Slide out downward (100px) |
| `exit-slide-left/2500/500` | Slide out to left (100px) |
| `exit-slide-right/2500/500` | Slide out to right (100px) |
| `exit-scale-out/2500/500` | Scale out to 150% |
| `exit-zoom-out/2500/500` | Zoom out to 200% |
| `exit-rotate-out/2500/500` | Rotate out to 180° |
| `exit-bounce-out/2500/500` | Bounce out with scale |
| `exit-bounce-out-up/2500/500` | Bounce out upward |
| `exit-bounce-out-down/2500/500` | Bounce out downward |
| `exit-bounce-out-left/2500/500` | Bounce out to left |
| `exit-bounce-out-right/2500/500` | Bounce out to right |

## Loop Animations

Format: `loop-{type}/{durationMs}`

Loop animations repeat every `{durationMs}` milliseconds:
- `/1000` = 1 second loop
- `/500` = 0.5 second loop
- `/2000` = 2 second loop

When duration is omitted (`loop-bounce`), it defaults to 1000ms (1 second).

```tsx
// Pulse opacity every 500ms
<div style={tw('loop-fade/500')}>Pulsing</div>

// Bounce every 800ms
<div style={tw('loop-bounce/800')}>Bouncing</div>

// Full rotation every 2000ms
<div style={tw('loop-spin/2000')}>Spinning</div>
```

| Class | Description |
|-------|-------------|
| `loop-fade/{ms}` | Opacity pulse (0.5 → 1 → 0.5) |
| `loop-bounce/{ms}` | Bounce up and down |
| `loop-spin/{ms}` | Full 360° rotation |
| `loop-ping/{ms}` | Scale up + fade out (radar effect) |
| `loop-wiggle/{ms}` | Side to side wiggle |
| `loop-float/{ms}` | Gentle up and down floating |
| `loop-pulse/{ms}` | Scale pulse (1.0 → 1.05 → 1.0) |
| `loop-shake/{ms}` | Shake side to side |

## Easing Functions

Add an easing class **before** the animation class to control the timing curve.

```tsx
// Ease in (accelerate)
<h1 style={tw('ease-in enter-fade-in/0/1000')}>Accelerating</h1>

// Ease out (decelerate) - default
<h1 style={tw('ease-out enter-fade-in/0/1000')}>Decelerating</h1>

// Ease in-out (smooth)
<h1 style={tw('ease-in-out enter-fade-in/0/1000')}>Smooth</h1>

// Strong cubic easing
<h1 style={tw('ease-out-cubic enter-bounce-in/0/500')}>Dramatic</h1>
```

| Class | Description | Best For |
|-------|-------------|----------|
| `linear` | Constant speed | Mechanical motion |
| `ease-in` | Slow start, fast end | Exit animations |
| `ease-out` | Fast start, slow end (default) | Enter animations |
| `ease-in-out` | Slow start and end | Subtle transitions |
| `ease-in-cubic` | Strong slow start | Dramatic exits |
| `ease-out-cubic` | Strong fast start | Impactful entrances |
| `ease-in-out-cubic` | Strong both ends | Emphasis animations |
| `ease-in-quart` | Very strong slow start | Powerful exits |
| `ease-out-quart` | Very strong fast start | Punchy entrances |
| `ease-in-out-quart` | Very strong both ends | Maximum drama |

### Per-Animation-Type Easing

You can apply **different easing functions** to enter, exit, and loop animations on the same element using `enter-ease-*`, `exit-ease-*`, and `loop-ease-*` classes.

```tsx
// Different easing for enter and exit
<h1 style={tw('enter-ease-out-cubic enter-fade-in/0/500 exit-ease-in exit-fade-out/2500/500')}>
  Smooth entrance, sharp exit
</h1>

// Loop with linear easing, enter with bounce
<div style={tw('enter-ease-out enter-bounce-in/0/400 loop-ease-linear loop-fade/1000')}>
  Bouncy entrance, linear loop
</div>

// Default easing still works (applies to all animations)
<div style={tw('ease-in-out enter-fade-in/0/500 exit-fade-out/2500/500')}>
  Same easing for both
</div>

// Mix default with specific overrides
<div style={tw('ease-out enter-fade-in/0/500 exit-ease-in-cubic exit-fade-out/2500/500')}>
  Default ease-out for enter, cubic-in for exit
</div>
```

**How it works:**

1. **Default easing** (`ease-*`) applies to ALL animations if no specific override is set
2. **Specific easing** (`enter-ease-*`, `exit-ease-*`, `loop-ease-*`) overrides the default for that animation type
3. If both are present, specific easing takes priority for its animation type

**Available easing classes:**

| Default (all animations) | Enter only | Exit only | Loop only |
|--------------------------|------------|-----------|-----------|
| `ease-in` | `enter-ease-in` | `exit-ease-in` | `loop-ease-in` |
| `ease-out` | `enter-ease-out` | `exit-ease-out` | `loop-ease-out` |
| `ease-in-out` | `enter-ease-in-out` | `exit-ease-in-out` | `loop-ease-in-out` |
| `ease-in-cubic` | `enter-ease-in-cubic` | `exit-ease-in-cubic` | `loop-ease-in-cubic` |
| `ease-out-cubic` | `enter-ease-out-cubic` | `exit-ease-out-cubic` | `loop-ease-out-cubic` |
| `ease-in-out-cubic` | `enter-ease-in-out-cubic` | `exit-ease-in-out-cubic` | `loop-ease-in-out-cubic` |
| `ease-in-quart` | `enter-ease-in-quart` | `exit-ease-in-quart` | `loop-ease-in-quart` |
| `ease-out-quart` | `enter-ease-out-quart` | `exit-ease-out-quart` | `loop-ease-out-quart` |
| `ease-in-out-quart` | `enter-ease-in-out-quart` | `exit-ease-in-out-quart` | `loop-ease-in-out-quart` |
| `linear` | `enter-ease-linear` | `exit-ease-linear` | `loop-ease-linear` |
| `ease-spring` | `enter-ease-spring` | `exit-ease-spring` | `loop-ease-spring` |

### Spring Easing

Spring easing creates natural, physics-based bouncy animations. Use the built-in `ease-spring` easing or create custom springs with configurable parameters.

```tsx
// Default spring easing
<h1 style={tw('ease-spring enter-bounce-in/0/500')}>Bouncy spring!</h1>

// Per-animation-type spring
<div style={tw('enter-ease-spring enter-fade-in/0/500 exit-ease-out exit-fade-out/2500/500')}>
  Spring entrance, smooth exit
</div>

// Custom spring with parameters: ease-spring/mass/stiffness/damping
<h1 style={tw('ease-spring/1/100/10 enter-scale-in/0/800')}>
  Custom spring (mass=1, stiffness=100, damping=10)
</h1>

// More bouncy spring (lower damping)
<div style={tw('ease-spring/1/170/8 enter-bounce-in-up/0/600')}>
  Extra bouncy!
</div>

// Stiffer spring (higher stiffness, faster)
<div style={tw('ease-spring/1/200/12 enter-fade-in-up/0/400')}>
  Snappy spring
</div>

// Per-animation-type custom springs
<div style={tw('enter-ease-spring/1/150/10 enter-fade-in/0/500 exit-ease-spring/1/100/15 exit-fade-out/2500/500')}>
  Different springs for enter and exit
</div>
```

**Spring parameters:**

| Parameter | Description | Effect when increased | Default |
|-----------|-------------|----------------------|---------|
| **mass** | Mass of the spring | Slower, more inertia | 1 |
| **stiffness** | Spring stiffness | Faster, snappier | 100 |
| **damping** | Damping coefficient | Less bounce, smoother | 10 |

**Common spring presets:**

```tsx
// Gentle bounce (default)
ease-spring/1/100/10

// Extra bouncy
ease-spring/1/170/8

// Snappy (no bounce)
ease-spring/1/200/15

// Slow and bouncy
ease-spring/2/100/8

// Fast and tight
ease-spring/0.5/300/20
```

**How spring works:**

1. **Default `ease-spring`** - Uses a pre-calculated spring curve optimized for most use cases
2. **Custom `ease-spring/mass/stiffness/damping`** - Generates a physics-based spring curve using the [damped harmonic oscillator](https://www.kvin.me/css-springs) formula
3. The spring automatically calculates its ideal duration to reach the final state
4. Works with all animation types: `ease-spring`, `enter-ease-spring`, `exit-ease-spring`, `loop-ease-spring`

## Combining Enter and Exit

You can use both enter and exit animations on the same element:

```tsx
export default function EnterExit({ tw, title }) {
  return (
    <div style={tw('flex items-center justify-center w-full h-full bg-black')}>
      {/* Fade in during first 500ms, fade out during last 500ms (assuming 3s video) */}
      <h1 style={tw('text-8xl font-bold text-white enter-fade-in/0/500 exit-fade-out/2500/500')}>
        {title}
      </h1>
    </div>
  );
}
```

The opacities from multiple animations are **multiplied together**, so you get smooth transitions that combine properly.

## Staggered Animations

Create sequenced animations by offsetting start times:

```tsx
export default function StaggeredList({ tw, items }) {
  return (
    <div style={tw('flex flex-col gap-4')}>
      {/* First item: starts at 0ms, lasts 300ms */}
      <div style={tw('ease-out enter-fade-in-left/0/300')}>
        {items[0]}
      </div>

      {/* Second item: starts at 100ms, lasts 300ms */}
      <div style={tw('ease-out enter-fade-in-left/100/300')}>
        {items[1]}
      </div>

      {/* Third item: starts at 200ms, lasts 300ms */}
      <div style={tw('ease-out enter-fade-in-left/200/300')}>
        {items[2]}
      </div>
    </div>
  );
}
```

### Dynamic Staggering

For dynamic lists, calculate the timing programmatically:

```tsx
export default function DynamicStagger({ tw, items }) {
  return (
    <div style={tw('flex flex-col gap-4')}>
      {items.map((item, i) => {
        const start = i * 100;      // Each item starts 100ms later
        const duration = 300;       // Each animation lasts 300ms

        return (
          <div
            key={i}
            style={tw(`ease-out enter-fade-in-up/${start}/${duration}`)}
          >
            {item}
          </div>
        );
      })}
    </div>
  );
}
```

## Common Patterns

### Intro Sequence

```tsx
export default function IntroVideo({ tw, title, subtitle, logo }) {
  return (
    <div style={tw('flex flex-col items-center justify-center w-full h-full bg-gradient-to-br from-blue-600 to-purple-700')}>
      {/* Logo appears first */}
      <img
        src={logo}
        style={tw('h-20 mb-8 ease-out enter-scale-in/0/300')}
      />

      {/* Title bounces in */}
      <h1 style={tw('text-7xl font-bold text-white ease-out enter-bounce-in-up/200/500')}>
        {title}
      </h1>

      {/* Subtitle fades in last */}
      <p style={tw('text-2xl text-white/80 mt-4 ease-out enter-fade-in-up/400/700')}>
        {subtitle}
      </p>
    </div>
  );
}
```

### Text Reveal

```tsx
export default function TextReveal({ tw, words }) {
  return (
    <div style={tw('flex flex-wrap gap-2 justify-center')}>
      {words.split(' ').map((word, i) => (
        <span
          key={i}
          style={tw(`text-4xl font-bold ease-out enter-fade-in-up/${i * 100}/200`)}
        >
          {word}
        </span>
      ))}
    </div>
  );
}
```

### Looping Background Element

```tsx
export default function AnimatedBackground({ tw, children }) {
  return (
    <div style={tw('relative w-full h-full')}>
      {/* Floating background circles */}
      <div style={tw('absolute top-10 left-10 w-20 h-20 rounded-full bg-white/10 loop-float/2000')} />
      <div style={tw('absolute bottom-20 right-20 w-32 h-32 rounded-full bg-white/10 loop-fade/1500')} />

      {/* Main content */}
      <div style={tw('relative z-10')}>
        {children}
      </div>
    </div>
  );
}
```

### Full Enter/Exit Animation

```tsx
export default function FullAnimation({ tw, title }) {
  return (
    <div style={tw('flex items-center justify-center w-full h-full bg-black')}>
      {/* Enter: starts at 0, lasts 400ms. Exit: starts at 2600ms, lasts 400ms */}
      <h1 style={tw('text-8xl font-bold text-white ease-out enter-bounce-in-up/0/400 exit-fade-out-up/2600/400')}>
        {title}
      </h1>
    </div>
  );
}
```

## Programmatic Animations

For complete control beyond animation classes, use `progress` and `frame` directly.

### Available Props

| Prop | Type | Description |
|------|------|-------------|
| `progress` | `number` | 0 to 1 through the video (0% to 100%) |
| `frame` | `number` | Current frame number (0, 1, 2, ... totalFrames-1) |

These are **only available in video templates**. Use them when animation classes aren't flexible enough.

### Using `frame`

```tsx
export default function FrameAnimation({ tw, frame, title }) {
  // Color cycling using frame number
  const hue = (frame * 5) % 360; // Cycle through colors

  // Pulsing based on frame
  const fps = 30;
  const pulse = Math.sin(frame / fps * Math.PI * 2) * 0.2 + 0.8; // 0.6 to 1.0

  return (
    <div style={tw('flex items-center justify-center w-full h-full bg-black')}>
      <h1 style={{
        ...tw('text-8xl font-bold'),
        color: `hsl(${hue}, 70%, 60%)`,
        transform: `scale(${pulse})`
      }}>
        {title}
      </h1>
    </div>
  );
}
```

### Using `progress`

```tsx
export default function ProgressAnimation({ tw, progress, title }) {
  // Custom fade based on progress
  const opacity = progress < 0.3 ? progress / 0.3 : 1;

  // Custom scale based on progress
  const scale = 0.8 + progress * 0.2; // 0.8 to 1.0

  return (
    <div style={tw('flex items-center justify-center w-full h-full bg-gray-900')}>
      <h1 style={{
        ...tw('text-8xl font-bold text-white'),
        opacity,
        transform: `scale(${scale})`
      }}>
        {title}
      </h1>
    </div>
  );
}
```

### Custom Easing

```tsx
export default function CustomEasing({ tw, progress, title }) {
  // Smoothstep easing
  const eased = progress * progress * (3 - 2 * progress);

  // Elastic easing
  const elastic = Math.pow(2, -10 * progress) * Math.sin((progress - 0.075) * (2 * Math.PI) / 0.3) + 1;

  return (
    <div style={tw('flex items-center justify-center w-full h-full')}>
      <h1 style={{
        ...tw('text-8xl font-bold'),
        opacity: eased,
        transform: `translateY(${(1 - elastic) * 100}px)`
      }}>
        {title}
      </h1>
    </div>
  );
}
```

### When to Use Programmatic Animations

Use `progress`/`frame` instead of animation classes when you need:
- **Custom easing functions** (elastic, bounce with specific curves beyond built-in ease-spring)
- **Color cycling or gradients** based on time
- **Mathematical animations** (sine waves, spirals, etc.)
- **Complex multi-property animations** that need precise coordination
- **Conditional logic** based on specific frame numbers

For everything else, prefer animation classes - they're simpler and more maintainable.

### Animating Along Paths

Animate elements along SVG paths with proper rotation using built-in **path helpers**:

```tsx
export default function PathFollowing({ tw, progress, path }) {
  // Follow a quadratic Bezier curve - one line!
  const rocket = path.followQuadratic(
    { x: 200, y: 400 },   // Start point
    { x: 960, y: 150 },   // Control point
    { x: 1720, y: 400 },  // End point
    progress
  );

  return (
    <div style={{ display: 'flex', ...tw('relative w-full h-full bg-gray-900') }}>
      {/* Draw the path (optional) */}
      <svg width="1920" height="1080" style={{ position: 'absolute' }}>
        <path
          d="M 200 400 Q 960 150 1720 400"
          stroke="rgba(255,255,255,0.2)"
          strokeWidth={2}
          fill="none"
        />
      </svg>

      {/* Element following the path */}
      <div
        style={{
          position: "absolute",
          left: rocket.x,
          top: rocket.y,
          transform: `translate(-50%, -50%) rotate(${rocket.angle}deg)`,
          fontSize: '48px'
        }}
      >
        🚀
      </div>
    </div>
  );
}
```

### Text Path Animations

Combine `textPath` helpers with animation classes to create animated text along curves:

**Rotating text around a circle:**
```tsx
export default function RotatingCircleText({ tw, textPath, progress }) {
  return (
    <div style={tw('relative w-full h-full bg-black')}>
      {/* Text rotates around circle using progress */}
      {textPath.onCircle(
        "SPINNING TEXT • AROUND • ",
        960,      // center x
        540,      // center y
        400,      // radius
        progress, // rotation offset (0-1 animates full rotation)
        {
          fontSize: "3xl",
          fontWeight: "bold",
          color: "yellow-300"
        }
      )}
    </div>
  );
}
```

**Animated text reveal along a path:**
```tsx
export default function PathTextReveal({ tw, textPath, progress }) {
  // Create custom path follower that animates position
  const pathFollower = (t) => {
    // Only show characters up to current progress
    const visibleProgress = progress * 1.5; // Extend range for smooth reveal
    const opacity = t < visibleProgress ? 1 : 0;

    // Follow quadratic curve
    const pos = {
      x: (1 - t) * (1 - t) * 200 + 2 * (1 - t) * t * 960 + t * t * 1720,
      y: (1 - t) * (1 - t) * 400 + 2 * (1 - t) * t * 150 + t * t * 400,
      angle: 0
    };

    return { ...pos, opacity };
  };

  return (
    <div style={tw('relative w-full h-full bg-gray-900')}>
      {textPath.onPath(
        "REVEALING TEXT",
        pathFollower,
        {
          fontSize: "4xl",
          fontWeight: "bold",
          color: "blue-300"
        }
      ).map((char, i) => (
        <div key={i} style={{ ...char.props.style, opacity: char.props.style.opacity || 1 }}>
          {char}
        </div>
      ))}
    </div>
  );
}
```

**Staggered character entrance:**
```tsx
export default function StaggeredCircleText({ tw, textPath }) {
  const text = "HELLO WORLD";

  return (
    <div style={tw('relative w-full h-full bg-slate-900')}>
      {textPath.onCircle(
        text,
        960, 540, 400, 0,
        { fontSize: "4xl", fontWeight: "bold", color: "white" }
      ).map((char, i) => {
        // Stagger fade-in: each character starts 50ms later
        const staggerDelay = i * 50;
        return (
          <div
            key={i}
            style={{
              ...char.props.style,
              ...tw(`enter-fade-in/${staggerDelay}/300 enter-scale-100/${staggerDelay}/300`)
            }}
          >
            {char.props.children}
          </div>
        );
      })}
    </div>
  );
}
```

**Text with bounce entrance along arc:**
```tsx
export default function BouncyArcText({ tw, textPath }) {
  return (
    <div style={tw('relative w-full h-full bg-gradient-to-br from-purple-600 to-blue-500')}>
      {/* Draw the arc path */}
      <svg width="1920" height="1080" style={{ position: 'absolute' }}>
        <path
          d="M 300 900 A 600 600 0 0 1 1620 900"
          stroke="rgba(255,255,255,0.2)"
          strokeWidth={2}
          fill="none"
          strokeDasharray="5 5"
        />
      </svg>

      {/* Text follows arc with staggered bounce */}
      {textPath.onArc(
        "BOUNCING ON ARC",
        960,  // cx
        300,  // cy
        600,  // radius
        180,  // start angle
        360,  // end angle
        { fontSize: "3xl", fontWeight: "bold", color: "white" }
      ).map((char, i) => (
        <div
          key={i}
          style={{
            ...char.props.style,
            ...tw(`ease-out enter-bounce-in-up/${i * 80}/500`)
          }}
        >
          {char.props.children}
        </div>
      ))}
    </div>
  );
}
```

**Loop animation with text on curve:**
```tsx
export default function LoopingCurveText({ tw, textPath, frame }) {
  // Calculate wave effect using frame
  const waveOffset = Math.sin(frame / 30 * Math.PI * 2) * 0.1;

  return (
    <div style={tw('relative w-full h-full bg-black')}>
      {textPath.onQuadratic(
        "WAVY TEXT",
        { x: 200, y: 400 },
        { x: 960, y: 150 },
        { x: 1720, y: 400 },
        { fontSize: "4xl", fontWeight: "bold", color: "pink-300" }
      ).map((char, i) => (
        <div
          key={i}
          style={{
            ...char.props.style,
            transform: `${char.props.style.transform} translateY(${Math.sin((i + frame) / 5) * 10}px)`
          }}
        >
          {char.props.children}
        </div>
      ))}
    </div>
  );
}
```

**Tips for animating text paths:**
1. **Use `progress` for smooth rotation** on circles and arcs
2. **Map over returned characters** to apply individual animations
3. **Combine with animation classes** like `enter-fade-in`, `enter-bounce-in`, etc.
4. **Stagger character animations** by calculating delays: `i * delayMs`
5. **Use `frame` for continuous effects** like waves or pulsing
6. **Preserve the original transform** when adding animations: `transform: '${char.props.style.transform} ...'`

**Common path types:**

**Quadratic Bezier** (Q command):
```tsx
// Position: (1-t)²·P0 + 2(1-t)t·P1 + t²·P2
function pointOnQuadraticBezier(p0, p1, p2, t) {
  const x = (1 - t) * (1 - t) * p0.x + 2 * (1 - t) * t * p1.x + t * t * p2.x;
  const y = (1 - t) * (1 - t) * p0.y + 2 * (1 - t) * t * p1.y + t * t * p2.y;
  return { x, y };
}

// Tangent angle
function angleOnQuadraticBezier(p0, p1, p2, t) {
  const dx = 2 * (1 - t) * (p1.x - p0.x) + 2 * t * (p2.x - p1.x);
  const dy = 2 * (1 - t) * (p1.y - p0.y) + 2 * t * (p2.y - p1.y);
  return Math.atan2(dy, dx) * (180 / Math.PI);
}
```

**Cubic Bezier** (C command):
```tsx
// Position: (1-t)³·P0 + 3(1-t)²t·P1 + 3(1-t)t²·P2 + t³·P3
function pointOnCubicBezier(p0, p1, p2, p3, t) {
  const mt = 1 - t;
  const mt2 = mt * mt;
  const mt3 = mt2 * mt;
  const t2 = t * t;
  const t3 = t2 * t;
  const x = mt3 * p0.x + 3 * mt2 * t * p1.x + 3 * mt * t2 * p2.x + t3 * p3.x;
  const y = mt3 * p0.y + 3 * mt2 * t * p1.y + 3 * mt * t2 * p2.y + t3 * p3.y;
  return { x, y };
}

// Tangent angle
function angleOnCubicBezier(p0, p1, p2, p3, t) {
  const mt = 1 - t;
  const mt2 = mt * mt;
  const t2 = t * t;
  const dx = -3 * mt2 * p0.x + 3 * mt2 * p1.x - 6 * mt * t * p1.x - 3 * t2 * p2.x + 6 * mt * t * p2.x + 3 * t2 * p3.x;
  const dy = -3 * mt2 * p0.y + 3 * mt2 * p1.y - 6 * mt * t * p1.y - 3 * t2 * p2.y + 6 * mt * t * p2.y + 3 * t2 * p3.y;
  return Math.atan2(dy, dx) * (180 / Math.PI);
}
```

**Circle**:
```tsx
function pointOnCircle(cx, cy, radius, angleRadians) {
  return {
    x: cx + radius * Math.cos(angleRadians),
    y: cy + radius * Math.sin(angleRadians)
  };
}

// Usage
const angleRadians = progress * Math.PI * 2;
const pos = pointOnCircle(300, 300, 100, angleRadians);
const tangentAngle = (angleRadians * 180 / Math.PI) + 90; // Tangent is perpendicular
```

**Tips:**
- Use `progress` (0-1) for smooth animation
- The `translate(-50%, -50%)` centers the element on the path
- Combine rotation with the translate: `translate(-50%, -50%) rotate(${angle}deg)`
- For text following a path, you can animate individual characters at different progress values

## SVG Stroke Animations

Animate SVG path strokes with the **stroke-dash** classes, perfect for drawing or erasing line art, icons, and illustrations.

### How It Works

SVG stroke animations use `strokeDasharray` and `strokeDashoffset` CSS properties to create drawing effects:

1. **Enter animations** - Draw the stroke from start to finish
2. **Exit animations** - Erase the stroke from finish to start
3. **Loop animations** - Continuously draw and erase

### Format

All stroke-dash animations require the **path length** in brackets:

```tsx
enter-stroke-dash-[length]/start/duration
exit-stroke-dash-[length]/start/duration
loop-stroke-dash-[length]/duration
```

### Basic Examples

```tsx
export default function SVGAnimation({ tw }) {
  return (
    <svg width="400" height="200" viewBox="0 0 400 200">
      {/* Draw a curve over 1 second */}
      <path
        d="M10 150 Q 95 10 180 150"
        stroke="black"
        strokeWidth={4}
        fill="none"
        style={tw('enter-stroke-dash-[300]/0/1000')}
      />
    </svg>
  );
}
```

### Enter Animations (Drawing)

Draw strokes from 0% to 100%:

```tsx
// Draw a 300px path over 1 second
<path style={tw('enter-stroke-dash-[300]/0/1000')} />

// Draw with spring easing
<path style={tw('ease-spring enter-stroke-dash-[500]/0/1500')} />

// Stagger multiple paths
<path style={tw('enter-stroke-dash-[200]/0/600')} />
<path style={tw('enter-stroke-dash-[200]/200/600')} />
<path style={tw('enter-stroke-dash-[200]/400/600')} />
```

### Exit Animations (Erasing)

Erase strokes from 100% to 0%:

```tsx
// Erase starting at 2000ms, lasting 500ms
<path style={tw('exit-stroke-dash-[300]/2000/500')} />

// Draw then erase the same path
<path style={tw('enter-stroke-dash-[400]/0/800 exit-stroke-dash-[400]/2200/800')} />
```

### Loop Animations

Continuously draw and erase:

```tsx
// Loop every 2 seconds (draws in first half, erases in second half)
<path style={tw('loop-stroke-dash-[300]/2000')} />

// Faster loop
<path style={tw('loop-stroke-dash-[200]/1000')} />
```

### Getting Path Length

To find the path length for your SVG:

```tsx
// In browser console or component:
const path = document.querySelector('path');
const length = path.getTotalLength();
console.log(length); // e.g., 347.89
```

Then use that value:

```tsx
<path style={tw('enter-stroke-dash-[347.89]/0/1000')} />
```

### Complete Example

```tsx
export default function DrawingEffect({ tw }) {
  return (
    <div style={tw('flex items-center justify-center w-full h-full bg-gray-900')}>
      <svg width="600" height="400" viewBox="0 0 600 400">
        {/* Checkmark icon drawn in sequence */}
        <path
          d="M100 200 L 200 300 L 400 100"
          stroke="#10b981"
          strokeWidth={8}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          style={tw('ease-out enter-stroke-dash-[600]/0/1200')}
        />

        {/* Circle drawn after checkmark */}
        <circle
          cx="250"
          cy="200"
          r="150"
          stroke="#10b981"
          strokeWidth={6}
          fill="none"
          style={tw('ease-out enter-stroke-dash-[942]/1000/1000')}
        />
      </svg>
    </div>
  );
}
```

### Combining with Other Animations

Stroke animations work alongside other animation classes:

```tsx
// Fade in while drawing
<path style={tw('enter-stroke-dash-[300]/0/1000 enter-fade-in/0/1000')} />

// Draw with pulsing color
<svg>
  <path
    stroke="url(#gradient)"
    style={tw('enter-stroke-dash-[500]/0/1500')}
  />
  <defs>
    <linearGradient id="gradient">
      <stop offset="0%" stopColor="#8b5cf6" />
      <stop offset="100%" stopColor="#ec4899" />
    </linearGradient>
  </defs>
</svg>
```

### Animated Dashed Strokes (Marching Ants)

For **marching ants** or **animated dashed patterns**, use `frame` or `progress` directly instead of animation classes:

```tsx
export default function MarchingAnts({ tw, frame }) {
  // Calculate animated offset (loops every 30 frames)
  const dashOffset = -(frame % 30) * 2;

  return (
    <div style={tw('flex items-center justify-center w-full h-full bg-gray-900')}>
      <svg width="600" height="400" viewBox="0 0 600 400">
        {/* Marching ants border */}
        <rect
          x="50"
          y="50"
          width="500"
          height="300"
          fill="none"
          stroke="#3b82f6"
          strokeWidth={3}
          strokeDasharray="10 5"
          strokeDashoffset={dashOffset}
        />

        {/* Animated circle with different speed */}
        <circle
          cx="300"
          cy="200"
          r="80"
          fill="none"
          stroke="#10b981"
          strokeWidth={4}
          strokeDasharray="15 8"
          strokeDashoffset={dashOffset * 1.5}
        />
      </svg>
    </div>
  );
}
```

**Tips:**
- `strokeDasharray="10 5"` - 10px dash, 5px gap
- `strokeDashoffset={dashOffset}` - animates the pattern position
- Negative offset moves forward, positive moves backward
- Different speeds: multiply by different values (e.g., `dashOffset * 2`)

This technique is different from `stroke-dash` classes:
- **`stroke-dash` classes** - Draw/erase the stroke (reveal animation)
- **Marching ants** - Move a dashed pattern along the stroke

## Performance Tips

1. **Use Tailwind classes** when possible - they're optimized for the renderer
2. **Avoid too many nested animations** - each adds computation per frame
3. **Use loop animations sparingly** - they're computed every frame
4. **Prefer opacity and transform** - they're the most performant properties

## Next Steps

- [Templates](/templates) - Creating image and video templates
- [Helpers](/helpers) - QR codes, images, and more


# Template Helpers

Additional helpers for creating powerful, composable templates.

## Overview

Beyond the basics, loopwind provides:
- `template()` - Compose templates together
- `qr()` - Generate QR codes on the fly
- `config` - Access user configuration

For image embedding, see the [Images](/images) page.

## Template Composition

Compose multiple templates together to create complex designs.

### Usage

```tsx
export default function CompositeCard({ tw, template, title, author, avatar }) {
  return (
    <div style={tw('w-full h-full bg-gradient-to-br from-purple-600 to-blue-500 p-12')}>
      <div style={tw('bg-white rounded-2xl p-8 shadow-xl')}>
        <h1 style={tw('text-4xl font-bold text-gray-900 mb-6')}>{title}</h1>
        
        {/* Embed another template */}
        <div style={tw('mb-6')}>
          {template('user-badge', {
            name: author,
            avatar: avatar
          })}
        </div>
        
        <p style={tw('text-gray-600')}>Published by {author}</p>
      </div>
    </div>
  );
}
```

**How it works:**
1. `template(name, props)` renders another installed template
2. The embedded template is rendered at its specified size
3. You can embed multiple templates in one design
4. Templates can be nested (template within a template)

### Use Cases

**1. Reusable components:**
```tsx
// Create a logo template once, use it everywhere
<div>{template('company-logo', { variant: 'dark' })}</div>
```

**2. Complex layouts:**
```tsx
// Combine multiple templates into one design
<div style={tw('grid grid-cols-2 gap-4')}>
  {template('product-card', { product: product1 })}
  {template('product-card', { product: product2 })}
</div>
```

**3. Dynamic content:**
```tsx
// Render templates based on data
{users.map(user => 
  template('user-avatar', { name: user.name, image: user.avatar })
)}
```

### Best Practices

1. **Keep templates focused** - Each template should do one thing well
2. **Pass minimal props** - Only pass what the embedded template needs
3. **Document dependencies** - Note which templates are required in your README
4. **Avoid deep nesting** - Too many nested templates can be hard to debug

## QR Codes

Generate QR codes dynamically in your templates.

### Usage

```tsx
export default function QRCard({ tw, qr, title, url }) {
  return (
    <div style={tw('flex flex-col items-center justify-center w-full h-full bg-white p-10')}>
      <h1 style={tw('text-4xl font-bold text-black mb-8')}>{title}</h1>
      
      {/* Generate QR code for the URL */}
      <img src={qr(url)} style={tw('w-64 h-64')} />
      
      <p style={tw('text-gray-600 mt-4')}>{url}</p>
    </div>
  );
}
```

**Props format:**
```json
{
  "title": "Scan Me",
  "url": "https://example.com"
}
```

### QR Options

You can customize QR code appearance:

```tsx
// Basic QR code
<img src={qr('https://example.com')} />

// With error correction level
<img src={qr('https://example.com', { errorCorrectionLevel: 'H' })} />

// With custom size
<img src={qr('https://example.com', { width: 512 })} />
```

**Error correction levels:**
- `L` - Low (~7% correction)
- `M` - Medium (~15% correction) - default
- `Q` - Quartile (~25% correction)
- `H` - High (~30% correction)

## User Configuration

Access user settings from `.loopwind/loopwind.json` using the `config` prop:

```tsx
export default function BrandedTemplate({ tw, config, title }) {
  // Access custom colors from loopwind.json
  const primaryColor = config?.colors?.brand || '#6366f1';
  
  return (
    <div style={tw('w-full h-full p-12')}>
      <h1 style={{ 
        ...tw('text-6xl font-bold'),
        color: primaryColor 
      }}>
        {title}
      </h1>
    </div>
  );
}
```

**User's `.loopwind/loopwind.json`:**
```json title=".loopwind/loopwind.json"
{
  "colors": {
    "brand": "#ff6b6b"
  },
  "fonts": {
    "sans": ["Inter", "system-ui", "sans-serif"]
  }
}
```

This allows templates to adapt to user preferences and brand guidelines.

## Text on Path

Render text along curves, circles, and custom paths with automatic character positioning and rotation.

### Usage

```tsx
export default function CircleText({ tw, textPath, message }) {
  return (
    <div style={tw('relative w-full h-full bg-slate-900')}>
      {textPath.onCircle(
        message,
        960,  // center x
        540,  // center y
        400,  // radius
        0,    // rotation offset (0-1)
        {
          fontSize: "4xl",
          fontWeight: "bold",
          color: "white",
          letterSpacing: 0.05
        }
      )}
    </div>
  );
}
```

### Available Functions

All `textPath` functions return an array of positioned character elements:

**`textPath.onCircle(text, cx, cy, radius, offset, options?)`**
```tsx
// Text around a circle
textPath.onCircle("HELLO WORLD", 960, 540, 400, 0, {
  fontSize: "4xl",
  color: "white"
})
```

**`textPath.onPath(text, pathFollower, options?)`**
```tsx
// Text along any custom path
textPath.onPath("CUSTOM PATH", (t) => ({
  x: 100 + t * 800,
  y: 200 + Math.sin(t * Math.PI) * 100,
  angle: Math.cos(t * Math.PI) * 20
}), {
  fontSize: "2xl",
  fontWeight: "semibold"
})
```

**`textPath.onQuadratic(text, p0, p1, p2, options?)`**
```tsx
// Text along a quadratic Bezier curve
textPath.onQuadratic(
  "CURVED TEXT",
  { x: 200, y: 400 },   // start
  { x: 960, y: 100 },   // control point
  { x: 1720, y: 400 },  // end
  { fontSize: "3xl", color: "blue-300" }
)
```

**`textPath.onCubic(text, p0, p1, p2, p3, options?)`**
```tsx
// Text along a cubic Bezier curve
textPath.onCubic(
  "S-CURVE",
  { x: 200, y: 600 },   // start
  { x: 600, y: 400 },   // control 1
  { x: 1320, y: 800 },  // control 2
  { x: 1720, y: 600 },  // end
  { fontSize: "3xl", color: "purple-300" }
)
```

**`textPath.onArc(text, cx, cy, radius, startAngle, endAngle, options?)`**
```tsx
// Text along a circular arc
textPath.onArc(
  "ARC TEXT",
  960,   // center x
  540,   // center y
  400,   // radius
  0,     // start angle (degrees)
  180,   // end angle (degrees)
  { fontSize: "2xl", color: "pink-300" }
)
```

### Options

All `textPath` functions accept an optional `options` object:

```typescript
{
  fontSize?: string;      // Tailwind size: "xl", "2xl", "4xl", etc.
  fontWeight?: string;    // Tailwind weight: "bold", "semibold", etc.
  color?: string;         // Tailwind color: "white", "blue-500", etc.
  letterSpacing?: number; // Space between characters (0-1, default: 0)
  style?: any;           // Additional inline styles
}
```

### Examples

**Animated rotating text:**
```tsx
export default function RotatingText({ tw, textPath, progress }) {
  return (
    <div style={tw('relative w-full h-full bg-black')}>
      {textPath.onCircle(
        "SPINNING • TEXT • ",
        960, 540, 400,
        progress,  // Rotate based on video progress
        { fontSize: "3xl", color: "yellow-300" }
      )}
    </div>
  );
}
```

**Multiple text paths:**
```tsx
export default function MultiPath({ tw, textPath }) {
  return (
    <div style={tw('relative w-full h-full bg-gradient-to-br from-slate-900 to-slate-700')}>
      {/* Text on outer circle */}
      {textPath.onCircle(
        "OUTER RING",
        960, 540, 500, 0,
        { fontSize: "5xl", fontWeight: "bold", color: "white" }
      )}

      {/* Text on inner circle */}
      {textPath.onCircle(
        "inner ring",
        960, 540, 300, 0.5,  // offset by 50% for rotation
        { fontSize: "2xl", color: "white/60" }
      )}
    </div>
  );
}
```

**Text following a drawn path:**
```tsx
export default function PathText({ tw, textPath }) {
  return (
    <div style={tw('relative w-full h-full bg-gray-900')}>
      {/* Draw the path */}
      <svg width="1920" height="1080" style={{ position: 'absolute' }}>
        <path
          d="M 200 400 Q 960 150 1720 400"
          stroke="rgba(255,255,255,0.2)"
          strokeWidth={2}
          fill="none"
        />
      </svg>

      {/* Text following the path */}
      {textPath.onQuadratic(
        "FOLLOWING THE CURVE",
        { x: 200, y: 400 },
        { x: 960, y: 150 },
        { x: 1720, y: 400 },
        { fontSize: "3xl", fontWeight: "bold", color: "blue-300" }
      )}
    </div>
  );
}
```

For animated text paths, see [Text Path Animations](/animation#text-path-animations).

## Reserved Prop Names

The following prop names are **reserved** and cannot be used in your template's `meta.props`:

- `tw`, `qr`, `image`, `template` - Core helpers
- `path`, `textPath` - Path and text helpers
- `config`, `frame`, `progress` - System props

**Why?** These names are used for loopwind's built-in helpers. Using them as prop names would cause conflicts.

**Example:**
```tsx
// ❌ BAD - 'image' is reserved
export const meta = {
  props: {
    title: "string",
    image: "string"  // Error!
  }
};

// ✅ GOOD - Use descriptive alternatives
export const meta = {
  props: {
    title: "string",
    imageUrl: "string",    // or imageSrc, photoUrl, etc.
    logoUrl: "string"
  }
};
```

If you try to use a reserved name, you'll get a helpful error:
```
Template uses reserved prop names: image

Try renaming: "image" → "imageUrl" or "imageSrc"

Reserved names: tw, qr, image, template, path, textPath, config, frame, progress
```

## All Props Reference

Every template receives these props:

```tsx
export default function MyTemplate({
  // Core helpers (RESERVED - cannot be used as prop names)
  tw,        // Tailwind class converter
  qr,        // QR code generator (this page)
  template,  // Template composer (this page)
  config,    // User config from loopwind.json (this page)
  textPath,  // Text on path helpers (this page)

  // Media helpers (RESERVED)
  image,     // Image embedder → see /images
  path,      // Path following → see /animation

  // Video-specific (RESERVED - only in video templates)
  frame,     // Current frame number → see /templates
  progress,  // Animation progress 0-1 → see /templates

  // Your custom props (use any names EXCEPT the reserved ones above)
  ...props   // Any props from your meta.props
}) {
  // Your template code
}
```

## Next Steps

- [Embedding Images](/images)
- [Templates](/templates)
- [Styling with Tailwind & shadcn/ui](/styling)
- [Custom Fonts](/fonts)



# Styling Templates

Style your templates with Tailwind utility classes and shadcn/ui's beautiful design system.

## Quick Start

```tsx
export default function MyTemplate({ title, tw }) {
  return (
    <div style={tw('flex items-center justify-center w-full h-full bg-gradient-to-br from-blue-600 to-purple-700')}>
      <h1 style={tw('text-7xl font-bold text-white')}>
        {title}
      </h1>
    </div>
  );
}
```

## The `tw()` Function

Every template receives a `tw()` function that converts Tailwind classes to inline styles compatible with Satori:

```tsx
// Tailwind classes
tw('flex items-center justify-center p-8 bg-blue-500')

// Converts to inline styles:
{
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '2rem',
  backgroundColor: '#3b82f6'
}
```

### Basic Usage

```tsx
export default function Banner({ title, subtitle, tw }) {
  return (
    <div style={tw('w-full h-full p-12 bg-gray-50')}>
      <h1 style={tw('text-6xl font-bold text-gray-900 mb-4')}>
        {title}
      </h1>
      <p style={tw('text-2xl text-gray-600')}>
        {subtitle}
      </p>
    </div>
  );
}
```

### Combining with Custom Styles

Mix Tailwind classes with custom styles using the spread operator:

```tsx
export default function CustomGradient({ title, tw }) {
  return (
    <div
      style={{
        ...tw('flex flex-col items-center justify-center w-full h-full p-20'),
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <h1 style={tw('text-8xl font-bold text-white')}>{title}</h1>
    </div>
  );
}
```

## shadcn/ui Design System

loopwind uses **shadcn/ui's design system** by default, providing semantic color tokens for beautiful, consistent designs.

### Default Color Palette

All templates automatically have access to these semantic colors defined in `.loopwind/loopwind.json`:

```typescript
colors: {
  // Primary colors
  primary: '#18181b',           // Main brand color
  'primary-foreground': '#fafafa',

  // Secondary colors
  secondary: '#f4f4f5',         // Subtle accents
  'secondary-foreground': '#18181b',

  // Background
  background: '#ffffff',        // Page background
  foreground: '#09090b',        // Main text color

  // Muted
  muted: '#f4f4f5',            // Subtle backgrounds
  'muted-foreground': '#71717a', // Muted text

  // Accent
  accent: '#f4f4f5',           // Highlight color
  'accent-foreground': '#18181b',

  // Destructive
  destructive: '#ef4444',       // Error/danger states
  'destructive-foreground': '#fafafa',

  // UI Elements
  border: '#e4e4e7',           // Border color
  input: '#e4e4e7',            // Input borders
  ring: '#18181b',             // Focus rings
  card: '#ffffff',             // Card background
  'card-foreground': '#09090b',
}
```

### Using Semantic Colors

```tsx
export default function SemanticCard({ title, description, price, tw }) {
  return (
    <div style={tw('bg-card border border-border rounded-lg p-6')}>
      <h2 style={tw('text-card-foreground text-2xl font-bold mb-2')}>
        {title}
      </h2>
      <p style={tw('text-muted-foreground mb-4')}>
        {description}
      </p>
      <div style={tw('text-primary text-3xl font-bold')}>
        ${price}
      </div>
    </div>
  );
}
```

### Opacity Modifiers

Use Tailwind's slash syntax for opacity with any color:

```tsx
export default function OpacityExample({ tw }) {
  return (
    <div style={tw('bg-primary/50')}>          {/* 50% opacity */}
      <p style={tw('text-muted-foreground/75')}> {/* 75% opacity */}
        Subtle text
      </p>
      <div style={tw('border border-border/30')}> {/* 30% opacity */}
        Faint border
      </div>
    </div>
  );
}
```

**Supported syntax:**
- `bg-{color}/{opacity}` - Background with opacity
- `text-{color}/{opacity}` - Text with opacity  
- `border-{color}/{opacity}` - Border with opacity

### Text Hierarchy

```tsx
// Primary text
tw('text-foreground')

// Secondary/muted text
tw('text-muted-foreground')

// Accent/brand text
tw('text-primary')

// Destructive/error text
tw('text-destructive')
```

### Backgrounds

```tsx
// Page background
tw('bg-background')

// Card/elevated surfaces
tw('bg-card')

// Subtle backgrounds
tw('bg-muted')

// Accent backgrounds
tw('bg-accent')
```

## Supported Tailwind Classes

### Layout

- **Display**: `flex`, `inline-flex`, `block`, `inline-block`, `hidden`
- **Flex Direction**: `flex-row`, `flex-col`, `flex-row-reverse`, `flex-col-reverse`
- **Justify**: `justify-start`, `justify-end`, `justify-center`, `justify-between`, `justify-around`
- **Align**: `items-start`, `items-end`, `items-center`, `items-baseline`, `items-stretch`

### Spacing

- **Padding**: `p-{n}`, `px-{n}`, `py-{n}`, `pt-{n}`, `pb-{n}`, `pl-{n}`, `pr-{n}`
- **Margin**: `m-{n}`, `mx-{n}`, `my-{n}`, `mt-{n}`, `mb-{n}`, `ml-{n}`, `mr-{n}`
- **Gap**: `gap-{n}`, `gap-x-{n}`, `gap-y-{n}`
- **Sizes**: 0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 56, 64

Examples:
```tsx
tw('p-4')      // padding: 1rem
tw('px-8')     // paddingLeft: 2rem, paddingRight: 2rem
tw('m-6')      // margin: 1.5rem
tw('gap-4')    // gap: 1rem
```

### Sizing

- **Width**: `w-{n}`, `w-full`, `w-screen`, `w-1/2`, `w-1/3`, `w-2/3`
- **Height**: `h-{n}`, `h-full`, `h-screen`

Examples:
```tsx
tw('w-full')   // width: 100%
tw('h-64')     // height: 16rem
tw('w-1/2')    // width: 50%
```

### Typography

- **Font Size**: `text-xs`, `text-sm`, `text-base`, `text-lg`, `text-xl`, `text-2xl`, `text-3xl`, `text-4xl`, `text-5xl`, `text-6xl`, `text-7xl`, `text-8xl`, `text-9xl`
- **Font Weight**: `font-thin`, `font-light`, `font-normal`, `font-medium`, `font-semibold`, `font-bold`, `font-extrabold`, `font-black`
- **Text Align**: `text-left`, `text-center`, `text-right`
- **Line Height**: `leading-none`, `leading-tight`, `leading-normal`, `leading-relaxed`, `leading-loose`

### Colors

All standard Tailwind colors plus shadcn semantic colors:

**Standard colors:**
- `text-{color}-{shade}`, `bg-{color}-{shade}`, `border-{color}-{shade}`
- Colors: `red`, `blue`, `green`, `yellow`, `purple`, `pink`, `gray`, `indigo`, `teal`, `orange`
- Shades: `50`, `100`, `200`, `300`, `400`, `500`, `600`, `700`, `800`, `900`

**shadcn semantic colors:**
- `text-foreground`, `text-primary`, `text-muted-foreground`, `text-destructive`
- `bg-background`, `bg-card`, `bg-muted`, `bg-accent`, `bg-primary`
- `border-border`, `border-input`

```tsx
tw('text-blue-500')        // Standard Tailwind color
tw('bg-purple-600')        // Standard Tailwind color
tw('text-primary')         // shadcn semantic color
tw('bg-card')              // shadcn semantic color
```

### Position & Layout

- **Position**: `relative`, `absolute`, `fixed`, `sticky`
- **Inset**: `inset-0`, `top-0`, `bottom-0`, `left-0`, `right-0`
- **Z-Index**: `z-0`, `z-10`, `z-20`, `z-30`, `z-40`, `z-50`

### Borders

- **Border Width**: `border`, `border-{n}`, `border-t`, `border-b`, `border-l`, `border-r`
- **Border Radius**: `rounded`, `rounded-sm`, `rounded-md`, `rounded-lg`, `rounded-xl`, `rounded-2xl`, `rounded-3xl`, `rounded-full`
- **Border Color**: `border-{color}-{shade}`, `border-border`, `border-input`

### Effects

- **Shadow**: `shadow-sm`, `shadow`, `shadow-md`, `shadow-lg`, `shadow-xl`, `shadow-2xl`
- **Opacity**: `opacity-0`, `opacity-25`, `opacity-50`, `opacity-75`, `opacity-100`

### Filters

- **Blur**: `blur-none`, `blur-sm`, `blur`, `blur-md`, `blur-lg`, `blur-xl`
- **Brightness**: `brightness-0`, `brightness-50`, `brightness-100`, `brightness-150`, `brightness-200`
- **Contrast**: `contrast-0`, `contrast-50`, `contrast-100`, `contrast-150`, `contrast-200`

## Gradients

### Linear Gradients

```tsx
// Gradient direction
tw('bg-gradient-to-r')      // left to right
tw('bg-gradient-to-br')     // top-left to bottom-right
tw('bg-gradient-to-t')      // bottom to top

// Gradient colors
tw('from-blue-500')         // Start color
tw('via-purple-500')        // Middle color
tw('to-pink-500')           // End color

// Complete gradient
tw('bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500')
```

### Gradient Examples

```tsx
export default function GradientCard({ title, tw }) {
  return (
    <div style={tw('w-full h-full bg-gradient-to-br from-cyan-500 to-blue-600 p-12')}>
      <h1 style={tw('text-white text-6xl font-bold')}>
        {title}
      </h1>
    </div>
  );
}
```

## Custom Theme Colors

You can override the default shadcn colors or add your own custom colors in `.loopwind/loopwind.json`:

```json title=".loopwind/loopwind.json"
{
  "theme": {
    "colors": {
      "primary": "#3b82f6",
      "primary-foreground": "#ffffff",
      "accent": "#10b981",
      "brand": "#ff6b6b"
    }
  }
}
```

Then use these custom colors in your templates:

```tsx
tw('text-brand')    // Uses your custom brand color
tw('bg-primary')    // Uses your custom primary color
tw('bg-accent')     // Uses your custom accent color
```

## Auto-Detection from tailwind.config.js

loopwind automatically detects and loads your project's Tailwind configuration:

```
your-project/
├── tailwind.config.js  ← Automatically detected
└── .loopwind/
    ├── loopwind.json
    └── templates/
```

This includes:
- Custom colors
- Custom spacing values
- Custom fonts
- Theme extensions
- Custom utilities

## Complete Example

```tsx
export default function ModernCard({ 
  tw, 
  image,
  title, 
  description, 
  category,
  author,
  avatar 
}) {
  return (
    <div style={tw('w-full h-full bg-card')}>
      {/* Hero image */}
      <div style={tw('relative h-2/3')}>
        <img 
          src={image(hero)} 
          style={tw('w-full h-full object-cover')}
        />
        {/* Category badge */}
        <div style={tw('absolute top-4 left-4 bg-primary/90 backdrop-blur px-4 py-2 rounded-full')}>
          <span style={tw('text-sm font-semibold text-primary-foreground')}>
            {category}
          </span>
        </div>
      </div>
      
      {/* Content */}
      <div style={tw('h-1/3 p-8 flex flex-col justify-between')}>
        <div>
          <h2 style={tw('text-3xl font-bold text-foreground mb-2')}>
            {title}
          </h2>
          <p style={tw('text-muted-foreground line-clamp-2')}>
            {description}
          </p>
        </div>
        
        {/* Author */}
        <div style={tw('flex items-center gap-3')}>
          <img 
            src={image(avatar)} 
            style={tw('w-10 h-10 rounded-full border-2 border-border')}
          />
          <span style={tw('text-sm text-muted-foreground')}>
            {author}
          </span>
        </div>
      </div>
    </div>
  );
}
```

## Why This Approach?

- **Semantic naming**: `text-primary` instead of `text-blue-600`
- **Consistency**: All templates use the same design language
- **Flexibility**: Easy to customize entire theme
- **Accessibility**: Pre-tested color contrasts
- **Modern**: Same system as shadcn/ui components
- **Familiar**: Standard Tailwind syntax

## Next Steps

- [Custom Fonts](/fonts)
- [Built-in Helpers](/helpers)
- [Templates](/templates)
- [Embedding Images](/images)



# Font Handling in loopwind

The recommended way to use fonts is through `loopwind.json` - configure fonts once, use everywhere.

## Using Fonts from loopwind.json (Recommended)

Configure fonts in your `.loopwind/loopwind.json` and use Tailwind classes in templates.

### Simple Setup

Define font families in `.loopwind/loopwind.json` without loading custom fonts (uses system fonts):

```json title=".loopwind/loopwind.json"
{
  "fonts": {
    "sans": ["Inter", "system-ui", "-apple-system", "sans-serif"],
    "serif": ["Georgia", "serif"],
    "mono": ["Courier New", "monospace"]
  }
}
```

**Template usage:**
```tsx
export default function({ title, tw }) {
  return (
    <div style={tw('w-full h-full')}>
      {/* Uses fonts.sans from loopwind.json */}
      <h1 style={tw('font-sans text-6xl font-bold')}>
        {title}
      </h1>

      {/* Uses fonts.mono from loopwind.json */}
      <code style={tw('font-mono text-sm')}>
        {code}
      </code>
    </div>
  );
}
```

**Result:** Uses system fonts, falls back to Inter for rendering.

### Complete Setup (With Font Files)

Load custom font files for brand-specific typography in `.loopwind/loopwind.json`:

```json title=".loopwind/loopwind.json"
{
  "fonts": {
    "sans": {
      "family": ["Inter", "system-ui", "sans-serif"],
      "files": [
        { "path": "./fonts/Inter-Regular.woff", "weight": 400 },
        { "path": "./fonts/Inter-Bold.woff", "weight": 700 }
      ]
    },
    "mono": {
      "family": ["JetBrains Mono", "monospace"],
      "files": [
        { "path": "./fonts/JetBrainsMono-Regular.woff", "weight": 400 }
      ]
    }
  }
}
```

**Project structure:**
```
your-project/
├── .loopwind/
│   ├── loopwind.json
│   └── templates/
└── fonts/
    ├── Inter-Regular.woff
    ├── Inter-Bold.woff
    └── JetBrainsMono-Regular.woff
```

**Template usage (same as before):**
```tsx
<h1 style={tw('font-sans font-bold')}>
  {/* Uses Inter Bold from loopwind.json */}
  {title}
</h1>
```

**Available classes:**
- `font-sans` - Uses `fonts.sans` from loopwind.json
- `font-serif` - Uses `fonts.serif` from loopwind.json
- `font-mono` - Uses `fonts.mono` from loopwind.json

**Supported formats:**
- ✅ **WOFF** (`.woff`) - Recommended for best compatibility
- ✅ **TTF** (`.ttf`) - Also supported
- ✅ **OTF** (`.otf`) - Also supported
- ❌ **WOFF2** (`.woff2`) - Not supported by renderer

## Font Loading Priority

loopwind loads fonts in this order:

1. **loopwind.json fonts** (if configured with `files`)
2. **Bundled Inter fonts** (included with CLI)

This ensures fonts work out of the box with no configuration.

## Default Fonts

If no fonts are configured, loopwind uses **Inter** (Regular 400, Bold 700) which is bundled with the CLI. This means fonts work offline with no configuration required.

## Best Practices

1. ✅ **Use loopwind.json for project-wide fonts** - Configure once, use everywhere
2. ✅ **Use font classes** - `tw('font-sans')` instead of `fontFamily: 'Inter'`
3. ✅ **Include fallbacks** - Always add system fonts: `["Inter", "system-ui", "sans-serif"]`
4. ✅ **Match names** - First font in `family` array is used as the loaded font name
5. ✅ **Relative paths** - Font paths are relative to `loopwind.json` location

## Examples

### Minimal Setup (System Fonts)
```json title=".loopwind/loopwind.json"
{
  "fonts": {
    "sans": ["Inter", "-apple-system", "sans-serif"]
  }
}
```
Uses system Inter if available, falls back to Noto Sans for rendering.

### Brand Fonts Setup
```json title=".loopwind/loopwind.json"
{
  "fonts": {
    "sans": {
      "family": ["Montserrat", "sans-serif"],
      "files": [
        { "path": "./fonts/Montserrat-Regular.woff", "weight": 400 },
        { "path": "./fonts/Montserrat-Bold.woff", "weight": 700 }
      ]
    }
  }
}
```
Loads and uses Montserrat for all templates.

### Multi-Font Setup
```json title=".loopwind/loopwind.json"
{
  "fonts": {
    "sans": {
      "family": ["Inter", "sans-serif"],
      "files": [
        { "path": "./fonts/Inter-Regular.woff", "weight": 400 },
        { "path": "./fonts/Inter-Bold.woff", "weight": 700 }
      ]
    },
    "serif": {
      "family": ["Playfair Display", "serif"],
      "files": [
        { "path": "./fonts/Playfair-Regular.woff", "weight": 400 }
      ]
    },
    "mono": {
      "family": ["Fira Code", "monospace"],
      "files": [
        { "path": "./fonts/FiraCode-Regular.woff", "weight": 400 }
      ]
    }
  }
}
```
Loads different fonts for each style class.

### External Font URLs
Load fonts directly from CDNs without downloading files:

```json title=".loopwind/loopwind.json"
{
  "fonts": {
    "sans": {
      "family": ["Inter", "sans-serif"],
      "files": [
        {
          "path": "https://unpkg.com/@fontsource/inter@5.0.18/files/inter-latin-400-normal.woff",
          "weight": 400
        },
        {
          "path": "https://unpkg.com/@fontsource/inter@5.0.18/files/inter-latin-700-normal.woff",
          "weight": 700
        }
      ]
    }
  }
}
```

You can also mix local and external fonts:

```json title=".loopwind/loopwind.json"
{
  "fonts": {
    "sans": {
      "family": ["Inter", "sans-serif"],
      "files": [
        { "path": "./fonts/Inter-Regular.woff", "weight": 400 },
        {
          "path": "https://unpkg.com/@fontsource/inter@5.0.18/files/inter-latin-700-normal.woff",
          "weight": 700
        }
      ]
    }
  }
}
```

**Note:** Use WOFF format (`.woff`) for best compatibility. WOFF2 is not supported by the underlying renderer.

## Performance

- ✅ **Font caching** - Fonts load once and are cached for all renders
- ✅ **Video optimization** - 90-frame video loads fonts once, not 90 times
- ✅ **No CDN delays** - Local fonts load instantly

## Next Steps

- [Styling with Tailwind & shadcn/ui](/styling)
- [Built-in Helpers](/helpers)
- [Templates](/templates)
- [Embedding Images](/images)


# loopwind.json

Configure colors and fonts for all your templates in `.loopwind/loopwind.json`.

## File Location

```
your-project/
├── .loopwind/
│   ├── loopwind.json     ← Configuration file
│   └── templates/
```

## Minimal Example

```json title=".loopwind/loopwind.json"
{
  "theme": {
    "colors": {
      "primary": "#3b82f6",
      "background": "#ffffff"
    }
  }
}
```

## Theme Colors

### Default shadcn/ui Palette

```json title=".loopwind/loopwind.json"
{
  "theme": {
    "colors": {
      "primary": "#18181b",
      "primary-foreground": "#fafafa",
      
      "secondary": "#f4f4f5",
      "secondary-foreground": "#18181b",
      
      "background": "#ffffff",
      "foreground": "#09090b",
      
      "muted": "#f4f4f5",
      "muted-foreground": "#71717a",
      
      "accent": "#f4f4f5",
      "accent-foreground": "#18181b",
      
      "destructive": "#ef4444",
      "destructive-foreground": "#fafafa",
      
      "border": "#e4e4e7",
      "input": "#e4e4e7",
      "ring": "#18181b",
      
      "card": "#ffffff",
      "card-foreground": "#09090b"
    }
  }
}
```

### Custom Colors

```json title=".loopwind/loopwind.json"
{
  "theme": {
    "colors": {
      "primary": "#3b82f6",
      "brand": "#ff6b6b",
      "success": "#22c55e",
      "warning": "#f59e0b"
    }
  }
}
```

**Use in templates:**

```tsx
tw('text-brand')      // #ff6b6b
tw('bg-success')      // #22c55e
tw('border-warning')  // #f59e0b
```

## Fonts

### Simple (System Fonts)

```json title=".loopwind/loopwind.json"
{
  "fonts": {
    "sans": ["Inter", "system-ui", "sans-serif"],
    "serif": ["Georgia", "serif"],
    "mono": ["Courier New", "monospace"]
  }
}
```

### With Font Files

```json title=".loopwind/loopwind.json"
{
  "fonts": {
    "sans": {
      "family": ["Inter", "system-ui", "sans-serif"],
      "files": [
        { "path": "./fonts/Inter-Regular.woff", "weight": 400 },
        { "path": "./fonts/Inter-Bold.woff", "weight": 700 }
      ]
    }
  }
}
```

Paths are relative to `loopwind.json`.

**Supported formats:**
- ✅ WOFF (`.woff`)
- ✅ TTF (`.ttf`)
- ✅ OTF (`.otf`)
- ❌ WOFF2 (`.woff2`)

### External URLs

```json title=".loopwind/loopwind.json"
{
  "fonts": {
    "sans": {
      "family": ["Inter", "sans-serif"],
      "files": [
        {
          "path": "https://unpkg.com/@fontsource/inter@5.0.18/files/inter-latin-400-normal.woff",
          "weight": 400
        }
      ]
    }
  }
}
```

## Complete Example

```json title=".loopwind/loopwind.json"
{
  "theme": {
    "colors": {
      "primary": "#6366f1",
      "primary-foreground": "#ffffff",
      "background": "#ffffff",
      "foreground": "#0f172a",
      "muted": "#f1f5f9",
      "muted-foreground": "#64748b",
      "border": "#e2e8f0",
      "card": "#ffffff",
      "brand": "#8b5cf6"
    }
  },
  "fonts": {
    "sans": {
      "family": ["Inter", "sans-serif"],
      "files": [
        { "path": "./fonts/Inter-Regular.woff", "weight": 400 },
        { "path": "./fonts/Inter-Bold.woff", "weight": 700 }
      ]
    },
    "serif": {
      "family": ["Playfair Display", "serif"],
      "files": [
        { "path": "./fonts/Playfair-Regular.woff", "weight": 400 }
      ]
    }
  }
}
```

## Schema

```typescript
{
  "theme"?: {
    "colors"?: {
      [name: string]: string;  // Hex color
    }
  },
  "fonts"?: {
    [class: string]: string[] | {
      family: string[];
      files: Array<{
        path: string;    // Local or URL
        weight: number;  // 100-900
      }>;
    }
  }
}
```

## Auto-Detection

If no `loopwind.json` exists, loopwind auto-detects `tailwind.config.js`:

```
your-project/
├── tailwind.config.js  ← Auto-detected
└── .loopwind/
    └── templates/
```

**Priority:**
1. `.loopwind/loopwind.json`
2. `tailwind.config.js`
3. Built-in defaults

## Next Steps

- [Styling](/styling) - Use colors in templates
- [Fonts](/fonts) - Font configuration details
- [Getting Started](/getting-started) - Setup guide




