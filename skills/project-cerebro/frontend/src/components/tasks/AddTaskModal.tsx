import { useState, useEffect } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Toggle } from '../ui/Toggle';
import type { BrainStatus } from '../../api/types';

interface AddTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  brains: BrainStatus[];
  onCreateTask: (taskData: any) => Promise<void>;
  onCreateRecurring: (taskData: any) => Promise<void>;
}

export function AddTaskModal({
  isOpen,
  onClose,
  brains,
  onCreateTask,
  onCreateRecurring,
}: AddTaskModalProps) {
  // Model selection removed: OpenClaw agent models are configured in OpenClaw, not per-task.

  // Use first brain as default instead of hardcoded 'nexus'
  const defaultBrainId = brains.length > 0 ? brains[0].id : '';

  const [formData, setFormData] = useState({
    brainId: defaultBrainId,
    title: '',
    description: '',
    // modelOverride removed
    isRecurring: false,
    scheduleType: 'DAILY' as 'INTERVAL' | 'HOURLY' | 'DAILY' | 'WEEKLY',
    intervalMinutes: 60,
    dailyTime: '09:00',
    weeklyDay: '1',
  });

  // Model selection removed (no per-task model override).

  // Update brainId if brains change and current selection is invalid
  useEffect(() => {
    if (brains.length > 0 && !brains.find(b => b.id === formData.brainId)) {
      setFormData(prev => ({ ...prev, brainId: brains[0].id }));
    }
  }, [brains, formData.brainId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim()) return;

    try {
      if (formData.isRecurring) {
        let scheduleConfig: any = {};
        
        if (formData.scheduleType === 'HOURLY') {
          scheduleConfig = { minute: Number(formData.dailyTime.split(':')[1] || 0) };
        } else if (formData.scheduleType === 'DAILY') {
          const [h, m] = formData.dailyTime.split(':');
          scheduleConfig = { hour: Number(h), minute: Number(m || 0) };
        } else if (formData.scheduleType === 'WEEKLY') {
          const [h, m] = formData.dailyTime.split(':');
          scheduleConfig = {
            day: Number(formData.weeklyDay),
            hour: Number(h),
            minute: Number(m || 0),
          };
        }

        await onCreateRecurring({
          brainId: formData.brainId,
          title: formData.title,
          description: formData.description,
          scheduleType: formData.scheduleType,
          intervalMinutes: formData.intervalMinutes,
          scheduleConfig,
        });
      } else {
        await onCreateTask({
          brainId: formData.brainId,
          title: formData.title,
          description: formData.description,
        });
      }

      setFormData({
        ...formData,
        title: '',
        description: '',
      });
      onClose();
    } catch (error) {
      console.error('Failed to create task:', error);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add New Task" className="max-w-4xl">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex items-center gap-3 p-3 bg-secondary/30 rounded-lg">
          <span className="text-sm">One-time Task</span>
          <Toggle
            checked={formData.isRecurring}
            onChange={(checked) => setFormData({ ...formData, isRecurring: checked })}
          />
          <span className="text-sm">Recurring Task</span>
        </div>

        <div className="grid grid-cols-1 gap-4">
          <div>
            <label className="text-sm font-medium block mb-2">Brain</label>
            <select
              className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm"
              value={formData.brainId}
              onChange={(e) => setFormData({ ...formData, brainId: e.target.value })}
            >
              {brains.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="text-sm font-medium block mb-2">Title</label>
          <input
            type="text"
            className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="Task title..."
            required
          />
        </div>

        <div>
          <label className="text-sm font-medium block mb-2">Description (optional)</label>
          <textarea
            className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm min-h-[220px]"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Task description..."
          />
        </div>

        {formData.isRecurring && (
          <>
            <div>
              <label className="text-sm font-medium block mb-2">Schedule Type</label>
              <select
                className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm"
                value={formData.scheduleType}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    scheduleType: e.target.value as any,
                  })
                }
              >
                <option value="INTERVAL">Interval</option>
                <option value="HOURLY">Hourly</option>
                <option value="DAILY">Daily</option>
                <option value="WEEKLY">Weekly</option>
              </select>
            </div>

            {formData.scheduleType === 'INTERVAL' && (
              <div>
                <label className="text-sm font-medium block mb-2">
                  Interval (minutes)
                </label>
                <input
                  type="number"
                  className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm"
                  value={formData.intervalMinutes}
                  onChange={(e) =>
                    setFormData({ ...formData, intervalMinutes: Number(e.target.value) })
                  }
                  min={1}
                />
              </div>
            )}

            {(formData.scheduleType === 'DAILY' || formData.scheduleType === 'HOURLY') && (
              <div>
                <label className="text-sm font-medium block mb-2">Time</label>
                <input
                  type="time"
                  className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm"
                  value={formData.dailyTime}
                  onChange={(e) => setFormData({ ...formData, dailyTime: e.target.value })}
                />
              </div>
            )}

            {formData.scheduleType === 'WEEKLY' && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium block mb-2">Day of Week</label>
                  <select
                    className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm"
                    value={formData.weeklyDay}
                    onChange={(e) =>
                      setFormData({ ...formData, weeklyDay: e.target.value })
                    }
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
                <div>
                  <label className="text-sm font-medium block mb-2">Time</label>
                  <input
                    type="time"
                    className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm"
                    value={formData.dailyTime}
                    onChange={(e) =>
                      setFormData({ ...formData, dailyTime: e.target.value })
                    }
                  />
                </div>
              </div>
            )}
          </>
        )}

        <div className="flex gap-2 pt-4 border-t border-border">
          <Button type="button" variant="secondary" onClick={onClose} className="flex-1">
            Cancel
          </Button>
          <Button type="submit" variant="primary" className="flex-1">
            Create {formData.isRecurring ? 'Recurring' : ''} Task
          </Button>
        </div>
      </form>
    </Modal>
  );
}
