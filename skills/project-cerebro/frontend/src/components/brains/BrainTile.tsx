import { Play } from 'lucide-react';
import type { BrainStatus } from '../../api/types';
import { GlowCard } from '../ui/GlowCard';
import { Badge } from '../ui/Badge';
import { Toggle } from '../ui/Toggle';
import { Button } from '../ui/Button';
import { PulseIndicator } from '../ui/PulseIndicator';
import { getBrainIcon, brainColors } from '../../utils/brainIcons';
import { cn } from '../../utils/cn';

interface BrainTileProps {
  brain: BrainStatus;
  onToggle: (id: string, enabled: boolean) => void;
  onRun: (id: string) => void;
  onClick: (id: string) => void;
  className?: string;
}

export function BrainTile({ brain, onToggle, onRun, onClick, className }: BrainTileProps) {
  const isExecuting = brain.status === 'EXECUTING';
  const iconColor = brainColors[brain.id] || 'text-gray-400';

  const displayStatus = isExecuting ? 'ACTIVE' : brain.status;

  return (
    <GlowCard
      onClick={() => onClick(brain.id)}
      animate={isExecuting}
      glowColor={isExecuting ? 'rgba(34, 197, 94, 0.45)' : 'rgba(59, 130, 246, 0.25)'}
      className={cn(
        'relative group min-w-[260px] sm:min-w-[320px] max-w-[420px]',
        'bg-gradient-to-r from-blue-600/5 to-purple-600/5 bg-[length:200%_auto] animate-gradient-shift',
        className
      )}
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className={cn('p-2 rounded-xl bg-secondary shrink-0', iconColor)}>
            {getBrainIcon(brain.id, 'w-5 h-5')}
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold truncate">{brain.name}</h3>
              {isExecuting && <PulseIndicator active size="sm" color="green" />}
            </div>
            <p className="text-xs text-muted-foreground truncate">{brain.id}</p>
          </div>
        </div>

        <Badge variant={isExecuting ? 'success' : 'default'} className={cn('shrink-0', isExecuting && 'text-green-100')}>
          {displayStatus}
        </Badge>
      </div>

      <div
        className="mt-4 flex items-center justify-between gap-3"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Auto</span>
          <Toggle checked={brain.autoMode} onChange={(enabled) => onToggle(brain.id, enabled)} />
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            onRun(brain.id);
          }}
          className="flex items-center gap-2 rounded-full bg-black/5 hover:bg-black/10 dark:bg-white/5 dark:hover:bg-white/10"
        >
          <Play className="w-3.5 h-3.5" />
          Force Run
        </Button>
      </div>
    </GlowCard>
  );
}
