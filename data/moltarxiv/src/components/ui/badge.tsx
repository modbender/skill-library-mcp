import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2',
  {
    variants: {
      variant: {
        default:
          'border-transparent bg-brand-500 text-white',
        secondary:
          'border-transparent bg-dark-surface text-dark-text',
        destructive:
          'border-transparent bg-red-500 text-white',
        outline:
          'border-dark-border text-dark-text',
        preprint:
          'border-brand-500/30 bg-brand-500/20 text-brand-300',
        idea:
          'border-accent-500/30 bg-accent-500/20 text-accent-300',
        discussion:
          'border-purple-500/30 bg-purple-500/20 text-purple-300',
        success:
          'border-green-500/30 bg-green-500/20 text-green-300',
        warning:
          'border-yellow-500/30 bg-yellow-500/20 text-yellow-300',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
