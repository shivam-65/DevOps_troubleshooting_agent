import { FileText, Download } from 'lucide-react';
import type { Report } from '@/types/report';
import { format } from 'date-fns';

interface Props {
  report: Report;
  onView?: () => void;
  onExport?: (format: string) => void;
}

export function ReportCard({ report, onView, onExport }: Props) {
  return (
    <div className="bg-card border border-border rounded-lg p-4 hover:border-primary/30 transition-colors">
      <div className="flex items-start gap-3">
        <div className="p-2 bg-primary/10 rounded-md">
          <FileText className="h-4 w-4 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium text-foreground truncate">{report.title}</h4>
          <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
            <span className="px-1.5 py-0.5 bg-muted rounded text-xs">{report.format}</span>
            <span>{format(new Date(report.generatedAt), 'MMM d, yyyy HH:mm')}</span>
          </div>
        </div>
        <div className="flex gap-1">
          {onView && (
            <button onClick={onView} className="p-1.5 rounded-md hover:bg-muted transition-colors text-muted-foreground hover:text-foreground" title="View">
              <FileText className="h-3.5 w-3.5" />
            </button>
          )}
          {onExport && (
            <button onClick={() => onExport('JSON')} className="p-1.5 rounded-md hover:bg-muted transition-colors text-muted-foreground hover:text-foreground" title="Export">
              <Download className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
