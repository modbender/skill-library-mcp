import { AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface DataAlertProps {
  title?: string
  description?: string
  className?: string
}

export function DataAlert({
  title = 'Data temporarily unavailable',
  description = 'We are having trouble connecting to the database. Please refresh in a minute.',
  className,
}: DataAlertProps) {
  return (
    <div className={cn('border border-dark-border rounded-xl bg-dark-surface/50 p-4 flex gap-3 items-start', className)}>
      <AlertCircle className="h-5 w-5 text-accent-400 mt-0.5" />
      <div>
        <p className="font-semibold text-dark-text">{title}</p>
        <p className="text-sm text-dark-muted">{description}</p>
      </div>
    </div>
  )
}
