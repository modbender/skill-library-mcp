import { useState, useEffect } from 'react';
import { Trash2, AlertTriangle, Play } from 'lucide-react';
import { Modal } from '../ui/Modal';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import type { Task, BrainStatus } from '../../api/types';
import { formatDateTime } from '../../utils/format';

interface TaskDetailModalProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  onDelete: (id: string) => void;
  onUpdate?: (
    id: string,
    data: {
      brainId?: string;
      title?: string;
      description?: string;
      modelOverride?: string;
      sendDiscordNotification?: boolean;
    }
  ) => Promise<void>;
  onExecute?: (id: string) => void;
  brains: BrainStatus[];
  // models removed
}

export function TaskDetailModal({
  task,
  isOpen,
  onClose,
  onDelete,
  onUpdate,
  onExecute,
  brains,
}: TaskDetailModalProps) {
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  // Initialize editing state when task changes
  useEffect(() => {
    if (task) {
      setEditingTask({ ...task });
    }
  }, [task]);

  if (!task || !editingTask) return null;

  const handleDelete = () => {
    onDelete(task.id);
    onClose();
  };

  const handleSave = async () => {
    if (onUpdate && editingTask) {
      await onUpdate(editingTask.id, {
        brainId: editingTask.brainId,
        title: editingTask.title,
        description: editingTask.description,
        // modelOverride removed
        sendDiscordNotification: editingTask.sendDiscordNotification,
      });
      onClose();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Task Details" className="max-w-4xl">
      <div className="space-y-4">
        {/* Brain Selection */}
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

        {/* Title */}
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

        {/* Description */}
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
              setEditingTask({
                ...editingTask,
                sendDiscordNotification: !editingTask.sendDiscordNotification,
              })
            }
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              editingTask.sendDiscordNotification !== false
                ? 'bg-green-500'
                : 'bg-gray-500'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                editingTask.sendDiscordNotification !== false
                  ? 'translate-x-6'
                  : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Status & Created (read-only) */}
        <div className="grid grid-cols-2 gap-4 p-3 rounded-lg bg-secondary/30">
          <div>
            <label className="text-xs text-muted-foreground">Status</label>
            <div className="mt-1">
              <Badge>{task.status}</Badge>
            </div>
          </div>
          <div>
            <label className="text-xs text-muted-foreground">Created</label>
            <p className="mt-1 text-sm">{formatDateTime(task.createdAt)}</p>
          </div>
        </div>

        {/* Error details for failed tasks */}
        {task.status === 'FAILED' && task.error && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-3">
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <label className="text-xs text-red-400 font-medium">Failure Reason</label>
                <p className="mt-1 text-sm text-red-300 break-words whitespace-pre-wrap font-mono text-xs">
                  {task.error}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Output for completed tasks */}
        {task.status === 'COMPLETED' && task.output && (
          <div>
            <label className="text-xs text-muted-foreground">Output</label>
            <div className="mt-1 p-3 rounded-lg bg-secondary/30 max-h-[200px] overflow-y-auto">
              <pre className="text-sm whitespace-pre-wrap font-mono text-xs">
                {task.output}
              </pre>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2 pt-4 border-t border-border">
          <Button
            variant="secondary"
            onClick={onClose}
            className="flex-1"
          >
            Cancel
          </Button>
          {onUpdate && (
            <Button
              variant="primary"
              onClick={handleSave}
              className="flex-1"
            >
              Save
            </Button>
          )}
          {onExecute && task.status === 'READY' && (
            <Button
              variant="secondary"
              onClick={() => {
                onExecute(task.id);
                onClose();
              }}
              className="flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              Run
            </Button>
          )}
          <Button
            variant="danger"
            onClick={handleDelete}
            className="flex items-center gap-2"
          >
            <Trash2 className="w-4 h-4" />
            Delete
          </Button>
        </div>
      </div>
    </Modal>
  );
}
