import { useEffect, useRef, useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Plus, Repeat } from 'lucide-react';
import type { BrainStatus, Task, RecurringTask } from '../api/types';
import { SummaryCards } from '../components/dashboard/SummaryCards';
import { TaskStream } from '../components/tasks/TaskStream';
import { RecurringTaskRow } from '../components/tasks/RecurringTaskRow';
import { TaskDetailModal } from '../components/tasks/TaskDetailModal';
import { AddTaskModal } from '../components/tasks/AddTaskModal';
import { Button } from '../components/ui/Button';
import { GradientText } from '../components/ui/GradientText';
import { BrainTile } from '../components/brains/BrainTile';
import { Card } from '../components/ui/Card';
import { Modal } from '../components/ui/Modal';
import { Input } from '../components/ui/Input';
import { formatHm12, formatMinuteOnly } from '../utils/time';
import { cn } from '../utils/cn';

interface DashboardPageProps {
  brains: BrainStatus[];
  tasks: Task[];
  recurringTasks: RecurringTask[];
  loadingBrains: boolean;
  loadingTasks: boolean;
  loadingRecurring: boolean;
  onToggleBrain: (id: string, enabled: boolean) => void;
  onRunBrain: (id: string) => void;
  onBrainClick: (id: string) => void;
  onCreateTask: (taskData: any) => Promise<void>;
  onCreateRecurring: (taskData: any) => Promise<void>;
  onDeleteRecurring: (id: string) => void;
  onRunRecurring: (id: string) => void;
  onUpdateRecurring: (
    id: string,
    data: {
      brainId?: string;
      title?: string;
      description?: string;
      modelOverride?: string;
      scheduleType?: 'INTERVAL' | 'HOURLY' | 'DAILY' | 'WEEKLY';
      intervalMinutes?: number;
      enabled?: boolean;
      sendDiscordNotification?: boolean;
      triggersReport?: boolean;
      reportDelayMinutes?: number;
    }
  ) => Promise<void>;
  onToggleRecurring: (id: string, enabled: boolean) => Promise<void>;
  onDeleteTask: (id: string) => void;
  onExecuteTask: (id: string) => void;
  onUpdateTask?: (
    id: string,
    data: {
      brainId?: string;
      title?: string;
      description?: string;
      modelOverride?: string;
      sendDiscordNotification?: boolean;
    }
  ) => Promise<void>;
  onClearAllTasks: () => void;
  // models removed
}

