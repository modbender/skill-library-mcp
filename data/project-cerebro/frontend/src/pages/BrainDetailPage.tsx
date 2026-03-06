import { useEffect } from 'react';
import { ChevronLeft, Save } from 'lucide-react';
import type { BrainStatus } from '../api/types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Toggle } from '../components/ui/Toggle';
import { BrainConfigEditor } from '../components/brains/BrainConfigEditor';
import { ReportViewer } from '../components/reports/ReportViewer';
import { getBrainIcon, brainColors } from '../utils/brainIcons';
import { useReports } from '../hooks/useReports';
import { useBrainConfig } from '../hooks/useBrainConfig';

interface BrainDetailPageProps {
  brain: BrainStatus;
  onBack: () => void;
  onToggle: (id: string, enabled: boolean) => void;
}

export function BrainDetailPage({ brain, onBack, onToggle }: BrainDetailPageProps) {
  const { reports, loading: reportsLoading, fetchReports } = useReports();
  const { config, getCfg, setCfg, lastSaved, saveConfig } = useBrainConfig(brain.id);

  useEffect(() => {
    fetchReports(brain.id, 10);
  }, [brain.id, fetchReports]);

  const iconColor = brainColors[brain.id] || 'text-gray-400';

  return (
    <div className="min-h-screen p-8">
      {/* Header */}
      <header className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={onBack}
            className="mr-2"
          >
            <ChevronLeft className="w-6 h-6" />
          </Button>
          <div className={`p-2 bg-secondary rounded-lg ${iconColor}`}>
            {getBrainIcon(brain.id)}
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              {brain.name}
            </h1>
            <p className="text-muted-foreground text-sm">Configuration & Reports</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {lastSaved && (
            <span className="text-xs text-muted-foreground">
              Saved {lastSaved.toLocaleTimeString()}
            </span>
          )}
          <Button
            variant="primary"
            size="sm"
            onClick={() => saveConfig(brain.id, config)}
            className="flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            Save
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Config */}
        <div className="lg:col-span-2 space-y-6">
          {/* Core Automation */}
          <Card>
            <h2 className="text-lg font-semibold mb-6">Core Automation</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-secondary/30 rounded-lg border border-border">
                <div>
                  <div className="font-medium">Autonomous Execution</div>
                  <div className="text-sm text-muted-foreground">
                    Allow this brain to pull and execute tasks automatically
                  </div>
                </div>
                <Toggle
                  checked={brain.autoMode}
                  onChange={(v) => onToggle(brain.id, v)}
                />
              </div>
            </div>
          </Card>

          {/* Brain Config */}
          <BrainConfigEditor
            brainId={brain.id}
            config={config}
            getCfg={getCfg}
            setCfg={setCfg}
          />
        </div>

        {/* Right Column - Reports & Metadata */}
        <div className="space-y-6">
          {/* Reports */}
          <ReportViewer
            reports={reports}
            loading={reportsLoading}
            onRefresh={() => fetchReports(brain.id, 10)}
          />

          {/* Metadata */}
          <Card className="bg-blue-600/5 border-blue-600/20">
            <h2 className="text-sm font-bold uppercase tracking-wider text-blue-400 mb-2">
              Metadata
            </h2>
            <div className="text-xs space-y-2 font-mono">
              <div className="flex justify-between border-b border-white/5 pb-2">
                <span className="text-muted-foreground">ID:</span>
                <span>{brain.id}</span>
              </div>
              <div className="flex justify-between border-b border-white/5 pb-2">
                <span className="text-muted-foreground">Status:</span>
                <span className={brain.status === 'EXECUTING' ? 'text-green-400' : ''}>
                  {brain.status}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Auto Mode:</span>
                <span className={brain.autoMode ? 'text-green-400' : 'text-gray-400'}>
                  {brain.autoMode ? 'Enabled' : 'Disabled'}
                </span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
