import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, AlertTriangle } from 'lucide-react';
import { incidentService } from '@/services/incidentService';
import type { Incident, IncidentFilters as IFilters, CreateIncidentRequest } from '@/types/incident';
import { usePagination } from '@/hooks/usePagination';
import { IncidentFilters } from '@/components/incidents/IncidentFilters';
import { IncidentForm } from '@/components/incidents/IncidentForm';
import { PagedTable } from '@/components/shared/PagedTable';
import { SeverityBadge } from '@/components/shared/SeverityBadge';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { TimeAgo } from '@/components/shared/TimeAgo';
import { LoadingState } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { EmptyState } from '@/components/shared/EmptyState';

export function IncidentsListPage() {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);
  const { pagination, setPage, setSize, updateFromResponse } = usePagination();
  const [filters, setFilters] = useState<IFilters>({ sortBy: 'createdAt', sortDir: 'desc' });

  const fetchIncidents = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params: Record<string, any> = {
        page: pagination.page,
        size: pagination.size,
        sortBy: filters.sortBy,
        sortDir: filters.sortDir,
      };
      if (filters.status) params.status = filters.status;
      if (filters.severity) params.severity = filters.severity;
      if (filters.search) params.search = filters.search;

      const res = await incidentService.getAll(params);
      setIncidents(res.content);
      updateFromResponse(res);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.size, filters, updateFromResponse]);

  useEffect(() => { fetchIncidents(); }, [fetchIncidents]);

  const handleCreate = async (data: CreateIncidentRequest) => {
    try {
      setCreating(true);
      setError(null);
      await incidentService.create(data);
      setShowCreate(false);
      fetchIncidents();
    } catch (err: any) {
      console.error('Failed to create incident:', err);
      setError(err.message || 'Failed to create incident');
    } finally {
      setCreating(false);
    }
  };

  const columns = [
    { header: 'Title', accessor: (r: Incident) => <span className="font-medium text-foreground">{r.title}</span> },
    { header: 'Severity', accessor: (r: Incident) => <SeverityBadge severity={r.severity} /> },
    { header: 'Status', accessor: (r: Incident) => <StatusBadge status={r.status} /> },
    { header: 'Services', accessor: (r: Incident) => (
      <span className="text-xs text-muted-foreground">
        {r.affectedServices.slice(0, 3).join(', ')}
        {r.affectedServices.length > 3 && ` +${r.affectedServices.length - 3}`}
      </span>
    )},
    { header: 'Assignee', accessor: (r: Incident) => <span className="text-muted-foreground">{r.assignee || '—'}</span> },
    { header: 'Created', accessor: (r: Incident) => <TimeAgo date={r.createdAt} /> },
  ];

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-foreground">Incidents</h2>
        <button onClick={() => { setShowCreate(true); setError(null); }}
          className="inline-flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors">
          <Plus className="h-4 w-4" /> Create Incident
        </button>
      </div>

      <IncidentFilters filters={filters} onFilterChange={setFilters} />

      {/* Create Dialog */}
      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="fixed inset-0 bg-black/60" onClick={() => !creating && setShowCreate(false)} />
          <div className="relative z-50 bg-card border border-border rounded-lg p-6 max-w-lg w-full mx-4 shadow-xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold text-foreground mb-4">Create Incident</h3>
            {error && (
              <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md text-sm text-destructive">
                {error}
              </div>
            )}
            <IncidentForm onSubmit={handleCreate} onCancel={() => setShowCreate(false)} loading={creating} />
          </div>
        </div>
      )}

      {loading ? <LoadingState /> : error ? <ErrorState error={error} onRetry={fetchIncidents} /> :
        incidents.length === 0 ? (
          <EmptyState icon={<AlertTriangle className="h-10 w-10" />} title="No incidents found"
            description="No incidents match your filters, or none have been created yet."
            action={<button onClick={() => setShowCreate(true)} className="px-4 py-2 rounded-md text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors">Create your first incident</button>} />
        ) : (
          <PagedTable columns={columns} data={incidents} pagination={pagination}
            onPageChange={setPage} onSizeChange={setSize}
            onRowClick={(r) => navigate(`/incidents/${r.id}`)} keyExtractor={(r) => r.id} />
        )}
    </div>
  );
}
