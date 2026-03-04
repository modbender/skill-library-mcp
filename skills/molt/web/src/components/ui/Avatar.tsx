import type { HTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

interface AvatarProps extends HTMLAttributes<HTMLDivElement> {
  src?: string;
  alt?: string;
  name?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  fallback?: string;
}

export default function Avatar({
  src,
  alt,
  name,
  size = 'md',
  fallback,
  className,
  ...props
}: AvatarProps) {
  const sizes = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
    xl: 'w-16 h-16 text-lg',
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const displayFallback = fallback || (name ? getInitials(name) : '?');

  return (
    <div
      className={cn(
        'rounded-full bg-gradient-primary flex items-center justify-center text-white font-semibold overflow-hidden',
        sizes[size],
        className
      )}
      {...props}
    >
      {src ? (
        <img src={src} alt={alt || name} className="w-full h-full object-cover" />
      ) : (
        <span>{displayFallback}</span>
      )}
    </div>
  );
}
