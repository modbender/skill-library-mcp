import { useEffect, useMemo, useRef, useState, type ComponentType, type MouseEvent } from 'react';
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  CheckCircle,
  Copy,
  Download,
  FolderPlus,
  FolderSearch,
  GitBranch,
  Globe,
  Lightbulb,
  Play,
  RefreshCw,
  Search,
  Share2,
  Target,
  Terminal,
} from 'lucide-react';

import DecryptedText from '@/components/DecryptedText';
import SpotlightCard from '@/components/SpotlightCard';
import DiagnosticsPanel from '@/components/DiagnosticsPanel';
import GraphView from '@/components/GraphView';
import ResearchPulseBar from '@/components/ResearchPulseBar';

import {
  apiJson,
  runVaultGet,
  runVaultPost,
  systemGet,
  systemPost,
  type Branch,
  type Insight,
  type Project,
  type SecretsStatusResponse,
  type StatusData,
  type SystemDbsResponse,
  type VaultRunResult,
  type VerificationMission,
} from '@/lib/api';
import { usePortalStream } from '@/lib/usePortalStream';

function CommandOutput({ result }: { result: VaultRunResult | null }) {
  if (!result) {
    return <div className="text-gray-400 italic text-sm p-4">No commands executed yet.</div>;
  }

  const cmd = result.argv.length >= 3 ? result.argv.slice(2).join(' ') : result.argv.join(' ');

  return (
    <div className="bg-gray-900 text-gray-100 p-4 rounded-md font-mono text-xs overflow-auto max-h-72 border border-gray-800 shadow-inner">
      <div className="flex gap-2 mb-2 border-b border-gray-800 pb-2">
        <span className="text-green-400">$ {cmd}</span>
        <span className={result.exit_code === 0 ? 'text-gray-500' : 'text-red-400'}>(exit {result.exit_code}{result.truncated ? ', truncated' : ''})</span>
      </div>
      {result.db_path && (
        <div className="text-[11px] text-gray-400 mb-2">
          DB: <span className="text-gray-300 break-all">{result.db_path}</span>
          {result.db_source ? <span className="text-gray-500"> (src:{result.db_source})</span> : null}
        </div>
      )}
      {result.stderr && (
        <pre className="text-red-300 whitespace-pre-wrap mb-2">{result.stderr}</pre>
      )}
      <pre className="text-gray-200 whitespace-pre-wrap">{result.stdout}</pre>
    </div>
  );
}

