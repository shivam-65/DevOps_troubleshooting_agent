import { format } from 'date-fns';
import { Circle, Play, CheckCircle, XCircle, Search, Zap, AlertTriangle } from 'lucide-react';
import type { TimelineEvent } from '@/types/common';

const iconMap: Record<string, React.ReactNode> = {
  CREATED: <Circle className="h-3.5 w-3.5 text-blue-400" />,
  STATUS_CHANGE: <Play className="h-3.5 w-3.5 text-amber-400" />,
  INVESTIGATION_STARTED: <Search className="h-3.5 w-3.5 text-indigo-400" />,
  INVESTIGATION_COMPLETED: <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />,
  INVESTIGATION_FAILED: <AlertTriangle className="h-3.5 w-3.5 text-red-400" />,
  ACTION_APPROVED: <Zap className="h-3.5 w-3.5 text-emerald-400" />,
  ACTION_EXECUTED: <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />,
  RESOLVED: <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />,
  CLOSED: <XCircle className="h-3.5 w-3.5 text-slate-400" />,
};

export function IncidentTimeline({ events }: { events: TimelineEvent[] }) {
  if (!events.length) return null;
  return (
    <div className="space-y-0">
      {events.map((event, i) => (
        <div key={event.id} className="flex gap-3 relative">
          <div className="flex flex-col items-center">
            <div className="flex items-center justify-center w-7 h-7 rounded-full bg-muted border border-border">
              {iconMap[event.type] || <Circle className="h-3.5 w-3.5 text-muted-foreground" />}
            </div>
            {i < events.length - 1 && <div className="w-px flex-1 bg-border my-1" />}
          </div>
          <div className="pb-4 pt-0.5">
            <p className="text-sm font-medium text-foreground">{event.title}</p>
            {event.description && <p className="text-xs text-muted-foreground mt-0.5">{event.description}</p>}
            <p className="text-xs text-muted-foreground mt-1">{format(new Date(event.timestamp), 'MMM d, yyyy HH:mm:ss')}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
