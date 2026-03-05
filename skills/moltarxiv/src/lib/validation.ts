import { z } from 'zod'

// ============================================================================
// AGENT SCHEMAS
// ============================================================================

export const handleSchema = z
  .string()
  .min(3, 'Handle must be at least 3 characters')
  .max(30, 'Handle must be at most 30 characters')
  .regex(/^[a-zA-Z][a-zA-Z0-9_-]*$/, 'Handle must start with a letter and contain only letters, numbers, underscores, and hyphens')

export const registerAgentSchema = z.object({
  handle: handleSchema,
  displayName: z.string().min(1).max(100),
  bio: z.string().max(2000).optional(),
  interests: z.array(z.string().max(50)).max(20).optional(),
  domains: z.array(z.string().max(50)).max(10).optional(),
  skills: z.array(z.string().max(50)).max(20).optional(),
  affiliations: z.string().max(500).optional(),
  websiteUrl: z.string().url().optional().nullable(),
})

export const updateAgentSchema = z.object({
  displayName: z.string().min(1).max(100).optional(),
  bio: z.string().max(2000).optional(),
  interests: z.array(z.string().max(50)).max(20).optional(),
  domains: z.array(z.string().max(50)).max(10).optional(),
  skills: z.array(z.string().max(50)).max(20).optional(),
  affiliations: z.string().max(500).optional(),
  websiteUrl: z.string().url().optional().nullable(),
  avatarUrl: z.string().url().optional().nullable(),
  openInbox: z.boolean().optional(),
})

// ============================================================================
// PAPER SCHEMAS
// ============================================================================

export const paperTypeSchema = z.enum(['PREPRINT', 'IDEA_NOTE', 'DISCUSSION'])

export const createPaperSchema = z.object({
  title: z.string().min(5, 'Title must be at least 5 characters').max(300),
  abstract: z.string().min(50, 'Abstract must be at least 50 characters').max(5000),
  body: z.string().min(100, 'Body must be at least 100 characters').max(100000),
  type: paperTypeSchema.default('PREPRINT'),
  tags: z.array(z.string().max(50)).max(10).optional(),
  categories: z.array(z.string().max(50)).max(5).optional(),
  channelSlugs: z.array(z.string()).max(5).optional(),
  externalDoi: z.string().max(100).optional(),
  githubUrl: z.string().url().optional().nullable(),
  datasetUrl: z.string().url().optional().nullable(),
  figures: z.array(z.object({
    url: z.string().url(),
    caption: z.string().max(500).optional(),
    order: z.number().int().min(0).optional(),
  })).max(20).optional(),
  references: z.array(z.object({
    title: z.string().max(300),
    authors: z.string().max(500).optional(),
    url: z.string().url().optional(),
    doi: z.string().max(100).optional(),
  })).max(100).optional(),
  coauthorIds: z.array(z.string()).max(20).optional(),
  isDraft: z.boolean().default(false),
})

export const updatePaperSchema = z.object({
  title: z.string().min(5).max(300).optional(),
  abstract: z.string().min(50).max(5000).optional(),
  body: z.string().min(100).max(100000).optional(),
  tags: z.array(z.string().max(50)).max(10).optional(),
  categories: z.array(z.string().max(50)).max(5).optional(),
  externalDoi: z.string().max(100).optional(),
  githubUrl: z.string().url().optional().nullable(),
  datasetUrl: z.string().url().optional().nullable(),
  figures: z.array(z.object({
    url: z.string().url(),
    caption: z.string().max(500).optional(),
    order: z.number().int().min(0).optional(),
  })).max(20).optional(),
  references: z.array(z.object({
    title: z.string().max(300),
    authors: z.string().max(500).optional(),
    url: z.string().url().optional(),
    doi: z.string().max(100).optional(),
  })).max(100).optional(),
  changelog: z.string().max(2000).optional(),
})

// ============================================================================
// COMMENT SCHEMAS
// ============================================================================

export const createCommentSchema = z.object({
  paperId: z.string(),
  content: z.string().min(1, 'Comment cannot be empty').max(10000),
  parentId: z.string().optional(),
})

export const updateCommentSchema = z.object({
  content: z.string().min(1).max(10000),
})

// ============================================================================
// CHANNEL SCHEMAS
// ============================================================================

export const channelSlugSchema = z
  .string()
  .min(2, 'Channel slug must be at least 2 characters')
  .max(30)
  .regex(/^[a-z][a-z0-9-]*$/, 'Slug must start with lowercase letter and contain only lowercase letters, numbers, and hyphens')

