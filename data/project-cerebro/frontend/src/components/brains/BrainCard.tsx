import { Play } from 'lucide-react';
import type { BrainStatus } from '../../api/types';
import { GlowCard } from '../ui/GlowCard';
import { Badge } from '../ui/Badge';
import { Toggle } from '../ui/Toggle';
import { Button } from '../ui/Button';
import { PulseIndicator } from '../ui/PulseIndicator';
import { getBrainIcon, brainColors } from '../../utils/brainIcons';

interface BrainCardProps {
  brain: BrainStatus;
  onToggle: (id: string, enabled: boolean) => void;
  onRun: (id: string) => void;
  onClick: (id: string) => void;
}

export function BrainCard({ brain, onToggle, onRun, onClick }: BrainCardProps) {
  const isExecuting = brain.status === 'EXECUTING';
  const iconColor = brainColors[brain.id] || 'text-gray-400';

  return (
    <GlowCard
      onClick={() => onClick(brain.id)}
      animate={isExecuting}
      glowColor={
        isExecuting ? 'rgba(34, 197, 94, 0.4)' : 'rgba(59, 130, 246, 0.3)'
      }
      className="relative group"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-xl bg-secondary ${iconColor}`}>
            {getBrainIcon(brain.id)}
          </div>
          <div>
            <h3 className="font-semibold flex items-center gap-2">
              {brain.name}
              {isExecuting && <PulseIndicator active size="sm" color="green" />}
            </h3>
            <p className="text-xs text-muted-foreground">{brain.id}</p>
          </div>
        </div>
        
        <Badge variant={isExecuting ? 'success' : 'default'}>
          {brain.status}
        </Badge>
      </div>

      <div className="flex items-center justify-between gap-3" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Auto Mode</span>
          <Toggle
            checked={brain.autoMode}
            onChange={(enabled) => onToggle(brain.id, enabled)}
          />
        </div>

        <Button
          variant="secondary"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            onRun(brain.id);
          }}
          className="flex items-center gap-2"
        >
          <Play className="w-3 h-3" />
          Force Run
        </Button>
      </div>

    </GlowCard>
  );
}