function EntryScreen({
  onSelectProject,
  setLastResult,
  refreshKey,
  dbs,
  onSelectDb,
  secrets,
  onOpenDiagnostics,
}: {
  onSelectProject: (id: string) => void;
  setLastResult: (r: VaultRunResult) => void;
  refreshKey: number;
  dbs: SystemDbsResponse | null;
  onSelectDb: (path: string) => void;
  secrets: SecretsStatusResponse | null;
  onOpenDiagnostics: () => void;
}) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [showNew, setShowNew] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [newId, setNewId] = useState('');
  const [newName, setNewName] = useState('');
  const [newObjective, setNewObjective] = useState('');
  const [newPriority, setNewPriority] = useState(0);
  const [autoSeed, setAutoSeed] = useState(true);

  const [searchQuery, setSearchQuery] = useState('');

  const braveConfigured = secrets?.brave_api_key_configured ?? false;
  const serperConfigured = secrets?.serper_api_key_configured ?? false;
  const searxngConfigured = secrets?.searxng_base_url_configured ?? false;
  const apiBackedSearchReady = braveConfigured || serperConfigured || searxngConfigured;

  function slugify(raw: string): string {
    return (raw || '')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+/, '')
      .replace(/-+$/, '');
  }

  async function handleListProjects(showInConsole: boolean) {
    setError(null);
    setLoading(true);
    try {
      const res = await runVaultGet('/vault/list');
      if (showInConsole) setLastResult(res);

      if (!res.ok) {
        throw new Error(res.stderr || 'vault list failed');
      }

      const parsed = JSON.parse(res.stdout) as Project[];
      setProjects(parsed);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  async function handleInit() {
    setError(null);
    setLoading(true);
    try {
      const payload: any = {
        name: newName || null,
        objective: newObjective,
        priority: newPriority,
      };
      if (newId.trim()) {
        payload.id = newId;
      }
      const res = await runVaultPost('/vault/init', payload);
      setLastResult(res);

      if (!res.ok) {
        throw new Error(res.stderr || 'vault init failed');
      }

      const createdId = (newId.trim() || slugify(newName)).trim();

      // Optional: create a watch target from the objective and run watchdog once.
      // This makes "new project" immediately produce research output (via configured providers or fallbacks).
      if (autoSeed) {
        const seedQuery = (newObjective || newName || '').trim().slice(0, 200);
        if (createdId && seedQuery) {
          const w = await runVaultPost('/vault/watch/add', { id: createdId, type: 'query', target: seedQuery, interval: 6 * 60 * 60 });
          setLastResult(w);
          if (!w.ok) {
            setError(w.stderr || 'vault watch add failed');
          } else {
            const wd = await runVaultPost('/vault/watchdog/once', { id: createdId, limit: 3, dry_run: false });
            setLastResult(wd);
            if (!wd.ok) {
              const err = (wd.stderr || '').toLowerCase();
              if (
                err.includes('brave_api_key') ||
                err.includes('serper_api_key') ||
                err.includes('searxng_base_url') ||
                err.includes('missing api key') ||
                err.includes('provider not configured') ||
                err.includes('no usable search provider') ||
                err.includes('not configured')
              ) {
                setError(
                  "Auto-seed created a watch target, but search is blocked due to provider setup. Open Diagnostics to configure Brave/Serper/SearxNG (recommended), then run Watchdog again.",
                );
              } else {
                setError(wd.stderr || 'vault watchdog once failed');
              }
            }
          }
        }
      }

      await handleListProjects(false);
      if (createdId) onSelectProject(createdId);

      setShowNew(false);
      setNewId('');
      setNewName('');
      setNewObjective('');
      setNewPriority(0);
      setShowAdvanced(false);
      setAutoSeed(true);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch() {
    setError(null);
    setLoading(true);
    try {
      const res = await runVaultPost('/vault/search', { query: searchQuery });
      setLastResult(res);
      if (!res.ok) throw new Error(res.stderr || 'vault search failed');
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // Populate the table, but do not spam the console.
    // refreshKey ticks whenever the DB changes (SSE pulse) or the user switches DBs.
    handleListProjects(false).catch(() => undefined);
     
  }, [refreshKey]);

  const recommendedDb = useMemo(() => {
    const currentProjects = dbs?.current.counts?.projects ?? null;
    if (currentProjects === null) return null;
    if (currentProjects > 0) return null;
    const best = (dbs?.candidates ?? [])
      .filter((c) => (c.counts?.projects ?? 0) > 0)
      .sort((a, b) => (b.counts?.projects ?? 0) - (a.counts?.projects ?? 0))[0];
    return best ?? null;
  }, [dbs]);

  return (
    <div className="space-y-6">
      {recommendedDb && (
        <div className="border border-amber/40 bg-amber/10 text-amber rounded-lg p-4">
          <div className="font-mono text-xs uppercase tracking-wider">DB Split Detected</div>
          <div className="text-sm text-gray-200 mt-1">
            Your active DB looks empty, but another vault DB contains projects.
          </div>
          <div className="mt-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-xs font-mono text-gray-300 break-all">{recommendedDb.path}</div>
            <button
              type="button"
              onClick={() => onSelectDb(recommendedDb.path)}
              className="text-xs font-mono px-3 py-1.5 rounded border border-cyan text-cyan bg-cyan-dim"
            >
              Switch DB
            </button>
          </div>
        </div>
      )}

      {!loading && projects.length === 0 && !apiBackedSearchReady && (
        <div className="border border-cyan/30 bg-cyan-dim/40 rounded-lg p-4">
          <div className="font-mono text-xs uppercase tracking-wider text-cyan">Setup Recommended</div>
          <div className="text-sm text-gray-200 mt-1">
            Query-based research works best with an API-backed search provider. You can still run best-effort fallbacks (DuckDuckGo/Wikipedia),
            but for consistent results configure a provider key.
          </div>
          <div className="mt-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-xs font-mono text-gray-300">
              Brave:{braveConfigured ? 'on' : 'off'} | Serper:{serperConfigured ? 'on' : 'off'} | SearxNG:{searxngConfigured ? 'on' : 'off'}
            </div>
            <button
              type="button"
              onClick={onOpenDiagnostics}
              className="text-xs font-mono px-3 py-1.5 rounded border border-cyan text-cyan bg-cyan-dim hover:border-cyan/80"
            >
              Open Diagnostics
            </button>
          </div>
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={() => handleListProjects(true)}
          className="flex items-center justify-center gap-2 p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-50 transition"
        >
          <RefreshCw className="w-5 h-5 text-blue-600" />
          <span className="font-semibold text-gray-800">LIST</span>
        </button>

        <button
          onClick={() => setShowNew((v) => !v)}
          className="flex items-center justify-center gap-2 p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-50 transition shadow-[0_0_15px_rgba(0,255,100,0.1)]"
        >
          <FolderPlus className="w-5 h-5 text-green-600" />
          <span className="font-semibold text-gray-800">NEW PROJECT</span>
        </button>

        <div className="flex p-0 bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
          <input
            className="flex-1 p-4 outline-none text-gray-900 placeholder:text-gray-400"
            placeholder="SEARCH (vault search)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleSearch();
            }}
          />
          <button
            onClick={handleSearch}
            className="px-4 hover:bg-gray-50"
            disabled={!searchQuery.trim() || loading}
            aria-label="Search"
          >
            <Search className="w-5 h-5 text-purple-600" />
          </button>
        </div>
      </div>

      {showNew && (
        <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg shadow-md animate-in fade-in zoom-in duration-300">
          <div className="flex items-center gap-2 mb-3">
            <FolderSearch className="w-4 h-4 text-gray-600" />
            <div className="font-bold text-gray-700">Initialize New Project</div>
          </div>

          <div className="grid grid-cols-1 gap-3">
            <input
              className="w-full p-2 border border-gray-300 rounded text-gray-900 placeholder:text-gray-400"
              placeholder="Project Name (e.g. 'Best Pizza 2026')"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
            />
            <textarea
              className="w-full p-2 border border-gray-300 rounded h-24 text-gray-900 placeholder:text-gray-400"
              placeholder="Objective (What are we solving?)"
              value={newObjective}
              onChange={(e) => setNewObjective(e.target.value)}
            />

            <label className="flex items-start gap-2 text-xs text-gray-600">
              <input
                type="checkbox"
                className="mt-0.5"
                checked={autoSeed}
                onChange={(e) => setAutoSeed(e.target.checked)}
              />
              <span>
                Auto-seed research: create a watchdog query from the objective and run it once.
                {!apiBackedSearchReady ? (
                  <span className="block text-[11px] text-amber mt-1">
                    No API-backed provider configured. Auto-seed will use best-effort fallbacks (DuckDuckGo/Wikipedia). Configure Brave/Serper/SearxNG for more stable results.
                  </span>
                ) : null}
              </span>
            </label>

            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-xs text-gray-500 hover:text-gray-800 text-left underline"
            >
              {showAdvanced ? 'Hide Advanced Settings' : 'Show Advanced Settings (ID, Priority)'}
            </button>

            {showAdvanced && (
              <>
                <input
                  className="w-full p-2 border border-gray-300 rounded bg-gray-50 text-gray-900 placeholder:text-gray-400"
                  placeholder="Project ID (Optional - Auto-generated)"
                  value={newId}
                  onChange={(e) => setNewId(e.target.value)}
                />
                <input
                  className="w-full p-2 border border-gray-300 rounded bg-gray-50 text-gray-900 placeholder:text-gray-400"
                  type="number"
                  placeholder="Priority"
                  value={newPriority}
                  onChange={(e) => setNewPriority(parseInt(e.target.value || '0', 10))}
                />
              </>
            )}

            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowNew(false)}
                className="px-3 py-1 text-gray-600 hover:text-gray-900"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleInit}
                disabled={(!newId.trim() && !newName.trim()) || !newObjective.trim() || loading}
                className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 shadow-[0_0_10px_rgba(37,99,235,0.3)] transition-all"
              >
                Initialize
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="border border-red-200 bg-red-50 text-red-800 text-sm p-3 rounded">
          {error}
        </div>
      )}

      <div className="bg-white text-gray-900 border border-gray-200 rounded-lg shadow-sm overflow-hidden">
        <div className="px-4 py-2 border-b border-gray-200 flex items-center justify-between">
          <div className="font-semibold text-gray-800">Projects</div>
          <div className="text-xs text-gray-500">
            {loading ? 'Loading…' : `${projects.length} total`}
          </div>
        </div>

        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="p-3 font-semibold text-gray-600 text-sm">ID</th>
              <th className="p-3 font-semibold text-gray-600 text-sm">Objective</th>
              <th className="p-3 font-semibold text-gray-600 text-sm">Status</th>
              <th className="p-3 font-semibold text-gray-600 text-sm">Pri</th>
              <th className="p-3 font-semibold text-gray-600 text-sm">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {projects.map((p) => (
              <tr
                key={p.id}
                onClick={() => onSelectProject(p.id)}
                className="hover:bg-blue-50 cursor-pointer transition"
              >
                <td className="p-3 font-mono text-sm text-blue-700 font-semibold">{p.id}</td>
                <td className="p-3 text-sm text-gray-700 truncate max-w-xs">{p.objective}</td>
                <td className="p-3 text-sm">
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-medium ${p.status === 'active'
                      ? 'bg-green-100 text-green-800'
                      : p.status === 'completed'
                        ? 'bg-blue-100 text-blue-800'
                        : p.status === 'failed'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                  >
                    {p.status}
                  </span>
                </td>
                <td className="p-3 text-sm text-gray-500">{p.priority}</td>
                <td className="p-3 text-sm text-gray-400">
                  {p.created_at ? new Date(p.created_at).toLocaleDateString() : ''}
                </td>
              </tr>
            ))}

            {!loading && projects.length === 0 && (
              <tr>
                <td colSpan={5} className="p-8 text-center text-gray-500">
                  No projects found. Create one with NEW PROJECT.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ProjectDetail({
  projectId,
  onBack,
  setLastResult,
  devMode,
  refreshKey,
}: {
  projectId: string;
  onBack: () => void;
  setLastResult: (r: VaultRunResult) => void;
  devMode: boolean;
  refreshKey: number;
}) {
  const [tab, setTab] = useState<'status' | 'findings' | 'discovery' | 'branches'>('status');
  const [statusData, setStatusData] = useState<StatusData | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [isWatchdogging, setIsWatchdogging] = useState(false);

  // Ingest State
  const [showIngest, setShowIngest] = useState(false);
  const [ingestUrl, setIngestUrl] = useState('');
  const [ingestBranch, setIngestBranch] = useState('');
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestAllowPrivate, setIngestAllowPrivate] = useState(false);

  // Expand Mission State
  const [showExpand, setShowExpand] = useState(false);
  const [expandQuery, setExpandQuery] = useState('');
  const [isExpanding, setIsExpanding] = useState(false);

  // Export State
  const [showExport, setShowExport] = useState(false);
  const [exportFormat, setExportFormat] = useState<'json' | 'markdown'>('markdown');
  const [isExporting, setIsExporting] = useState(false);
  const [exportContent, setExportContent] = useState<string | null>(null);

  // Dev Mode inputs (low-level commands)
  const [watchType, setWatchType] = useState<'url' | 'query'>('url');
  const [watchTarget, setWatchTarget] = useState('');
  const watchInterval = 3600;
  const watchTags = '';

  const [cacheQuery, setCacheQuery] = useState('');
  const [cacheSetJson, setCacheSetJson] = useState('{}');

  async function run(endpoint: string, payload?: unknown) {
    const res = await runVaultPost(endpoint, payload);
    setLastResult(res);
    return res;
  }

  async function refreshStatus() {
    try {
      const res = await runVaultPost('/vault/status', { id: projectId, format: 'json' });
      if (res.ok && res.stdout) {
        // Handle potential parsing errors gracefully
        try {
          const parsed = JSON.parse(res.stdout);
          setStatusData(parsed);
        } catch (err) {
          console.warn('Backend returned non-JSON status, cannot update GUI.', err);
        }
      }
    } catch (e) {
      console.error('Failed to refresh status', e);
    }
  }

  useEffect(() => {
    if (tab === 'status' && projectId) {
      refreshStatus();
    }
  }, [projectId, tab, refreshKey]);

  function TabButton({
    id,
    label,
    icon: Icon,
  }: {
    id: 'status' | 'findings' | 'discovery' | 'branches';
    label: string;
    icon: ComponentType<{ className?: string }>;
  }) {
    const active = tab === id;
    return (
      <button
        onClick={() => setTab(id)}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 transition whitespace-nowrap ${active ? 'border-cyan text-cyan' : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
      >
        <Icon className="w-4 h-4" />
        <span className="font-medium">{label}</span>
      </button>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-4 mb-6">
        <button onClick={onBack} className="p-2 rounded-full text-gray-200 hover:bg-white/10" aria-label="Back">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <div className="text-xs text-gray-300">Project</div>
          <h1 className="text-2xl font-bold text-gray-100 font-mono">
            <DecryptedText text={projectId} speed={50} />
          </h1>
        </div>
      </div>

      <div className="flex gap-1 border-b border-white/10 mb-6 overflow-x-auto">
        <TabButton id="status" label="Status" icon={Activity} />
        <TabButton id="findings" label="Findings" icon={Lightbulb} />
        <TabButton id="discovery" label="Discovery" icon={CheckCircle} />
        <TabButton id="branches" label="Branches" icon={GitBranch} />
      </div>

      <div className="flex-1 overflow-auto">
        {tab === 'status' && (
          <div className="space-y-6">
            {actionError && (
              <div className="border border-red-500/40 bg-red-500/10 text-red-200 text-sm p-3 rounded font-mono">
                {actionError}
              </div>
            )}
            <div className="flex justify-between items-start flex-wrap gap-2">
              <div className="flex gap-2">
                <button
                  onClick={refreshStatus}
                  className="border border-gray-300 bg-white text-gray-800 px-4 py-2 rounded hover:bg-gray-50 text-sm flex items-center gap-2 shadow-sm active:scale-95 transition-all"
                >
                  <RefreshCw className="w-4 h-4" /> Refresh
                </button>

                <button
                  onClick={async () => {
                    setActionError(null);
                    setIsWatchdogging(true);
                    try {
                      const wd = await run('/vault/watchdog/once', { id: projectId, limit: 5, dry_run: false });
                      if (!wd.ok) {
                        throw new Error(wd.stderr || 'vault watchdog once failed');
                      }
                      await refreshStatus();
                    } catch (e: unknown) {
                      const msg = e instanceof Error ? e.message : String(e);
                      setActionError(msg);
                    } finally {
                      setIsWatchdogging(false);
                    }
                  }}
                  className="border border-cyan/40 bg-cyan-dim text-cyan px-4 py-2 rounded hover:border-cyan/70 text-sm flex items-center gap-2 font-bold shadow-[0_0_10px_rgba(0,240,255,0.18)] transition-all disabled:opacity-50"
                  disabled={isWatchdogging}
                >
                  <Play className={`w-4 h-4 ${isWatchdogging ? 'animate-pulse' : ''}`} /> {isWatchdogging ? 'Researching…' : 'Run Watchdog Now'}
                </button>

                <button
                  onClick={() => setShowIngest(!showIngest)}
                  className="border border-blue-300 bg-blue-50 text-blue-700 px-4 py-2 rounded hover:bg-blue-100 text-sm flex items-center gap-2 font-bold shadow-[0_0_10px_rgba(37,99,235,0.2)] transition-all"
                >
                  <Globe className="w-4 h-4" /> Ingest from Web
                </button>

                <button
                  onClick={() => setShowExpand(!showExpand)}
                  className="border border-purple-300 bg-purple-50 text-purple-700 px-4 py-2 rounded hover:bg-purple-100 text-sm flex items-center gap-2 font-bold shadow-[0_0_10px_rgba(147,51,234,0.2)] transition-all"
                >
                  <Target className="w-4 h-4" /> Expand Mission
                </button>

                <button
                  onClick={() => setShowExport(!showExport)}
                  className="border border-green-300 bg-green-50 text-green-700 px-4 py-2 rounded hover:bg-green-100 text-sm flex items-center gap-2 font-bold shadow-[0_0_10px_rgba(34,197,94,0.2)] transition-all"
                >
                  <Download className="w-4 h-4" /> Export
                </button>
              </div>
            </div>

            {showIngest && (
              <div className="bg-white text-gray-900 border border-blue-200 p-4 rounded shadow-lg animate-in fade-in zoom-in duration-300">
                <h3 className="font-bold text-gray-800 mb-2 flex items-center gap-2">
                  <Globe className="w-4 h-4 text-blue-600" /> Ingest Content
                </h3>
                <div className="flex gap-2">
                  <input
                    value={ingestUrl}
                    onChange={e => setIngestUrl(e.target.value)}
                    className="flex-1 p-2 border border-gray-300 rounded text-sm outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 placeholder:text-gray-400"
                    placeholder="Paste URL (e.g. https://arxiv.org/...)"
                  />
                  <input
                    value={ingestBranch}
                    onChange={e => setIngestBranch(e.target.value)}
                    className="w-32 p-2 border border-gray-300 rounded text-sm outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 placeholder:text-gray-400"
                    placeholder="main"
                    title="Optional: CLI --branch (default: main). Branch names are case-sensitive."
                  />
                  <button
                    onClick={async () => {
                      setActionError(null);
                      setIsIngesting(true);
                      try {
                        const b = ingestBranch.trim();
                        const r = await run('/vault/scuttle', {
                          id: projectId,
                          url: ingestUrl,
                          branch: b ? b : undefined,
                          allow_private_networks: ingestAllowPrivate,
                        });
                        if (!r.ok) throw new Error(r.stderr || 'vault scuttle failed');
                      } catch (e: unknown) {
                        setActionError(e instanceof Error ? e.message : String(e));
                      }
                      setIngestUrl('');
                      setIngestBranch('');
                      setIsIngesting(false);
                      setShowIngest(false);
                      setIngestAllowPrivate(false);
                      await refreshStatus();
                    }}
                    disabled={!ingestUrl || isIngesting}
                    className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50 font-semibold"
                  >
                    {isIngesting ? 'Ingesting...' : 'Run Ingest'}
                  </button>
                </div>
                <div className="text-xs text-gray-500 mt-2">
                  Optional: set <code>--branch</code> (default: <code>main</code>, case-sensitive).
                </div>
                <div className="mt-3 flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="allow-private"
                    checked={ingestAllowPrivate}
                    onChange={e => setIngestAllowPrivate(e.target.checked)}
                    className="rounded text-blue-600 focus:ring-blue-500"
                  />
                  <label htmlFor="allow-private" className="text-xs text-gray-600 flex items-center gap-1 cursor-pointer">
                    <AlertTriangle className="w-3 h-3 text-amber-500" /> Allow private networks (SSRF risk)
                  </label>
                </div>
                <div className="text-xs text-gray-500 mt-2">
                  Extracts text, summarizes, and tags content automatically.
                </div>
              </div>
            )}

            {showExport && (
              <div className="bg-white text-gray-900 border border-green-200 p-4 rounded shadow-lg animate-in fade-in zoom-in duration-300">
                <h3 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                  <Download className="w-4 h-4 text-green-600" /> Export Research Data
                </h3>

                <div className="space-y-3">
                  <div>
                    <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Format</label>
                    <div className="flex gap-3">
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="radio"
                          checked={exportFormat === 'markdown'}
                          onChange={() => setExportFormat('markdown')}
                          className="text-green-600"
                        />
                        <span className="text-sm text-gray-700">Markdown (.md)</span>
                      </label>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="radio"
                          checked={exportFormat === 'json'}
                          onChange={() => setExportFormat('json')}
                          className="text-green-600"
                        />
                        <span className="text-sm text-gray-700">JSON (.json)</span>
                      </label>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={async () => {
                        setIsExporting(true);
                        setExportContent(null);
                        try {
                          const r = await run('/vault/export', { id: projectId, format: exportFormat });
                          if (r.ok && r.stdout) {
                            setExportContent(r.stdout);
                            // Auto-download
                            const blob = new Blob([r.stdout], { type: 'text/plain' });
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `${projectId}_export.${exportFormat === 'json' ? 'json' : 'md'}`;
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                            URL.revokeObjectURL(url);
                          } else {
                            throw new Error(r.stderr || 'Export failed');
                          }
                        } catch (e: unknown) {
                          setActionError(e instanceof Error ? e.message : String(e));
                        }
                        setIsExporting(false);
                      }}
                      disabled={isExporting}
                      className="bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-700 disabled:opacity-50 font-semibold flex items-center gap-2"
                    >
                      {isExporting ? <><RefreshCw className="w-4 h-4 animate-spin" /> Exporting...</> : <><Download className="w-4 h-4" /> Download</>}
                    </button>

                    {exportContent && (
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(exportContent);
                        }}
                        className="border border-green-600 text-green-600 px-4 py-2 rounded text-sm hover:bg-green-50 font-semibold flex items-center gap-2"
                      >
                        <Copy className="w-4 h-4" /> Copy to Clipboard
                      </button>
                    )}
                  </div>

                  {exportContent && (
                    <div className="border-t border-gray-200 pt-3">
                      <div className="text-xs font-bold text-gray-500 uppercase mb-1">Preview (first 500 chars)</div>
                      <pre className="bg-gray-50 p-3 rounded text-xs font-mono text-gray-700 overflow-auto max-h-32 border border-gray-200">
                        {exportContent.substring(0, 500)}{exportContent.length > 500 ? '...' : ''}
                      </pre>
                    </div>
                  )}

                  <div className="text-xs text-gray-500">
                    Export all findings, events, and research data for this project.
                  </div>
                </div>
              </div>
            )}

            {showExpand && (
              <div className="bg-white text-gray-900 border border-purple-200 p-4 rounded shadow-lg animate-in fade-in zoom-in duration-300">
                <h3 className="font-bold text-gray-800 mb-2 flex items-center gap-2">
                  <Target className="w-4 h-4 text-purple-600" /> Track New Angle
                </h3>
                <div className="flex gap-2">
                  <input
                    value={expandQuery}
                    onChange={e => setExpandQuery(e.target.value)}
                    className="flex-1 p-2 border border-gray-300 rounded text-sm outline-none focus:ring-2 focus:ring-purple-500 text-gray-900 placeholder:text-gray-400"
                    placeholder="What should we watch? (e.g. 'competitor release notes')"
                  />
                  <button
                    onClick={async () => {
                      setActionError(null);
                      setIsExpanding(true);
                      try {
                        const a = await run('/vault/watch/add', {
                          id: projectId,
                          type: 'query',
                          target: expandQuery,
                          interval: 3600
                        });
                        if (!a.ok) throw new Error(a.stderr || 'vault watch add failed');
                        const wd = await run('/vault/watchdog/once', { id: projectId, limit: 3, dry_run: false });
                        if (!wd.ok) throw new Error(wd.stderr || 'vault watchdog once failed');
                      } catch (e: unknown) {
                        setActionError(e instanceof Error ? e.message : String(e));
                      }
                      setExpandQuery('');
                      setIsExpanding(false);
                      setShowExpand(false);
                      await refreshStatus();
                    }}
                    disabled={!expandQuery || isExpanding}
                    className="bg-purple-600 text-white px-4 py-2 rounded text-sm hover:bg-purple-700 disabled:opacity-50 font-semibold"
                  >
                    {isExpanding ? 'Adding...' : 'Start Tracking'}
                  </button>
                </div>
                <div className="text-xs text-gray-500 mt-2">
                  The Vault will periodically search for this topic and alert you to new findings.
                </div>
              </div>
            )}

            {statusData && (
              <div className="bg-white text-gray-900 border border-gray-200 rounded-lg p-6 shadow-sm">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h2 className="text-xl font-bold text-gray-800">{statusData.project.name}</h2>
                    <div className="text-sm text-gray-500 font-mono">{statusData.project.id}</div>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${statusData.project.status === 'active'
                      ? 'bg-green-100 text-green-800'
                      : statusData.project.status === 'completed'
                        ? 'bg-blue-100 text-blue-800'
                        : statusData.project.status === 'failed'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                  >
                    {statusData.project.status.toUpperCase()}
                  </span>
                </div>

                <div className="mb-6">
                  <div className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Objective</div>
                  <p className="text-gray-800 bg-gray-50 p-3 rounded border border-gray-100">{statusData.project.objective}</p>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <SpotlightCard className="bg-blue-50 rounded border border-blue-100" spotlightColor="rgba(59, 130, 246, 0.15)">
                    <div className="p-3">
                      <div className="text-xs text-blue-600 font-bold uppercase">Priority</div>
                      <div className="text-2xl font-mono text-blue-900">{statusData.project.priority}</div>
                    </div>
                  </SpotlightCard>
                  <SpotlightCard className="bg-purple-50 rounded border border-purple-100" spotlightColor="rgba(147, 51, 234, 0.15)">
                    <div className="p-3">
                      <div className="text-xs text-purple-600 font-bold uppercase">Findings</div>
                      <div className="text-2xl font-mono text-purple-900">{statusData.insights.length}</div>
                    </div>
                  </SpotlightCard>
                  <SpotlightCard className="bg-orange-50 rounded border border-orange-100" spotlightColor="rgba(249, 115, 22, 0.15)">
                    <div className="p-3">
                      <div className="text-xs text-orange-600 font-bold uppercase">Events</div>
                      <div className="text-2xl font-mono text-orange-900">{statusData.recent_events.length}</div>
                    </div>
                  </SpotlightCard>
                </div>

                <div>
                  <div className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Recent Events</div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                          <th className="p-2 text-gray-600">Time</th>
                          <th className="p-2 text-gray-600">Source</th>
                          <th className="p-2 text-gray-600">Type</th>
                          <th className="p-2 text-gray-600">Conf</th>
                          <th className="p-2 text-gray-600">Data</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {statusData.recent_events.map((e, i) => (
                          <tr key={i} className="hover:bg-gray-50">
                            <td className="p-2 font-mono text-xs text-gray-500">{new Date(e.timestamp).toLocaleTimeString()}</td>
                            <td className="p-2 text-cyan-700">{e.source}</td>
                            <td className="p-2 font-medium">{e.type}</td>
                            <td className={`p-2 font-mono ${e.confidence > 0.8 ? 'text-green-600' : e.confidence < 0.5 ? 'text-red-500' : 'text-yellow-600'}`}>
                              {e.confidence.toFixed(2)}
                            </td>
                            <td className="p-2 text-gray-600 max-w-xs truncate" title={e.payload}>{e.payload.substring(0, 100)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {devMode && (
              <div className="border border-yellow-300 bg-yellow-50 p-4 rounded space-y-4">
                <div className="font-bold text-yellow-900 text-sm flex items-center gap-2">
                  <Terminal className="w-4 h-4" />
                  Advanced / Dev Mode Actions
                </div>

                {/* Log */}
                <div className="border-t border-yellow-200 pt-2">
                  <div className="text-[10px] font-bold text-yellow-700 uppercase mb-2">Manual Event Log</div>
                  <button
                    onClick={() => run('/vault/log', { id: projectId, type: 'NOTE', step: 0, payload: {}, conf: 1.0, source: 'portal', tags: 'dev' })}
                    className="w-full border border-yellow-300 bg-white text-gray-900 px-3 py-2 rounded hover:bg-yellow-100 text-sm text-left"
                  >
                    Run: vault log --type NOTE --tags dev
                  </button>
                </div>

                {/* Watch */}
                <div className="border-t border-yellow-200 pt-2 space-y-2">
                  <div className="text-[10px] font-bold text-yellow-700 uppercase">Watchdog Management</div>
                  <div className="grid grid-cols-2 gap-2">
                    <select
                      value={watchType}
                      onChange={(e) => setWatchType(e.target.value as any)}
                      className="p-2 border border-yellow-300 rounded text-xs bg-white text-gray-900"
                    >
                      <option value="url">URL</option>
                      <option value="query">Query</option>
                    </select>
                    <input
                      placeholder="Target (URL/Query)"
                      value={watchTarget}
                      onChange={(e) => setWatchTarget(e.target.value)}
                      className="p-2 border border-yellow-300 rounded text-xs bg-white text-gray-900 placeholder:text-gray-500"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => run('/vault/watch/add', { id: projectId, type: watchType, target: watchTarget, interval: watchInterval, tags: watchTags })}
                      disabled={!watchTarget.trim()}
                      className="w-full bg-yellow-600 text-white px-3 py-2 rounded hover:bg-yellow-700 text-sm disabled:opacity-50"
                    >
                      Run: vault watch add
                    </button>
                    <button
                      onClick={() => run('/vault/watch/list', { id: projectId })}
                      className="w-full border border-yellow-300 bg-white text-gray-900 px-3 py-2 rounded hover:bg-yellow-100 text-sm"
                    >
                      Run: vault watch list
                    </button>
                  </div>
                </div>

                {/* Cache / Search set-result */}
                <div className="border-t border-yellow-200 pt-2 space-y-2">
                  <div className="text-[10px] font-bold text-yellow-700 uppercase">Cache Injection</div>
                  <input
                    placeholder="Query"
                    value={cacheQuery}
                    onChange={(e) => setCacheQuery(e.target.value)}
                    className="w-full p-2 border border-yellow-300 rounded text-xs bg-white text-gray-900 placeholder:text-gray-500"
                  />
                  <textarea
                    placeholder="Result JSON"
                    value={cacheSetJson}
                    onChange={(e) => setCacheSetJson(e.target.value)}
                    className="w-full p-2 border border-yellow-300 rounded text-xs font-mono h-20 bg-white text-gray-900 placeholder:text-gray-500"
                  />
                  <button
                    onClick={() => {
                      try {
                        const parsed = JSON.parse(cacheSetJson);
                        run('/vault/search', { query: cacheQuery, set_result: JSON.stringify(parsed) });
                      } catch (e) {
                        alert('Invalid JSON in result');
                      }
                    }}
                    disabled={!cacheQuery.trim()}
                    className="w-full bg-yellow-600 text-white px-3 py-2 rounded hover:bg-yellow-700 text-sm disabled:opacity-50"
                  >
                    Run: vault search --set-result
                  </button>
                </div>

                {/* Watchdog Once */}
                <div className="border-t border-yellow-200 pt-2">
                  <button
                    onClick={() => run('/vault/watchdog/once', { id: projectId, limit: 5, dry_run: true })}
                    className="w-full border border-yellow-300 bg-white text-gray-900 px-3 py-2 rounded hover:bg-yellow-100 text-sm text-left"
                  >
                    Run: vault watchdog --once --dry-run
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {tab === 'findings' && (
          <InsightsPanel projectId={projectId} run={run} refreshKey={refreshKey} />
        )}

        {tab === 'discovery' && (
          <VerificationPanel projectId={projectId} run={run} refreshKey={refreshKey} />
        )}

        {tab === 'branches' && (
          <BranchesPanel projectId={projectId} run={run} refreshKey={refreshKey} />
        )}
      </div>
    </div>
  );
}

function InsightsPanel({
  projectId,
  run,
  refreshKey,
}: {
  projectId: string;
  run: (endpoint: string, payload?: unknown) => Promise<VaultRunResult>;
  refreshKey: number;
}) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [insights, setInsights] = useState<Insight[]>([]);
  const [isAdding, setIsAdding] = useState(false);
  const [summary, setSummary] = useState<{ counts: { insights: number; events: number } } | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  useEffect(() => {
    loadInsights();
    loadSummary();
     
  }, [projectId, refreshKey]);

  async function loadSummary() {
    setSummaryLoading(true);
    setSummaryError(null);
    try {
      const res = await run('/vault/summary', { id: projectId, format: 'json' });
      if (res.ok) {
        try {
          const data = JSON.parse(res.stdout);
          setSummary(data);
        } catch {
          setSummaryError('Failed to parse summary');
        }
      } else {
        setSummaryError(res.stderr || 'Failed to load summary');
      }
    } catch (e) {
      setSummaryError(String(e));
    } finally {
      setSummaryLoading(false);
    }
  }

  async function loadInsights() {
    const res = await run('/vault/insight/list', { id: projectId, format: 'json' });
    if (res.ok) {
      try {
        setInsights(JSON.parse(res.stdout));
      } catch (e) {
        console.error("Failed to parse insights", e);
      }
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white text-gray-900 border border-gray-200 p-6 rounded-lg shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <div className="bg-yellow-100 p-2 rounded-full">
            <Lightbulb className="w-5 h-5 text-yellow-600" />
          </div>
          <div>
            <h3 className="font-bold text-gray-800">New Finding</h3>
            <div className="text-xs text-gray-500">Log a key finding or observation</div>
          </div>
        </div>

        <div className="space-y-3">
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Finding Headline</label>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 outline-none text-gray-900 placeholder:text-gray-400"
              placeholder="E.g. 'Database latency spikes during backups'"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Observation / Evidence</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded text-sm h-24 focus:ring-2 focus:ring-blue-500 outline-none resize-none text-gray-900 placeholder:text-gray-400"
              placeholder="Describe what you found. Markdown is supported."
            />
          </div>
        </div>

        <div className="flex justify-end mt-4">
          <button
            disabled={!title.trim() || !content.trim() || isAdding}
            onClick={async () => {
              setIsAdding(true);
              await run('/vault/insight/add', { id: projectId, title, content, tags: '' });
              setTitle('');
              setContent('');
              setIsAdding(false);
              loadInsights();
            }}
            className="bg-black text-white px-5 py-2 rounded-md hover:bg-gray-800 disabled:opacity-50 text-sm font-medium flex items-center gap-2 transition-all shadow-[0_0_10px_rgba(0,0,0,0.2)]"
          >
            {isAdding ? <RefreshCw className="w-4 h-4 animate-spin" /> : null}
            {isAdding ? 'Saving...' : 'Add a Finding'}
          </button>
        </div>
      </div>

      {/* Project Summary */}
      {summary && !summaryError && (
        <div className="bg-gradient-to-br from-purple-50 to-blue-50 border border-purple-200 rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="bg-purple-100 p-2 rounded-full">
              <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-gray-800 text-lg">Project Summary</h3>
              <div className="text-xs text-gray-500">Overview of your research progress</div>
            </div>
            <button onClick={loadSummary} className="text-purple-600 hover:text-purple-800 transition" title="Refresh Summary">
              <RefreshCw className={`w-4 h-4 ${summaryLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-yellow-600" />
                <span className="text-gray-700"><strong>{summary.counts.insights}</strong> finding{summary.counts.insights !== 1 ? 's' : ''}</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <span className="text-gray-700"><strong>{summary.counts.events}</strong> event{summary.counts.events !== 1 ? 's' : ''}</span>
              </div>
            </div>
          </div>
        </div>
      )}
      {summaryLoading && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-6 text-center">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto text-gray-400 mb-2" />
          <div className="text-sm text-gray-500">Generating summary...</div>
        </div>
      )}
      {summaryError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="text-sm text-red-600">Failed to load summary</div>
        </div>
      )}

      <div className="bg-white text-gray-900 border border-gray-200 rounded-lg shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
          <h3 className="font-bold text-gray-700">Key Findings ({insights.length})</h3>
          <button onClick={loadInsights} className="text-gray-500 hover:text-gray-900 transition" title="Refresh">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
        <div className="divide-y divide-gray-100">
          {insights.length === 0 && (
            <div className="p-12 text-center">
              <div className="text-gray-300 mb-2"><Lightbulb className="w-12 h-12 mx-auto" /></div>
              <div className="text-gray-500 font-medium">No findings yet</div>
              <div className="text-gray-400 text-sm">Add your first finding above.</div>
            </div>
          )}
          {insights.map((insight, idx) => (
            <div key={idx} className="p-6 hover:bg-gray-50 transition group">
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-bold text-gray-900 text-lg leading-tight">{insight.title}</h4>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-xs text-gray-400 font-mono">{new Date(insight.timestamp).toLocaleDateString()}</span>
                  <span className={`text-xs font-bold px-2 py-0.5 rounded ${insight.confidence > 0.8 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {(insight.confidence * 100).toFixed(0)}% Conf
                  </span>
                </div>
              </div>
              <div className="prose prose-sm max-w-none text-gray-700">
                <p className="whitespace-pre-wrap">{insight.content}</p>
              </div>
              {insight.tags && (
                <div className="flex gap-2 mt-3 flex-wrap">
                  {insight.tags.split(',').map(tag => (
                    <span key={tag} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full border border-gray-200">
                      #{tag.trim()}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function BranchesPanel({
  projectId,
  run,
  refreshKey,
}: {
  projectId: string;
  run: (endpoint: string, payload?: unknown) => Promise<VaultRunResult>;
  refreshKey: number;
}) {
  const [name, setName] = useState('');
  const [branches, setBranches] = useState<Branch[]>([]);

  useEffect(() => {
    loadBranches();
     
  }, [projectId, refreshKey]);

  async function loadBranches() {
    const res = await run('/vault/branch/list', { id: projectId, format: 'json' });
    if (res.ok) {
      try {
        setBranches(JSON.parse(res.stdout));
      } catch (e) {
        console.error(e);
      }
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white text-gray-900 border border-gray-200 p-6 rounded-lg shadow-sm">
        <div className="font-bold text-gray-800 mb-4 flex items-center gap-2">
          <GitBranch className="w-5 h-5 text-gray-500" />
          <span>Create Divergent Branch</span>
        </div>
        <div className="flex gap-2">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="flex-1 p-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 outline-none text-gray-900 placeholder:text-gray-400"
            placeholder="Branch name (e.g. hypothesis-alpha)"
          />
          <button
            disabled={!name.trim()}
            onClick={async () => {
              await run('/vault/branch/create', { id: projectId, name });
              setName('');
              loadBranches();
            }}
            className="bg-black text-white px-5 py-2 rounded-md hover:bg-gray-800 disabled:opacity-50 text-sm font-medium"
          >
            Create Branch
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Branches allow you to pursue alternative hypotheses without polluting the main timeline.
        </p>
      </div>

      <div className="bg-white text-gray-900 border border-gray-200 rounded-lg shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
          <h3 className="font-bold text-gray-700">Active Branches</h3>
          <button onClick={loadBranches} className="text-gray-500 hover:text-gray-900 transition" title="Refresh">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
        <table className="w-full text-left text-sm">
          <thead className="bg-white border-b border-gray-100">
            <tr>
              <th className="px-6 py-3 text-gray-500 font-medium">Name</th>
              <th className="px-6 py-3 text-gray-500 font-medium">Status</th>
              <th className="px-6 py-3 text-gray-500 font-medium">Hypothesis</th>
              <th className="px-6 py-3 text-gray-500 font-medium">Parent</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {branches.map((b) => (
              <tr key={b.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 font-mono text-blue-700 font-bold">{b.name}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-0.5 rounded text-xs uppercase font-bold ${b.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>{b.status}</span>
                </td>
                <td className="px-6 py-4 text-gray-600 italic">{b.hypothesis || '-'}</td>
                <td className="px-6 py-4 text-gray-400 font-mono text-xs">{b.parent_id || 'root'}</td>
              </tr>
            ))}
            {branches.length === 0 && (
              <tr><td colSpan={4} className="p-8 text-center text-gray-400 italic">No divergent branches found.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function VerificationPanel({
  projectId,
  run,
  refreshKey,
}: {
  projectId: string;
  run: (endpoint: string, payload?: unknown) => Promise<VaultRunResult>;
  refreshKey: number;
}) {
  const [missions, setMissions] = useState<VerificationMission[]>([]);
  const [loading, setLoading] = useState(false);
  const autoPlannedRef = useRef<Record<string, boolean>>({});

  useEffect(() => {
    loadMissions();
     
  }, [projectId, refreshKey]);

  async function loadMissions({ allowAutoPlan }: { allowAutoPlan?: boolean } = {}) {
    setLoading(true);
    try {
      const res = await run('/vault/verify/list', { id: projectId, limit: 50, format: 'json' });
      if (!res.ok) return;

      let parsed: VerificationMission[] = [];
      try {
        parsed = JSON.parse(res.stdout) as VerificationMission[];
      } catch (e) {
        console.error(e);
      }
      setMissions(parsed);

      // Usability: when the log is empty, most users expect the system to "do something".
      // Auto-plan once per project to avoid the "empty discovery page" trap.
      if ((allowAutoPlan ?? true) && parsed.length === 0 && !autoPlannedRef.current[projectId]) {
        autoPlannedRef.current[projectId] = true;
        await run('/vault/verify/plan', { id: projectId, format: 'json' });
        const res2 = await run('/vault/verify/list', { id: projectId, limit: 50, format: 'json' });
        if (res2.ok) {
          try {
            setMissions(JSON.parse(res2.stdout) as VerificationMission[]);
          } catch (e) {
            console.error(e);
          }
        }
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={async () => {
            setLoading(true);
            await run('/vault/verify/plan', { id: projectId, format: 'json' });
            await loadMissions();
            setLoading(false);
          }}
          disabled={loading}
          className="bg-white border border-gray-200 p-6 rounded-lg shadow-sm hover:shadow-md hover:border-purple-300 transition flex flex-col items-center gap-3 text-center group"
        >
          <div className="p-3 bg-purple-50 rounded-full group-hover:bg-purple-100 transition">
            <Play className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <div className="font-bold text-gray-800">Plan Verification</div>
            <div className="text-xs text-gray-500 mt-1">Identify low-confidence gaps</div>
          </div>
        </button>

        <button
          onClick={async () => {
            setLoading(true);
            await run('/vault/synthesize', { id: projectId, threshold: 0.65, format: 'json' });
            await loadMissions();
            setLoading(false);
          }}
          disabled={loading}
          className="bg-white border border-gray-200 p-6 rounded-lg shadow-sm hover:shadow-md hover:border-blue-300 transition flex flex-col items-center gap-3 text-center group"
        >
          <div className="p-3 bg-blue-50 rounded-full group-hover:bg-blue-100 transition">
            <Share2 className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <div className="font-bold text-gray-800">Discover Connections</div>
            <div className="text-xs text-gray-500 mt-1">Link related findings via AI</div>
          </div>
        </button>

        <button
          onClick={async () => {
            setLoading(true);
            await run('/vault/verify/run', { id: projectId, status: 'open', limit: 5, format: 'json' });
            await loadMissions();
            setLoading(false);
          }}
          disabled={loading}
          className="bg-white border border-gray-200 p-6 rounded-lg shadow-sm hover:shadow-md hover:border-green-300 transition flex flex-col items-center gap-3 text-center group"
        >
          <div className="p-3 bg-green-50 rounded-full group-hover:bg-green-100 transition">
            <Activity className="w-6 h-6 text-green-600" />
          </div>
          <div>
            <div className="font-bold text-gray-800">Verify Links</div>
            <div className="text-xs text-gray-500 mt-1">Run active discovery missions</div>
          </div>
        </button>

        <SpotlightCard className="bg-gray-50 border border-gray-200 rounded-lg flex flex-col justify-center gap-2" spotlightColor="rgba(0,0,0,0.05)">
          <div className="p-6">
            <div className="text-sm font-bold text-gray-600 uppercase tracking-wider text-center mb-2">Discovery Overview</div>
            <div className="flex justify-between px-4">
              <div className="text-center">
                <div className="text-2xl font-mono text-blue-600">{missions.filter(m => m.status === 'open').length}</div>
                <div className="text-[10px] text-gray-500 font-bold uppercase">Open</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-mono text-green-600">{missions.filter(m => m.status === 'done').length}</div>
                <div className="text-[10px] text-gray-500 font-bold uppercase">Done</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-mono text-red-600">{missions.filter(m => m.status === 'blocked').length}</div>
                <div className="text-[10px] text-gray-500 font-bold uppercase">Blocked</div>
              </div>
            </div>
          </div>
        </SpotlightCard>
      </div>

      <div className="bg-white text-gray-900 border border-gray-200 rounded-lg shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
          <div className="font-bold text-gray-700">Discovery Log</div>
          <button onClick={() => loadMissions({ allowAutoPlan: false })} disabled={loading} className="text-gray-500 hover:text-gray-900 transition">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
        <table className="w-full text-left text-sm">
          <thead className="bg-white border-b border-gray-100">
            <tr>
              <th className="px-6 py-3 text-gray-500 font-medium">Status</th>
              <th className="px-6 py-3 text-gray-500 font-medium">Finding Context</th>
              <th className="px-6 py-3 text-gray-500 font-medium">Search Query</th>
              <th className="px-6 py-3 text-gray-500 font-medium text-right">Conf</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {missions.map((m) => (
              <tr key={m.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${m.status === 'done' ? 'bg-green-100 text-green-800' :
                    m.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                      m.status === 'open' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                    }`}>
                    {m.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-gray-800 font-medium max-w-xs truncate" title={m.finding_title}>
                  {m.finding_title || 'Unknown Finding'}
                </td>
                <td className="px-6 py-4 text-gray-600 font-mono text-xs max-w-xs truncate" title={m.query}>
                  {m.query}
                </td>
                <td className="px-6 py-4 text-right font-mono">{(m.finding_conf * 100).toFixed(0)}%</td>
              </tr>
            ))}
            {missions.length === 0 && (
              <tr><td colSpan={4} className="p-8 text-center text-gray-400 italic">No missions found. Click 'Discover Links' to start.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function MainApp() {
  const [authState, setAuthState] = useState<'checking' | 'authed' | 'unauth'>('checking');
  const [token, setToken] = useState('');
  const [authError, setAuthError] = useState<string | null>(null);

  const [devMode, setDevMode] = useState(false);
  const [mode, setMode] = useState<'command' | 'graph' | 'diagnostics'>('command');

  const [dbs, setDbs] = useState<SystemDbsResponse | null>(null);
  const [secrets, setSecrets] = useState<SecretsStatusResponse | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [systemError, setSystemError] = useState<string | null>(null);

  const [currentProject, setCurrentProject] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<VaultRunResult | null>(null);

  const initOnce = useRef(false);

  const stream = usePortalStream(
    authState === 'authed',
    {
      onHello: (payload) => {
        setDbs((prev) =>
          prev
            ? { ...prev, now_ms: payload.now_ms, current: payload.db }
            : { now_ms: payload.now_ms, current: payload.db, candidates: [] },
        );
        setRefreshKey((k) => k + 1);
      },
      onPulse: (payload) => {
        setDbs((prev) =>
          prev
            ? { ...prev, now_ms: payload.now_ms, current: payload.db }
            : { now_ms: payload.now_ms, current: payload.db, candidates: [] },
        );
        setRefreshKey((k) => k + 1);
      },
      onDbs: (payload) => {
        setDbs(payload);
      },
    },
    2,
  );

  useEffect(() => {
    if (initOnce.current) return;
    initOnce.current = true;

    // 1. Check if we already have a session cookie
    apiJson('/auth/status', { method: 'GET' })
      .then(() => {
        setAuthState('authed');
        const hash = window.location.hash;
        if (hash.startsWith('#token=')) {
          window.history.replaceState(null, '', window.location.pathname + window.location.search);
        }
      })
      .catch(() => {
        // 2. Not authed? Check URL for #token=
        const hash = window.location.hash;
        if (hash.startsWith('#token=')) {
          const urlToken = hash.substring(7);
          if (urlToken) {
            handleLogin(urlToken);
            // Clear the hash so it doesn't linger in the address bar
            window.history.replaceState(null, '', window.location.pathname + window.location.search);
            return;
          }
        }
        setAuthState('unauth');
      });
  }, []);

  async function handleLogin(providedToken?: string | MouseEvent) {
    const loginToken = (typeof providedToken === 'string' ? providedToken : token);
    if (!loginToken) return;

    setAuthError(null);
    setAuthState('checking');
    try {
      await apiJson('/auth/login', { method: 'POST', body: JSON.stringify({ token: loginToken }) });
      setToken('');
      setAuthState('authed');
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setAuthError(msg);
      setAuthState('unauth');
    }
  }

  async function handleLogout() {
    try {
      await apiJson('/auth/logout', { method: 'POST', body: '{}' });
    } finally {
      setAuthState('unauth');
      setCurrentProject(null);
      setLastResult(null);
      setSecrets(null);
    }
  }

  async function refreshDbs() {
    try {
      const data = await systemGet<SystemDbsResponse>('/dbs');
      setDbs(data);
      setSystemError(null);
    } catch {
      setSystemError('Failed to load DB candidates. Check that the backend is running and you are logged in.');
    }
  }

  async function refreshSecrets() {
    try {
      const st = await systemGet<SecretsStatusResponse>('/secrets/status');
      setSecrets(st);
    } catch {
      // Non-fatal: portal can still operate; research commands will surface errors.
      setSecrets(null);
    }
  }

  async function selectDb(path: string | null) {
    try {
      const next = await systemPost<SystemDbsResponse>('/db/select', { path });
      setDbs(next);
      setSystemError(null);
      setRefreshKey((k) => k + 1);
      // DB switches can invalidate the current project context.
      setCurrentProject(null);
      setMode('command');
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setSystemError(msg);
    }
  }

  useEffect(() => {
    if (authState !== 'authed') return;
    refreshDbs();
    refreshSecrets();
     
  }, [authState]);

  useEffect(() => {
    if (authState !== 'authed') return;
    if (mode === 'diagnostics') return;
    refreshSecrets();
     
  }, [mode]);

  if (authState === 'checking') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-void p-6 font-mono">
        <div className="text-gray-400">Connecting…</div>
      </div>
    );
  }

  if (authState !== 'authed') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-void p-4 font-mono">
        <div className="bg-void-surface p-8 rounded border border-white/10 max-w-sm w-full space-y-4 text-gray-100">
          <h1 className="text-xl font-bold text-gray-100">ResearchVault Portal — Login</h1>
          <div className="text-sm text-gray-400">Enter your <code>RESEARCHVAULT_PORTAL_TOKEN</code> or use a tokenized link.</div>
          <div className="text-xs text-gray-500 mt-1">
            💡 <strong>Where's my token?</strong> Run <code>./start_portal.sh</code> (it exports <code>RESEARCHVAULT_PORTAL_TOKEN</code>) and read <code>.portal_auth</code>
          </div>
          <input
            type="password"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            className="w-full border border-white/10 p-2 rounded text-gray-100 bg-void font-mono"
            placeholder="Token"
          />
          <button
            onClick={handleLogin}
            disabled={!token.trim()}
            className="w-full bg-cyan-dim text-cyan p-2 rounded disabled:opacity-50 border border-cyan/30 hover:border-cyan/60"
          >
            Login
          </button>
          {authError && (
            <div className="text-sm text-red-200 space-y-2">
              <div className="font-bold">❌ Login Failed</div>
              <div>Invalid or expired token.</div>
              <div className="text-xs bg-red-900/20 p-2 rounded border border-red-500/30">
                <strong>How to fix:</strong> Run <code>./start_portal.sh</code>, then paste the token from <code>.portal_auth</code> (or set <code>RESEARCHVAULT_PORTAL_SHOW_TOKEN=1</code> to print tokenized URLs).
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-void text-gray-100 font-sans flex flex-col ${devMode ? 'border-4 border-yellow-400' : ''}`}>
      {devMode && (
        <div className="bg-yellow-400 text-yellow-900 px-4 py-1 text-center text-xs font-bold uppercase tracking-wider">
          <AlertTriangle className="inline w-3 h-3 mr-1" /> Advanced / Developer Mode Active
        </div>
      )}

      <header className="bg-void-surface border-b border-white/10 px-6 py-3 flex justify-between items-center sticky top-0 z-20">
        <div className="flex items-center gap-3">
          <Terminal className="w-6 h-6 text-cyan text-glow" />
          <div>
            <div className="font-bold text-lg tracking-tight">
              <DecryptedText text="Portal Command Center" speed={70} className="text-gray-100" />
            </div>
            <div className="text-xs text-gray-400">A visual shell over <code>scripts.vault</code>. DB-aware, live-updating.</div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setDevMode((v) => !v)}
            className={`text-xs px-2 py-1 rounded border ${devMode
              ? 'bg-yellow-100 border-yellow-400 text-yellow-900'
              : 'bg-void border-white/10 text-gray-300 hover:text-white hover:border-white/20'
              }`}
          >
            {devMode ? 'Dev Mode ON' : 'Dev Mode OFF'}
          </button>
          <button onClick={handleLogout} className="text-sm text-gray-300 hover:text-red-300">
            Logout
          </button>
        </div>
      </header>

      <ResearchPulseBar
        mode={mode}
        setMode={setMode}
        dbs={dbs}
        stream={stream}
        onSelectDb={selectDb}
        onRefreshDbs={refreshDbs}
      />
      {systemError && (
        <div className="bg-red-500/10 border-b border-red-500/20 text-red-200 px-6 py-2 text-xs font-mono">
          {systemError}
        </div>
      )}

      <main className="flex-1 p-6 max-w-6xl mx-auto w-full grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          {mode === 'diagnostics' ? (
            <DiagnosticsPanel
              refreshKey={refreshKey}
              onApplyDb={async (path) => {
                await selectDb(path);
              }}
            />
          ) : mode === 'graph' ? (
            <GraphView projectId={currentProject} refreshKey={refreshKey} onCommandResult={setLastResult} />
          ) : !currentProject ? (
            <EntryScreen
              onSelectProject={setCurrentProject}
              setLastResult={setLastResult}
              refreshKey={refreshKey}
              dbs={dbs}
              onSelectDb={(p) => selectDb(p)}
              secrets={secrets}
              onOpenDiagnostics={() => setMode('diagnostics')}
            />
          ) : (
            <ProjectDetail
              projectId={currentProject}
              onBack={() => setCurrentProject(null)}
              setLastResult={setLastResult}
              devMode={devMode}
              refreshKey={refreshKey}
            />
          )}
        </div>

        <div className="lg:col-span-1">
          <div className="sticky top-20">
            <div className="flex items-center gap-2 mb-2 text-gray-400 font-mono text-xs uppercase tracking-wider">
              <Terminal className="w-3 h-3" /> Last Command Output
            </div>
            <CommandOutput result={lastResult} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default function App() {
  return <MainApp />;
}
