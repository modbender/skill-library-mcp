import { Activity, Clock, CheckCircle2, Zap } from 'lucide-react';
import { GlowCard } from '../ui/GlowCard';
import type { BrainStatus, Task } from '../../api/types';

interface SummaryCardsProps {
  brains: BrainStatus[];
  tasks: Task[];
}

export function SummaryCards({ brains, tasks }: SummaryCardsProps) {
  const activeBrains = brains.filter((b) => b.autoMode).length;
  const executingBrains = brains.filter((b) => b.status === 'EXECUTING').length;
  const readyTasks = tasks.filter((t) => t.status === 'READY').length;
  const completedToday = tasks.filter((t) => {
    const today = new Date().setHours(0, 0, 0, 0);
    return t.status === 'COMPLETED' && t.createdAt >= today;
  }).length;

  const cards = [
    {
      icon: Activity,
      label: 'Active Brains',
      value: activeBrains,
      total: brains.length,
      color: 'text-blue-400',
      glow: 'rgba(59, 130, 246, 0.3)',
    },
    {
      icon: Zap,
      label: 'Executing',
      value: executingBrains,
      total: brains.length,
      color: 'text-green-400',
      glow: 'rgba(34, 197, 94, 0.3)',
      animate: executingBrains > 0,
    },
    {
      icon: Clock,
      label: 'Ready Tasks',
      value: readyTasks,
      total: tasks.length,
      color: 'text-yellow-400',
      glow: 'rgba(234, 179, 8, 0.3)',
    },
    {
      icon: CheckCircle2,
      label: 'Completed Today',
      value: completedToday,
      total: tasks.length,
      color: 'text-purple-400',
      glow: 'rgba(168, 85, 247, 0.3)',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
      {cards.map((card) => (
        <GlowCard
          key={card.label}
          glowColor={card.glow}
          animate={card.animate}
          className="relative overflow-hidden"
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">{card.label}</p>
              <p className="text-3xl font-bold">
                {card.value}
                <span className="text-lg text-muted-foreground ml-1">/ {card.total}</span>
              </p>
            </div>
            <div className={`p-3 rounded-xl bg-secondary ${card.color}`}>
              <card.icon className="w-6 h-6" />
            </div>
          </div>
        </GlowCard>
      ))}
    </div>
  );
}
