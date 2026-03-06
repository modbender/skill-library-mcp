# UI Development Skill

An OpenClaw skill for generating production-ready Next.js 14+ projects with TypeScript, shadcn/ui, and API integration.

**GitHub Repository:** https://github.com/wing8169/openclaw-frontend-dev

## Features

- 🚀 Next.js 14+ App Router with TypeScript
- 🎨 shadcn/ui component library (recommended)
- 📡 API integration with axios + React Query
- 🏗️ Industrial-standard folder structure
- 🎯 Feature-based component organization
- 🔒 Type-safe with TypeScript
- 📱 Mobile-first responsive design
- ⚡ Optional visual review with Chromium
- 🌐 Optional live preview with Nginx

## Tech Stack

**Core:**
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS v3
- shadcn/ui
- ESLint + Prettier

**API Integration:**
- axios (HTTP client)
- @tanstack/react-query (data fetching, caching)

**Optional:**
- Zustand (state management)
- Zod (validation)
- next-auth (authentication)
- Prisma (database ORM)

## Installation

1. Copy `ui-development.skill` to your OpenClaw skills directory
2. Or load the skill folder directly

## Requirements

**Required:**
- Node.js 18+
- npm/yarn/pnpm
- Git

**Optional:**
- Chromium (for auto-revision with visual review)
- Nginx (for live preview server)

## Project Structure

The skill generates a comprehensive Next.js project with:

- Route groups for logical organization (`(auth)`, `(dashboard)`)
- Feature-based component architecture
- Server Actions support
- Config files for site metadata and navigation
- Type-safe API hooks with React Query
- shadcn/ui components integration

## Usage

The skill triggers when you ask to:
- Build/create/develop a Next.js application
- Scaffold a web app or full-stack project
- Add features or integrate APIs to existing projects

## Workflow

1. **Project Setup** - Initialize Next.js project
2. **Create Directory Structure** - Set up industrial folder structure
3. **Install Dependencies** - Core packages + shadcn/ui
4. **Configure Base Files** - API client, React Query, providers
5. **Generate Features** - Build pages and components
6. **Build UI** - Use shadcn/ui components
7. **Visual Review** - Screenshot analysis (optional)
8. **Environment Setup** - .env configuration
9. **Scripts & Documentation** - README and package.json
10. **Export & Deploy** - Zip project and deployment guidance

## Design Principles

- Mobile-first responsive design
- WCAG AA accessibility standards
- Consistent spacing and typography
- shadcn/ui for accessible, customizable components
- TypeScript strict mode
- Performance optimization (Image component, lazy loading)

## Deployment Options

- **Vercel** (recommended)
- **Netlify**
- **Docker**
- **Self-hosted** (systemd + nginx)

## License

MIT

## Author

Created for OpenClaw by ClawBit 🦀

## Version

1.0.0 (2026-02-11)
