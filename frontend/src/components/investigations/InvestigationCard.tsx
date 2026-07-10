import type { Investigation } from '@/types/investigation';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { ConfidenceScore } from '@/components/shared/ConfidenceScore';
import { TimeAgo } from '@/components/shared/TimeAgo';

interface Props {
  investigation: Investigation;
  onClick?: () => void;
}

export function InvestigationCard({ investigation, onClick }: Props) {
  return (
    <div onClick={onClick}
      className="bg-card border border-border rounded-lg p-4 hover:border-primary/30 transition-colors cursor-pointer">
      <div className="flex items-start justify-between gap-3 mb-2">
        <StatusBadge status={investigation.status} />
        {investigation.confidence !== null && <ConfidenceScore value={investigation.confidence} size={36} />}
      </div>
      {investigation.summary && (
        <p className="text-xs text-muted-foreground line-clamp-2 mb-2">{investigation.summary}</p>
      )}
      {investigation.rootCause && (
        <p className="text-xs text-foreground/80 line-clamp-1 mb-2">Root Cause: {investigation.rootCause}</p>
      )}
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        {investigation.aiModelUsed && <span>{investigation.aiModelUsed}</span>}
        <TimeAgo date={investigation.startedAt || investigation.createdAt} />
      </div>
    </div>
  );
}
