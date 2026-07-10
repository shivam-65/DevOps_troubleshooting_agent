import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, Search, Zap, BarChart3 } from 'lucide-react';
import { incidentService } from '@/services/incidentService';
import { actionService } from '@/services/actionService';
import type { Incident } from '@/types/incident';
import type { Action } from '@/types/action';
import { SeverityBadge } from '@/components/shared/SeverityBadge';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { TimeAgo } from '@/components/shared/TimeAgo';
import { LoadingState } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { ActionCard } from '@/components/actions/ActionCard';
import { SeverityDistribution } from '@/components/charts/SeverityDistribution';
import { StatusOverview } from '@/components/charts/StatusOverview';

interface DashboardStats {
  totalIncidents: number;
  openIncidents: number;
  activeInvestigations: number;
  pendingActions: number;
}

export function DashboardPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<DashboardStats>({ totalIncidents: 0, openIncidents: 0, activeInvestigations: 0, pendingActions: 0 });
  const [activeIncidents, setActiveIncidents] = useState<Incident[]>([]);
  const [recentActions, setRecentActions] = useState<Action[]>([]);
  const [severityData, setSeverityData] = useState<{ severity: string; count: number }[]>([]);
  const [statusData, setStatusData] = useState<{ status: string; count: number }[]>([]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [allRes, openRes, investigatingRes, actionsRes] = await Promise.all([
        incidentService.getAll({ page: 0, size: 1 }),
        incidentService.getAll({ page: 0, size: 10, status: 'OPEN', sortBy: 'severity', sortDir: 'asc' }),
        incidentService.getAll({ page: 0, size: 10, status: 'INVESTIGATING' }),
        actionService.getAll({ page: 0, size: 5, status: 'PROPOSED' }),
      ]);

      const active = [...openRes.content, ...investigatingRes.content].slice(0, 10);
      setActiveIncidents(active);
      setRecentActions(actionsRes.content);

      setStats({
        totalIncidents: allRes.totalElements,
        openIncidents: openRes.totalElements,
        activeInvestigations: investigatingRes.totalElements,
        pendingActions: actionsRes.totalElements,
      });

      // Compute severity/status distribution from available data
      const sevCounts: Record<string, number> = {};
      const statusCounts: Record<string, number> = {};
      active.forEach((inc) => {
        sevCounts[inc.severity] = (sevCounts[inc.severity] || 0) + 1;
        statusCounts[inc.status] = (statusCounts[inc.status] || 0) + 1;
      });
      setSeverityData(Object.entries(sevCounts).map(([severity, count]) => ({ severity, count })));
      setStatusData(Object.entries(statusCounts).map(([status, count]) => ({ status, count })));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleApprove = async (id: string) => {
    try {
      await actionService.approve(id, 'dashboard-user');
      fetchData();
    } catch { /* ignore */ }
  };

  const handleReject = async (id: string) => {
    try {
      await actionService.reject(id);
      fetchData();
    } catch { /* ignore */ }
  };

  if (loading) return <LoadingState message="Loading dashboard..." />;
  if (error) return <ErrorState error={error} onRetry={fetchData} />;

  const statCards = [
    { label: 'Total Incidents', value: stats.totalIncidents, icon: <BarChart3 className="h-5 w-5" />, color: 'text-primary' },
    { label: 'Open Incidents', value: stats.openIncidents, icon: <AlertTriangle className="h-5 w-5" />, color: stats.openIncidents > 0 ? 'text-red-400' : 'text-emerald-400' },
    { label: 'Active Investigations', value: stats.activeInvestigations, icon: <Search className="h-5 w-5" />, color: 'text-amber-400' },
    { label: 'Pending Actions', value: stats.pendingActions, icon: <Zap className="h-5 w-5" />, color: 'text-indigo-400' },
  ];

  return (
    <div className="space-y-6">
      {/* Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card) => (
          <div key={card.label} className="bg-card border border-border rounded-lg p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-muted-foreground">{card.label}</span>
              <span className={card.color}>{card.icon}</span>
            </div>
            <p className={`text-3xl font-bold ${card.color}`}>{card.value}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SeverityDistribution data={severityData} />
        <StatusOverview data={statusData} />
      </div>

      {/* Active Incidents Table */}
      <div className="bg-card border border-border rounded-lg">
        <div className="px-5 py-4 border-b border-border">
          <h3 className="text-sm font-medium text-foreground">Active Incidents</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                <th className="text-left px-5 py-3 text-xs font-medium text-muted-foreground uppercase">Title</th>
                <th className="text-left px-5 py-3 text-xs font-medium text-muted-foreground uppercase">Severity</th>
                <th className="text-left px-5 py-3 text-xs font-medium text-muted-foreground uppercase">Status</th>
                <th className="text-left px-5 py-3 text-xs font-medium text-muted-foreground uppercase">Services</th>
                <th className="text-left px-5 py-3 text-xs font-medium text-muted-foreground uppercase">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {activeIncidents.length === 0 ? (
                <tr><td colSpan={5} className="px-5 py-8 text-center text-muted-foreground">No active incidents — all clear!</td></tr>
              ) : (
                activeIncidents.map((inc) => (
                  <tr key={inc.id} onClick={() => navigate(`/incidents/${inc.id}`)}
                    className="hover:bg-muted/30 cursor-pointer transition-colors">
                    <td className="px-5 py-3 font-medium text-foreground">{inc.title}</td>
                    <td className="px-5 py-3"><SeverityBadge severity={inc.severity} /></td>
                    <td className="px-5 py-3"><StatusBadge status={inc.status} /></td>
                    <td className="px-5 py-3 text-muted-foreground text-xs">
                      {inc.affectedServices.slice(0, 2).join(', ')}
                      {inc.affectedServices.length > 2 && ` +${inc.affectedServices.length - 2}`}
                    </td>
                    <td className="px-5 py-3"><TimeAgo date={inc.createdAt} /></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Actions */}
      {recentActions.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-foreground mb-3">Pending Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {recentActions.map((action) => (
              <ActionCard key={action.id} action={action} onApprove={handleApprove} onReject={handleReject} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
