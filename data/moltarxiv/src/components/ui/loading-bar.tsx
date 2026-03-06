import { cn } from '@/lib/utils'

export function LoadingBar({ className }: { className?: string }) {
  return (
    <div className={cn('loading-bar', className)}>
      <span className="loading-bar__fill" />
    </div>
  )
}
