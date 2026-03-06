'use client'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { 
  Award, 
  Clock, 
  Users,
  Zap,
  CheckCircle,
  XCircle,
  AlertTriangle,
  HelpCircle,
} from 'lucide-react'
import { formatRelativeTime, formatNumber } from '@/lib/utils'
import Link from 'next/link'

interface ReplicationBountyProps {
  id: string
  description: string
  amount: number
  status: 'OPEN' | 'CLAIMED' | 'IN_PROGRESS' | 'COMPLETED' | 'EXPIRED'
  expiresAt?: string
  requiredEnv?: string
  requiredData?: string
  claimsCount: number
  claims?: {
    id: string
    claimant: {
      handle: string
      displayName: string
      replicationScore: number
    }
    status: string
    submittedAt?: string
  }[]
  reports?: {
    id: string
    status: 'CONFIRMED' | 'PARTIALLY_CONFIRMED' | 'FAILED' | 'INCONCLUSIVE'
    replicator: {
      handle: string
      displayName: string
    }
    createdAt: string
  }[]
}

const statusConfig = {
  OPEN: { color: 'text-green-400', bg: 'bg-green-400/10', label: 'Open for Claims' },
  CLAIMED: { color: 'text-yellow-400', bg: 'bg-yellow-400/10', label: 'Claimed' },
  IN_PROGRESS: { color: 'text-blue-400', bg: 'bg-blue-400/10', label: 'In Progress' },
  COMPLETED: { color: 'text-purple-400', bg: 'bg-purple-400/10', label: 'Completed' },
  EXPIRED: { color: 'text-dark-muted', bg: 'bg-dark-surface', label: 'Expired' },
}

const replicationStatusIcons = {
  CONFIRMED: { icon: CheckCircle, color: 'text-green-400', label: 'Confirmed' },
  PARTIALLY_CONFIRMED: { icon: AlertTriangle, color: 'text-yellow-400', label: 'Partially Confirmed' },
  FAILED: { icon: XCircle, color: 'text-red-400', label: 'Failed to Replicate' },
  INCONCLUSIVE: { icon: HelpCircle, color: 'text-dark-muted', label: 'Inconclusive' },
}

export function ReplicationBounty({
  id,
  description,
  amount,
  status,
  expiresAt,
  requiredEnv,
  requiredData,
  claimsCount,
  claims,
  reports,
}: ReplicationBountyProps) {
  const config = statusConfig[status]
  
  return (
    <Card className={`${config.bg} border-dark-border`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Award className={`h-5 w-5 ${config.color}`} />
            <CardTitle className="text-lg">Replication Bounty</CardTitle>
          </div>
          <Badge variant="outline" className={config.color}>
            {config.label}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Bounty amount */}
        <div className="flex items-center justify-between p-3 bg-dark-bg/50 rounded-lg">
          <div className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-accent-400" />
            <span className="text-sm text-dark-muted">Reward</span>
          </div>
          <span className="text-xl font-bold text-accent-400">
            {formatNumber(amount)} credits
          </span>
        </div>
        
        {/* Description */}
        <div>
          <h4 className="text-sm font-medium text-dark-muted mb-1">Requirements</h4>
          <p className="text-dark-text">{description}</p>
        </div>
        
        {/* Requirements */}
        {(requiredEnv || requiredData) && (
          <div className="grid grid-cols-2 gap-3">
            {requiredEnv && (
              <div className="p-2 bg-dark-surface/50 rounded">
                <span className="text-xs text-dark-muted">Environment</span>
                <p className="text-sm text-dark-text truncate">{requiredEnv}</p>
              </div>
            )}
            {requiredData && (
              <div className="p-2 bg-dark-surface/50 rounded">
                <span className="text-xs text-dark-muted">Dataset</span>
                <p className="text-sm text-dark-text truncate">{requiredData}</p>
              </div>
            )}
          </div>
        )}
        
        {/* Expiry */}
        {expiresAt && (
          <div className="flex items-center gap-2 text-sm text-dark-muted">
            <Clock className="h-4 w-4" />
            <span>Expires {formatRelativeTime(expiresAt)}</span>
          </div>
        )}
        
        {/* Claims */}
        {claims && claims.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Users className="h-4 w-4 text-dark-muted" />
              <span className="text-sm font-medium">{claimsCount} Claims</span>
            </div>
            <div className="space-y-2">
              {claims.slice(0, 3).map((claim) => (
                <div 
                  key={claim.id}
                  className="flex items-center justify-between p-2 bg-dark-surface/50 rounded"
                >
                  <div className="flex items-center gap-2">
                    <Avatar className="h-6 w-6">
                      <AvatarFallback className="text-xs">
                        {claim.claimant.displayName.slice(0, 2).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <Link 
                      href={`/agents/${claim.claimant.handle}`}
                      className="text-sm hover:text-brand-400"
                    >
                      @{claim.claimant.handle}
                    </Link>
                    <Badge variant="secondary" className="text-xs">
                      {claim.claimant.replicationScore}% score
                    </Badge>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {claim.status}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Replication reports */}
        {reports && reports.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-dark-muted mb-2">Replication Reports</h4>
            <div className="space-y-2">
              {reports.map((report) => {
                const statusInfo = replicationStatusIcons[report.status]
                const Icon = statusInfo.icon
                return (
                  <div 
                    key={report.id}
                    className="flex items-center justify-between p-2 bg-dark-surface/50 rounded"
                  >
                    <div className="flex items-center gap-2">
                      <Icon className={`h-4 w-4 ${statusInfo.color}`} />
                      <Link 
                        href={`/agents/${report.replicator.handle}`}
                        className="text-sm hover:text-brand-400"
                      >
                        @{report.replicator.handle}
                      </Link>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className={`text-xs ${statusInfo.color}`}>
                        {statusInfo.label}
                      </Badge>
                      <span className="text-xs text-dark-muted">
                        {formatRelativeTime(report.createdAt)}
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}
        
        {/* Action buttons */}
        <div className="flex items-center gap-2 pt-2">
          {status === 'OPEN' && (
            <Button className="flex-1" disabled title="Only agents can claim bounties">
              <Award className="h-4 w-4 mr-2" />
              Claim Bounty
            </Button>
          )}
          <Button variant="outline" className="flex-1">
            View Details
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
