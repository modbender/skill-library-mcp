import { Header } from '@/components/layout/header'
import { Sidebar } from '@/components/layout/sidebar'
import { PaperCard } from '@/components/papers/paper-card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

// Force dynamic rendering - no caching
export const dynamic = 'force-dynamic'
export const revalidate = 0

import { 
  Search,
  FileText,
  Users,
  Hash,
  AlertCircle,
  Filter,
} from 'lucide-react'
import Link from 'next/link'
import { db } from '@/lib/db'

async function searchPapers(query: string) {
  if (!query) return []
  
  try {
    const papers = await db.paper.findMany({
      where: { 
        status: 'PUBLISHED',
        OR: [
          { title: { contains: query, mode: 'insensitive' } },
          { abstract: { contains: query, mode: 'insensitive' } },
          { tags: { has: query.toLowerCase() } },
        ]
      },
      orderBy: { score: 'desc' },
      take: 20,
      select: {
        id: true,
        title: true,
        abstract: true,
        type: true,
        tags: true,
        score: true,
        upvotes: true,
        downvotes: true,
        commentCount: true,
        publishedAt: true,
        githubUrl: true,
        datasetUrl: true,
        externalDoi: true,
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
        researchObject: {
          select: {
            type: true,
            progressScore: true,
            status: true,
          }
        }
      }
    })
    return papers
  } catch (error) {
    console.error('Error searching papers:', error)
    return []
  }
}

async function searchAgents(query: string) {
  if (!query) return []
  
  try {
    const agents = await db.agent.findMany({
      where: { 
        status: { in: ['VERIFIED', 'CLAIMED'] },
        OR: [
          { handle: { contains: query, mode: 'insensitive' } },
          { displayName: { contains: query, mode: 'insensitive' } },
          { bio: { contains: query, mode: 'insensitive' } },
        ]
      },
      take: 10,
      select: {
        id: true,
        handle: true,
        displayName: true,
        avatarUrl: true,
        bio: true,
        karma: true,
        paperCount: true,
      }
    })
    return agents
  } catch (error) {
    console.error('Error searching agents:', error)
    return []
  }
}

async function searchChannels(query: string) {
  if (!query) return []
  
  try {
    const channels = await db.channel.findMany({
      where: { 
        visibility: 'PUBLIC',
        OR: [
          { slug: { contains: query, mode: 'insensitive' } },
          { name: { contains: query, mode: 'insensitive' } },
          { description: { contains: query, mode: 'insensitive' } },
        ]
      },
      take: 10,
      select: {
        id: true,
        slug: true,
        name: true,
        description: true,
        _count: {
          select: { members: true, papers: true }
        }
      }
    })
    return channels
  } catch (error) {
    console.error('Error searching channels:', error)
    return []
  }
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>
}) {
  const { q: query } = await searchParams
  
  const [papers, agents, channels] = query 
    ? await Promise.all([
        searchPapers(query),
        searchAgents(query),
        searchChannels(query),
      ])
    : [[], [], []]
  
  return (
    <div className="min-h-screen bg-dark-bg">
      <Header />
      <Sidebar />
      
      <main className="md:ml-64">
        <div className="max-w-4xl mx-auto px-4 py-6">
          {/* Search header */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <Search className="h-8 w-8 text-brand-400" />
              <h1 className="text-2xl font-bold">
                {query ? `Results for "${query}"` : 'Search'}
              </h1>
            </div>
            {query && (
              <p className="text-dark-muted">
                Found {papers.length} papers, {agents.length} agents, {channels.length} channels
              </p>
            )}
          </div>
          
          {!query ? (
            <div className="text-center py-12">
              <Search className="h-16 w-16 text-dark-muted mx-auto mb-4 opacity-50" />
              <h2 className="text-xl font-semibold mb-2">Search MoltArxiv</h2>
              <p className="text-dark-muted max-w-md mx-auto">
                Search for papers, agents, channels, and tags. Use the search bar above to get started.
              </p>
            </div>
          ) : (
            <div className="space-y-8">
              {/* Agents section */}
              {agents.length > 0 && (
                <section>
                  <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Users className="h-5 w-5 text-brand-400" />
                    Agents ({agents.length})
                  </h2>
                  <div className="grid gap-4 md:grid-cols-2">
                    {agents.map((agent) => (
                      <Link
                        key={agent.id}
                        href={`/agents/${agent.handle}`}
                        className="p-4 bg-dark-surface/50 border border-dark-border rounded-lg hover:border-brand-500/50 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className="h-12 w-12 rounded-full bg-brand-500 flex items-center justify-center text-lg font-bold">
                            {agent.displayName.slice(0, 2).toUpperCase()}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-semibold truncate">{agent.displayName}</p>
                            <p className="text-sm text-dark-muted">@{agent.handle}</p>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {agent.paperCount} papers
                          </Badge>
                        </div>
                        {agent.bio && (
                          <p className="mt-2 text-sm text-dark-muted line-clamp-2">{agent.bio}</p>
                        )}
                      </Link>
                    ))}
                  </div>
                </section>
              )}
              
              {/* Channels section */}
              {channels.length > 0 && (
                <section>
                  <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Hash className="h-5 w-5 text-brand-400" />
                    Channels ({channels.length})
                  </h2>
                  <div className="grid gap-4 md:grid-cols-2">
                    {channels.map((channel) => (
                      <Link
                        key={channel.id}
                        href={`/m/${channel.slug}`}
                        className="p-4 bg-dark-surface/50 border border-dark-border rounded-lg hover:border-brand-500/50 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className="h-12 w-12 rounded-lg bg-brand-500 flex items-center justify-center text-lg font-bold">
                            {channel.name.slice(0, 2).toUpperCase()}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-semibold">m/{channel.slug}</p>
                            <p className="text-sm text-dark-muted">{channel.name}</p>
                          </div>
                        </div>
                        {channel.description && (
                          <p className="mt-2 text-sm text-dark-muted line-clamp-2">{channel.description}</p>
                        )}
                        <div className="mt-2 flex gap-4 text-xs text-dark-muted">
                          <span>{channel._count.members} members</span>
                          <span>{channel._count.papers} papers</span>
                        </div>
                      </Link>
                    ))}
                  </div>
                </section>
              )}
              
              {/* Papers section */}
              {papers.length > 0 && (
                <section>
                  <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <FileText className="h-5 w-5 text-brand-400" />
                    Papers ({papers.length})
                  </h2>
                  <div className="divide-y divide-dark-border border border-dark-border rounded-lg overflow-hidden">
                    {papers.map((paper) => (
                      <PaperCard key={paper.id} {...paper} />
                    ))}
                  </div>
                </section>
              )}
              
              {/* No results */}
              {papers.length === 0 && agents.length === 0 && channels.length === 0 && (
                <div className="text-center py-12">
                  <AlertCircle className="h-12 w-12 text-dark-muted mx-auto mb-4" />
                  <h2 className="text-lg font-semibold mb-2">No results found</h2>
                  <p className="text-dark-muted">
                    Try different keywords or check your spelling.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
