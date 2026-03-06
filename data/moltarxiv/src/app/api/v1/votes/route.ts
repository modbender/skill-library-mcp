import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { requireAgent } from '@/lib/auth'
import { voteSchema } from '@/lib/validation'
import { checkRateLimit } from '@/lib/rate-limit'
import { success, handleError, rateLimitExceeded, notFound } from '@/lib/api-response'

/**
 * POST /api/v1/votes
 * Vote on a paper or comment (agent only)
 */
export async function POST(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    
    // Check rate limit
    const rateCheck = await checkRateLimit(agent.id, 'votes/create')
    if (!rateCheck.allowed) {
      return rateLimitExceeded(rateCheck.resetAt)
    }
    
    const body = await request.json()
    const data = voteSchema.parse(body)
    
    if (data.paperId) {
      return await votePaper(agent.id, data.paperId, data.type)
    } else if (data.commentId) {
      return await voteComment(agent.id, data.commentId, data.type)
    }
    
    return handleError(new Error('Must provide paperId or commentId'))
    
  } catch (err) {
    return handleError(err)
  }
}

export async function votePaper(agentId: string, paperId: string, type: 'UP' | 'DOWN') {
  // Check paper exists
  const paper = await db.paper.findUnique({
    where: { id: paperId },
    select: { id: true, authorId: true, status: true }
  })
  
  if (!paper || paper.status === 'REMOVED') {
    return notFound('Paper')
  }
  
  // Check existing vote
  const existingVote = await db.vote.findUnique({
    where: { agentId_paperId: { agentId, paperId } }
  })
  
  // Calculate karma/score changes
  let scoreDelta = 0
  let authorKarmaDelta = 0
  
  if (existingVote) {
    if (existingVote.type === type) {
      // Same vote = remove vote
      await db.vote.delete({
        where: { id: existingVote.id }
      })
      
      scoreDelta = type === 'UP' ? -1 : 1
      authorKarmaDelta = type === 'UP' ? -1 : 1
      
    } else {
      // Different vote = flip vote
      await db.vote.update({
        where: { id: existingVote.id },
        data: { type }
      })
      
      scoreDelta = type === 'UP' ? 2 : -2
      authorKarmaDelta = type === 'UP' ? 2 : -2
    }
  } else {
    // New vote
    await db.vote.create({
      data: {
        agentId,
        paperId,
        type,
      }
    })
    
    scoreDelta = type === 'UP' ? 1 : -1
    authorKarmaDelta = type === 'UP' ? 1 : -1
  }
  
  // Update paper score
  await db.paper.update({
    where: { id: paperId },
    data: {
      score: { increment: scoreDelta },
      upvotes: { increment: type === 'UP' ? (existingVote?.type === 'UP' ? -1 : existingVote?.type === 'DOWN' ? 1 : 1) : (existingVote?.type === 'DOWN' ? -1 : 0) },
      downvotes: { increment: type === 'DOWN' ? (existingVote?.type === 'DOWN' ? -1 : existingVote?.type === 'UP' ? 1 : 1) : (existingVote?.type === 'UP' ? -1 : 0) },
    }
  })
  
  // Update author karma (if not voting on own paper)
  if (paper.authorId !== agentId) {
    await db.agent.update({
      where: { id: paper.authorId },
      data: { karma: { increment: authorKarmaDelta } }
    })
  }
  
  // Get new vote state
  const newVote = await db.vote.findUnique({
    where: { agentId_paperId: { agentId, paperId } }
  })
  
  const updatedPaper = await db.paper.findUnique({
    where: { id: paperId },
    select: { score: true, upvotes: true, downvotes: true }
  })
  
  return success({
    userVote: newVote?.type || null,
    score: updatedPaper?.score,
    upvotes: updatedPaper?.upvotes,
    downvotes: updatedPaper?.downvotes,
  })
}

export async function voteComment(agentId: string, commentId: string, type: 'UP' | 'DOWN') {
  // Check comment exists
  const comment = await db.comment.findUnique({
    where: { id: commentId },
    select: { id: true, authorId: true, isDeleted: true }
  })
  
  if (!comment || comment.isDeleted) {
    return notFound('Comment')
  }
  
  // Check existing vote
  const existingVote = await db.vote.findUnique({
    where: { agentId_commentId: { agentId, commentId } }
  })
  
  let scoreDelta = 0
  let authorKarmaDelta = 0
  
  if (existingVote) {
    if (existingVote.type === type) {
      // Same vote = remove vote
      await db.vote.delete({
        where: { id: existingVote.id }
      })
      
      scoreDelta = type === 'UP' ? -1 : 1
      authorKarmaDelta = type === 'UP' ? -1 : 1
      
    } else {
      // Different vote = flip vote
      await db.vote.update({
        where: { id: existingVote.id },
        data: { type }
      })
      
      scoreDelta = type === 'UP' ? 2 : -2
      authorKarmaDelta = type === 'UP' ? 2 : -2
    }
  } else {
    // New vote
    await db.vote.create({
      data: {
        agentId,
        commentId,
        type,
      }
    })
    
    scoreDelta = type === 'UP' ? 1 : -1
    authorKarmaDelta = type === 'UP' ? 1 : -1
  }
  
  // Update comment score
  await db.comment.update({
    where: { id: commentId },
    data: {
      score: { increment: scoreDelta },
      upvotes: { increment: type === 'UP' ? (existingVote?.type === 'UP' ? -1 : existingVote?.type === 'DOWN' ? 1 : 1) : (existingVote?.type === 'DOWN' ? -1 : 0) },
      downvotes: { increment: type === 'DOWN' ? (existingVote?.type === 'DOWN' ? -1 : existingVote?.type === 'UP' ? 1 : 1) : (existingVote?.type === 'UP' ? -1 : 0) },
    }
  })
  
  // Update author karma (if not voting on own comment)
  if (comment.authorId !== agentId) {
    await db.agent.update({
      where: { id: comment.authorId },
      data: { karma: { increment: authorKarmaDelta } }
    })
  }
  
  // Get new vote state
  const newVote = await db.vote.findUnique({
    where: { agentId_commentId: { agentId, commentId } }
  })
  
  const updatedComment = await db.comment.findUnique({
    where: { id: commentId },
    select: { score: true, upvotes: true, downvotes: true }
  })
  
  return success({
    userVote: newVote?.type || null,
    score: updatedComment?.score,
    upvotes: updatedComment?.upvotes,
    downvotes: updatedComment?.downvotes,
  })
}

/**
 * DELETE /api/v1/votes
 * Remove a vote (convenience endpoint)
 */
export async function DELETE(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    const { searchParams } = new URL(request.url)
    
    const paperId = searchParams.get('paperId')
    const commentId = searchParams.get('commentId')
    
    if (paperId) {
      const vote = await db.vote.findUnique({
        where: { agentId_paperId: { agentId: agent.id, paperId } }
      })
      
      if (vote) {
        // Use the vote function to handle removal
        return await votePaper(agent.id, paperId, vote.type)
      }
    } else if (commentId) {
      const vote = await db.vote.findUnique({
        where: { agentId_commentId: { agentId: agent.id, commentId } }
      })
      
      if (vote) {
        return await voteComment(agent.id, commentId, vote.type)
      }
    }
    
    return success({ userVote: null })
    
  } catch (err) {
    return handleError(err)
  }
}
