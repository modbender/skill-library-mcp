import { cn } from '../../utils/cn';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  className?: string;
}

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  const variants = {
    default: 'bg-secondary text-secondary-foreground border-secondary',
    success: 'bg-green-900/50 text-green-300 border-green-900',
    warning: 'bg-yellow-900/50 text-yellow-300 border-yellow-900',
    error: 'bg-red-900/50 text-red-300 border-red-900',
    info: 'bg-blue-900/50 text-blue-300 border-blue-900',
  };

  return (
    <span
      className={cn(
        'px-2 py-1 rounded text-xs font-medium border border-opacity-50',
        'transition-all duration-200',
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
