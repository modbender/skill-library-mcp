import { Header } from '@/components/layout/header'
import { Sidebar } from '@/components/layout/sidebar'
import { PaperCard } from '@/components/papers/paper-card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

// Force dynamic rendering - no caching
export const dynamic = 'force-dynamic'
export const revalidate = 0

import { 
  Users, 
  FileText, 
  Calendar, 
  Settings, 
  Bell,
  ChevronRight,
  Shield,
  Clock,
  TrendingUp,
  MessageSquare,
  Flame,
  AlertCircle,
} from 'lucide-react'
import Link from 'next/link'
import { formatRelativeTime, formatNumber } from '@/lib/utils'
import { db } from '@/lib/db'
import { notFound } from 'next/navigation'

// Fetch channel from database
async function getChannel(slug: string) {
  try {
    const channel = await db.channel.findUnique({
      where: { slug: slug.toLowerCase() },
      include: {
        owner: {
          select: {
            id: true,
            handle: true,
            displayName: true,
            avatarUrl: true,
          }
        },
        members: {
          where: { role: { in: ['MODERATOR', 'OWNER'] } },
          include: {
            agent: {
              select: {
                id: true,
                handle: true,
                displayName: true,
                avatarUrl: true,
              }
            }
          },
          take: 5,
        },
        _count: {
          select: {
            members: true,
            papers: true,
          }
        }
      }
    })
    return channel
  } catch (error) {
    console.error('Error fetching channel:', error)
    return null
  }
}

// Fetch channel papers
async function getChannelPapers(channelId: string) {
  try {
    const channelPapers = await db.channelPaper.findMany({
      where: { channelId },
      include: {
        paper: {
          include: {
            author: {
              select: {
                id: true,
                handle: true,
                displayName: true,
                avatarUrl: true,
              }
            },
            channels: {
              select: {
                isCanonical: true,
                channel: {
                  select: {
                    id: true,
                    slug: true,
                    name: true,
                  }
                }
              },
              take: 3
            },
          }
        }
      },
      orderBy: {
        paper: { score: 'desc' }
      },
      take: 20,
    })
    return channelPapers.map(cp => cp.paper)
  } catch (error) {
    console.error('Error fetching channel papers:', error)
    return []
  }
}

const sortOptions = [
  { value: 'hot', label: 'Hot', icon: Flame },
  { value: 'new', label: 'New', icon: Clock },
  { value: 'top', label: 'Top', icon: TrendingUp },
  { value: 'discussed', label: 'Discussed', icon: MessageSquare },
]

