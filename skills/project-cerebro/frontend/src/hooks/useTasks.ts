import { useState, useCallback, useRef } from 'react';
import { api } from '../api/client';
import type { Task } from '../api/types';
import { usePolling } from './usePolling';

export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const pendingDeleteRef = useRef<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetch = useCallback(async () => {
    try {
      const data = await api.getTasks();
      const incoming = data.tasks || [];
      // Don’t let polling re-introduce items we’re deleting optimistically.
      const filtered = incoming.filter((t: Task) => !pendingDeleteRef.current.has(t.id));
      setTasks(filtered);
      setError(null);
    } catch (e) {
      setError(e as Error);
      console.error('Failed to fetch tasks:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  usePolling(fetch);

  const createTask = useCallback(
    async (taskData: {
      brainId: string;
      title: string;
      description?: string;
      modelOverride?: string;
    }) => {
      try {
        await api.createTask(taskData);
        await fetch();
      } catch (e) {
        console.error('Failed to create task:', e);
        throw e;
      }
    },
    [fetch]
  );

  const deleteTask = useCallback(
    async (id: string) => {
      // Optimistic UI: remove immediately, then confirm with API.
      const prev = tasks;
      pendingDeleteRef.current.add(id);
      setTasks((cur) => cur.filter((t) => t.id !== id));

      try {
        await api.deleteTask(id);
        pendingDeleteRef.current.delete(id);
        // Best-effort refresh (keeps other status changes in sync)
        await fetch();
      } catch (e) {
        console.error('Failed to delete task:', e);
        pendingDeleteRef.current.delete(id);
        // Revert on failure
        setTasks(prev);
      }
    },
    [fetch, tasks]
  );

  const executeTask = useCallback(
    async (id: string) => {
      try {
        await api.executeTask(id);
        // Wait a bit then refresh to see status change
        setTimeout(fetch, 1000);
      } catch (e) {
        console.error('Failed to execute task:', e);
      }
    },
    [fetch]
  );

  const clearAllTasks = useCallback(async () => {
    try {
      await api.clearAllTasks();
      await fetch();
    } catch (e) {
      console.error('Failed to clear tasks:', e);
    }
  }, [fetch]);

  const updateTask = useCallback(
    async (
      id: string,
      data: {
        brainId?: string;
        title?: string;
        description?: string;
        modelOverride?: string;
        sendDiscordNotification?: boolean;
      }
    ) => {
      try {
        await api.updateTask(id, data);
        await fetch();
      } catch (e) {
        console.error('Failed to update task:', e);
        throw e;
      }
    },
    [fetch]
  );

  return {
    tasks,
    loading,
    error,
    createTask,
    deleteTask,
    executeTask,
    updateTask,
    clearAllTasks,
    refetch: fetch,
  };
}
