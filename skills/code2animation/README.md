# Code2Animation

A code-based video generation project that provides video materials for FFmpeg composition by rendering code animations.

## Project Overview

Code2Animation is an alternertive to Replit Animaiton and Remotion.

https://github.com/user-attachments/assets/2659aa26-b093-48d6-8e53-c6bb8b899750


## Key Features

- 🎬 **Multiple Clip Types**: Support for code display, fullscreen video, typography animation, split-screen display, and chatbot interface
- 🎨 **Theme Customization**: Support for dark, light, and neon themes
- 🗣️ **Text-to-Speech**: Integrated TTS functionality with customizable voice parameters
- 🎵 **Media Integration**: Support for various media types including video, images, and code
- ⚡ **Real-time Rendering**: High-performance real-time rendering based on React

## Tech Stack

- **Frontend Framework**: React 19 + TypeScript
- **Build Tool**: Vite
- **Styling Framework**: Tailwind CSS
- **Animation Library**: Motion
- **Text-to-Speech**: Microsoft Edge TTS
- **Backend Service**: Vite
- **Rendering Scripts**: Puppeteer frame-by-frame rendering with FFmpeg composition

## Quick Start

### Prerequisites

- Node.js >= 18
- pnpm >= 10.14.0

### Install Dependencies

```bash
pnpm install
```

### Development Mode

```bash
pnpm dev
```

The application will start at http://localhost:3000

### Build for Production

```bash
pnpm build
```

### Preview Production Build

```bash
pnpm preview
```

### Video Rendering

```bash
# Render a specific project (e.g., video-1)
pnpm render:video-1

# Render any project with custom parameters
pnpm render <projectId> --script <script> --port <port>
```

## Project Structure

```
code2animation/
├── src/
│   ├── components/          # React components
│   ├── hooks/              # Custom hooks
│   ├── projects/           # Project configurations
│   ├── App.tsx             # Main app component
│   ├── main.tsx            # App entry point
│   └── types.ts            # TypeScript type definitions
├── scripts/
│   ├── generate-audio.ts   # Audio generation script
│   └── render.js           # Rendering script
├── public/                 # Static assets
│   ├──audio/               # Static assets
│   ├──footage/             # Static assets
│   └──script/              # video scripts, use url param to switch
```

## Core Types

### VideoClip

The core data structure for video clips:

```typescript
interface VideoClip {
  type: ClipType;
  title?: string;
  subtitle?: string;
  speech: string;
  media?: MediaItem[];
  duration?: number;
  theme?: 'dark' | 'light' | 'neon';
  voice?: string;
  rate?: string;
  pitch?: string;
}
```

### Clip Types

- `footagesAroundTitle`: Footages around title
- `footagesFullScreen`: Fullscreen footages

## Development Guide

### Adding New Clip Types

1. Extend the `ClipType` type in `src/types.ts`
2. Create the corresponding render component in `src/components/`
3. Register the new component in `src/App.tsx`

### Custom Themes

Use the `theme` property in components to apply different visual styles:

```typescript
const theme = clip.theme || 'dark';
```

## Scripts Documentation

### generate-audio.ts

Responsible for generating text-to-speech audio, supporting:
- Text-to-speech conversion
- Audio timeline alignment
- Multiple voice parameter configurations

### render.js

Video rendering engine that handles:
- Video frame rendering
- Media file composition
- FFmpeg integration

Usage:

```bash
# Direct script usage
node scripts/render.js <projectId> --script <script> --port <port>

# PNPM commands (recommended)
pnpm render <projectId> --script <script> --port <port>
pnpm render:video-1  # Pre-configured command for video-1 project
```

Output:
- `public/video/render-<projectId>.mp4`

Notes:
- Requires FFmpeg installed and a system Chrome/Chromium browser available (or set `PUPPETEER_EXECUTABLE_PATH`).

## License

MIT
