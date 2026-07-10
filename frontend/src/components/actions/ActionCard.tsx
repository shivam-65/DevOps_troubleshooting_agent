import { Check, X, Play, Zap } from 'lucide-react';
import type { Action } from '@/types/action';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { TimeAgo } from '@/components/shared/TimeAgo';

interface Props {
  action: Action;
  onApprove?: (id: string) => void;
  onReject?: (id: string) => void;
  onExecute?: (id: string) => void;
  onClick?: () => void;
}

const riskColors: Record<string, string> = {
  LOW: 'text-emerald-400',
  MEDIUM: 'text-yellow-400',
  HIGH: 'text-red-400',
};

export function ActionCard({ action, onApprove, onReject, onExecute, onClick }: Props) {
  return (
    <div onClick={onClick} className="bg-card border border-border rounded-lg p-4 hover:border-primary/30 transition-colors">
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium text-foreground truncate">{action.title}</h4>
          {action.description && <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{action.description}</p>}
        </div>
        <StatusBadge status={action.status} />
      </div>

      <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground mb-3">
        <span className="inline-flex items-center gap-1"><Zap className="h-3 w-3" />{action.type.replace(/_/g, ' ')}</span>
        {action.targetService && <span>Target: {action.targetService}</span>}
        {action.risk && <span className={riskColors[action.risk] || ''}>Risk: {action.risk}</span>}
        <TimeAgo date={action.createdAt} />
      </div>

      {action.command && (
        <div className="bg-muted rounded-md px-3 py-2 mb-3">
          <code className="text-xs text-foreground font-mono break-all">{action.command}</code>
        </div>
      )}

      <div className="flex gap-2">
        {action.status === 'PROPOSED' && onApprove && (
          <button onClick={(e) => { e.stopPropagation(); onApprove(action.id); }}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-600 hover:bg-emerald-700 text-white transition-colors">
            <Check className="h-3 w-3" /> Approve
          </button>
        )}
        {(action.status === 'PROPOSED' || action.status === 'APPROVED') && onReject && (
          <button onClick={(e) => { e.stopPropagation(); onReject(action.id); }}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-red-600/20 text-red-400 hover:bg-red-600/30 transition-colors">
            <X className="h-3 w-3" /> Reject
          </button>
        )}
        {action.status === 'APPROVED' && onExecute && (
          <button onClick={(e) => { e.stopPropagation(); onExecute(action.id); }}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-primary hover:bg-primary/90 text-primary-foreground transition-colors">
            <Play className="h-3 w-3" /> Execute
          </button>
        )}
      </div>
    </div>
  );
}
