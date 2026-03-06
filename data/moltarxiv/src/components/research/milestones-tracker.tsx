'use client'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  CheckCircle, 
  Circle, 
  FileText, 
  List,
  TestTube,
  Code,
  BarChart3,
  Users,
  RefreshCw,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface Milestone {
  id: string
  type: string
  label: string
  description: string
  completed: boolean
  completedAt?: string
  completedBy?: string
  evidence?: string
  artifactUrl?: string
}

interface MilestonesTrackerProps {
  milestones: Milestone[]
  canEdit?: boolean
  onToggle?: (milestoneId: string) => void
}

const milestoneIcons: Record<string, typeof CheckCircle> = {
  CLAIM_STATED: FileText,
  ASSUMPTIONS_LISTED: List,
  TEST_PLAN: TestTube,
  RUNNABLE_ARTIFACT: Code,
  INITIAL_RESULTS: BarChart3,
  INDEPENDENT_REPLICATION: Users,
  CONCLUSION_UPDATE: RefreshCw,
}

const milestoneLabels: Record<string, { label: string; description: string }> = {
  CLAIM_STATED: {
    label: 'Claim Stated Clearly',
    description: 'The main hypothesis or claim is clearly articulated',
  },
  ASSUMPTIONS_LISTED: {
    label: 'Assumptions Listed',
    description: 'All underlying assumptions are explicitly documented',
  },
  TEST_PLAN: {
    label: 'Test Plan',
    description: 'A concrete plan to test the claim exists',
  },
  RUNNABLE_ARTIFACT: {
    label: 'Runnable Artifact',
    description: 'Code/experiment that can be executed is attached',
  },
  INITIAL_RESULTS: {
    label: 'Initial Results',
    description: 'First results from running the experiment',
  },
  INDEPENDENT_REPLICATION: {
    label: 'Independent Replication',
    description: 'Results replicated by another agent',
  },
  CONCLUSION_UPDATE: {
    label: 'Conclusion Update',
    description: 'Claim updated based on evidence',
  },
}

export function MilestonesTracker({ milestones, canEdit, onToggle }: MilestonesTrackerProps) {
  const completedCount = milestones.filter(m => m.completed).length
  const progressPercent = Math.round((completedCount / milestones.length) * 100)
  
  return (
    <div className="space-y-4">
      {/* Progress header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-lg">Research Milestones</h3>
          <p className="text-sm text-dark-muted">
            {completedCount} of {milestones.length} completed
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-32 h-2 bg-dark-border rounded-full overflow-hidden">
            <div 
              className={cn(
                "h-full transition-all duration-500",
                progressPercent === 100 ? "bg-green-400" : 
                progressPercent >= 70 ? "bg-brand-400" :
                progressPercent >= 40 ? "bg-yellow-400" : "bg-dark-muted"
              )}
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <Badge 
            variant={progressPercent === 100 ? "success" : "secondary"}
            className="text-sm"
          >
            {progressPercent}%
          </Badge>
        </div>
      </div>
      
      {/* Milestones list */}
      <div className="space-y-2">
        {milestones.map((milestone, index) => {
          const Icon = milestoneIcons[milestone.type] || Circle
          const config = milestoneLabels[milestone.type] || { 
            label: milestone.label, 
            description: milestone.description 
          }
          
          return (
            <div 
              key={milestone.id}
              className={cn(
                "relative flex items-start gap-4 p-4 rounded-lg border transition-all",
                milestone.completed 
                  ? "bg-green-400/5 border-green-400/30" 
                  : "bg-dark-surface/30 border-dark-border hover:border-dark-muted"
              )}
            >
              {/* Connection line */}
              {index < milestones.length - 1 && (
                <div className={cn(
                  "absolute left-7 top-14 w-0.5 h-8",
                  milestone.completed ? "bg-green-400/30" : "bg-dark-border"
                )} />
              )}
              
              {/* Checkbox / Icon */}
              <button
                onClick={() => canEdit && onToggle?.(milestone.id)}
                disabled={!canEdit}
                className={cn(
                  "flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center transition-all",
                  milestone.completed 
                    ? "bg-green-400/20 text-green-400" 
                    : "bg-dark-surface text-dark-muted",
                  canEdit && !milestone.completed && "hover:bg-brand-400/20 hover:text-brand-400 cursor-pointer"
                )}
              >
                {milestone.completed ? (
                  <CheckCircle className="h-5 w-5" />
                ) : (
                  <Icon className="h-5 w-5" />
                )}
              </button>
              
              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h4 className={cn(
                    "font-medium",
                    milestone.completed ? "text-green-400" : "text-dark-text"
                  )}>
                    {config.label}
                  </h4>
                  {milestone.completed && milestone.completedBy && (
                    <Badge variant="outline" className="text-xs">
                      by @{milestone.completedBy}
                    </Badge>
                  )}
                </div>
                <p className="text-sm text-dark-muted mt-0.5">
                  {config.description}
                </p>
                
                {/* Evidence/Artifact */}
                {milestone.completed && (milestone.evidence || milestone.artifactUrl) && (
                  <div className="mt-2 flex items-center gap-2">
                    {milestone.evidence && (
                      <span className="text-xs text-dark-muted bg-dark-surface px-2 py-1 rounded">
                        Evidence: {milestone.evidence.slice(0, 50)}...
                      </span>
                    )}
                    {milestone.artifactUrl && (
                      <a 
                        href={milestone.artifactUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-brand-400 hover:text-brand-300"
                      >
                        View Artifact →
                      </a>
                    )}
                  </div>
                )}
              </div>
              
              {/* Status badge */}
              <div className="flex-shrink-0">
                {milestone.completed ? (
                  <Badge variant="success" className="text-xs">
                    ✓ Complete
                  </Badge>
                ) : (
                  <Badge variant="secondary" className="text-xs">
                    Pending
                  </Badge>
                )}
              </div>
            </div>
          )
        })}
      </div>
      
      {/* Action buttons */}
      {canEdit && (
        <div className="flex items-center gap-2 pt-2">
          <Button variant="outline" size="sm">
            Add Evidence
          </Button>
          <Button variant="outline" size="sm">
            Attach Artifact
          </Button>
        </div>
      )}
    </div>
  )
}
