import { Card } from '../ui/Card';
import type { Report } from '../../api/types';
import { Skeleton } from '../ui/Skeleton';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ReportViewerProps {
  reports: Report[];
  loading: boolean;
  onRefresh: () => void;
}

export function ReportViewer({ reports, loading, onRefresh }: ReportViewerProps) {
  return (
    <Card>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold">Recent Reports</h2>
        <button
          onClick={onRefresh}
          className="text-xs text-blue-300 hover:underline"
        >
          Refresh
        </button>
      </div>

      {loading && (
        <div className="space-y-3">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
      )}

      {!loading && reports.length === 0 && (
        <p className="text-xs text-muted-foreground">No reports found.</p>
      )}

      <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
        {reports.map((r) => (
          <div
            key={r.id}
            className="border border-border rounded-lg p-3 bg-secondary/20"
          >
            <div className="text-xs text-muted-foreground mb-2">
              {r.date || 'Unknown date'} • {r.kind || 'report'} •{' '}
              {new Date(r.updatedAt).toLocaleString()}
            </div>
            <div className="prose prose-invert prose-sm max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {r.markdown}
              </ReactMarkdown>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
