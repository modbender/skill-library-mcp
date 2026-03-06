import { cn } from '../../utils/cn';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  draggable?: boolean;
  onDragStart?: (e: React.DragEvent<HTMLDivElement>) => void;
  onDragEnd?: (e: React.DragEvent<HTMLDivElement>) => void;
  onDragOver?: (e: React.DragEvent<HTMLDivElement>) => void;
  onDragEnter?: (e: React.DragEvent<HTMLDivElement>) => void;
  onDragLeave?: (e: React.DragEvent<HTMLDivElement>) => void;
  onDrop?: (e: React.DragEvent<HTMLDivElement>) => void;
}

export function Card({
  children,
  className,
  onClick,
  draggable,
  onDragStart,
  onDragEnd,
  onDragOver,
  onDragEnter,
  onDragLeave,
  onDrop,
}: CardProps) {
  return (
    <div
      className={cn(
        'bg-white/90 dark:bg-white/5',
        'border border-black/10 dark:border-white/10',
        'text-foreground rounded-xl p-6',
        'shadow-[0_0_0_1px_rgba(255,255,255,0.02)]',
        'backdrop-blur',
        'transition-all duration-200',
        onClick && 'cursor-pointer hover:shadow-lg hover:-translate-y-0.5',
        className
      )}
      draggable={draggable}
      onClick={onClick}
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
      onDragOver={onDragOver}
      onDragEnter={onDragEnter}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      {children}
    </div>
  );
}
