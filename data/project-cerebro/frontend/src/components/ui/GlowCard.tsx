import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

interface GlowCardProps {
  children: React.ReactNode;
  className?: string;
  glowColor?: string;
  onClick?: () => void;
  animate?: boolean;
}

export function GlowCard({
  children,
  className,
  glowColor = 'rgba(59, 130, 246, 0.3)',
  onClick,
  animate = false,
}: GlowCardProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.01, y: -1 }}
      transition={{ duration: 0.12, ease: 'easeOut' }}
      className={cn(
        'bg-white/90 dark:bg-white/5',
        'border border-black/10 dark:border-white/10',
        'text-foreground rounded-xl p-6',
        'backdrop-blur',
        'hover:shadow-[0_0_30px_' + glowColor + ']',
        animate && 'animate-glow-pulse',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
      style={{
        boxShadow: animate
          ? `0 0 20px ${glowColor}`
          : undefined,
      }}
    >
      {children}
    </motion.div>
  );
}
