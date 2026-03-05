import { Header } from '@/components/layout/header'
import { Sidebar } from '@/components/layout/sidebar'
import { RightSidebar } from '@/components/layout/right-sidebar'
import { PaperCard } from '@/components/papers/paper-card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { DataAlert } from '@/components/ui/data-alert'
import { 
  TrendingUp, 
  Beaker,
  CheckCircle,
  XCircle,
  BarChart3,
  Target,
  AlertCircle,
  Lightbulb,
} from 'lucide-react'
import Link from 'next/link'
import { db } from '@/lib/db'

// Cache briefly to avoid long loaders on navigation
export const revalidate = 60

const feedTabs = [
  { value: 'progress', label: 'By Progress', icon: TrendingUp, href: '/' },
  { value: 'ideas', label: 'Ideas', icon: Target, href: '/feed/ideas', active: true },
  { value: 'in-progress', label: 'In Progress', icon: Beaker, href: '/feed/in-progress' },
  { value: 'replicated', label: 'Replicated', icon: CheckCircle, href: '/feed/replicated' },
  { value: 'negative', label: 'Negative Results', icon: XCircle, href: '/feed/negative' },
  { value: 'benchmarks', label: 'Benchmarks', icon: BarChart3, href: '/feed/benchmarks' },
]

async function getPapers() {
  try {
    const papers = await db.paper.findMany({
      where: { 
        status: 'PUBLISHED',
        OR: [
          { type: 'IDEA_NOTE' },
          { researchObject: { type: 'HYPOTHESIS' } }
        ]
      },
      orderBy: { publishedAt: 'desc' },
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
    console.error('Error fetching papers:', error)
    return null
  }
}

export default async function IdeasFeedPage() {
  const papers = await getPapers()
  const dataError = !papers
  const safePapers = papers ?? []
  
  return (
    <div className="min-h-screen bg-dark-bg">
      <Header />
      <Sidebar />
      <RightSidebar />
      
      <main className="md:ml-64 lg:mr-80">
        <div className="max-w-3xl mx-auto">
          <div className="border-b border-dark-border p-6 bg-gradient-to-b from-yellow-500/5 to-transparent">
            <div className="flex items-center gap-3 mb-2">
              <Lightbulb className="h-8 w-8 text-yellow-400" />
              <h1 className="text-2xl font-bold">Ideas & Hypotheses</h1>
            </div>
            <p className="text-dark-muted">New research ideas and testable hypotheses awaiting validation</p>
            <div className="mt-4 flex gap-2">
              <Badge variant="outline" className="text-yellow-400 border-yellow-400/30">Early Stage</Badge>
              <Badge variant="outline">Needs Testing</Badge>
            </div>
          </div>
          
          <div className="sticky top-16 z-40 bg-dark-bg/90 backdrop-blur-sm border-b border-dark-border">
            <div className="p-4">
              <div className="flex items-center gap-1 overflow-x-auto pb-2 -mx-4 px-4">
                {feedTabs.map((tab) => {
                  const Icon = tab.icon
                  const isActive = tab.active
                  return (
                    <Link key={tab.value} href={tab.href}>
                      <Button 
                        variant={isActive ? 'secondary' : 'ghost'} 
                        size="sm" 
                        className={isActive ? 'text-brand-400' : 'text-dark-muted'}
                      >
                        <Icon className="h-4 w-4 mr-1.5" />
                        {tab.label}
                      </Button>
                    </Link>
                  )
                })}
              </div>
            </div>
          </div>
          
          <div className="divide-y divide-dark-border">
            {dataError ? (
              <div className="p-6">
                <DataAlert />
              </div>
            ) : safePapers.length === 0 ? (
              <div className="p-12 text-center">
                <AlertCircle className="h-12 w-12 text-dark-muted mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No ideas yet</h3>
                <p className="text-dark-muted">Be the first to propose a hypothesis!</p>
              </div>
            ) : (
              safePapers.map((paper) => (
                <div key={paper.id} className="relative">
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-yellow-400/50 rounded-l" />
                  <div className="pl-2">
                    <PaperCard {...paper} />
                  </div>
                </div>
              ))
            )}
          </div>
          
          {safePapers.length > 0 && (
            <div className="p-6 flex justify-center">
              <Button variant="outline">Load more ideas</Button>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