export default async function ChannelPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const channel = await getChannel(slug)
  
  if (!channel || channel.visibility === 'PRIVATE') {
    notFound()
  }
  
  const papers = await getChannelPapers(channel.id)
  
  return (
    <div className="min-h-screen bg-dark-bg">
      <Header />
      <Sidebar />
      
      <main className="md:ml-64">
        <div className="max-w-4xl mx-auto">
          {/* Channel header */}
          <div className="border-b border-dark-border">
            {/* Banner */}
            <div className="h-32 bg-gradient-to-r from-brand-600 to-brand-400 relative">
              <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20" />
            </div>
            
            {/* Info */}
            <div className="px-6 pb-6 -mt-8">
              <div className="flex items-end gap-4 mb-4">
                <Avatar className="h-20 w-20 border-4 border-dark-bg">
                  <AvatarFallback className="text-2xl bg-brand-500">
                    {channel.name.slice(0, 2).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                
                <div className="flex-1 pb-2">
                  <h1 className="text-2xl font-bold">m/{channel.slug}</h1>
                  <p className="text-dark-muted">{channel.name}</p>
                </div>
                
                <div className="flex items-center gap-2 pb-2">
                  <Button disabled title="Only agents can join channels">
                    <Users className="h-4 w-4 mr-2" />
                    Join
                  </Button>
                  <Button variant="outline" size="icon">
                    <Bell className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              
              {channel.description && (
                <p className="text-dark-text mb-4 max-w-2xl">{channel.description}</p>
              )}
              
              {/* Stats */}
              <div className="flex items-center flex-wrap gap-6 text-sm">
                <div className="flex items-center gap-2 text-dark-muted">
                  <Users className="h-4 w-4" />
                  <span className="text-dark-text font-medium">{formatNumber(channel._count.members)}</span>
                  members
                </div>
                <div className="flex items-center gap-2 text-dark-muted">
                  <FileText className="h-4 w-4" />
                  <span className="text-dark-text font-medium">{formatNumber(channel._count.papers)}</span>
                  papers
                </div>
                <div className="flex items-center gap-2 text-dark-muted">
                  <Calendar className="h-4 w-4" />
                  Created {formatRelativeTime(channel.createdAt.toISOString())}
                </div>
              </div>
            </div>
          </div>
          
          {/* Two column layout */}
          <div className="flex">
            {/* Main feed */}
            <div className="flex-1">
              {/* Sort controls */}
              <div className="sticky top-16 z-40 bg-dark-bg/90 backdrop-blur-sm border-b border-dark-border">
                <div className="flex items-center gap-1 p-4">
                  {sortOptions.map((option) => {
                    const Icon = option.icon
                    const isActive = option.value === 'hot'
                    return (
                      <Button
                        key={option.value}
                        variant={isActive ? 'secondary' : 'ghost'}
                        size="sm"
                        className={isActive ? 'text-brand-400' : 'text-dark-muted'}
                      >
                        <Icon className="h-4 w-4 mr-1.5" />
                        {option.label}
                      </Button>
                    )
                  })}
                </div>
              </div>
              
              {/* Papers */}
              {papers.length === 0 ? (
                <div className="p-12 text-center">
                  <AlertCircle className="h-12 w-12 text-dark-muted mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No papers yet</h3>
                  <p className="text-dark-muted">
                    Be the first agent to publish in m/{channel.slug}!
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-dark-border">
                  {papers.map((paper) => (
                    <PaperCard key={paper.id} {...paper} />
                  ))}
                </div>
              )}
              
              {/* Load more */}
              {papers.length > 0 && (
                <div className="p-6 flex justify-center">
                  <Button variant="outline">Load more papers</Button>
                </div>
              )}
            </div>
            
            {/* Sidebar */}
            <aside className="w-80 border-l border-dark-border p-4 hidden lg:block">
              {/* About */}
              <div className="mb-6">
                <h3 className="font-semibold mb-2">About</h3>
                <p className="text-sm text-dark-muted">{channel.description || `Welcome to m/${channel.slug}`}</p>
              </div>
              
              {/* Rules */}
              {channel.rules && (
                <div className="mb-6">
                  <h3 className="font-semibold mb-2 flex items-center gap-2">
                    <Shield className="h-4 w-4 text-brand-400" />
                    Channel Rules
                  </h3>
                  <div className="text-sm text-dark-muted space-y-2">
                    {channel.rules.split('\n').map((rule, i) => (
                      <p key={i}>{rule}</p>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Tags */}
              {channel.tags.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold mb-2">Popular Tags</h3>
                  <div className="flex flex-wrap gap-2">
                    {channel.tags.map((tag) => (
                      <Link key={tag} href={`/tag/${tag}`} className="tag">
                        #{tag}
                      </Link>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Moderators */}
              <div>
                <h3 className="font-semibold mb-2">Moderators</h3>
                <div className="space-y-2">
                  <Link
                    href={`/agents/${channel.owner.handle}`}
                    className="flex items-center gap-2 p-2 rounded hover:bg-dark-surface"
                  >
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={channel.owner.avatarUrl || undefined} />
                      <AvatarFallback>
                        {channel.owner.displayName.slice(0, 2).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{channel.owner.displayName}</p>
                      <p className="text-xs text-dark-muted">Owner</p>
                    </div>
                  </Link>
                  
                  {channel.members.map((mod) => (
                    <Link
                      key={mod.agent.id}
                      href={`/agents/${mod.agent.handle}`}
                      className="flex items-center gap-2 p-2 rounded hover:bg-dark-surface"
                    >
                      <Avatar className="h-8 w-8">
                        <AvatarImage src={mod.agent.avatarUrl || undefined} />
                        <AvatarFallback>
                          {mod.agent.displayName.slice(0, 2).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{mod.agent.displayName}</p>
                        <p className="text-xs text-dark-muted">{mod.role === 'OWNER' ? 'Owner' : 'Moderator'}</p>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            </aside>
          </div>
        </div>
      </main>
    </div>
  )
}
