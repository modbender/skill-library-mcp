'use client'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  FileText, 
  Target,
  Beaker,
  TrendingUp,
  XCircle,
  HelpCircle,
  BarChart3,
} from 'lucide-react'
import { formatRelativeTime } from '@/lib/utils'

interface ClaimCardProps {
  claim: string
  evidenceLevel: 'preliminary' | 'reproduced' | 'established' | 'contested' | 'refuted'
  confidence: number // 0-100
  falsifiableBy: string
  mechanism?: string
  prediction?: string
  lastUpdated: string
  version: number
  progressScore: number
  researchType: string
}

const evidenceLevelConfig = {
  preliminary: { 
    icon: HelpCircle, 
    color: 'text-yellow-400', 
    bgColor: 'bg-yellow-400/10',
    borderColor: 'border-yellow-400/30',
    label: 'Preliminary'
  },
  reproduced: { 
    icon: CheckCircle, 
    color: 'text-green-400', 
    bgColor: 'bg-green-400/10',
    borderColor: 'border-green-400/30',
    label: 'Reproduced'
  },
  established: { 
    icon: CheckCircle, 
    color: 'text-blue-400', 
    bgColor: 'bg-blue-400/10',
    borderColor: 'border-blue-400/30',
    label: 'Established'
  },
  contested: { 
    icon: AlertTriangle, 
    color: 'text-orange-400', 
    bgColor: 'bg-orange-400/10',
    borderColor: 'border-orange-400/30',
    label: 'Contested'
  },
  refuted: { 
    icon: XCircle, 
    color: 'text-red-400', 
    bgColor: 'bg-red-400/10',
    borderColor: 'border-red-400/30',
    label: 'Refuted'
  },
}

const researchTypeConfig: Record<string, { icon: typeof Beaker; color: string; label: string }> = {
  HYPOTHESIS: { icon: Target, color: 'text-purple-400', label: 'Hypothesis' },
  LITERATURE_SYNTHESIS: { icon: FileText, color: 'text-blue-400', label: 'Literature Synthesis' },
  EXPERIMENT_PLAN: { icon: Beaker, color: 'text-cyan-400', label: 'Experiment Plan' },
  RESULT: { icon: BarChart3, color: 'text-green-400', label: 'Result' },
  REPLICATION_REPORT: { icon: CheckCircle, color: 'text-teal-400', label: 'Replication Report' },
  BENCHMARK: { icon: TrendingUp, color: 'text-orange-400', label: 'Benchmark' },
  NEGATIVE_RESULT: { icon: XCircle, color: 'text-red-400', label: 'Negative Result' },
}

export function ClaimCard({
  claim,
  evidenceLevel,
  confidence,
  falsifiableBy,
  mechanism,
  prediction,
  lastUpdated,
  version,
  progressScore,
  researchType,
}: ClaimCardProps) {
  const evidence = evidenceLevelConfig[evidenceLevel]
  const EvidenceIcon = evidence.icon
  const typeConfig = researchTypeConfig[researchType] || researchTypeConfig.HYPOTHESIS
  const TypeIcon = typeConfig.icon
  
  return (
    <Card className={`${evidence.bgColor} ${evidence.borderColor} border-2`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TypeIcon className={`h-5 w-5 ${typeConfig.color}`} />
            <span className={`text-sm font-medium ${typeConfig.color}`}>
              {typeConfig.label}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className={`${evidence.color} ${evidence.borderColor}`}>
              <EvidenceIcon className="h-3 w-3 mr-1" />
              {evidence.label}
            </Badge>
            <Badge variant="secondary" className="text-xs">
              v{version}
            </Badge>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Main Claim */}
        <div>
          <h3 className="font-semibold text-lg text-dark-text mb-1">Claim</h3>
          <p className="text-dark-text/90">{claim}</p>
        </div>
        
        {/* Confidence & Progress */}
        <div className="flex items-center gap-6">
          <div>
            <span className="text-xs text-dark-muted uppercase tracking-wide">Confidence</span>
            <div className="flex items-center gap-2 mt-1">
              <div className="w-24 h-2 bg-dark-border rounded-full overflow-hidden">
                <div 
                  className={`h-full ${confidence > 70 ? 'bg-green-400' : confidence > 40 ? 'bg-yellow-400' : 'bg-red-400'}`}
                  style={{ width: `${confidence}%` }}
                />
              </div>
              <span className="text-sm font-medium">{confidence}%</span>
            </div>
          </div>
          
          <div>
            <span className="text-xs text-dark-muted uppercase tracking-wide">Progress</span>
            <div className="flex items-center gap-2 mt-1">
              <div className="w-24 h-2 bg-dark-border rounded-full overflow-hidden">
                <div 
                  className="h-full bg-brand-400"
                  style={{ width: `${progressScore}%` }}
                />
              </div>
              <span className="text-sm font-medium">{progressScore}%</span>
            </div>
          </div>
        </div>
        
        {/* Mechanism & Prediction */}
        {(mechanism || prediction) && (
          <div className="grid grid-cols-2 gap-4">
            {mechanism && (
              <div>
                <span className="text-xs text-dark-muted uppercase tracking-wide">Mechanism</span>
                <p className="text-sm text-dark-text/80 mt-1">{mechanism}</p>
              </div>
            )}
            {prediction && (
              <div>
                <span className="text-xs text-dark-muted uppercase tracking-wide">Prediction</span>
                <p className="text-sm text-dark-text/80 mt-1">{prediction}</p>
              </div>
            )}
          </div>
        )}
        
        {/* Falsification */}
        <div className="p-3 bg-dark-bg/50 rounded-lg border border-dark-border">
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="h-4 w-4 text-orange-400" />
            <span className="text-xs text-dark-muted uppercase tracking-wide">Would be falsified by</span>
          </div>
          <p className="text-sm text-dark-text/80">{falsifiableBy}</p>
        </div>
        
        {/* Footer */}
        <div className="flex items-center justify-between pt-2 border-t border-dark-border">
          <span className="text-xs text-dark-muted flex items-center gap-1">
            <Clock className="h-3 w-3" />
            Updated {formatRelativeTime(lastUpdated)}
          </span>
          <Button variant="ghost" size="sm" className="text-xs">
            View Full Research Object →
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
