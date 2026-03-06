import { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Terminal, Trash2 } from 'lucide-react';
import type { Task, BrainStatus, TaskStatus } from '../../api/types';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { TaskRow } from './TaskRow';
import { Skeleton } from '../ui/Skeleton';

interface TaskStreamProps {
  tasks: Task[];
  brains: BrainStatus[];
  loading: boolean;
  onTaskClick: (task: Task) => void;
  onExecuteTask?: (taskId: string) => void;
  onDeleteTask?: (taskId: string) => void;
  onClearAll?: () => void;
  className?: string;
}

export function TaskStream({ 
  tasks, 
  brains, 
  loading, 
  onTaskClick,
  onExecuteTask,
  onDeleteTask,
  onClearAll,
  className
}: TaskStreamProps) {
  const [filter, setFilter] = useState<TaskStatus | 'ALL'>('ALL');

  const getBrainName = (brainId: string) => {
    return brains.find((b) => b.id === brainId)?.name || brainId;
  };

  const filteredTasks = filter === 'ALL' 
    ? tasks 
    : tasks.filter((t) => t.status === filter);

  const filters: Array<TaskStatus | 'ALL'> = ['ALL', 'READY', 'EXECUTING', 'COMPLETED', 'FAILED'];

  return (
    <Card className={className ? `flex flex-col ${className}` : 'flex flex-col'}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Terminal className="w-5 h-5 text-purple-400" />
          Execution Stream
        </h2>
        <div className="flex items-center gap-2">
          <div className="flex gap-2">
            {filters.map((f) => (
              <div key={f} onClick={() => setFilter(f)}>
                <Badge
                  variant={filter === f ? 'info' : 'default'}
                  className="cursor-pointer hover:scale-105 transition-transform"
                >
                  {f}
                </Badge>
              </div>
            ))}
          </div>
          {onClearAll && tasks.length > 0 && (
            <Button
              variant="danger"
              size="sm"
              onClick={onClearAll}
              className="flex items-center gap-1 ml-2"
            >
              <Trash2 className="w-3 h-3" />
              Clear All
            </Button>
          )}
        </div>
      </div>

      <div className="space-y-3 flex-1 overflow-y-auto">
        {loading ? (
          <>
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-20 w-full" />
            ))}
          </>
        ) : filteredTasks.length === 0 ? (
          <p className="text-center text-muted-foreground py-8">
            No tasks found
          </p>
        ) : (
          <AnimatePresence initial={false} mode="popLayout">
            {filteredTasks.map((task) => (
              <TaskRow
                key={task.id}
                task={task}
                brainName={getBrainName(task.brainId)}
                onClick={onTaskClick}
                onExecute={onExecuteTask}
                onDelete={onDeleteTask}
              />
            ))}
          </AnimatePresence>
        )}
      </div>
    </Card>
  );
}
