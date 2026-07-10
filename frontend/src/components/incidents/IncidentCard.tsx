import type { Incident } from '@/types/incident';
import { SeverityBadge } from '@/components/shared/SeverityBadge';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { TimeAgo } from '@/components/shared/TimeAgo';

interface Props {
  incident: Incident;
  onClick?: () => void;
}

export function IncidentCard({ incident, onClick }: Props) {
  return (
    <div onClick={onClick}
      className="bg-card border border-border rounded-lg p-4 hover:border-primary/40 transition-colors cursor-pointer group">
      <div className="flex items-start justify-between gap-3 mb-2">
        <h4 className="text-sm font-medium text-foreground group-hover:text-primary transition-colors line-clamp-1">{incident.title}</h4>
        <SeverityBadge severity={incident.severity} />
      </div>
      <p className="text-xs text-muted-foreground line-clamp-2 mb-3">{incident.description}</p>
      <div className="flex items-center justify-between">
        <StatusBadge status={incident.status} />
        <TimeAgo date={incident.createdAt} />
      </div>
      {incident.affectedServices.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {incident.affectedServices.slice(0, 3).map((s) => (
            <span key={s} className="text-[10px] px-1.5 py-0.5 bg-muted rounded text-muted-foreground">{s}</span>
          ))}
          {incident.affectedServices.length > 3 && (
            <span className="text-[10px] px-1.5 py-0.5 text-muted-foreground">+{incident.affectedServices.length - 3}</span>
          )}
        </div>
      )}
    </div>
  );
}
