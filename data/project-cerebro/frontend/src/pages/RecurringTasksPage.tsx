import { useState } from 'react';
import { Repeat, Plus, Clock, Trash2, Play, Power, PowerOff } from 'lucide-react';
import type { BrainStatus, RecurringTask } from '../api/types';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { Input } from '../components/ui/Input';
import { Toggle } from '../components/ui/Toggle';
import { formatHm12, formatMinuteOnly } from '../utils/time';

interface RecurringTasksPageProps {
  brains: BrainStatus[];
  recurringTasks: RecurringTask[];
  // models removed
  loading: boolean;
  onCreateRecurring: (data: {
    brainId: string;
    title: string;
    description?: string;
    modelOverride?: string;
    scheduleType: 'INTERVAL' | 'HOURLY' | 'DAILY' | 'WEEKLY';
    intervalMinutes?: number;
    sendDiscordNotification?: boolean;
    triggersReport?: boolean;
    reportDelayMinutes?: number;
  }) => Promise<void>;
  onDeleteRecurring: (id: string) => void;
  onRunRecurring: (id: string) => void;
  onToggleRecurring: (id: string, enabled: boolean) => Promise<void>;
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
}

export function RecurringTasksPage({
  brains,
  recurringTasks,
  loading,
  onCreateRecurring,
  onDeleteRecurring,
  onRunRecurring,
  onToggleRecurring,
  onUpdateRecurring,
}: RecurringTasksPageProps) {
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<RecurringTask | null>(null);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [newTask, setNewTask] = useState<{
    brainId: string;
    title: string;
    description: string;
    // modelOverride removed
    scheduleType: 'INTERVAL' | 'HOURLY' | 'DAILY' | 'WEEKLY';
    intervalMinutes: number;
    sendDiscordNotification: boolean;
    triggersReport: boolean;
    reportDelayMinutes: number;
  }>({
    brainId: '',
    title: '',
    description: '',
    // modelOverride removed
    scheduleType: 'DAILY',
    intervalMinutes: 60,
    sendDiscordNotification: true,
    triggersReport: false,
    reportDelayMinutes: 0,
  });

  const handleCreate = async () => {
    if (!newTask.brainId || !newTask.title) return;
    await onCreateRecurring(newTask);
    setIsAddOpen(false);
    setNewTask({
      brainId: '',
      title: '',
      description: '',
      // modelOverride removed
      scheduleType: 'DAILY',
      intervalMinutes: 60,
      sendDiscordNotification: true,
      triggersReport: false,
      reportDelayMinutes: 0,
    });
  };

  const getBrainName = (brainId: string) => {
    return brains.find((b) => b.id === brainId)?.name || brainId;
  };

  const formatSchedule = (task: RecurringTask) => {
    const cfg = task.scheduleConfig || {};

    switch (task.scheduleType) {
      case 'INTERVAL':
        return `Every ${task.intervalMs ? Math.round(task.intervalMs / 60000) : '?'} minutes`;
      case 'HOURLY':
        return `Hourly at ${formatMinuteOnly(cfg.minute ?? 0)}`;
      case 'DAILY':
        return `Daily at ${formatHm12(cfg.hour ?? 0, cfg.minute ?? 0)}`;
      case 'WEEKLY': {
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        const dayName = cfg.day !== undefined ? days[cfg.day] : 'Mon';
        return `Weekly on ${dayName} at ${formatHm12(cfg.hour ?? 0, cfg.minute ?? 0)}`;
      }
      default:
        return task.scheduleType;
    }
  };

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
            <Repeat className="w-8 h-8 text-purple-400" />
            Recurring Tasks
          </h1>
          <p className="text-muted-foreground">
            Configure scheduled tasks that create instances in the execution stream
          </p>
        </div>
        <Button
          variant="primary"
          size="lg"
          onClick={() => setIsAddOpen(true)}
          className="flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Add Recurring Task
        </Button>
      </header>

      {/* Task List */}
      <Card>
        <div className="space-y-3 max-h-[600px] overflow-y-auto">
          {loading ? (
            <div className="p-8 text-center text-muted-foreground">Loading...</div>
          ) : recurringTasks.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              <Repeat className="w-12 h-12 mx-auto mb-4 opacity-30" />
              <p>No recurring tasks configured</p>
              <p className="text-sm mt-2">
                Add a recurring task to automatically create task instances on a schedule
              </p>
            </div>
          ) : (
            recurringTasks.map((task) => (
              <div
                key={task.id}
                className="p-4 rounded-lg border border-border bg-secondary/20 flex items-start justify-between gap-4 cursor-pointer"
                onClick={() => {
                  setEditingTask(task);
                  setIsEditOpen(true);
                }}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h4 className="font-medium">{task.title}</h4>
                    <Badge variant={task.enabled ? 'success' : 'default'}>
                      {task.enabled ? 'Enabled' : 'Disabled'}
                    </Badge>
                  </div>
                  {/* Model selection removed */}
                  <p className="text-xs text-muted-foreground mt-1">
                    {getBrainName(task.brainId)} · {formatSchedule(task)}
                  </p>
                  {task.description && (
                    <p className="text-sm text-muted-foreground mt-2">
                      {task.description}
                    </p>
                  )}
                  {task.nextRunAt && (
                    <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      Next run: {new Date(task.nextRunAt).toLocaleString()}
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleRecurring(task.id, !task.enabled);
                    }}
                    className="p-2"
                    title={task.enabled ? 'Disable' : 'Enable'}
                  >
                    {task.enabled ? (
                      <Power className="w-4 h-4 text-green-500" />
                    ) : (
                      <PowerOff className="w-4 h-4 text-red-500" />
                    )}
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      onRunRecurring(task.id);
                    }}
                    className="p-2"
                    title="Run now"
                  >
                    <Play className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteRecurring(task.id);
                    }}
                    className="p-2"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>

      {/* Add Modal */}
      <Modal
        isOpen={isAddOpen}
        onClose={() => setIsAddOpen(false)}
        title="Add Recurring Task"
        className="max-w-4xl"
      >
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">Brain</label>
            <select
              value={newTask.brainId}
              onChange={(e) => setNewTask({ ...newTask, brainId: e.target.value })}
              className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary"
            >
              <option value="">Select a brain...</option>
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
              value={newTask.title}
              onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
              placeholder="Task title"
            />
          </div>

          <div>
            <label className="text-sm font-medium">Description (optional)</label>
            <textarea
              value={newTask.description}
              onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
              placeholder="Task description"
              className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary min-h-[220px]"
            />
          </div>

          {/* Model selection removed */}

          <div>
            <label className="text-sm font-medium">Schedule</label>
            <select
              value={newTask.scheduleType}
              onChange={(e) =>
                setNewTask({
                  ...newTask,
                  scheduleType: e.target.value as typeof newTask.scheduleType,
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

          {newTask.scheduleType === 'INTERVAL' && (
            <div>
              <label className="text-sm font-medium">Interval (minutes)</label>
              <Input
                type="number"
                value={newTask.intervalMinutes}
                onChange={(e) =>
                  setNewTask({
                    ...newTask,
                    intervalMinutes: parseInt(e.target.value) || 60,
                  })
                }
              />
            </div>
          )}

          {/* Notification & Report Settings */}
          <div className="space-y-3 pt-2 border-t border-border">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium">Send Discord Notification</div>
                <div className="text-xs text-muted-foreground">Notify on completion</div>
              </div>
              <Toggle
                checked={newTask.sendDiscordNotification}
                onChange={(v) => setNewTask({ ...newTask, sendDiscordNotification: v })}
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium">Trigger Report</div>
                <div className="text-xs text-muted-foreground">Generate report after task</div>
              </div>
              <Toggle
                checked={newTask.triggersReport}
                onChange={(v) => setNewTask({ ...newTask, triggersReport: v })}
              />
            </div>
            {newTask.triggersReport && (
              <div>
                <label className="text-sm font-medium">Report Delay (minutes)</label>
                <Input
                  type="number"
                  value={newTask.reportDelayMinutes}
                  onChange={(e) =>
                    setNewTask({
                      ...newTask,
                      reportDelayMinutes: parseInt(e.target.value) || 0,
                    })
                  }
                  placeholder="0"
                />
              </div>
            )}
          </div>

          <div className="flex gap-2 pt-4">
            <Button variant="secondary" onClick={() => setIsAddOpen(false)} className="flex-1">
              Cancel
            </Button>
            <Button variant="primary" onClick={handleCreate} className="flex-1">
              Create
            </Button>
          </div>
        </div>
      </Modal>

      {/* Edit Modal */}
      {editingTask && (
        <Modal
          isOpen={isEditOpen}
          onClose={() => setIsEditOpen(false)}
          title="Edit Recurring Task"
          className="max-w-4xl"
        >
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Brain</label>
              <select
                value={editingTask.brainId}
                onChange={(e) =>
                  setEditingTask({ ...editingTask, brainId: e.target.value })
                }
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
                value={editingTask.title}
                onChange={(e) =>
                  setEditingTask({ ...editingTask, title: e.target.value })
                }
                placeholder="Task title"
              />
            </div>

            <div>
              <label className="text-sm font-medium">Description (optional)</label>
              <textarea
                value={editingTask.description || ''}
                onChange={(e) =>
                  setEditingTask({ ...editingTask, description: e.target.value })
                }
                placeholder="Task description"
                className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary min-h-[220px]"
              />
            </div>

            {/* Model selection removed */}

            <div>
              <label className="text-sm font-medium">Schedule</label>
              <select
                value={editingTask.scheduleType}
                onChange={(e) =>
                  setEditingTask({
                    ...editingTask,
                    scheduleType: e.target.value as typeof editingTask.scheduleType,
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

            {editingTask.scheduleType === 'INTERVAL' && (
              <div>
                <label className="text-sm font-medium">Interval (minutes)</label>
                <Input
                  type="number"
                  value={editingTask.intervalMs ? Math.round(editingTask.intervalMs / 60000) : 60}
                  onChange={(e) =>
                    setEditingTask({
                      ...editingTask,
                      intervalMs: parseInt(e.target.value) * 60000 || 60000,
                    })
                  }
                />
              </div>
            )}

            {/* Notification & Report Settings */}
            <div className="space-y-3 pt-2 border-t border-border">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">Send Discord Notification</div>
                  <div className="text-xs text-muted-foreground">Notify on completion</div>
                </div>
                <Toggle
                  checked={editingTask.sendDiscordNotification ?? true}
                  onChange={(v) => setEditingTask({ ...editingTask, sendDiscordNotification: v })}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">Trigger Report</div>
                  <div className="text-xs text-muted-foreground">Generate report after task</div>
                </div>
                <Toggle
                  checked={editingTask.triggersReport ?? false}
                  onChange={(v) => setEditingTask({ ...editingTask, triggersReport: v })}
                />
              </div>
              {editingTask.triggersReport && (
                <div>
                  <label className="text-sm font-medium">Report Delay (minutes)</label>
                  <Input
                    type="number"
                    value={editingTask.reportDelayMinutes ?? 0}
                    onChange={(e) =>
                      setEditingTask({
                        ...editingTask,
                        reportDelayMinutes: parseInt(e.target.value) || 0,
                      })
                    }
                    placeholder="0"
                  />
                </div>
              )}
            </div>

            <div className="flex gap-2 pt-4">
              <Button
                variant="secondary"
                onClick={() => setIsEditOpen(false)}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={async () => {
                  if (editingTask) {
                    await onUpdateRecurring(editingTask.id, {
                      brainId: editingTask.brainId,
                      title: editingTask.title,
                      description: editingTask.description,
                      // modelOverride removed
                      scheduleType: editingTask.scheduleType,
                      intervalMinutes: editingTask.intervalMs ? Math.round(editingTask.intervalMs / 60000) : undefined,
                      sendDiscordNotification: editingTask.sendDiscordNotification,
                      triggersReport: editingTask.triggersReport,
                      reportDelayMinutes: editingTask.reportDelayMinutes,
                    });
                    setIsEditOpen(false);
                    setEditingTask(null);
                  }
                }}
                className="flex-1"
              >
                Save
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