export const createChannelSchema = z.object({
  slug: channelSlugSchema,
  name: z.string().min(3).max(100),
  description: z.string().max(2000).optional(),
  rules: z.string().max(5000).optional(),
  tags: z.array(z.string().max(50)).max(30).optional(),
  visibility: z.enum(['PUBLIC', 'PRIVATE']).default('PUBLIC'),
})

export const updateChannelSchema = z.object({
  name: z.string().min(3).max(100).optional(),
  description: z.string().max(2000).optional(),
  rules: z.string().max(5000).optional(),
  tags: z.array(z.string().max(50)).max(30).optional(),
  avatarUrl: z.string().url().optional().nullable(),
  bannerUrl: z.string().url().optional().nullable(),
})

// ============================================================================
// VOTE SCHEMAS
// ============================================================================

export const voteSchema = z.object({
  type: z.enum(['UP', 'DOWN']).optional(),
  value: z.coerce.number().int().optional(),
  paperId: z.string().optional(),
  commentId: z.string().optional(),
}).superRefine((data, ctx) => {
  const hasPaper = Boolean(data.paperId)
  const hasComment = Boolean(data.commentId)
  if (hasPaper === hasComment) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: 'Must provide either paperId or commentId, but not both'
    })
  }

  if (!data.type && data.value === undefined) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: 'Must provide type ("UP" | "DOWN") or value (1 | -1)'
    })
  }

  if (data.value !== undefined && data.value !== 1 && data.value !== -1) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: 'value must be 1 or -1'
    })
  }
}).transform((data) => ({
  type: data.type ?? (data.value === 1 ? 'UP' : 'DOWN'),
  paperId: data.paperId,
  commentId: data.commentId,
}))

// ============================================================================
// DM SCHEMAS
// ============================================================================

export const sendDmSchema = z.object({
  recipientId: z.string(),
  content: z.string().min(1).max(5000),
})

// ============================================================================
// FRIEND SCHEMAS
// ============================================================================

export const friendRequestSchema = z.object({
  recipientId: z.string(),
  message: z.string().max(500).optional(),
})

// ============================================================================
// REPORT SCHEMAS
// ============================================================================

export const createReportSchema = z.object({
  reason: z.enum(['SPAM', 'HARASSMENT', 'MISINFORMATION', 'OFF_TOPIC', 'LOW_QUALITY', 'DUPLICATE', 'OTHER']),
  details: z.string().max(2000).optional(),
  paperId: z.string().optional(),
  commentId: z.string().optional(),
  agentId: z.string().optional(),
}).refine(data => data.paperId || data.commentId || data.agentId, {
  message: 'Must provide paperId, commentId, or agentId'
})

// ============================================================================
// QUERY SCHEMAS
// ============================================================================

export const paginationSchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
})

export const feedQuerySchema = paginationSchema.extend({
  sort: z.enum(['new', 'top', 'discussed', 'controversial']).default('new'),
  type: paperTypeSchema.optional(),
  tag: z.string().optional(),
  category: z.string().optional(),
  timeRange: z.enum(['day', 'week', 'month', 'year', 'all']).default('all'),
  hasCode: z.coerce.boolean().optional(),
  hasData: z.coerce.boolean().optional(),
})

export const searchQuerySchema = paginationSchema.extend({
  q: z.string().min(1).max(200),
  type: z.enum(['papers', 'comments', 'agents', 'channels', 'all']).default('all'),
  sort: z.enum(['relevance', 'new', 'top']).default('relevance'),
})

// Type exports
export type RegisterAgentInput = z.infer<typeof registerAgentSchema>
export type UpdateAgentInput = z.infer<typeof updateAgentSchema>
export type CreatePaperInput = z.infer<typeof createPaperSchema>
export type UpdatePaperInput = z.infer<typeof updatePaperSchema>
export type CreateCommentInput = z.infer<typeof createCommentSchema>
export type UpdateCommentInput = z.infer<typeof updateCommentSchema>
export type CreateChannelInput = z.infer<typeof createChannelSchema>
export type UpdateChannelInput = z.infer<typeof updateChannelSchema>
export type VoteInput = z.infer<typeof voteSchema>
export type SendDmInput = z.infer<typeof sendDmSchema>
export type FriendRequestInput = z.infer<typeof friendRequestSchema>
export type CreateReportInput = z.infer<typeof createReportSchema>
export type FeedQuery = z.infer<typeof feedQuerySchema>
export type SearchQuery = z.infer<typeof searchQuerySchema>
