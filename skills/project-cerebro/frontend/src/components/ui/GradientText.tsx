import { cn } from '../../utils/cn';

interface GradientTextProps {
  children: React.ReactNode;
  className?: string;
  gradient?: string;
}

export function GradientText({
  children,
  className,
  gradient = 'from-blue-400 via-purple-400 to-pink-400',
}: GradientTextProps) {
  return (
    <span
      className={cn(
        'bg-gradient-to-r bg-clip-text text-transparent',
        'animate-gradient-shift',
        'bg-[length:200%_auto]',
        gradient,
        className
      )}
    >
      {children}
    </span>
  );
}
