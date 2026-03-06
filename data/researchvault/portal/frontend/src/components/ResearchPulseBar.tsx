import { useMemo } from 'react';
import { Activity, Database, Network, Wrench } from 'lucide-react';

import type { DbCandidate, SystemDbsResponse } from '@/lib/api';
import type { StreamStatus } from '@/lib/usePortalStream';

type Mode = 'command' | 'graph' | 'diagnostics';

function basename(p: string): string {
  const parts = (p || '').split('/');
  return parts[parts.length - 1] || p;
}

function humanBytes(n: number | null | undefined): string {
  if (!n || n <= 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let v = n;
  let i = 0;
  while (v >= 1024 && i < units.length - 1) {
    v /= 1024;
    i += 1;
  }
  return `${v.toFixed(v >= 10 || i === 0 ? 0 : 1)} ${units[i]}`;
}

function candidateLabel(c: DbCandidate): string {
  const p = basename(c.path);
  const projects = c.counts?.projects;
  const findings = c.counts?.findings;
  const pStr = typeof projects === 'number' ? String(projects) : '?';
  const fStr = typeof findings === 'number' ? String(findings) : '?';
  const mark = c.exists ? '' : ' (missing)';
  return `${p} | projects:${pStr} findings:${fStr}${mark}`;
}

export default function ResearchPulseBar({
  mode,
  setMode,
  dbs,
  stream,
  onSelectDb,
  onRefreshDbs,
}: {
  mode: Mode;
  setMode: (m: Mode) => void;
  dbs: SystemDbsResponse | null;
  stream: StreamStatus;
  onSelectDb: (path: string | null) => void;
  onRefreshDbs: () => void;
}) {
  const current = dbs?.current;
  const candidates = dbs?.candidates ?? [];

  const streamDot = useMemo(() => {
    if (stream.state === 'open') return 'bg-green-400';
    if (stream.state === 'connecting' || stream.state === 'reconnecting') return 'bg-amber';
    if (stream.state === 'idle') return 'bg-gray-500';
    return 'bg-red-400';
  }, [stream.state]);

  return (
    <div className="bg-void-panel border-b border-white/10">
      <div className="max-w-6xl mx-auto px-6 py-3 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className={`h-2 w-2 rounded-full ${streamDot} shadow-[0_0_12px_rgba(0,240,255,0.35)]`} />
            <div className="text-xs uppercase tracking-wider text-gray-400 font-mono">Research Pulse</div>
          </div>

          <div className="hidden md:flex items-center gap-2 text-xs text-gray-400">
            <Activity className="h-3.5 w-3.5 text-cyan" />
            <span>
              {stream.state === 'open'
                ? 'live'
                : stream.reconnectInMs != null
                  ? `reconnect in ${(stream.reconnectInMs / 1000).toFixed(1)}s`
                  : stream.state}
            </span>
          </div>
        </div>

        <div className="flex flex-col gap-2 md:flex-row md:items-center md:gap-3">
          <div className="flex items-center gap-2">
            <Database className="h-4 w-4 text-cyan text-glow" />
            <select
              value={current?.path ?? ''}
              onChange={(e) => onSelectDb(e.target.value || null)}
              className="bg-void-surface border border-white/10 text-gray-200 text-xs font-mono rounded px-2 py-1.5 max-w-[22rem] w-full md:w-[22rem]"
              title={current?.note ?? ''}
            >
              {candidates.length === 0 ? (
                <option value="">Scanning vault DBs…</option>
              ) : (
                candidates.map((c) => (
                  <option key={c.path} value={c.path}>
                    {candidateLabel(c)}
                  </option>
                ))
              )}
            </select>

            <button
              type="button"
              onClick={onRefreshDbs}
              className="text-xs font-mono px-2 py-1.5 rounded border border-white/10 text-gray-300 hover:text-white hover:border-white/20"
              title="Rescan DBs"
            >
              Rescan
            </button>
          </div>

          <div className="flex items-center gap-2 text-xs text-gray-400 font-mono">
            <span className="hidden sm:inline">
              {current?.counts
                ? `projects:${typeof current.counts.projects === 'number' ? current.counts.projects : '?'} findings:${
                    typeof current.counts.findings === 'number' ? current.counts.findings : '?'
                  }`
                : 'counts: n/a'}
            </span>
            <span className="hidden sm:inline text-gray-600">|</span>
            <span className="hidden sm:inline">{humanBytes(current?.size_bytes ?? null)}</span>
            <span className="hidden md:inline text-gray-600">|</span>
            <span className="hidden md:inline">src:{current?.source ?? 'auto'}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setMode('command')}
              className={`text-xs font-mono px-3 py-1.5 rounded border ${
                mode === 'command'
                  ? 'border-cyan text-cyan bg-cyan-dim'
                  : 'border-white/10 text-gray-300 hover:text-white hover:border-white/20'
              }`}
              title="Command Center"
            >
              <Network className="inline h-3.5 w-3.5 mr-1" />
              Command
            </button>

            <button
              type="button"
              onClick={() => setMode('graph')}
              className={`text-xs font-mono px-3 py-1.5 rounded border ${
                mode === 'graph'
                  ? 'border-bio text-bio bg-bio-dim'
                  : 'border-white/10 text-gray-300 hover:text-white hover:border-white/20'
              }`}
              title="Graph View"
            >
              <Network className="inline h-3.5 w-3.5 mr-1" />
              Graph
            </button>

            <button
              type="button"
              onClick={() => setMode('diagnostics')}
              className={`text-xs font-mono px-3 py-1.5 rounded border ${
                mode === 'diagnostics'
                  ? 'border-amber text-amber bg-amber/10'
                  : 'border-white/10 text-gray-300 hover:text-white hover:border-white/20'
              }`}
              title="Diagnostics"
            >
              <Wrench className="inline h-3.5 w-3.5 mr-1" />
              Diag
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
