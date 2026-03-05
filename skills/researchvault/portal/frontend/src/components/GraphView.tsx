import { useEffect, useMemo, useState } from 'react';
import { Network, RefreshCw, Sparkles } from 'lucide-react';

import type { GraphEdge, GraphNode, GraphResponse, VaultRunResult } from '@/lib/api';
import { runVaultPost, systemGet } from '@/lib/api';

type Pos = { x: number; y: number };

function edgeColor(t: string): string {
  if ((t || '').includes('SYNTHESIS')) return '#00f0ff';
  return '#bd00ff';
}

function nodeColor(n: GraphNode): string {
  return n.type === 'finding' ? '#00f0ff' : '#ffae00';
}

function layout(nodes: GraphNode[], width: number, height: number): Record<string, Pos> {
  const findings = nodes.filter((n) => n.type === 'finding');
  const artifacts = nodes.filter((n) => n.type === 'artifact');

  const pos: Record<string, Pos> = {};
  const padY = 40;
  const usableH = Math.max(200, height - padY * 2);

  const place = (arr: GraphNode[], x: number) => {
    const n = arr.length;
    for (let i = 0; i < n; i += 1) {
      const y = padY + ((i + 1) / (n + 1)) * usableH;
      pos[arr[i].id] = { x, y };
    }
  };

  place(findings, width * 0.25);
  place(artifacts, width * 0.75);

  // If only one side exists, fall back to a single column on the left.
  if (findings.length === 0 || artifacts.length === 0) {
    const x = 80; // Left margin instead of center
    place(nodes, x);
  }

  return pos;
}

function bezier(a: Pos, b: Pos): string {
  const mid = (a.x + b.x) / 2;
  return `M ${a.x} ${a.y} C ${mid} ${a.y}, ${mid} ${b.y}, ${b.x} ${b.y}`;
}

