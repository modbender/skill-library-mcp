import { formatRelativeTime } from '../../utils/format';
import type { Task } from '../../api/types';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { motion } from 'framer-motion';
import { Play, Trash2, RotateCcw } from 'lucide-react';
import { cn } from '../../utils/cn';

interface TaskRowProps {
  task: Task;
  brainName: string;
  onClick: (task: Task) => void;
  onExecute?: (taskId: string) => void;
  onDelete?: (taskId: string) => void;
}

export function TaskRow({ task, brainName, onClick, onExecute, onDelete }: TaskRowProps) {
  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'success';
      case 'FAILED':
        return 'error';
      case 'EXECUTING':
        return 'info';
      default:
        return 'warning';
    }
  };

  const canExecute = task.status === 'READY';
  const canRetry = task.status === 'FAILED';

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6, height: 0, marginTop: 0, marginBottom: 0, paddingTop: 0, paddingBottom: 0 }}
      transition={{ duration: 0.14, ease: 'easeOut' }}
      className={cn(
        'p-5 rounded-2xl',
        // Light mode: brighter cell so rows pop against the panel background
        'bg-gradient-to-r from-white/80 to-white/70 hover:from-white/90 hover:to-white/80 border border-white/60 dark:border-white/10',
        // Dark mode: keep the subtle blue/purple glow
        'dark:bg-gradient-to-r dark:from-blue-600/10 dark:to-purple-600/10 dark:hover:from-blue-600/15 dark:hover:to-purple-600/15',
        'bg-[length:200%_auto]',
        'shadow-[0_10px_30px_rgba(0,0,0,0.08)] dark:shadow-[0_10px_30px_rgba(0,0,0,0.35)]',
        'transition-all duration-200 hover:-translate-y-0.5 animate-gradient-shift',
        'group'
      )}
    >
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1 min-w-0 cursor-pointer" onClick={() => onClick(task)}>
          <h4 className="text-base font-semibold truncate">{task.title}</h4>
          <p className="text-xs text-muted-foreground mt-1">
            {brainName} · {formatRelativeTime(task.createdAt)}
          </p>
        </div>

        <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
          <Badge variant={getStatusVariant(task.status)} className="shrink-0">
            {task.status}
          </Badge>

          {/* Run now (READY) */}
          {canExecute && onExecute && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onExecute(task.id)}
              className="p-2 rounded-full bg-black/5 hover:bg-black/10 dark:bg-white/5 dark:hover:bg-white/10"
              title="Run now"
            >
              <Play className="w-4 h-4" />
            </Button>
          )}

          {/* Retry (FAILED) */}
          {canRetry && onExecute && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onExecute(task.id)}
              className="p-2 rounded-full bg-black/5 hover:bg-black/10 dark:bg-white/5 dark:hover:bg-white/10"
              title="Retry"
            >
              <RotateCcw className="w-4 h-4" />
            </Button>
          )}

          {/* Delete */}
          {onDelete && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDelete(task.id)}
              className="p-2 rounded-full bg-black/5 hover:bg-red-500/10 text-red-500 dark:bg-white/5 dark:text-red-300"
              title="Delete"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>
    </motion.div>
  );
}
