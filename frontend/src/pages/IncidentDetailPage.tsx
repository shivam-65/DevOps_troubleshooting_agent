import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Trash2, Search, FileText } from 'lucide-react';
import { incidentService } from '@/services/incidentService';
import { investigationService } from '@/services/investigationService';
import { actionService } from '@/services/actionService';
import { reportService } from '@/services/reportService';
import type { Incident } from '@/types/incident';
import type { Investigation } from '@/types/investigation';
import type { Action } from '@/types/action';
import type { Report } from '@/types/report';
import type { TimelineEvent } from '@/types/common';
import { SeverityBadge } from '@/components/shared/SeverityBadge';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { TimeAgo } from '@/components/shared/TimeAgo';
import { LoadingState } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { ConfirmDialog } from '@/components/shared/ConfirmDialog';
import { IncidentStatusTransition } from '@/components/incidents/IncidentStatusTransition';
import { IncidentTimeline } from '@/components/incidents/IncidentTimeline';
import { InvestigationCard } from '@/components/investigations/InvestigationCard';
import { ActionCard } from '@/components/actions/ActionCard';
import { ReportCard } from '@/components/reports/ReportCard';
import { format } from 'date-fns';

export function IncidentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [incident, setIncident] = useState<Incident | null>(null);
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [actions, setActions] = useState<Action[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDelete, setShowDelete] = useState(false);
  const [actionTab, setActionTab] = useState('ALL');

  const fetchData = async () => {
    if (!id) return;
    try {
      setLoading(true);
      setError(null);
      const [inc, invs, acts, reps] = await Promise.all([
        incidentService.getById(id),
        investigationService.getByIncident(id),
        actionService.getAll({ incidentId: id, size: 50 }).then((r) => r.content),
        reportService.getAll({ incidentId: id, size: 50 }).then((r) => r.content),
      ]);
      setIncident(inc);
      setInvestigations(invs);
      setActions(acts);
      setReports(reps);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [id]);

  const handleTransition = async (status: string) => {
    if (!id) return;
    try {
      if (status === 'INVESTIGATING') {
        await investigationService.trigger(id);
      }
      const updated = await incidentService.update(id, { status: status as any });
      setIncident(updated);
      fetchData();
    } catch { /* ignore */ }
  };

  const handleDelete = async () => {
    if (!id) return;
    try {
      await incidentService.delete(id);
      navigate('/incidents');
    } catch { /* ignore */ }
  };

  const handleApprove = async (actionId: string) => {
    try { await actionService.approve(actionId, 'user'); fetchData(); } catch { /* ignore */ }
  };
  const handleReject = async (actionId: string) => {
    try { await actionService.reject(actionId); fetchData(); } catch { /* ignore */ }
  };
  const handleExecute = async (actionId: string) => {
    try { await actionService.execute(actionId); fetchData(); } catch { /* ignore */ }
  };

  if (loading) return <LoadingState />;
  if (error || !incident) return <ErrorState error={error || 'Incident not found'} onRetry={fetchData} />;

  const timeline: TimelineEvent[] = [
    { id: '1', type: 'CREATED', title: 'Incident created', description: null, timestamp: incident.createdAt, icon: 'circle' },
    ...investigations.map((inv) => ({
      id: `inv-${inv.id}`, type: inv.status === 'COMPLETED' ? 'INVESTIGATION_COMPLETED' : inv.status === 'FAILED' ? 'INVESTIGATION_FAILED' : 'INVESTIGATION_STARTED',
      title: `Investigation ${inv.status.toLowerCase()}`, description: inv.summary, timestamp: inv.startedAt || inv.createdAt, icon: 'search',
    })),
    ...(incident.resolvedAt ? [{ id: 'resolved', type: 'RESOLVED', title: 'Incident resolved', description: null, timestamp: incident.resolvedAt, icon: 'check' }] : []),
    ...(incident.closedAt ? [{ id: 'closed', type: 'CLOSED', title: 'Incident closed', description: null, timestamp: incident.closedAt, icon: 'x' }] : []),
  ].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

  const filteredActions = actionTab === 'ALL' ? actions : actions.filter((a) => a.status === actionTab);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h2 className="text-xl font-semibold text-foreground">{incident.title}</h2>
            <SeverityBadge severity={incident.severity} />
            <StatusBadge status={incident.status} />
          </div>
          <p className="text-sm text-muted-foreground">
            Created <TimeAgo date={incident.createdAt} /> · Updated <TimeAgo date={incident.updatedAt} />
          </p>
        </div>
        <div className="flex items-center gap-2">
          <IncidentStatusTransition incident={incident} onTransition={handleTransition} />
          <button onClick={() => setShowDelete(true)} className="p-2 rounded-md text-muted-foreground hover:text-red-400 hover:bg-red-500/10 transition-colors">
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Info Panel */}
      <div className="bg-card border border-border rounded-lg p-5">
        <p className="text-sm text-muted-foreground mb-4">{incident.description}</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-xs text-muted-foreground uppercase">Assignee</span>
            <p className="text-foreground mt-0.5">{incident.assignee || 'Unassigned'}</p>
          </div>
          <div>
            <span className="text-xs text-muted-foreground uppercase">Services</span>
            <div className="flex flex-wrap gap-1 mt-0.5">
              {incident.affectedServices.map((s) => (
                <span key={s} className="text-xs px-1.5 py-0.5 bg-muted rounded text-foreground">{s}</span>
              ))}
            </div>
          </div>
          <div>
            <span className="text-xs text-muted-foreground uppercase">Tags</span>
            <div className="flex flex-wrap gap-1 mt-0.5">
              {incident.tags.length ? incident.tags.map((t) => (
                <span key={t} className="text-xs px-1.5 py-0.5 bg-primary/10 text-primary rounded">{t}</span>
              )) : <span className="text-muted-foreground">—</span>}
            </div>
          </div>
          <div>
            <span className="text-xs text-muted-foreground uppercase">Timestamps</span>
            <div className="text-xs text-muted-foreground mt-0.5 space-y-0.5">
              <p>Created: {format(new Date(incident.createdAt), 'MMM d, HH:mm')}</p>
              {incident.resolvedAt && <p>Resolved: {format(new Date(incident.resolvedAt), 'MMM d, HH:mm')}</p>}
              {incident.closedAt && <p>Closed: {format(new Date(incident.closedAt), 'MMM d, HH:mm')}</p>}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Timeline */}
        <div className="lg:col-span-1">
          <div className="bg-card border border-border rounded-lg p-5">
            <h3 className="text-sm font-medium text-foreground mb-4">Timeline</h3>
            <IncidentTimeline events={timeline} />
          </div>
        </div>

        {/* Right: Investigations + Actions + Reports */}
        <div className="lg:col-span-2 space-y-6">
          {/* Investigations */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-foreground">Investigations ({investigations.length})</h3>
              <button onClick={() => investigationService.trigger(id!).then(fetchData)}
                className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-medium bg-primary/10 text-primary hover:bg-primary/20 transition-colors">
                <Search className="h-3 w-3" /> New Investigation
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {investigations.map((inv) => (
                <InvestigationCard key={inv.id} investigation={inv}
                  onClick={() => navigate(`/incidents/${id}/investigations/${inv.id}`)} />
              ))}
            </div>
          </div>

          {/* Actions */}
          <div>
            <h3 className="text-sm font-medium text-foreground mb-3">Actions ({actions.length})</h3>
            <div className="flex gap-1 mb-3 overflow-x-auto">
              {['ALL', 'PROPOSED', 'APPROVED', 'COMPLETED', 'FAILED'].map((tab) => (
                <button key={tab} onClick={() => setActionTab(tab)}
                  className={`px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${actionTab === tab ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:text-foreground'}`}>
                  {tab}
                </button>
              ))}
            </div>
            <div className="space-y-2">
              {filteredActions.map((action) => (
                <ActionCard key={action.id} action={action} onApprove={handleApprove} onReject={handleReject} onExecute={handleExecute} />
              ))}
              {filteredActions.length === 0 && <p className="text-sm text-muted-foreground py-4">No actions in this category.</p>}
            </div>
          </div>

          {/* Reports */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-foreground">Reports ({reports.length})</h3>
              <button onClick={async () => {
                try {
                  await reportService.generate({ incidentId: id!, title: `Post-Incident Report: ${incident.title}`, format: 'JSON' });
                  fetchData();
                } catch { /* ignore */ }
              }}
                className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-medium bg-primary/10 text-primary hover:bg-primary/20 transition-colors">
                <FileText className="h-3 w-3" /> Generate Report
              </button>
            </div>
            <div className="space-y-2">
              {reports.map((report) => (
                <ReportCard key={report.id} report={report} onView={() => navigate(`/reports`)} />
              ))}
            </div>
          </div>
        </div>
      </div>

      <ConfirmDialog open={showDelete} title="Delete Incident" description="This will permanently delete this incident and all related data."
        confirmLabel="Delete" destructive onConfirm={handleDelete} onCancel={() => setShowDelete(false)} />
    </div>
  );
}
