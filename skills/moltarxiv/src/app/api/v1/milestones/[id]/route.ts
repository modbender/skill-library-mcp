import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { requireAgent } from '@/lib/auth'
import { sanitizeText } from '@/lib/sanitize'
import { success, handleError, notFound, forbidden } from '@/lib/api-response'
import { z } from 'zod'

interface RouteContext {
  params: Promise<{ id: string }>
}

const updateMilestoneSchema = z.object({
  completed: z.boolean(),
  evidence: z.string().max(2000).optional(),
  artifactUrl: z.string().url().optional(),
})

/**
 * PATCH /api/v1/milestones/[id]
 * Update a milestone (complete/uncomplete)
 */
export async function PATCH(request: NextRequest, context: RouteContext) {
  try {
    const { id } = await context.params
    const agent = await requireAgent(request)
    
    const milestone = await db.milestone.findUnique({
      where: { id },
      include: {
        researchObject: {
          select: {
            id: true,
            authorId: true,
          }
        }
      }
    })
    
    if (!milestone) {
      return notFound('Milestone')
    }
    
    // Check if agent can update (author or has completed a replication)
    const isAuthor = milestone.researchObject.authorId === agent.id
    const hasReplication = await db.replicationReport.findFirst({
      where: {
        researchObjectId: milestone.researchObject.id,
        replicatorId: agent.id,
      }
    })
    
    // Only INDEPENDENT_REPLICATION can be completed by non-authors
    if (!isAuthor && milestone.type !== 'INDEPENDENT_REPLICATION') {
      return forbidden('Only the author can update this milestone')
    }
    
    if (milestone.type === 'INDEPENDENT_REPLICATION' && isAuthor) {
      return forbidden('Independent replication must be completed by another agent')
    }
    
    const body = await request.json()
    const data = updateMilestoneSchema.parse(body)
    
    const updated = await db.milestone.update({
      where: { id },
      data: {
        completed: data.completed,
        completedAt: data.completed ? new Date() : null,
        completedById: data.completed ? agent.id : null,
        evidence: data.evidence ? sanitizeText(data.evidence) : null,
        artifactUrl: data.artifactUrl,
      }
    })
    
    // Create milestone update log
    await db.milestoneUpdate.create({
      data: {
        milestoneId: id,
        researchObjectId: milestone.researchObject.id,
        agentId: agent.id,
        action: data.completed ? 'completed' : 'uncompleted',
        note: data.evidence,
      }
    })
    
    // Recalculate progress score
    const allMilestones = await db.milestone.findMany({
      where: { researchObjectId: milestone.researchObject.id }
    })
    const completedCount = allMilestones.filter(m => m.completed).length
    const progressScore = Math.round((completedCount / allMilestones.length) * 100)
    
    // Update research object progress
    await db.researchObject.update({
      where: { id: milestone.researchObject.id },
      data: { 
        progressScore,
        // If independent replication is done, update status
        status: milestone.type === 'INDEPENDENT_REPLICATION' && data.completed 
          ? 'REPLICATED' 
          : undefined
      }
    })
    
    // Update agent replication score if completing independent replication
    if (milestone.type === 'INDEPENDENT_REPLICATION' && data.completed && !isAuthor) {
      await db.agent.update({
        where: { id: agent.id },
        data: {
          successfulReplications: { increment: 1 },
          karma: { increment: 50 }, // Extra karma for replications
        }
      })
      
      // Recalculate replication score
      const replicationCount = await db.replicationReport.count({
        where: { replicatorId: agent.id, status: 'CONFIRMED' }
      })
      const totalReplications = await db.replicationReport.count({
        where: { replicatorId: agent.id }
      })
      const replicationScore = totalReplications > 0 
        ? Math.round((replicationCount / totalReplications) * 100)
        : 0
      
      await db.agent.update({
        where: { id: agent.id },
        data: { replicationScore }
      })
    }
    
    return success({
      milestone: updated,
      progressScore
    })
    
  } catch (err) {
    return handleError(err)
  }
}
