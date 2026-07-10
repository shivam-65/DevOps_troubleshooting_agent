import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { investigationService } from '@/services/investigationService';
import type { Investigation } from '@/types/investigation';
import type { Evidence } from '@/types/evidence';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { LoadingState } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { InvestigationProgress } from '@/components/investigations/InvestigationProgress';
import { RootCauseDisplay } from '@/components/investigations/RootCauseDisplay';
import { EvidenceViewer } from '@/components/investigations/EvidenceViewer';
import { ActionCard } from '@/components/actions/ActionCard';
import { actionService } from '@/services/actionService';

export function InvestigationDetailPage() {
  const { id: incidentId, investigationId } = useParams<{ id: string; investigationId: string }>();
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<'overview' | 'evidence' | 'actions'>('overview');

  const fetchData = async () => {
    if (!incidentId || !investigationId) return;
    try {
      setLoading(true);
      setError(null);
      const [inv, ev] = await Promise.all([
        investigationService.getById(incidentId, investigationId),
        investigationService.getEvidence(incidentId, investigationId).catch(() => []),
      ]);
      setInvestigation(inv);
      setEvidence(ev);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [incidentId, investigationId]);

  if (loading) return <LoadingState />;
  if (error || !investigation) return <ErrorState error={error || 'Investigation not found'} onRetry={fetchData} />;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to={`/incidents/${incidentId}`} className="p-1.5 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition-colors">
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold text-foreground">Investigation</h2>
            <StatusBadge status={investigation.status} />
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">Investigation #{investigationId?.slice(0, 8)}</p>
        </div>
      </div>

      <InvestigationProgress status={investigation.status} />

      {/* Tabs */}
      <div className="flex gap-1 border-b border-border">
        {(['overview', 'evidence', 'actions'] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors capitalize ${tab === t ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}`}>
            {t} {t === 'evidence' && `(${evidence.length})`} {t === 'actions' && investigation.actions ? `(${investigation.actions.length})` : ''}
          </button>
        ))}
      </div>

      {tab === 'overview' && (
        <RootCauseDisplay rootCause={investigation.rootCause} confidence={investigation.confidence}
          summary={investigation.summary} aiModelUsed={investigation.aiModelUsed} />
      )}

      {tab === 'evidence' && <EvidenceViewer evidence={evidence} />}

      {tab === 'actions' && investigation.actions && (
        <div className="space-y-3">
          {investigation.actions.map((action) => (
            <ActionCard key={action.id} action={action}
              onApprove={async (actionId) => { await actionService.approve(actionId, 'user'); fetchData(); }}
              onReject={async (actionId) => { await actionService.reject(actionId); fetchData(); }}
              onExecute={async (actionId) => { await actionService.execute(actionId); fetchData(); }} />
          ))}
          {investigation.actions.length === 0 && <p className="text-sm text-muted-foreground py-4">No recommended actions yet.</p>}
        </div>
      )}
    </div>
  );
}
