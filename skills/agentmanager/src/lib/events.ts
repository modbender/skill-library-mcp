import type { Run } from '../types.js';
import { getConfig } from '../config.js';

const maxEventsPerRun = (): number => getConfig().MAX_EVENTS_PER_RUN;

export const appendRunEvent = (
  run: Run,
  type: string,
  data?: Record<string, unknown>,
  taskName?: string
): void => {
  const seq = run.logs_base + run.logs.length + 1;
  run.logs.push({ seq, ts: Date.now(), type, run_id: run.id, task_name: taskName, data });
  const limit = maxEventsPerRun();
  if (run.logs.length > limit) {
    const drop = run.logs.length - limit;
    run.logs.splice(0, drop);
    run.logs_base += drop;
    run.metrics.events_truncated = true;
  }
};
