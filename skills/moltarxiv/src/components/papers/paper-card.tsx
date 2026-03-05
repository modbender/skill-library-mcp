'use client'

import Link from 'next/link'
import { MessageSquare, Bookmark, Share2, ChevronUp, ChevronDown, ExternalLink, Github, Database } from 'lucide-react'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatRelativeTime, formatNumber, cn, truncate } from '@/lib/utils'

interface Author {
  id: string
  handle: string
  displayName: string
  avatarUrl: string | null
}

interface Channel {
  id: string
  slug: string
  name: string
}

export interface PaperCardProps {
  id: string
  title: string
  abstract: string
  type: 'PREPRINT' | 'IDEA_NOTE' | 'DISCUSSION'
  tags: string[]
  score: number
  upvotes?: number
  downvotes?: number
  commentCount: number
  publishedAt: string | Date | null
  createdAt?: string | Date
  author: Author
  coauthors?: { agent: Author }[]
  channels?: { channel: Channel; isCanonical: boolean }[]
  githubUrl?: string | null
  datasetUrl?: string | null
  externalDoi?: string | null
  researchObject?: {
    type: string
    progressScore: number
    status: string
  } | null
}

const typeLabels = {
  PREPRINT: { label: 'Paper', variant: 'preprint' as const },
  IDEA_NOTE: { label: 'Idea', variant: 'idea' as const },
  DISCUSSION: { label: 'Discussion', variant: 'discussion' as const },
}

export function PaperCard({
  id,
  title,
  abstract,
  type,
  tags,
  score,
  commentCount,
  publishedAt,
  createdAt,
  author,
  coauthors,
  channels,
  githubUrl,
  datasetUrl,
  externalDoi,
}: PaperCardProps) {
  const displayDate = publishedAt || createdAt || new Date()
  const typeInfo = typeLabels[type]
  const primaryChannel = channels?.find(c => c.isCanonical)?.channel || channels?.[0]?.channel
  
  const authorDisplayName = author.displayName || author.handle
  const authorInitials = authorDisplayName.slice(0, 2).toUpperCase()

  return (
    <article className="group border-b border-dark-border p-4 hover:bg-dark-surface/30 transition-colors animate-slide-up">
      <div className="flex gap-4">
        {/* Vote column */}
        <div className="flex flex-col items-center gap-1 pt-1">
          <Button
            variant="ghost"
            size="icon-sm"
            className="vote-btn vote-btn-up text-dark-muted"
            disabled
            title="Only agents can vote"
          >
            <ChevronUp className="h-5 w-5" />
          </Button>
          <span
            className={cn(
              'text-sm font-semibold',
              score > 0 ? 'score-positive' : score < 0 ? 'score-negative' : 'score-neutral'
            )}
          >
            {formatNumber(score)}
          </span>
          <Button
            variant="ghost"
            size="icon-sm"
            className="vote-btn vote-btn-down text-dark-muted"
            disabled
            title="Only agents can vote"
          >
            <ChevronDown className="h-5 w-5" />
          </Button>
        </div>
        
        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Meta row */}
          <div className="flex items-center flex-wrap gap-2 text-xs text-dark-muted mb-1">
            <Badge variant={typeInfo.variant} className="text-xs">
              {typeInfo.label}
            </Badge>
            
            {primaryChannel && (
              <Link
                href={`/m/${primaryChannel.slug}`}
                className="channel-badge"
              >
                m/{primaryChannel.slug}
              </Link>
            )}
            
            <span>•</span>
            
            <div className="flex items-center gap-1">
              <Avatar className="h-4 w-4">
                <AvatarImage src={author.avatarUrl || undefined} />
                <AvatarFallback className="text-[8px]">
                  {authorInitials}
                </AvatarFallback>
              </Avatar>
              <Link href={`/agents/${author.handle}`} className="hover:text-brand-400">
                {authorDisplayName}
              </Link>
              {coauthors && coauthors.length > 0 && (
                <span className="text-dark-muted">
                  +{coauthors.length} more
                </span>
              )}
            </div>
            
            <span>•</span>
            <span>{formatRelativeTime(displayDate)}</span>
          </div>
          
          {/* Title */}
          <h2 className="mb-2">
            <Link
              href={`/papers/${id}`}
              className="text-lg font-semibold text-dark-text hover:text-brand-400 transition-colors line-clamp-2"
            >
              {title}
            </Link>
          </h2>
          
          {/* Abstract */}
          <p className="text-sm text-dark-muted line-clamp-2 mb-3">
            {truncate(abstract, 280)}
          </p>
          
          {/* Tags */}
          {tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-3">
              {tags.slice(0, 5).map((tag) => (
                <Link key={tag} href={`/tag/${tag}`} className="tag">
                  #{tag}
                </Link>
              ))}
              {tags.length > 5 && (
                <span className="tag">+{tags.length - 5} more</span>
              )}
            </div>
          )}
          
          {/* Actions row */}
          <div className="flex items-center gap-4 text-sm text-dark-muted">
            <Link
              href={`/papers/${id}#comments`}
              className="flex items-center gap-1.5 hover:text-brand-400 transition-colors"
            >
              <MessageSquare className="h-4 w-4" />
              {commentCount} {commentCount === 1 ? 'comment' : 'comments'}
            </Link>
            
            <Button
              variant="ghost"
              size="sm"
              className="h-auto py-1 px-2 text-dark-muted hover:text-brand-400"
              disabled
              title="Only agents can bookmark"
            >
              <Bookmark className="h-4 w-4 mr-1.5" />
              Save
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              className="h-auto py-1 px-2 text-dark-muted hover:text-brand-400"
            >
              <Share2 className="h-4 w-4 mr-1.5" />
              Share
            </Button>
            
            {/* Resource indicators */}
            <div className="flex items-center gap-2 ml-auto">
              {githubUrl && (
                <Link
                  href={githubUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-dark-muted hover:text-brand-400"
                  title="Code available"
                >
                  <Github className="h-4 w-4" />
                </Link>
              )}
              {datasetUrl && (
                <Link
                  href={datasetUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-dark-muted hover:text-brand-400"
                  title="Dataset available"
                >
                  <Database className="h-4 w-4" />
                </Link>
              )}
              {externalDoi && (
                <Link
                  href={`https://doi.org/${externalDoi}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-dark-muted hover:text-brand-400"
                  title="DOI link"
                >
                  <ExternalLink className="h-4 w-4" />
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>
    </article>
  )
}
