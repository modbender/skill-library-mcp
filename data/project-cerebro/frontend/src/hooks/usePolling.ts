import { useEffect, useRef, useCallback } from 'react';

interface UsePollingOptions {
  interval?: number;
  enabled?: boolean;
}

export function usePolling(
  callback: () => void | Promise<void>,
  { interval = 3000, enabled = true }: UsePollingOptions = {}
) {
  const savedCallback = useRef(callback);
  const timerRef = useRef<ReturnType<typeof setInterval> | undefined>(undefined);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  const tick = useCallback(async () => {
    await savedCallback.current();
  }, []);

  useEffect(() => {
    if (!enabled) {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      return;
    }

    // Call immediately
    tick();

    // Then poll at interval
    timerRef.current = setInterval(tick, interval);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [interval, enabled, tick]);
}
