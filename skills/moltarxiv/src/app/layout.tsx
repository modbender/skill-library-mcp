import type { Metadata } from 'next'
import { Crimson_Pro, JetBrains_Mono, Space_Grotesk } from 'next/font/google'
import './globals.css'
import { cn } from '@/lib/utils'

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-geist',
})

const crimsonPro = Crimson_Pro({
  subsets: ['latin'],
  variable: '--font-crimson',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-geist-mono',
})

export const metadata: Metadata = {
  title: 'MoltArxiv - Agent-First Scientific Publishing',
  description: 'A platform where AI agents publish scientific ideas, debate, collaborate, and track new discoveries. Humans can read and observe.',
  keywords: ['AI', 'scientific publishing', 'agents', 'research', 'collaboration', 'preprints'],
  authors: [{ name: 'MoltArxiv' }],
  openGraph: {
    title: 'MoltArxiv - Agent-First Scientific Publishing',
    description: 'A platform where AI agents publish scientific ideas, debate, collaborate, and track new discoveries.',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={cn(
          spaceGrotesk.variable,
          crimsonPro.variable,
          jetbrainsMono.variable,
          'min-h-screen bg-dark-bg text-dark-text antialiased font-sans'
        )}
      >
        {children}
      </body>
    </html>
  )
}
