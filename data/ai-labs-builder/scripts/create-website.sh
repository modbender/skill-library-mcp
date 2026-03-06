#!/bin/bash
# Crea siti web moderni con Next.js 15

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATE_DIR="$SKILL_DIR/templates/website"

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Parse arguments
PROJECT_NAME=""
TYPE="portfolio"

while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            TYPE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ailabs create website <name> --type <portfolio|saas|blog>"
            exit 0
            ;;
        *)
            if [[ -z "$PROJECT_NAME" ]]; then
                PROJECT_NAME="$1"
            fi
            shift
            ;;
    esac
done

if [[ -z "$PROJECT_NAME" ]]; then
    log_error "Nome progetto richiesto"
    echo "Usage: ailabs create website <name> --type <portfolio|saas|blog>"
    exit 1
fi

if [[ ! "$TYPE" =~ ^(portfolio|saas|blog)$ ]]; then
    log_error "Tipo non valido. Usa: portfolio, saas, blog"
    exit 1
fi

log_info "Creazione sito web: $PROJECT_NAME (tipo: $TYPE)"

# Crea directory progetto
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Inizializza progetto Next.js
log_info "Inizializzazione Next.js 15..."
echo "my-app" | npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --yes 2>/dev/null || true

# Installa dipendenze aggiuntive
log_info "Installazione dipendenze..."
npm install framer-motion lucide-react clsx tailwind-merge

# Installa shadcn/ui
log_info "Setup shadcn/ui..."
npx shadcn@latest init -y -d

# Installa componenti shadcn utili
npx shadcn@latest add button card input textarea badge avatar separator -y

# Copia template specifico
if [[ -d "$TEMPLATE_DIR/$TYPE" ]]; then
    log_info "Applicazione template $TYPE..."
    cp -r "$TEMPLATE_DIR/$TYPE"/* . 2>/dev/null || true
fi

# Crea struttura base
cat > app/layout.tsx << 'EOF'
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Labs - Next.js App",
  description: "Created with AI Labs Builder",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}
EOF

# Crea globals.css con dark mode
cat > app/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --card: 0 0% 100%;
  --card-foreground: 222.2 84% 4.9%;
  --popover: 0 0% 100%;
  --popover-foreground: 222.2 84% 4.9%;
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
  --secondary: 210 40% 96.1%;
  --secondary-foreground: 222.2 47.4% 11.2%;
  --muted: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;
  --accent: 210 40% 96.1%;
  --accent-foreground: 222.2 47.4% 11.2%;
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 210 40% 98%;
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 4.9%;
  --radius: 0.5rem;
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --card: 222.2 84% 4.9%;
  --card-foreground: 210 40% 98%;
  --popover: 222.2 84% 4.9%;
  --popover-foreground: 210 40% 98%;
  --primary: 210 40% 98%;
  --primary-foreground: 222.2 47.4% 11.2%;
  --secondary: 217.2 32.6% 17.5%;
  --secondary-foreground: 210 40% 98%;
  --muted: 217.2 32.6% 17.5%;
  --muted-foreground: 215 20.2% 65.1%;
  --accent: 217.2 32.6% 17.5%;
  --accent-foreground: 210 40% 98%;
  --destructive: 0 62.8% 30.6%;
  --destructive-foreground: 210 40% 98%;
  --border: 217.2 32.6% 17.5%;
  --input: 217.2 32.6% 17.5%;
  --ring: 212.7 26.8% 83.9%;
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
EOF

# Crea theme provider
cat > components/theme-provider.tsx << 'EOF'
"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"

export function ThemeProvider({
  children,
  ...props
}: React.ComponentProps<typeof NextThemesProvider>) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
EOF

# Crea theme toggle
cat > components/theme-toggle.tsx << 'EOF'
"use client"

import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "light" ? "dark" : "light")}
    >
      <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}
EOF

# Aggiorna layout con theme provider
cat > app/layout.tsx << 'EOF'
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Labs - Next.js App",
  description: "Created with AI Labs Builder",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
EOF

# Crea pagina base
cat > app/page.tsx << 'EOF'
import { ThemeToggle } from "@/components/theme-toggle"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <div className="container mx-auto px-4 py-16">
        <div className="flex justify-between items-center mb-12">
          <h1 className="text-4xl font-bold tracking-tight">
            Welcome to {process.env.NEXT_PUBLIC_APP_NAME || "AI Labs"}
          </h1>
          <ThemeToggle />
        </div>
        
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Modern Stack</CardTitle>
              <CardDescription>
                Built with Next.js 15, TypeScript, and Tailwind CSS
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button>Get Started</Button>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Dark Mode</CardTitle>
              <CardDescription>
                Automatic dark/light mode switching
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline">Learn More</Button>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Components</CardTitle>
              <CardDescription>
                Pre-configured shadcn/ui components
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="secondary">Explore</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  )
}
EOF

# Crea .env.example
cat > .env.example << 'EOF'
# App Configuration
NEXT_PUBLIC_APP_NAME=My App
NEXT_PUBLIC_APP_URL=http://localhost:3000

# API Keys (add your own)
# OPENAI_API_KEY=
# CLAUDE_API_KEY=
EOF

# Crea README
cat > README.md << EOF
# $PROJECT_NAME

Sito web creato con AI Labs Builder

## Getting Started

\`\`\`bash
npm install
npm run dev
\`\`\`

Open [http://localhost:3000](http://localhost:3000)

## Features

- Next.js 15 con App Router
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Dark/Light mode
- Framer Motion animations

## Structure

\`\`\`
app/
├── page.tsx          # Home page
├── layout.tsx        # Root layout
├── globals.css       # Global styles
components/
├── ui/               # shadcn components
├── theme-provider.tsx
└── theme-toggle.tsx
\`\`\`
EOF

# Crea .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules
.pnp
.pnp.js

# Testing
coverage

# Next.js
.next/
out/

# Production
build

# Misc
.DS_Store
*.pem

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Local env files
.env*.local
.env

# Vercel
.vercel

# TypeScript
*.tsbuildinfo
next-env.d.ts
EOF

log_success "Sito web creato con successo!"
log_info "Per iniziare:"
echo "  cd $PROJECT_NAME"
echo "  npm install"
echo "  npm run dev"
echo ""
log_info "Template utilizzato: $TYPE"
