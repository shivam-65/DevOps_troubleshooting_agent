import { useEffect, useState, useCallback } from 'react';
import { Zap, Search } from 'lucide-react';
import { actionService } from '@/services/actionService';
import type { Action, ActionFilters as IFilters } from '@/types/action';
import { usePagination } from '@/hooks/usePagination';
import { ActionCard } from '@/components/actions/ActionCard';
import { LoadingState } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { EmptyState } from '@/components/shared/EmptyState';

export function ActionsPage() {
  const [actions, setActions] = useState<Action[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { pagination, setPage, updateFromResponse } = usePagination();
  const [statusFilter, setStatusFilter] = useState('');
  const [searchText, setSearchText] = useState('');

  const fetchActions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params: Record<string, any> = { page: pagination.page, size: pagination.size };
      if (statusFilter) params.status = statusFilter;
      const res = await actionService.getAll(params);
      setActions(res.content);
      updateFromResponse(res);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.size, statusFilter, updateFromResponse]);

  useEffect(() => { fetchActions(); }, [fetchActions]);

  const handleApprove = async (id: string) => {
    try { await actionService.approve(id, 'user'); fetchActions(); } catch { /* ignore */ }
  };
  const handleReject = async (id: string) => {
    try { await actionService.reject(id); fetchActions(); } catch { /* ignore */ }
  };
  const handleExecute = async (id: string) => {
    try { await actionService.execute(id); fetchActions(); } catch { /* ignore */ }
  };

  const filtered = searchText
    ? actions.filter((a) => a.title.toLowerCase().includes(searchText.toLowerCase()) || a.type.toLowerCase().includes(searchText.toLowerCase()))
    : actions;

  return (
    <div className="space-y-5">
      <h2 className="text-lg font-semibold text-foreground">Actions</h2>

      <div className="flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input value={searchText} onChange={(e) => setSearchText(e.target.value)}
            className="w-full bg-muted border border-border rounded-md pl-9 pr-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            placeholder="Search actions..." />
        </div>
        <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}
          className="bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary">
          <option value="">All Status</option>
          <option value="PROPOSED">Proposed</option>
          <option value="APPROVED">Approved</option>
          <option value="EXECUTING">Executing</option>
          <option value="COMPLETED">Completed</option>
          <option value="FAILED">Failed</option>
          <option value="REJECTED">Rejected</option>
        </select>
      </div>

      {loading ? <LoadingState /> : error ? <ErrorState error={error} onRetry={fetchActions} /> :
        filtered.length === 0 ? (
          <EmptyState icon={<Zap className="h-10 w-10" />} title="No actions found"
            description="Actions are created during AI investigations. Trigger an investigation on an incident to get recommended actions." />
        ) : (
          <div className="space-y-3">
            {filtered.map((action) => (
              <ActionCard key={action.id} action={action} onApprove={handleApprove} onReject={handleReject} onExecute={handleExecute} />
            ))}
            {pagination.totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 pt-4">
                <button disabled={pagination.page === 0} onClick={() => setPage(pagination.page - 1)}
                  className="px-3 py-1.5 rounded-md text-sm bg-muted hover:bg-secondary text-foreground disabled:opacity-30 transition-colors">
                  Previous
                </button>
                <span className="text-sm text-muted-foreground">Page {pagination.page + 1} of {pagination.totalPages}</span>
                <button disabled={pagination.page >= pagination.totalPages - 1} onClick={() => setPage(pagination.page + 1)}
                  className="px-3 py-1.5 rounded-md text-sm bg-muted hover:bg-secondary text-foreground disabled:opacity-30 transition-colors">
                  Next
                </button>
              </div>
            )}
          </div>
        )}
    </div>
  );
}
