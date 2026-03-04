import { useEffect, useMemo, useRef, useState } from 'react';

import type { SystemDbsResponse, ResolvedDb } from '@/lib/api';
import { systemStreamUrl } from '@/lib/api';

export type StreamStatus = {
  state: 'idle' | 'connecting' | 'open' | 'reconnecting' | 'error';
  lastEventMs: number | null;
  lastError: string | null;
  reconnectInMs: number | null;
};

export type StreamHandlers = {
  onHello?: (payload: { now_ms: number; db: ResolvedDb }) => void;
  onPulse?: (payload: { now_ms: number; db: ResolvedDb }) => void;
  onDbs?: (payload: SystemDbsResponse) => void;
};

function jitter(ms: number): number {
  const j = Math.floor(Math.random() * Math.min(250, Math.max(50, ms * 0.1)));
  return ms + j;
}

export function usePortalStream(enabled: boolean, handlers: StreamHandlers, intervalS = 2): StreamStatus {
  const url = useMemo(() => systemStreamUrl(intervalS), [intervalS]);
  const [status, setStatus] = useState<StreamStatus>({
    state: enabled ? 'connecting' : 'idle',
    lastEventMs: null,
    lastError: null,
    reconnectInMs: null,
  });

  const handlersRef = useRef<StreamHandlers>(handlers);
  handlersRef.current = handlers;

  const ref = useRef<{
    es: EventSource | null;
    closed: boolean;
    retryMs: number;
    timer: number | null;
    countdownTimer: number | null;
  }>({ es: null, closed: false, retryMs: 500, timer: null, countdownTimer: null });

  useEffect(() => {
    ref.current.closed = false;
    if (!enabled) {
      if (ref.current.es) ref.current.es.close();
      ref.current.es = null;
      if (ref.current.timer) window.clearTimeout(ref.current.timer);
      if (ref.current.countdownTimer) window.clearInterval(ref.current.countdownTimer);
      setStatus({ state: 'idle', lastEventMs: null, lastError: null, reconnectInMs: null });
      return;
    }

    const connect = () => {
      if (ref.current.closed) return;
      setStatus((s) => ({ ...s, state: s.state === 'open' ? 'reconnecting' : 'connecting', lastError: null, reconnectInMs: null }));

      const es = new EventSource(url, { withCredentials: true });
      ref.current.es = es;

      const markEvent = () => {
        setStatus((s) => ({ ...s, lastEventMs: Date.now() }));
      };

      es.onopen = () => {
        ref.current.retryMs = 500;
        markEvent();
        setStatus((s) => ({ ...s, state: 'open', lastError: null, reconnectInMs: null }));
      };

      es.addEventListener('hello', (e) => {
        markEvent();
        try {
          const payload = JSON.parse((e as MessageEvent).data);
          handlersRef.current.onHello?.(payload);
        } catch {
          // Ignore malformed payloads; stream must stay resilient.
        }
      });

      es.addEventListener('pulse', (e) => {
        markEvent();
        try {
          const payload = JSON.parse((e as MessageEvent).data);
          handlersRef.current.onPulse?.(payload);
        } catch {
          // ignore
        }
      });

      es.addEventListener('dbs', (e) => {
        markEvent();
        try {
          const payload = JSON.parse((e as MessageEvent).data);
          handlersRef.current.onDbs?.(payload);
        } catch {
          // ignore
        }
      });

      es.addEventListener('keepalive', () => {
        markEvent();
      });

      es.onerror = () => {
        if (ref.current.closed) return;
        try {
          es.close();
        } catch {
          // ignore
        }

        const next = Math.min(10_000, ref.current.retryMs * 2);
        const delay = jitter(ref.current.retryMs);
        ref.current.retryMs = next;

        // Update UI with a countdown until next reconnect attempt.
        const start = Date.now();
        setStatus((s) => ({
          ...s,
          state: 'error',
          lastError: 'Stream disconnected',
          reconnectInMs: delay,
        }));

        if (ref.current.countdownTimer) window.clearInterval(ref.current.countdownTimer);
        ref.current.countdownTimer = window.setInterval(() => {
          const remaining = Math.max(0, delay - (Date.now() - start));
          setStatus((s) => ({ ...s, reconnectInMs: remaining }));
        }, 250);

        if (ref.current.timer) window.clearTimeout(ref.current.timer);
        ref.current.timer = window.setTimeout(() => {
          if (ref.current.countdownTimer) window.clearInterval(ref.current.countdownTimer);
          ref.current.countdownTimer = null;
          connect();
        }, delay);
      };
    };

    connect();

    const onOnline = () => {
      if (!ref.current.es && !ref.current.closed) connect();
    };
    window.addEventListener('online', onOnline);

    return () => {
      ref.current.closed = true;
      window.removeEventListener('online', onOnline);
      if (ref.current.es) ref.current.es.close();
      ref.current.es = null;
      if (ref.current.timer) window.clearTimeout(ref.current.timer);
      if (ref.current.countdownTimer) window.clearInterval(ref.current.countdownTimer);
    };
     
  }, [enabled, url]);

  return status;
}