export function DashboardPage({
  brains,
  tasks,
  recurringTasks,
  loadingTasks,
  loadingRecurring,
  onToggleBrain,
  onRunBrain,
  onBrainClick,
  onCreateTask,
  onCreateRecurring,
  onDeleteRecurring,
  onRunRecurring,
  onUpdateRecurring,
  onToggleRecurring,
  onDeleteTask,
  onExecuteTask,
  onUpdateTask,
  onClearAllTasks,
}: DashboardPageProps) {
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isTaskDetailOpen, setIsTaskDetailOpen] = useState(false);
  const [isAddTaskOpen, setIsAddTaskOpen] = useState(false);
  const [isAddRecurringOpen, setIsAddRecurringOpen] = useState(false);
  const [recurringError, setRecurringError] = useState<string | null>(null);
  const [editingRecurring, setEditingRecurring] = useState<RecurringTask | null>(null);
  const [isEditRecurringOpen, setIsEditRecurringOpen] = useState(false);
  const [newRecurring, setNewRecurring] = useState({
    brainId: '',
    title: '',
    description: '',
    scheduleType: 'DAILY' as 'DAILY' | 'HOURLY' | 'WEEKLY' | 'INTERVAL',
    intervalMinutes: 60,
    time: '09:00',
    dayOfWeek: '1', // Monday
    // model selection removed
  });

  // Resizable split (Execution Stream vs Recurring Tasks) on large screens
  const SPLIT_STORAGE_KEY = 'cerebro.dashboard.split';
  const [splitPct, setSplitPct] = useState<number>(67); // percent width for left pane
  const draggingRef = useRef(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(SPLIT_STORAGE_KEY);
      const n = saved ? Number(saved) : NaN;
      if (!Number.isNaN(n) && n >= 45 && n <= 80) setSplitPct(n);
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (!draggingRef.current) return;
      const el = containerRef.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const pct = (x / rect.width) * 100;
      const clamped = Math.max(45, Math.min(80, pct));
      setSplitPct(clamped);
    };

    const onUp = () => {
      if (!draggingRef.current) return;
      draggingRef.current = false;
      document.body.classList.remove('select-none');
      document.body.style.cursor = '';
      try {
        localStorage.setItem(SPLIT_STORAGE_KEY, String(Math.round(splitPct)));
      } catch {
        // ignore
      }
    };

    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    return () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
    };
  }, [splitPct]);

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
    setIsTaskDetailOpen(true);
  };

  const getBrainName = (brainId: string) => {
    return brains.find((b) => b.id === brainId)?.name || brainId;
  };

  // Keep a stable baseline order so we can temporarily promote EXECUTING brains.
  const baselineOrderRef = useRef<Map<string, number>>(new Map());
  useEffect(() => {
    // Capture once (first time we see a brain id). This preserves "original position".
    brains.forEach((b, i) => {
      if (!baselineOrderRef.current.has(b.id)) baselineOrderRef.current.set(b.id, i);
    });
  }, [brains]);

  const orderedBrains = [...brains].sort((a, b) => {
    const aExec = a.status === 'EXECUTING';
    const bExec = b.status === 'EXECUTING';
    if (aExec !== bExec) return aExec ? -1 : 1;
    const ai = baselineOrderRef.current.get(a.id) ?? 9999;
    const bi = baselineOrderRef.current.get(b.id) ?? 9999;
    return ai - bi;
  });

  const handleCreateRecurring = async () => {
    if (!newRecurring.brainId || !newRecurring.title) {
      setRecurringError('Please select a brain and enter a title');
      return;
    }

    setRecurringError(null);

    try {
      // Build scheduleConfig based on schedule type
      const scheduleConfig: Record<string, any> = {};
      const [hours, minutes] = newRecurring.time.split(':').map(Number);

      if (newRecurring.scheduleType === 'HOURLY') {
        scheduleConfig.minute = minutes;
      } else if (newRecurring.scheduleType === 'DAILY') {
        scheduleConfig.hour = hours;
        scheduleConfig.minute = minutes;
      } else if (newRecurring.scheduleType === 'WEEKLY') {
        scheduleConfig.day = Number(newRecurring.dayOfWeek);
        scheduleConfig.hour = hours;
        scheduleConfig.minute = minutes;
      }

      // Only send fields the API expects
      const payload: any = {
        brainId: newRecurring.brainId,
        title: newRecurring.title,
        description: newRecurring.description,
        scheduleType: newRecurring.scheduleType,
        scheduleConfig,
        // modelOverride removed
      };

      // Only include intervalMinutes for INTERVAL type
      if (newRecurring.scheduleType === 'INTERVAL') {
        payload.intervalMinutes = newRecurring.intervalMinutes;
      }

      await onCreateRecurring(payload);

      setIsAddRecurringOpen(false);
      setNewRecurring({
        brainId: '',
        title: '',
        description: '',
        scheduleType: 'DAILY',
        intervalMinutes: 60,
        time: '09:00',
        dayOfWeek: '1',
        // modelId removed
      });
    } catch (err: any) {
      const message = err instanceof Error ? err.message : String(err);
      setRecurringError(message || 'Failed to create recurring task');
      console.error('Failed to create recurring task:', err);
    }
  };

  const formatSchedule = (task: RecurringTask) => {
    const config = task.scheduleConfig || {};

    switch (task.scheduleType) {
      case 'HOURLY':
        return `Hourly at ${formatMinuteOnly(config.minute ?? 0)}`;
      case 'DAILY':
        return `Daily at ${formatHm12(config.hour ?? 0, config.minute ?? 0)}`;
      case 'WEEKLY': {
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        const dayName = config.day !== undefined ? days[config.day] : 'Mon';
        return `Weekly on ${dayName} at ${formatHm12(config.hour ?? 0, config.minute ?? 0)}`;
      }
      case 'INTERVAL':
        return `Every ${task.intervalMs ? Math.round(task.intervalMs / 60000) : '?'} min`;
      default:
        return task.scheduleType;
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 lg:space-y-8">
      {/* Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-2">
            <GradientText>Project Cerebro</GradientText>
          </h1>
          <p className="text-muted-foreground">Autonomous AI Brain Control Center</p>
        </div>
        <Button
          variant="primary"
          size="lg"
          onClick={() => setIsAddTaskOpen(true)}
          className="flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Add Task
        </Button>
      </header>

      {/* Summary Cards */}
      <SummaryCards brains={brains} tasks={tasks} />

      {/* Brains Strip */}
      <div className="space-y-3">
        <div className="flex items-end justify-between">
          <h2 className="text-xl font-bold">Brains</h2>
          <p className="hidden sm:block text-xs text-muted-foreground">Scroll →</p>
        </div>
        <div className="flex gap-4 overflow-x-auto overflow-y-visible pb-4 pt-2 px-3">
          {orderedBrains.map((brain: any) => (
            <BrainTile
              key={brain.id}
              brain={brain}
              onToggle={onToggleBrain}
              onRun={onRunBrain}
              onClick={onBrainClick}
            />
          ))}
        </div>
      </div>

      {/* Main Split: Execution Stream | Recurring Tasks */}
      <div
        ref={containerRef}
        className="flex flex-col gap-6 items-start lg:flex-row lg:gap-0"
      >
        <div
          className="w-full lg:pr-3"
          style={{ flexBasis: `${splitPct}%` }}
        >
          <TaskStream
            className="h-[520px] sm:h-[600px] lg:h-[680px] bg-gradient-to-br from-blue-600/10 to-purple-600/10 dark:from-blue-600/5 dark:to-purple-600/5 bg-[length:200%_auto] animate-gradient-shift"
            tasks={tasks}
            brains={brains}
            loading={loadingTasks}
            onTaskClick={handleTaskClick}
            onExecuteTask={onExecuteTask}
            onDeleteTask={onDeleteTask}
            onClearAll={onClearAllTasks}
          />
        </div>

        {/* Drag handle (desktop only) */}
        <div className="hidden lg:flex w-6 self-stretch items-center justify-center">
          <div
            role="separator"
            aria-orientation="vertical"
            title="Drag to resize"
            onMouseDown={() => {
              draggingRef.current = true;
              document.body.classList.add('select-none');
              document.body.style.cursor = 'col-resize';
            }}
            className={cn(
              'w-1 h-[85%] rounded-full cursor-col-resize transition-colors',
              'bg-gradient-to-b from-blue-400/25 via-purple-400/20 to-blue-400/25',
              'hover:from-blue-500/45 hover:via-purple-500/40 hover:to-blue-500/45',
              'shadow-[0_0_0_1px_rgba(0,0,0,0.08)] dark:shadow-[0_0_0_1px_rgba(255,255,255,0.08)]'
            )}
          />
        </div>

        {/* Recurring Tasks */}
        <div
          className="w-full lg:pl-3"
          style={{ flexBasis: `${100 - splitPct}%` }}
        >
          <Card className="flex flex-col h-[520px] sm:h-[600px] lg:h-[680px] p-4 sm:p-6 bg-gradient-to-br from-blue-600/10 to-purple-600/10 dark:from-blue-600/5 dark:to-purple-600/5 bg-[length:200%_auto] animate-gradient-shift">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Repeat className="w-5 h-5 text-purple-400" />
              Recurring Tasks
            </h2>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setIsAddRecurringOpen(true)}
              className="px-3 py-2 rounded-lg"
              title="Add recurring task"
            >
              <Plus className="w-4 h-4" />
            </Button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-3">
            {loadingRecurring ? (
              <div className="text-center text-muted-foreground py-6">Loading...</div>
            ) : recurringTasks.length === 0 ? (
              <div className="text-center text-muted-foreground py-6">No recurring tasks</div>
            ) : (
              <AnimatePresence initial={false} mode="popLayout">
                {recurringTasks.map((task) => (
                  <RecurringTaskRow
                    key={task.id}
                    task={task}
                    brainName={getBrainName(task.brainId)}
                    scheduleText={formatSchedule(task)}
                    onClick={() => {
                      setEditingRecurring(task);
                      setIsEditRecurringOpen(true);
                    }}
                    onToggle={onToggleRecurring}
                    onRun={onRunRecurring}
                    onDelete={onDeleteRecurring}
                  />
                ))}
              </AnimatePresence>
            )}
          </div>
            {/* helper text removed */}
          </Card>
        </div>
      </div>

      {/* Execution Stream is rendered in the main grid above */}

      {/* Modals */}
      <TaskDetailModal
        task={selectedTask}
        isOpen={isTaskDetailOpen}
        onClose={() => setIsTaskDetailOpen(false)}
        onDelete={onDeleteTask}
        onUpdate={onUpdateTask}
        onExecute={onExecuteTask}
        brains={brains}
      />

      <AddTaskModal
        isOpen={isAddTaskOpen}
        onClose={() => setIsAddTaskOpen(false)}
        brains={brains}
        onCreateTask={onCreateTask}
        onCreateRecurring={onCreateRecurring}
      />

      {/* Add Recurring Modal */}
      <Modal
        isOpen={isAddRecurringOpen}
        onClose={() => {
          setIsAddRecurringOpen(false);
          setRecurringError(null);
        }}
        title="Add Recurring Task"
        className="max-w-4xl"
      >
        <div className="space-y-4">
          {recurringError && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
              {recurringError}
            </div>
          )}
          <div>
            <label className="text-sm font-medium">Brain</label>
            <select
              value={newRecurring.brainId}
              onChange={(e) => setNewRecurring({ ...newRecurring, brainId: e.target.value })}
              className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary"
            >
              <option value="">Select brain...</option>
              {brains.map((b) => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
            </select>
          </div>

          {/* Model selection removed */}

          <div>
            <label className="text-sm font-medium">Title</label>
            <Input
              value={newRecurring.title}
              onChange={(e) => setNewRecurring({ ...newRecurring, title: e.target.value })}
              placeholder="Task title"
            />
          </div>

          <div>
            <label className="text-sm font-medium">Description</label>
            <textarea
              value={newRecurring.description}
              onChange={(e) => setNewRecurring({ ...newRecurring, description: e.target.value })}
              placeholder="Task description"
              className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary min-h-[220px]"
            />
          </div>

          <div>
            <label className="text-sm font-medium">Schedule</label>
            <select
              value={newRecurring.scheduleType}
              onChange={(e) => setNewRecurring({ ...newRecurring, scheduleType: e.target.value as any })}
              className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary"
            >
              <option value="HOURLY">Hourly</option>
              <option value="DAILY">Daily</option>
              <option value="WEEKLY">Weekly</option>
              <option value="INTERVAL">Custom Interval</option>
            </select>
          </div>

          {newRecurring.scheduleType === 'INTERVAL' && (
            <div>
              <label className="text-sm font-medium">Interval (minutes)</label>
              <Input
                type="number"
                value={newRecurring.intervalMinutes}
                onChange={(e) => setNewRecurring({ ...newRecurring, intervalMinutes: parseInt(e.target.value) || 60 })}
              />
            </div>
          )}

          {(newRecurring.scheduleType === 'DAILY' || newRecurring.scheduleType === 'WEEKLY' || newRecurring.scheduleType === 'HOURLY') && (
            <div>
              <label className="text-sm font-medium">
                {newRecurring.scheduleType === 'HOURLY' ? 'At minute' : 'Time'}
              </label>
              <input
                type="time"
                value={newRecurring.time}
                onChange={(e) => setNewRecurring({ ...newRecurring, time: e.target.value })}
                className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary"
              />
            </div>
          )}

          {newRecurring.scheduleType === 'WEEKLY' && (
            <div>
              <label className="text-sm font-medium">Day of Week</label>
              <select
                value={newRecurring.dayOfWeek}
                onChange={(e) => setNewRecurring({ ...newRecurring, dayOfWeek: e.target.value })}
                className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary"
              >
                <option value="0">Sunday</option>
                <option value="1">Monday</option>
                <option value="2">Tuesday</option>
                <option value="3">Wednesday</option>
                <option value="4">Thursday</option>
                <option value="5">Friday</option>
                <option value="6">Saturday</option>
              </select>
            </div>
          )}

          <div className="flex gap-2 pt-4">
            <Button variant="secondary" onClick={() => setIsAddRecurringOpen(false)} className="flex-1">
              Cancel
            </Button>
            <Button variant="primary" onClick={handleCreateRecurring} className="flex-1">
              Create
            </Button>
          </div>
        </div>
      </Modal>

      {/* Edit Recurring Modal */}
      <Modal
        isOpen={isEditRecurringOpen}
        onClose={() => {
          setIsEditRecurringOpen(false);
          setEditingRecurring(null);
        }}
        title="Edit Recurring Task"
        className="max-w-4xl"
      >
        {editingRecurring && (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Brain</label>
              <select
                value={editingRecurring.brainId}
                onChange={(e) => setEditingRecurring({ ...editingRecurring, brainId: e.target.value })}
                className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary"
              >
                {brains.map((brain) => (
                  <option key={brain.id} value={brain.id}>
                    {brain.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-sm font-medium">Title</label>
              <Input
                value={editingRecurring.title}
                onChange={(e) => setEditingRecurring({ ...editingRecurring, title: e.target.value })}
                placeholder="Task title"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Description</label>
              <textarea
                value={editingRecurring.description || ''}
                onChange={(e) => setEditingRecurring({ ...editingRecurring, description: e.target.value })}
                placeholder="Task description"
                className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary min-h-[220px]"
              />
            </div>

            {/* Model selection removed */}

            <div>
              <label className="text-sm font-medium">Schedule</label>
              <select
                value={editingRecurring.scheduleType}
                onChange={(e) =>
                  setEditingRecurring({
                    ...editingRecurring,
                    scheduleType: e.target.value as typeof editingRecurring.scheduleType,
                  })
                }
                className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary"
              >
                <option value="HOURLY">Hourly</option>
                <option value="DAILY">Daily</option>
                <option value="WEEKLY">Weekly</option>
                <option value="INTERVAL">Custom Interval</option>
              </select>
            </div>

            {editingRecurring.scheduleType === 'INTERVAL' && (
              <div>
                <label className="text-sm font-medium">Interval (minutes)</label>
                <Input
                  type="number"
                  value={editingRecurring.intervalMs ? Math.round(editingRecurring.intervalMs / 60000) : 60}
                  onChange={(e) =>
                    setEditingRecurring({
                      ...editingRecurring,
                      intervalMs: parseInt(e.target.value) * 60000 || 60000,
                    })
                  }
                />
              </div>
            )}

            {(editingRecurring.scheduleType === 'DAILY' || editingRecurring.scheduleType === 'WEEKLY' || editingRecurring.scheduleType === 'HOURLY') && (
              <div>
                <label className="text-sm font-medium">
                  {editingRecurring.scheduleType === 'HOURLY' ? 'At minute' : 'Time'}
                </label>
                <input
                  type="time"
                  value={`${String(editingRecurring.scheduleConfig?.hour || 0).padStart(2, '0')}:${String(editingRecurring.scheduleConfig?.minute || 0).padStart(2, '0')}`}
                  onChange={(e) => {
                    const [hour, minute] = e.target.value.split(':').map(Number);
                    setEditingRecurring({
                      ...editingRecurring,
                      scheduleConfig: { 
                        ...editingRecurring.scheduleConfig, 
                        hour, 
                        minute 
                      },
                    });
                  }}
                  className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary"
                />
              </div>
            )}

            {editingRecurring.scheduleType === 'WEEKLY' && (
              <div>
                <label className="text-sm font-medium">Day of Week</label>
                <select
                  value={editingRecurring.scheduleConfig?.day?.toString() || '1'}
                  onChange={(e) =>
                    setEditingRecurring({
                      ...editingRecurring,
                      scheduleConfig: { 
                        ...editingRecurring.scheduleConfig, 
                        day: parseInt(e.target.value) 
                      },
                    })
                  }
                  className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary"
                >
                  <option value="0">Sunday</option>
                  <option value="1">Monday</option>
                  <option value="2">Tuesday</option>
                  <option value="3">Wednesday</option>
                  <option value="4">Thursday</option>
                  <option value="5">Friday</option>
                  <option value="6">Saturday</option>
                </select>
              </div>
            )}

            {/* Discord Notification Toggle */}
            <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/30">
              <div>
                <label className="text-sm font-medium">Send Discord Notification</label>
                <p className="text-xs text-muted-foreground">
                  Notify Discord when this task completes
                </p>
              </div>
              <button
                onClick={() =>
                  setEditingRecurring({
                    ...editingRecurring,
                    sendDiscordNotification: !editingRecurring.sendDiscordNotification,
                  })
                }
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  editingRecurring.sendDiscordNotification !== false
                    ? 'bg-green-500'
                    : 'bg-gray-500'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    editingRecurring.sendDiscordNotification !== false
                      ? 'translate-x-6'
                      : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            {/* Trigger Report Toggle */}
            <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/30">
              <div>
                <label className="text-sm font-medium">Auto-Trigger Report</label>
                <p className="text-xs text-muted-foreground">
                  Create a report task after this task completes
                </p>
              </div>
              <button
                onClick={() =>
                  setEditingRecurring({
                    ...editingRecurring,
                    triggersReport: !editingRecurring.triggersReport,
                  })
                }
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  editingRecurring.triggersReport
                    ? 'bg-green-500'
                    : 'bg-gray-500'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    editingRecurring.triggersReport
                      ? 'translate-x-6'
                      : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            {/* Report Delay (only show if triggersReport is enabled) */}
            {editingRecurring.triggersReport && (
              <div>
                <label className="text-sm font-medium">Report Delay (minutes)</label>
                <Input
                  type="number"
                  min={0}
                  value={editingRecurring.reportDelayMinutes ?? 0}
                  onChange={(e) =>
                    setEditingRecurring({
                      ...editingRecurring,
                      reportDelayMinutes: parseInt(e.target.value) || 0,
                    })
                  }
                  placeholder="0 = immediate"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Delay before creating the report task (0 = immediate)
                </p>
              </div>
            )}

            <div className="flex gap-2 pt-4">
              <Button 
                variant="secondary" 
                onClick={() => {
                  setIsEditRecurringOpen(false);
                  setEditingRecurring(null);
                }} 
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={async () => {
                  if (editingRecurring) {
                    const payload: any = {
                      brainId: editingRecurring.brainId,
                      title: editingRecurring.title,
                      description: editingRecurring.description,
                      // modelOverride removed
                      scheduleType: editingRecurring.scheduleType,
                      scheduleConfig: editingRecurring.scheduleConfig,
                      sendDiscordNotification: editingRecurring.sendDiscordNotification,
                      triggersReport: editingRecurring.triggersReport,
                      reportDelayMinutes: editingRecurring.reportDelayMinutes,
                    };

                    if (editingRecurring.scheduleType === 'INTERVAL') {
                      payload.intervalMinutes = editingRecurring.intervalMs ? Math.round(editingRecurring.intervalMs / 60000) : undefined;
                    }
                    await onUpdateRecurring(editingRecurring.id, payload);
                    setIsEditRecurringOpen(false);
                    setEditingRecurring(null);
                  }
                }}
                className="flex-1"
              >
                Save
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
