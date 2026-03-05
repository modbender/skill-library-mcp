#!/bin/bash
# Crea applicazioni AI con integrazione OpenAI/Claude

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATE_DIR="$SKILL_DIR/templates/ai-app"

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
TYPE="chat"

while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            TYPE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ailabs create ai-app <name> --type <chat|agent|rag>"
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
    exit 1
fi

if [[ ! "$TYPE" =~ ^(chat|agent|rag)$ ]]; then
    log_error "Tipo non valido. Usa: chat, agent, rag"
    exit 1
fi

log_info "Creazione AI App: $PROJECT_NAME (tipo: $TYPE)"

# Crea directory progetto
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Inizializza progetto Next.js
log_info "Inizializzazione Next.js 15..."
echo "my-app" | npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --yes 2>/dev/null || true

# Installa dipendenze AI
log_info "Installazione dipendenze AI..."
npm install ai openai @anthropic-ai/sdk framer-motion lucide-react
npm install @upstash/redis @upstash/ratelimit

# Installa shadcn/ui
log_info "Setup shadcn/ui..."
npx shadcn@latest init -y -d
npx shadcn@latest add button card input textarea badge avatar scroll-area -y

# Crea struttura API
mkdir -p app/api/chat app/api/agent app/lib app/hooks

# Crea lib AI
cat > app/lib/ai-config.ts << 'EOF'
import { OpenAIStream, StreamingTextResponse } from 'ai'
import OpenAI from 'openai'
import { Anthropic } from '@anthropic-ai/sdk'

export const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

export const anthropic = new Anthropic({
  apiKey: process.env.CLAUDE_API_KEY,
})

export type AIModel = 'gpt-4' | 'gpt-3.5-turbo' | 'claude-3-opus' | 'claude-3-sonnet'

export interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  id?: string
  createdAt?: Date
}

export interface ChatOptions {
  model?: AIModel
  temperature?: number
  maxTokens?: number
  stream?: boolean
}
EOF

# Crea API route per chat
cat > app/api/chat/route.ts << 'EOF'
import { OpenAIStream, StreamingTextResponse } from 'ai'
import { openai } from '@/app/lib/ai-config'

export const runtime = 'edge'

export async function POST(req: Request) {
  const { messages, model = 'gpt-4' } = await req.json()

  const response = await openai.chat.completions.create({
    model,
    stream: true,
    messages: messages.map((m: any) => ({
      role: m.role,
      content: m.content,
    })),
  })

  const stream = OpenAIStream(response)
  return new StreamingTextResponse(stream)
}
EOF

# Crea hook per chat
cat > app/hooks/use-chat.ts << 'EOF'
'use client'

import { useState, useCallback } from 'react'
import { useChat as useVercelChat } from 'ai/react'
import type { Message } from '@/app/lib/ai-config'

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const sendMessage = useCallback(async (content: string) => {
    setIsLoading(true)
    setError(null)

    const userMessage: Message = { role: 'user', content, id: Date.now().toString() }
    setMessages(prev => [...prev, userMessage])

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMessage],
        }),
      })

      if (!response.ok) throw new Error('Failed to send message')

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let assistantContent = ''

      const assistantMessage: Message = {
        role: 'assistant',
        content: '',
        id: (Date.now() + 1).toString(),
      }
      setMessages(prev => [...prev, assistantMessage])

      while (reader) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        assistantContent += chunk

        setMessages(prev =>
          prev.map(m =>
            m.id === assistantMessage.id
              ? { ...m, content: assistantContent }
              : m
          )
        )
      }
    } catch (err) {
      setError(err as Error)
    } finally {
      setIsLoading(false)
    }
  }, [messages])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
  }
}
EOF

# Crea componente Chat
cat > components/chat-interface.tsx << 'EOF'
'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Trash2, Bot, User } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { motion, AnimatePresence } from 'framer-motion'
import { useChat } from '@/app/hooks/use-chat'

