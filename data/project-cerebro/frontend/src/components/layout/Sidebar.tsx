import { Activity, Briefcase, User } from 'lucide-react';
import type { BrainStatus } from '../../api/types';
import { getBrainIcon } from '../../utils/brainIcons';
import { cn } from '../../utils/cn';
import { GradientText } from '../ui/GradientText';
import { FileIngestion } from '../dashboard/FileIngestion';

interface SidebarProps {
  brains: BrainStatus[];
  currentView: 'dashboard' | 'brain-detail' | 'job-applications' | 'job-profile';
  selectedBrainId: string | null;
  onNavigate: (view: 'dashboard' | 'brain-detail' | 'job-applications' | 'job-profile', brainId?: string) => void;
  isOpen: boolean;
  theme: 'light' | 'dark';
}

export function Sidebar({
  brains,
  currentView,
  selectedBrainId,
  onNavigate,
  isOpen,
  theme,
}: SidebarProps) {
  const jobsEnabled = brains.some((b) => b.id === 'job');
  const isDark = theme === 'dark';
  
  const activeClass = isDark
    ? 'bg-blue-600/20 text-blue-200 border border-blue-500/30'
    : 'bg-blue-200/70 text-blue-900 border border-blue-500/40';
  
  const inactiveClass = 'text-muted-foreground hover:bg-white/5 hover:shadow-md hover:-translate-y-0.5';

  return (
    <aside
      className={cn(
        'hidden lg:flex flex-col gap-6',
        'border-r backdrop-blur-xl p-6',
        'shadow-[inset_0_0_40px_rgba(59,130,246,0.05)]',
        'transition-all duration-300',
        isDark ? 'border-white/10 bg-white/5' : 'border-black/10 bg-white/80',
        isOpen ? 'w-64 opacity-100 translate-x-0' : 'w-0 opacity-0 -translate-x-full pointer-events-none'
      )}
    >
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-xl bg-blue-600/20 text-blue-300">
          <Activity className="w-5 h-5" />
        </div>
        <div>
          <div className="text-sm font-semibold">
            <GradientText>Project Cerebro</GradientText>
          </div>
          <div className="text-[11px] text-muted-foreground">Control Surface</div>
        </div>
      </div>

      <nav className="flex flex-col gap-1 text-sm flex-1">
        <button
          onClick={() => onNavigate('dashboard')}
          className={cn(
            'flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200',
            currentView === 'dashboard' ? activeClass : inactiveClass
          )}
        >
          <Activity className="w-4 h-4" /> Dashboard
        </button>

        {jobsEnabled && (
          <>
            <button
              onClick={() => onNavigate('job-applications')}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200',
                currentView === 'job-applications' ? activeClass : inactiveClass
              )}
            >
              <Briefcase className="w-4 h-4" /> Job Applications
            </button>

            <button
              onClick={() => onNavigate('job-profile')}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200',
                currentView === 'job-profile' ? activeClass : inactiveClass
              )}
            >
              <User className="w-4 h-4" /> Job Profile
            </button>
          </>
        )}

        <div className="mt-4 text-[11px] uppercase tracking-widest text-muted-foreground">
          Brains
        </div>

        {brains.map((brain) => (
          <button
            key={brain.id}
            onClick={() => onNavigate('brain-detail', brain.id)}
            className={cn(
              'flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200',
              selectedBrainId === brain.id && currentView === 'brain-detail'
                ? activeClass
                : inactiveClass
            )}
          >
            {getBrainIcon(brain.id, 'w-4 h-4')}
            {brain.name}
          </button>
        ))}

        {/* Spacer */}
        <div className="flex-1" />

        {/* File ingestion lives in the sidebar now */}
        <div className="pt-2">
          <FileIngestion brains={brains} defaultBrainId="nexus" variant="sidebar" />
        </div>
      </nav>
    </aside>
  );
}
