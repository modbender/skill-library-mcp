import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '../../lib/utils';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  children: ReactNode;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'info' | 'error';
  size?: 'sm' | 'md';
}

const categoryColors: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'error' | 'default'> = {
  MEDICAL: 'error',
  DISASTER_RELIEF: 'warning',
  EDUCATION: 'info',
  COMMUNITY: 'success',
  EMERGENCY: 'error',
  OTHER: 'default',
};

export function getCategoryVariant(category: string): 'default' | 'primary' | 'success' | 'warning' | 'info' | 'error' {
  return categoryColors[category] || 'default';
}

export default function Badge({
  children,
  variant = 'default',
  size = 'md',
  className,
  ...props
}: BadgeProps) {
  const baseStyles = 'inline-flex items-center font-semibold rounded-full';
  
  const variants = {
    default: 'bg-gray-100 text-gray-700',
    primary: 'bg-primary-100 text-primary-700',
    success: 'bg-success-light text-success-dark',
    warning: 'bg-warning-light text-warning-dark',
    info: 'bg-info-light text-info-dark',
    error: 'bg-error-light text-error-dark',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
  };

  return (
    <span
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      {...props}
    >
      {children}
    </span>
  );
}
