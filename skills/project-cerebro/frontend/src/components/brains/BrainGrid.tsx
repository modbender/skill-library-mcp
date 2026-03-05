import type { BrainStatus } from '../../api/types';
import { BrainCard } from './BrainCard';
import { SkeletonCard } from '../ui/Skeleton';

interface BrainGridProps {
  brains: BrainStatus[];
  loading: boolean;
  onToggle: (id: string, enabled: boolean) => void;
  onRun: (id: string) => void;
  onBrainClick: (id: string) => void;
}

export function BrainGrid({
  brains,
  loading,
  onToggle,
  onRun,
  onBrainClick,
}: BrainGridProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      {brains.map((brain) => (
        <BrainCard
          key={brain.id}
          brain={brain}
          onToggle={onToggle}
          onRun={onRun}
          onClick={onBrainClick}
        />
      ))}
    </div>
  );
}