export default function GraphView({
  projectId,
  refreshKey,
  onCommandResult,
}: {
  projectId: string | null;
  refreshKey: number;
  onCommandResult?: (r: VaultRunResult) => void;
}) {
  const [loading, setLoading] = useState(false);
  const [synthing, setSynthing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [graph, setGraph] = useState<GraphResponse | null>(null);
  const [selected, setSelected] = useState<GraphNode | null>(null);

  const width = 800;
  const height = 600;

  async function refresh() {
    if (!projectId) return;
    setLoading(true);
    setError(null);
    try {
      const g = await systemGet<GraphResponse>(`/graph?project_id=${encodeURIComponent(projectId)}&limit=250`);
      setGraph(g);
      setSelected(null);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
      setGraph(null);
      setSelected(null);
    } finally {
      setLoading(false);
    }
  }

  async function synthesize() {
    if (!projectId) return;
    setSynthing(true);
    setError(null);
    try {
      const res = await runVaultPost('/vault/synthesize', { id: projectId, format: 'json' });
      onCommandResult?.(res);
      if (res.ok) {
        await refresh();
      } else {
        setError(res.stderr || 'synthesize failed');
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSynthing(false);
    }
  }

  useEffect(() => {
    refresh();
     
  }, [projectId, refreshKey]);

  const nodes = graph?.nodes ?? [];
  const edges = graph?.edges ?? [];

  const positions = useMemo(() => layout(nodes, width, height), [nodes, width, height]);
  const byId = useMemo(() => new Map(nodes.map((n) => [n.id, n])), [nodes]);

  if (!projectId) {
    return (
      <div className="bg-void-surface border border-white/10 rounded-lg p-6">
        <div className="flex items-center gap-2 text-gray-100 font-semibold">
          <Network className="h-5 w-5 text-bio" /> Graph View
        </div>
        <div className="text-sm text-gray-400 mt-2">Select a project in Command mode, then come back here.</div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div className="lg:col-span-2 bg-void-surface border border-white/10 rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-white/10 flex items-center justify-between">
          <div>
            <div className="text-xs uppercase tracking-wider text-gray-400 font-mono">Graph</div>
            <div className="text-sm text-gray-100 font-mono">{projectId}</div>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-xs font-mono text-gray-400">
              nodes:{nodes.length} edges:{edges.length}
            </div>
            <button
              type="button"
              onClick={synthesize}
              className="text-xs font-mono px-3 py-1.5 rounded border border-bio text-bio bg-bio-dim hover:border-bio/80 disabled:opacity-50"
              disabled={loading || synthing}
              title="Run local synthesis to generate links"
            >
              <Sparkles className={`inline h-3.5 w-3.5 mr-1 ${synthing ? 'animate-pulse' : ''}`} />
              Synthesize
            </button>
            <button
              type="button"
              onClick={refresh}
              className="text-xs font-mono px-3 py-1.5 rounded border border-white/10 text-gray-300 hover:text-white hover:border-white/20"
              disabled={loading || synthing}
            >
              <RefreshCw className={`inline h-3.5 w-3.5 mr-1 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {error && <div className="p-4 text-sm text-red-200 font-mono">{error}</div>}

        {!error && (
          <div className="p-4">
            <svg
              viewBox={`0 0 ${width} ${height}`}
              className="w-full h-[520px] rounded border border-white/5"
              style={{ background: 'transparent' }}
            >
              <defs>
                <linearGradient id="edgeGlow" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#00f0ff" stopOpacity="0.15" />
                  <stop offset="100%" stopColor="#bd00ff" stopOpacity="0.15" />
                </linearGradient>
              </defs>

              {/* Edges */}
              {edges.map((e: GraphEdge) => {
                const a = positions[e.source];
                const b = positions[e.target];
                if (!a || !b) return null;
                return (
                  <path
                    key={String(e.id)}
                    d={bezier(a, b)}
                    stroke={edgeColor(e.type)}
                    strokeOpacity={0.5}
                    strokeWidth={1.25}
                    fill="none"
                  />
                );
              })}

              {nodes.map((n: GraphNode) => {
                const p = positions[n.id];
                if (!p) return null;
                const active = selected?.id === n.id;
                return (
                  <g
                    key={n.id}
                    onClick={() => setSelected(n)}
                    className="cursor-pointer"
                    style={{ pointerEvents: 'all' }}
                  >
                    <circle cx={p.x} cy={p.y} r={active ? 16 : 12} fill={nodeColor(n)} fillOpacity={active ? 0.9 : 0.65} />
                    <circle
                      cx={p.x}
                      cy={p.y}
                      r={active ? 24 : 20}
                      fill="none"
                      stroke={nodeColor(n)}
                      strokeOpacity={active ? 0.35 : 0.15}
                      strokeWidth={3}
                    />
                    <text x={p.x + 28} y={p.y + 6} fontSize="18" fill={active ? '#fff' : '#cbd5e1'} style={{ pointerEvents: 'none' }}>
                      {n.label}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
        )}
      </div>

      <div className="lg:col-span-1 bg-void-surface border border-white/10 rounded-lg">
        <div className="px-4 py-3 border-b border-white/10">
          <div className="text-xs uppercase tracking-wider text-gray-400 font-mono">Node Detail</div>
        </div>
        <div className="p-4 space-y-3">
          {!selected && <div className="text-sm text-gray-400">Click a node to inspect it.</div>}
          {selected && (
            <>
              <div className="text-sm text-gray-100 font-semibold break-words">{selected.label}</div>
              <div className="text-xs font-mono text-gray-500 break-all">{selected.id}</div>
              <div className="text-xs font-mono text-gray-400 break-words">
                type:{selected.type}
                {typeof selected.confidence === 'number' ? ` | conf:${selected.confidence.toFixed(2)}` : ''}
              </div>
              {selected.tags && <div className="text-xs text-gray-300 break-words">tags: {selected.tags}</div>}
              {selected.path && (
                <div className="text-xs text-gray-300 break-all">
                  path: <span className="font-mono text-gray-400">{selected.path}</span>
                </div>
              )}

              <div className="pt-3 border-t border-white/10">
                <div className="text-xs uppercase tracking-wider text-gray-500 font-mono mb-2">Connected</div>
                <div className="space-y-1">
                  {edges
                    .filter((e) => e.source === selected.id || e.target === selected.id)
                    .slice(0, 12)
                    .map((e) => {
                      const otherId = e.source === selected.id ? e.target : e.source;
                      const other = byId.get(otherId);
                      return (
                        <div key={String(e.id)} className="text-xs text-gray-300">
                          <span className="font-mono text-gray-500">{e.type}</span> → {other?.label ?? otherId}
                        </div>
                      );
                    })}
                  {edges.filter((e) => e.source === selected.id || e.target === selected.id).length === 0 && (
                    <div className="text-xs text-gray-500">No links yet. Run synthesis to generate edges.</div>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
