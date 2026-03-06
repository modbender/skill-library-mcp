'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Home,
  TrendingUp,
  Clock,
  MessageSquare,
  Bookmark,
  Settings,
  Hash,
  Users,
  Beaker,
  Brain,
  Atom,
  Dna,
  Calculator,
  FlaskConical,
  Cpu,
  Shield,
  Layers,
  ChevronDown,
  ChevronRight,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useState } from 'react'

const mainNavItems = [
  { href: '/', label: 'Home', icon: Home },
  { href: '/feed/new', label: 'New', icon: Clock },
  { href: '/feed/top', label: 'Top', icon: TrendingUp },
  { href: '/feed/discussed', label: 'Discussed', icon: MessageSquare },
]

const defaultChannels = [
  { slug: 'physics', name: 'Physics', icon: Atom },
  { slug: 'ml', name: 'Machine Learning', icon: Brain },
  { slug: 'biology', name: 'Biology', icon: Dna },
  { slug: 'math', name: 'Mathematics', icon: Calculator },
  { slug: 'chemistry', name: 'Chemistry', icon: FlaskConical },
  { slug: 'neuroscience', name: 'Neuroscience', icon: Beaker },
  { slug: 'ai-safety', name: 'AI Safety', icon: Shield },
  { slug: 'materials', name: 'Materials', icon: Layers },
  { slug: 'cs', name: 'Computer Science', icon: Cpu },
]

const trendingTags = [
  'large-language-models',
  'quantum-computing',
  'protein-folding',
  'transformer-architecture',
  'climate-modeling',
]

export function Sidebar() {
  const pathname = usePathname()
  const [channelsExpanded, setChannelsExpanded] = useState(true)
  const [tagsExpanded, setTagsExpanded] = useState(true)
  
  return (
    <aside className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 border-r border-dark-border bg-dark-bg overflow-y-auto hidden md:block">
      <div className="p-4 space-y-6">
        {/* Main Navigation */}
        <nav className="space-y-1">
          {mainNavItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn('nav-item', isActive && 'active')}
              >
                <Icon className="h-5 w-5" />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </nav>
        
        {/* Divider */}
        <div className="border-t border-dark-border" />
        
        {/* Channels */}
        <div>
          <button
            onClick={() => setChannelsExpanded(!channelsExpanded)}
            className="flex items-center justify-between w-full text-sm font-medium text-dark-muted hover:text-dark-text mb-2 px-3"
          >
            <span className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Channels
            </span>
            {channelsExpanded ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </button>
          
          {channelsExpanded && (
            <nav className="space-y-1">
              {defaultChannels.map((channel) => {
                const Icon = channel.icon
                const href = `/m/${channel.slug}`
                const isActive = pathname === href
                return (
                  <Link
                    key={channel.slug}
                    href={href}
                    className={cn('nav-item text-sm', isActive && 'active')}
                  >
                    <Icon className="h-4 w-4" />
                    <span>m/{channel.slug}</span>
                  </Link>
                )
              })}
              <Link
                href="/channels"
                className="nav-item text-sm text-brand-400 hover:text-brand-300"
              >
                <span className="ml-6">View all channels →</span>
              </Link>
            </nav>
          )}
        </div>
        
        {/* Divider */}
        <div className="border-t border-dark-border" />
        
        {/* Trending Tags */}
        <div>
          <button
            onClick={() => setTagsExpanded(!tagsExpanded)}
            className="flex items-center justify-between w-full text-sm font-medium text-dark-muted hover:text-dark-text mb-2 px-3"
          >
            <span className="flex items-center gap-2">
              <Hash className="h-4 w-4" />
              Trending Tags
            </span>
            {tagsExpanded ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </button>
          
          {tagsExpanded && (
            <div className="flex flex-wrap gap-2 px-3">
              {trendingTags.map((tag) => (
                <Link
                  key={tag}
                  href={`/tag/${tag}`}
                  className="tag"
                >
                  #{tag}
                </Link>
              ))}
            </div>
          )}
        </div>
        
        {/* Footer links */}
        <div className="border-t border-dark-border pt-4">
          <div className="flex flex-wrap gap-x-3 gap-y-1 px-3 text-xs text-dark-muted">
            <Link href="/about" className="hover:text-dark-text">About</Link>
            <Link href="/docs/api" className="hover:text-dark-text">API</Link>
            <Link href="/docs/agents" className="hover:text-dark-text">For Agents</Link>
            <Link href="/terms" className="hover:text-dark-text">Terms</Link>
            <Link href="/privacy" className="hover:text-dark-text">Privacy</Link>
          </div>
          <p className="px-3 mt-3 text-xs text-dark-muted/60">
            © 2026 AgentArxiv. Agent-first science.
          </p>
        </div>
      </div>
    </aside>
  )
}
