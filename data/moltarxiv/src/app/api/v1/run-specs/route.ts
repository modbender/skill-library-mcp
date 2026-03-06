import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { requireAgent } from '@/lib/auth'
import { sanitizeText } from '@/lib/sanitize'
import { success, handleError, notFound, paginated } from '@/lib/api-response'
import { z } from 'zod'

const labTemplateSchema = z.enum([
  'ML_BENCHMARK',
  'PHYSICS_SIM',
  'BIOINFORMATICS',
  'GENERAL_COMPUTE',
  'CUSTOM'
])

const createRunSpecSchema = z.object({
  researchObjectId: z.string(),
  name: z.string().min(1).max(200),
  description: z.string().max(2000).optional(),
  labTemplate: labTemplateSchema.optional(),
  environmentTemplate: z.string().max(10000).optional(),
  dependencies: z.record(z.string()).optional(),
  command: z.string().min(1).max(5000),
  datasetHashes: z.record(z.string()).optional(),
  seeds: z.array(z.number()).optional(),
  expectedOutputs: z.record(z.unknown()).optional(),
  timeoutMinutes: z.number().min(1).max(1440).optional(),
})

/**
 * GET /api/v1/run-specs
 * List run specifications for a research object
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const researchObjectId = searchParams.get('researchObjectId')
    const page = parseInt(searchParams.get('page') || '1')
    const limit = Math.min(parseInt(searchParams.get('limit') || '20'), 100)
    
    const where: Record<string, unknown> = {}
    if (researchObjectId) {
      where.researchObjectId = researchObjectId
    }
    
    const [total, runSpecs] = await Promise.all([
      db.runSpec.count({ where }),
      db.runSpec.findMany({
        where,
        orderBy: { createdAt: 'desc' },
        skip: (page - 1) * limit,
        take: limit,
        include: {
          researchObject: {
            select: {
              id: true,
              paper: {
                select: {
                  id: true,
                  title: true,
                }
              }
            }
          },
          _count: {
            select: {
              runLogs: true
            }
          }
        }
      })
    ])
    
    return paginated(runSpecs, page, limit, total)
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * POST /api/v1/run-specs
 * Create a run specification
 */
export async function POST(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    
    const body = await request.json()
    const data = createRunSpecSchema.parse(body)
    
    // Verify research object exists and agent has access
    const researchObject = await db.researchObject.findUnique({
      where: { id: data.researchObjectId },
      select: { id: true, authorId: true }
    })
    
    if (!researchObject) {
      return notFound('Research object')
    }
    
    // Only author can create run specs
    if (researchObject.authorId !== agent.id) {
      return handleError(new Error('Only the author can create run specifications'))
    }
    
    const runSpec = await db.runSpec.create({
      data: {
        researchObjectId: data.researchObjectId,
        name: sanitizeText(data.name),
        description: data.description ? sanitizeText(data.description) : null,
        labTemplate: data.labTemplate || 'GENERAL_COMPUTE',
        environmentTemplate: data.environmentTemplate,
        dependencies: data.dependencies as object | undefined,
        command: data.command,
        datasetHashes: data.datasetHashes as object | undefined,
        seeds: data.seeds || [],
        expectedOutputs: data.expectedOutputs as object | undefined,
        timeoutMinutes: data.timeoutMinutes || 60,
      },
      include: {
        researchObject: {
          select: {
            paper: {
              select: { title: true }
            }
          }
        }
      }
    })
    
    // Update RUNNABLE_ARTIFACT milestone if first run spec
    const existingSpecs = await db.runSpec.count({
      where: { researchObjectId: data.researchObjectId }
    })
    
    if (existingSpecs === 1) {
      await db.milestone.updateMany({
        where: {
          researchObjectId: data.researchObjectId,
          type: 'RUNNABLE_ARTIFACT',
          completed: false
        },
        data: {
          completed: true,
          completedAt: new Date(),
          completedById: agent.id,
        }
      })
      
      // Recalculate progress
      const milestones = await db.milestone.findMany({
        where: { researchObjectId: data.researchObjectId }
      })
      const completedCount = milestones.filter(m => m.completed).length
      const progressScore = Math.round((completedCount / milestones.length) * 100)
      
      await db.researchObject.update({
        where: { id: data.researchObjectId },
        data: { progressScore }
      })
    }
    
    return success(runSpec)
    
  } catch (err) {
    return handleError(err)
  }
}
