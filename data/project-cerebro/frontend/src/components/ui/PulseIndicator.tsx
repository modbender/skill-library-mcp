import { cn } from '../../utils/cn';

interface PulseIndicatorProps {
  active?: boolean;
  color?: 'green' | 'blue' | 'red' | 'yellow';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function PulseIndicator({
  active = false,
  color = 'green',
  size = 'md',
  className,
}: PulseIndicatorProps) {
  const colors = {
    green: 'bg-green-500',
    blue: 'bg-blue-500',
    red: 'bg-red-500',
    yellow: 'bg-yellow-500',
  };

  const sizes = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4',
  };

  return (
    <div className={cn('relative inline-flex', className)}>
      <span
        className={cn(
          'rounded-full',
          colors[color],
          sizes[size],
          active && 'animate-breathe'
        )}
      />
      {active && (
        <span
          className={cn(
            'absolute inset-0 rounded-full',
            colors[color],
            'opacity-75 animate-ping'
          )}
        />
      )}
    </div>
  );
}
