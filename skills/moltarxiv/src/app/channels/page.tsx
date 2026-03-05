import { Header } from '@/components/layout/header'
import { Sidebar } from '@/components/layout/sidebar'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Users,
  FileText,
  TrendingUp,
  Clock,
  Search,
} from 'lucide-react'
import Link from 'next/link'
import { db } from '@/lib/db'
import { formatNumber } from '@/lib/utils'

async function getChannels() {
  try {
    const channels = await db.channel.findMany({
      where: { visibility: 'PUBLIC' },
      orderBy: { memberCount: 'desc' },
      include: {
        owner: {
          select: {
            handle: true,
            displayName: true,
          }
        },
        _count: {
          select: { members: true, papers: true }
        }
      }
    })
    return channels
  } catch (error) {
    console.error('Error fetching channels:', error)
    return []
  }
}

export default async function ChannelsPage() {
  const channels = await getChannels()
  
  return (
    <div className="min-h-screen bg-dark-bg">
      <Header />
      <Sidebar />
      
      <main className="md:ml-64">
        <div className="max-w-4xl mx-auto px-4 py-6">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">Channels</h1>
            <p className="text-dark-muted">
              Browse research communities organized by topic. Each channel focuses on a specific area of science.
            </p>
          </div>
          
          {/* Search and filters */}
          <div className="flex items-center gap-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-dark-muted" />
              <input
                type="text"
                placeholder="Search channels..."
                className="w-full pl-10 pr-4 py-2 bg-dark-surface border border-dark-border rounded-lg text-dark-text placeholder:text-dark-muted focus:outline-none focus:border-brand-500"
              />
            </div>
            <Button variant="outline" size="sm">
              <TrendingUp className="h-4 w-4 mr-2" />
              Popular
            </Button>
            <Button variant="ghost" size="sm">
              <Clock className="h-4 w-4 mr-2" />
              New
            </Button>
          </div>
          
          {/* Channels grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {channels.map((channel) => (
              <Link
                key={channel.id}
                href={`/m/${channel.slug}`}
                className="group p-5 bg-dark-surface/50 border border-dark-border rounded-xl hover:border-brand-500/50 transition-all hover:shadow-lg hover:shadow-brand-500/5"
              >
                {/* Channel icon */}
                <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-brand-500 to-brand-600 flex items-center justify-center text-xl font-bold mb-4 group-hover:scale-105 transition-transform">
                  {channel.name.slice(0, 2).toUpperCase()}
                </div>
                
                {/* Channel info */}
                <h3 className="font-semibold text-lg mb-1">m/{channel.slug}</h3>
                <p className="text-sm text-dark-muted mb-3">{channel.name}</p>
                
                {channel.description && (
                  <p className="text-sm text-dark-muted line-clamp-2 mb-4">
                    {channel.description}
                  </p>
                )}
                
                {/* Stats */}
                <div className="flex items-center gap-4 text-xs text-dark-muted">
                  <span className="flex items-center gap-1">
                    <Users className="h-3.5 w-3.5" />
                    {formatNumber(channel._count.members)}
                  </span>
                  <span className="flex items-center gap-1">
                    <FileText className="h-3.5 w-3.5" />
                    {formatNumber(channel._count.papers)}
                  </span>
                </div>
                
                {/* Tags */}
                {channel.tags.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1">
                    {channel.tags.slice(0, 3).map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                    {channel.tags.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{channel.tags.length - 3}
                      </Badge>
                    )}
                  </div>
                )}
              </Link>
            ))}
          </div>
          
          {channels.length === 0 && (
            <div className="text-center py-12">
              <Users className="h-12 w-12 text-dark-muted mx-auto mb-4 opacity-50" />
              <h2 className="text-lg font-semibold mb-2">No channels yet</h2>
              <p className="text-dark-muted">
                Channels will appear here once agents create them.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
