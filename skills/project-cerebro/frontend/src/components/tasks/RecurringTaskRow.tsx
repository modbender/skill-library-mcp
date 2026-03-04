import { Power, PowerOff, Play, Trash2 } from 'lucide-react';
import type { RecurringTask } from '../../api/types';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { cn } from '../../utils/cn';
import { motion } from 'framer-motion';

interface RecurringTaskRowProps {
  task: RecurringTask;
  brainName: string;
  scheduleText: string;
  onClick: (task: RecurringTask) => void;
  onToggle: (id: string, enabled: boolean) => void;
  onRun: (id: string) => void;
  onDelete: (id: string) => void;
}

export function RecurringTaskRow({
  task,
  brainName,
  scheduleText,
  onClick,
  onToggle,
  onRun,
  onDelete,
}: RecurringTaskRowProps) {
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
        'cursor-pointer'
      )}
      onClick={() => onClick(task)}
    >
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h4 className="text-base font-semibold truncate">{task.title}</h4>
          <p className="text-xs text-muted-foreground mt-1 truncate">
            {brainName} · {scheduleText}
          </p>
        </div>

        <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
          <Badge variant={task.enabled ? 'success' : 'default'} className="shrink-0">
            {task.enabled ? 'ON' : 'OFF'}
          </Badge>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => onToggle(task.id, !task.enabled)}
            className={cn(
              'p-2 rounded-full bg-black/5 hover:bg-black/10 dark:bg-white/5 dark:hover:bg-white/10',
              // Make icon readable in light mode (green/red need to be darker than -300)
              task.enabled
                ? 'text-green-700 dark:text-green-300'
                : 'text-red-700 dark:text-red-300'
            )}
            title={task.enabled ? 'Disable' : 'Enable'}
          >
            {task.enabled ? <Power className="w-4 h-4" /> : <PowerOff className="w-4 h-4" />}
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => onRun(task.id)}
            className="p-2 rounded-full bg-black/5 hover:bg-black/10 dark:bg-white/5 dark:hover:bg-white/10"
            title="Run now"
          >
            <Play className="w-4 h-4" />
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDelete(task.id)}
            className="p-2 rounded-full bg-black/5 hover:bg-red-500/10 text-red-500 dark:bg-white/5 dark:text-red-300"
            title="Delete"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </motion.div>
  );
}
