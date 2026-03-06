import { Header } from '@/components/layout/header'
import { Sidebar } from '@/components/layout/sidebar'
import { RightSidebar } from '@/components/layout/right-sidebar'
import { PaperCard } from '@/components/papers/paper-card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Hash,
  TrendingUp,
  Clock,
  AlertCircle,
} from 'lucide-react'
import Link from 'next/link'
import { db } from '@/lib/db'

async function getTagPapers(tag: string) {
  try {
    const papers = await db.paper.findMany({
      where: { 
        status: 'PUBLISHED',
        tags: { has: tag.toLowerCase() }
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
    console.error('Error fetching tag papers:', error)
    return []
  }
}

async function getRelatedTags(tag: string) {
  try {
    // Get papers with this tag and collect their other tags
    const papers = await db.paper.findMany({
      where: { 
        status: 'PUBLISHED',
        tags: { has: tag.toLowerCase() }
      },
      select: { tags: true },
      take: 50,
    })
    
    const tagCounts: Record<string, number> = {}
    papers.forEach(paper => {
      paper.tags.forEach(t => {
        if (t !== tag.toLowerCase()) {
          tagCounts[t] = (tagCounts[t] || 0) + 1
        }
      })
    })
    
    return Object.entries(tagCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([t]) => t)
  } catch (error) {
    console.error('Error fetching related tags:', error)
    return []
  }
}

export default async function TagPage({ params }: { params: Promise<{ tag: string }> }) {
  const { tag } = await params
  const decodedTag = decodeURIComponent(tag)
  
  const [papers, relatedTags] = await Promise.all([
    getTagPapers(decodedTag),
    getRelatedTags(decodedTag),
  ])
  
  return (
    <div className="min-h-screen bg-dark-bg">
      <Header />
      <Sidebar />
      <RightSidebar />
      
      <main className="md:ml-64 lg:mr-80">
        <div className="max-w-3xl mx-auto">
          {/* Tag header */}
          <div className="border-b border-dark-border p-6">
            <div className="flex items-center gap-3 mb-2">
              <Hash className="h-8 w-8 text-brand-400" />
              <h1 className="text-2xl font-bold">#{decodedTag}</h1>
            </div>
            <p className="text-dark-muted">
              {papers.length} paper{papers.length !== 1 ? 's' : ''} tagged with #{decodedTag}
            </p>
            
            {/* Related tags */}
            {relatedTags.length > 0 && (
              <div className="mt-4">
                <p className="text-sm text-dark-muted mb-2">Related tags:</p>
                <div className="flex flex-wrap gap-2">
                  {relatedTags.map((t) => (
                    <Link key={t} href={`/tag/${t}`} className="tag">
                      #{t}
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          {/* Sort controls */}
          <div className="sticky top-16 z-40 bg-dark-bg/90 backdrop-blur-sm border-b border-dark-border">
            <div className="flex items-center gap-2 p-4">
              <Button variant="secondary" size="sm" className="text-brand-400">
                <TrendingUp className="h-4 w-4 mr-1.5" />
                Top
              </Button>
              <Button variant="ghost" size="sm" className="text-dark-muted">
                <Clock className="h-4 w-4 mr-1.5" />
                New
              </Button>
            </div>
          </div>
          
          {/* Papers */}
          <div className="divide-y divide-dark-border">
            {papers.length === 0 ? (
              <div className="p-12 text-center">
                <AlertCircle className="h-12 w-12 text-dark-muted mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No papers with this tag</h3>
                <p className="text-dark-muted">
                  Be the first to publish research tagged with #{decodedTag}
                </p>
              </div>
            ) : (
              papers.map((paper) => (
                <PaperCard key={paper.id} {...paper} />
              ))
            )}
          </div>
          
          {papers.length > 0 && (
            <div className="p-6 flex justify-center">
              <Button variant="outline">Load more</Button>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
