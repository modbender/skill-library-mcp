import { useState, useCallback, useRef } from 'react';
import { api } from '../api/client';
import type { RecurringTask } from '../api/types';
import { usePolling } from './usePolling';

export function useRecurring() {
  const [recurringTasks, setRecurringTasks] = useState<RecurringTask[]>([]);
  const pendingDeleteRef = useRef<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetch = useCallback(async () => {
    try {
      const data = await api.getRecurringTasks();
      const incoming = data.recurringTasks || [];
      const filtered = incoming.filter((t: RecurringTask) => !pendingDeleteRef.current.has(t.id));
      setRecurringTasks(filtered);
      setError(null);
    } catch (e) {
      setError(e as Error);
      console.error('Failed to fetch recurring tasks:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  usePolling(fetch);

  const createRecurringTask = useCallback(
    async (taskData: {
      brainId: string;
      title: string;
      description?: string;
      modelOverride?: string;
      scheduleType: 'INTERVAL' | 'HOURLY' | 'DAILY' | 'WEEKLY';
      intervalMinutes?: number;
      scheduleConfig?: Record<string, unknown>;
      sendDiscordNotification?: boolean;
      triggersReport?: boolean;
      reportDelayMinutes?: number;
    }) => {
      try {
        await api.createRecurringTask(taskData);
        await fetch();
      } catch (e) {
        console.error('Failed to create recurring task:', e);
        throw e;
      }
    },
    [fetch]
  );

  const updateRecurringTask = useCallback(
    async (
      id: string,
      taskData: {
        brainId?: string;
        title?: string;
        description?: string;
        modelOverride?: string;
        scheduleType?: 'INTERVAL' | 'HOURLY' | 'DAILY' | 'WEEKLY';
        intervalMinutes?: number;
        scheduleConfig?: Record<string, unknown>;
        sendDiscordNotification?: boolean;
        triggersReport?: boolean;
        reportDelayMinutes?: number;
      }
    ) => {
      try {
        console.log('Updating recurring task:', id, taskData);
        await api.updateRecurringTask(id, taskData);
        console.log('Update successful, refreshing...');
        await fetch();
      } catch (e) {
        console.error('Failed to update recurring task:', e);
        throw e;
      }
    },
    [fetch]
  );

  const toggleRecurringTask = useCallback(
    async (id: string, enabled: boolean) => {
      try {
        await api.toggleRecurringTask(id, enabled);
        await fetch();
      } catch (e) {
        console.error('Failed to toggle recurring task:', e);
      }
    },
    [fetch]
  );

  const runRecurringTask = useCallback(
    async (id: string) => {
      try {
        await api.runRecurringTask(id);
        await fetch();
      } catch (e) {
        console.error('Failed to run recurring task:', e);
      }
    },
    [fetch]
  );

  const deleteRecurringTask = useCallback(
    async (id: string) => {
      // Optimistic UI: remove immediately, then confirm with API.
      const prev = recurringTasks;
      pendingDeleteRef.current.add(id);
      setRecurringTasks((cur) => cur.filter((t) => t.id !== id));

      try {
        await api.deleteRecurringTask(id);
        pendingDeleteRef.current.delete(id);
        await fetch();
      } catch (e) {
        console.error('Failed to delete recurring task:', e);
        pendingDeleteRef.current.delete(id);
        setRecurringTasks(prev);
      }
    },
    [fetch, recurringTasks]
  );

  return {
    recurringTasks,
    loading,
    error,
    createRecurringTask,
    updateRecurringTask,
    toggleRecurringTask,
    runRecurringTask,
    deleteRecurringTask,
    refetch: fetch,
  };
}
