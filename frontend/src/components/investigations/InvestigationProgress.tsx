import { CheckCircle, Loader2, Clock, AlertTriangle } from 'lucide-react';
import type { AgentStep } from '@/types/common';

const defaultSteps: AgentStep[] = [
  { name: 'Planning', status: 'waiting', duration: null },
  { name: 'Collecting', status: 'waiting', duration: null },
  { name: 'Analyzing', status: 'waiting', duration: null },
  { name: 'Root Cause', status: 'waiting', duration: null },
  { name: 'Recommendations', status: 'waiting', duration: null },
];

const stepIcon = (status: string) => {
  switch (status) {
    case 'done': return <CheckCircle className="h-5 w-5 text-emerald-400" />;
    case 'running': return <Loader2 className="h-5 w-5 text-amber-400 animate-spin" />;
    case 'error': return <AlertTriangle className="h-5 w-5 text-red-400" />;
    default: return <Clock className="h-5 w-5 text-muted-foreground" />;
  }
};

export function InvestigationProgress({ steps, status }: { steps?: AgentStep[]; status: string }) {
  const displaySteps = steps?.length ? steps : status === 'COMPLETED'
    ? defaultSteps.map((s) => ({ ...s, status: 'done' as const }))
    : status === 'FAILED'
    ? defaultSteps.map((s, i) => ({ ...s, status: i < 2 ? 'done' as const : i === 2 ? 'error' as const : 'waiting' as const }))
    : status === 'IN_PROGRESS'
    ? defaultSteps.map((s, i) => ({ ...s, status: i < 1 ? 'done' as const : i === 1 ? 'running' as const : 'waiting' as const }))
    : defaultSteps;

  return (
    <div className="flex items-center gap-0 overflow-x-auto py-2">
      {displaySteps.map((step, i) => (
        <div key={step.name} className="flex items-center">
          <div className="flex flex-col items-center gap-1 px-3">
            {stepIcon(step.status)}
            <span className={`text-xs font-medium ${step.status === 'done' ? 'text-emerald-400' : step.status === 'running' ? 'text-amber-400' : step.status === 'error' ? 'text-red-400' : 'text-muted-foreground'}`}>
              {step.name}
            </span>
            {step.duration !== null && <span className="text-[10px] text-muted-foreground">{(step.duration / 1000).toFixed(1)}s</span>}
          </div>
          {i < displaySteps.length - 1 && (
            <div className={`w-8 h-px ${step.status === 'done' ? 'bg-emerald-400' : 'bg-border'}`} />
          )}
        </div>
      ))}
    </div>
  );
}