export function ChatInterface() {
  const [input, setInput] = useState('')
  const { messages, isLoading, sendMessage, clearMessages } = useChat()
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    await sendMessage(input)
    setInput('')
  }

  return (
    <Card className="w-full max-w-4xl mx-auto h-[600px] flex flex-col">
      <CardHeader className="flex flex-row items-center justify-between border-b">
        <div className="flex items-center gap-2">
          <Bot className="w-6 h-6 text-primary" />
          <CardTitle>AI Assistant</CardTitle>
          <Badge variant="secondary" className="ml-2">GPT-4</Badge>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={clearMessages}
          disabled={messages.length === 0}
        >
          <Trash2 className="w-4 h-4" />
        </Button>
      </CardHeader>

      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <AnimatePresence>
          {messages.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center text-muted-foreground py-12"
            >
              <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Start a conversation with the AI assistant</p>
            </motion.div>
          ) : (
            messages.map((message, index) => (
              <motion.div
                key={message.id || index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className={`flex gap-3 mb-4 ${
                  message.role === 'user' ? 'flex-row-reverse' : ''
                }`}
              >
                <Avatar className={message.role === 'user' ? 'bg-primary' : 'bg-muted'}>
                  <AvatarFallback>
                    {message.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </AvatarFallback>
                </Avatar>
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  <pre className="whitespace-pre-wrap font-sans text-sm">
                    {message.content}
                  </pre>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-3"
          >
            <Avatar className="bg-muted">
              <AvatarFallback><Bot className="w-4 h-4" /></AvatarFallback>
            </Avatar>
            <div className="bg-muted rounded-lg px-4 py-2">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-foreground/50 rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-foreground/50 rounded-full animate-bounce delay-100" />
                <span className="w-2 h-2 bg-foreground/50 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </motion.div>
        )}
      </ScrollArea>

      <CardContent className="border-t pt-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
EOF

# Crea pagina principale
cat > app/page.tsx << 'EOF'
import { ChatInterface } from '@/components/chat-interface'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-background to-muted/20 py-8">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold tracking-tight mb-2">
            AI Chat Application
          </h1>
          <p className="text-muted-foreground">
            Powered by OpenAI GPT-4 with streaming responses
          </p>
        </div>
        
        <ChatInterface />
      </div>
    </main>
  )
}
EOF

# Crea layout
cat > app/layout.tsx << 'EOF'
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Chat App",
  description: "AI-powered chat application",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
EOF

# Crea .env.example
cat > .env.example << 'EOF'
# OpenAI Configuration
OPENAI_API_KEY=sk-...

# Claude Configuration (optional)
CLAUDE_API_KEY=sk-ant-...

# Upstash Redis (for rate limiting)
UPSTASH_REDIS_REST_URL=
UPSTASH_REDIS_REST_TOKEN=
EOF

# Crea README
cat > README.md << EOF
# $PROJECT_NAME

Applicazione AI creata con AI Labs Builder

## Features

- Chat interface con streaming responses
- Integrazione OpenAI GPT-4
- Supporto Claude (opzionale)
- Rate limiting con Upstash Redis
- Framer Motion animations
- shadcn/ui components

## Setup

\`\`\`bash
# Install dependencies
npm install

# Configure environment variables
cp .env.example .env.local
# Edit .env.local with your API keys

# Run development server
npm run dev
\`\`\`

## Environment Variables

| Variable | Description |
|----------|-------------|
| OPENAI_API_KEY | Your OpenAI API key |
| CLAUDE_API_KEY | Your Anthropic API key (optional) |
| UPSTASH_REDIS_REST_URL | Upstash Redis URL (optional) |
| UPSTASH_REDIS_REST_TOKEN | Upstash Redis token (optional) |
EOF

log_success "AI App creata con successo!"
log_info "Tipo: $TYPE"
log_info "Per iniziare:"
echo "  cd $PROJECT_NAME"
echo "  cp .env.example .env.local"
echo "  # Aggiungi le tue API keys"
echo "  npm install"
echo "  npm run dev"
