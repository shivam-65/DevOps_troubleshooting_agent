import { AlertTriangle } from 'lucide-react';
import { ConfidenceScore } from '@/components/shared/ConfidenceScore';

interface Props {
  rootCause: string | null;
  confidence: number | null;
  summary: string | null;
  aiModelUsed?: string | null;
}

export function RootCauseDisplay({ rootCause, confidence, summary, aiModelUsed }: Props) {
  if (!rootCause && !summary) return null;

  return (
    <div className="space-y-4">
      {summary && (
        <div className="bg-card border border-border rounded-lg p-5">
          <h3 className="text-sm font-medium text-foreground mb-2">Summary</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">{summary}</p>
        </div>
      )}
      {rootCause && (
        <div className="bg-red-500/5 border border-red-500/20 rounded-lg p-5">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-red-400 mb-1">Root Cause Identified</h3>
              <p className="text-sm text-foreground leading-relaxed">{rootCause}</p>
            </div>
            <ConfidenceScore value={confidence} size={56} />
          </div>
        </div>
      )}
      {aiModelUsed && (
        <p className="text-xs text-muted-foreground">Analysis by: {aiModelUsed}</p>
      )}
    </div>
  );
}
