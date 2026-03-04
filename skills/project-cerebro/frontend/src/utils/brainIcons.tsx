import {
  Activity,
  Brain,
  Calendar,
  BookOpen,
  Database,
  DollarSign,
  Briefcase,
} from 'lucide-react';

export function getBrainIcon(id: string, className = 'w-5 h-5') {
  const icons: Record<string, React.ReactElement> = {
    nexus: <Activity className={className} />,
    personal: <Calendar className={className} />,
    school: <BookOpen className={className} />,
    research: <Database className={className} />,
    money: <DollarSign className={className} />,
    job: <Briefcase className={className} />,
  };

  return icons[id] || <Brain className={className} />;
}

export const brainColors: Record<string, string> = {
  nexus: 'text-blue-400',
  personal: 'text-green-400',
  school: 'text-purple-400',
  research: 'text-pink-400',
  money: 'text-yellow-400',
  job: 'text-orange-400',
};
