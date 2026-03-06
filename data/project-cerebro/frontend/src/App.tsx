import { useState } from 'react';
import { Shell } from './components/layout/Shell';
import { DashboardPage } from './pages/DashboardPage';
import { BrainDetailPage } from './pages/BrainDetailPage';
import { JobApplicationsPage } from './pages/JobApplicationsPage';
import { JobProfilePage } from './pages/JobProfilePage';
import { useBrains } from './hooks/useBrains';
import { useTasks } from './hooks/useTasks';
import { useRecurring } from './hooks/useRecurring';
import { useTheme } from './hooks/useTheme';
// api removed
// ModelAlias removed

type View = 'dashboard' | 'brain-detail' | 'job-applications' | 'job-profile';

export default function App() {
  const [currentView, setCurrentView] = useState<View>('dashboard');
  const [selectedBrainId, setSelectedBrainId] = useState<string | null>(null);
  // models removed

  const { brains, loading: loadingBrains, toggleBrain, runBrain } = useBrains();
  const { tasks, loading: loadingTasks, createTask, deleteTask, executeTask, updateTask, clearAllTasks } = useTasks();
  const {
    recurringTasks,
    loading: loadingRecurring,
    createRecurringTask,
    updateRecurringTask,
    toggleRecurringTask,
    deleteRecurringTask,
    runRecurringTask,
  } = useRecurring();
  const { theme, mode, toggleTheme } = useTheme();
  
  // Model fetching removed (models configured in OpenClaw, not Cerebro).

  const jobsEnabled = brains.some((b) => b.id === 'job');

  const handleNavigate = (view: View | 'recurring-tasks', brainId?: string) => {
    if (view === 'recurring-tasks') {
      // Recurring tasks is now on dashboard, just switch to dashboard
      setCurrentView('dashboard');
    } else if (view === 'job-applications') {
      setCurrentView(jobsEnabled ? 'job-applications' : 'dashboard');
    } else if (view === 'job-profile') {
      setCurrentView(jobsEnabled ? 'job-profile' : 'dashboard');
    } else {
      setCurrentView(view);
    }
    if (brainId) {
      setSelectedBrainId(brainId);
    }
  };

  const handleBrainClick = (brainId: string) => {
    setSelectedBrainId(brainId);
    setCurrentView('brain-detail');
  };

  const selectedBrain = selectedBrainId
    ? brains.find((b) => b.id === selectedBrainId)
    : null;

  return (
    <Shell
      brains={brains}
      currentView={currentView}
      selectedBrainId={selectedBrainId}
      onNavigate={handleNavigate}
      theme={theme}
      mode={mode}
      onToggleTheme={toggleTheme}
    >
      {currentView === 'dashboard' && (
        <DashboardPage
          brains={brains}
          tasks={tasks}
          recurringTasks={recurringTasks}
          loadingBrains={loadingBrains}
          loadingTasks={loadingTasks}
          loadingRecurring={loadingRecurring}
          onToggleBrain={toggleBrain}
          onRunBrain={runBrain}
          onBrainClick={handleBrainClick}
          onCreateTask={createTask}
          onCreateRecurring={createRecurringTask}
          onDeleteRecurring={deleteRecurringTask}
          onRunRecurring={runRecurringTask}
          onUpdateRecurring={updateRecurringTask} // New prop
          onToggleRecurring={toggleRecurringTask} // New prop
          onDeleteTask={deleteTask}
          onExecuteTask={executeTask}
          onUpdateTask={updateTask}
          onClearAllTasks={clearAllTasks}
        />
      )}

      {currentView === 'brain-detail' && selectedBrain && (
        <BrainDetailPage
          brain={selectedBrain}
          onBack={() => setCurrentView('dashboard')}
          onToggle={toggleBrain}
        />
      )}

      {jobsEnabled && currentView === 'job-applications' && <JobApplicationsPage />}

      {jobsEnabled && currentView === 'job-profile' && <JobProfilePage />}
    </Shell>
  );
}
