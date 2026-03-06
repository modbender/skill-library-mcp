import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '../../lib/utils';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  elevation?: 'sm' | 'md' | 'lg';
  hover?: boolean;
}

export default function Card({
  children,
  elevation = 'md',
  hover = false,
  className,
  ...props
}: CardProps) {
  const elevations = {
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
  };

  const hoverStyles = hover
    ? 'transition-all duration-200 hover:shadow-card-hover hover:-translate-y-1'
    : '';

  return (
    <div
      className={cn(
        'bg-white rounded-xl overflow-hidden',
        elevations[elevation],
        hoverStyles,
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
