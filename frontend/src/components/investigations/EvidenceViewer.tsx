import { useState } from 'react';
import { Database, FileText, BarChart3, GitBranch } from 'lucide-react';
import type { Evidence } from '@/types/evidence';
import { MetricsChart } from '@/components/charts/MetricsChart';

const sourceIcons: Record<string, React.ReactNode> = {
  kubernetes: <Database className="h-4 w-4" />,
  logs: <FileText className="h-4 w-4" />,
  metrics: <BarChart3 className="h-4 w-4" />,
  git: <GitBranch className="h-4 w-4" />,
};

export function EvidenceViewer({ evidence }: { evidence: Evidence[] }) {
  const sources = [...new Set(evidence.map((e) => e.source))];
  const [activeTab, setActiveTab] = useState(sources[0] || '');

  if (!evidence.length) return <p className="text-sm text-muted-foreground py-4">No evidence collected yet.</p>;

  const activeEvidence = evidence.filter((e) => e.source === activeTab);

  return (
    <div>
      <div className="flex gap-1 border-b border-border mb-4">
        {sources.map((source) => (
          <button key={source} onClick={() => setActiveTab(source)}
            className={`inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium border-b-2 transition-colors -mb-px ${activeTab === source ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}`}>
            {sourceIcons[source]}
            {source.charAt(0).toUpperCase() + source.slice(1)}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {activeEvidence.map((ev) => (
          <EvidencePanel key={ev.id} evidence={ev} />
        ))}
      </div>
    </div>
  );
}

function EvidencePanel({ evidence }: { evidence: Evidence }) {
  const data = typeof evidence.data === 'string' ? tryParse(evidence.data) : evidence.data;

  if (evidence.source === 'kubernetes') return <KubernetesPanel data={data} />;
  if (evidence.source === 'logs') return <LogsPanel data={data} />;
  if (evidence.source === 'metrics') return <MetricsPanel data={data} />;
  if (evidence.source === 'git') return <GitPanel data={data} />;

  return (
    <pre className="bg-muted rounded-lg p-4 text-xs text-foreground overflow-x-auto font-mono">
      {JSON.stringify(data, null, 2)}
    </pre>
  );
}

function tryParse(s: string) {
  try { return JSON.parse(s); } catch { return s; }
}

function KubernetesPanel({ data }: { data: any }) {
  const pods = data?.podEvents || data?.pods || [];
  const deployments = data?.deployments || [];

  return (
    <div className="space-y-4">
      {pods.length > 0 && (
        <div className="overflow-x-auto">
          <h4 className="text-xs font-medium text-muted-foreground uppercase mb-2">Pod Status</h4>
          <table className="w-full text-xs">
            <thead><tr className="border-b border-border">
              <th className="text-left py-2 px-3 text-muted-foreground font-medium">Pod</th>
              <th className="text-left py-2 px-3 text-muted-foreground font-medium">Status</th>
              <th className="text-left py-2 px-3 text-muted-foreground font-medium">Restarts</th>
              <th className="text-left py-2 px-3 text-muted-foreground font-medium">Events</th>
            </tr></thead>
            <tbody>
              {pods.map((pod: any, i: number) => (
                <tr key={i} className={`border-b border-border/50 ${['CrashLoopBackOff', 'OOMKilled', 'Failed'].includes(pod.status) ? 'bg-red-500/5' : ''}`}>
                  <td className="py-2 px-3 font-mono">{pod.podName || pod.name}</td>
                  <td className="py-2 px-3"><span className={`${['CrashLoopBackOff', 'OOMKilled', 'Failed'].includes(pod.status) ? 'text-red-400' : 'text-emerald-400'}`}>{pod.status}</span></td>
                  <td className="py-2 px-3">{pod.restarts ?? 0}</td>
                  <td className="py-2 px-3 text-muted-foreground">{(pod.events || []).join(', ') || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {deployments.length > 0 && (
        <div className="overflow-x-auto">
          <h4 className="text-xs font-medium text-muted-foreground uppercase mb-2">Deployments</h4>
          <table className="w-full text-xs">
            <thead><tr className="border-b border-border">
              <th className="text-left py-2 px-3 text-muted-foreground font-medium">Name</th>
              <th className="text-left py-2 px-3 text-muted-foreground font-medium">Ready</th>
              <th className="text-left py-2 px-3 text-muted-foreground font-medium">Conditions</th>
            </tr></thead>
            <tbody>
              {deployments.map((d: any, i: number) => (
                <tr key={i} className="border-b border-border/50">
                  <td className="py-2 px-3 font-mono">{d.name}</td>
                  <td className="py-2 px-3">{d.readyReplicas ?? 0}/{d.replicas ?? 0}</td>
                  <td className="py-2 px-3 text-muted-foreground">{(d.conditions || []).join(', ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function LogsPanel({ data }: { data: any }) {
  const errors = data?.errorLogs || data?.errors || [];
  const appLogs = data?.applicationLogs || [];
  const logs = [...errors, ...appLogs].sort((a: any, b: any) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  return (
    <div className="bg-muted rounded-lg p-3 max-h-96 overflow-y-auto font-mono text-xs space-y-1">
      {logs.length === 0 && <p className="text-muted-foreground">No log entries</p>}
      {logs.map((log: any, i: number) => (
        <div key={i} className="flex gap-2">
          <span className="text-muted-foreground shrink-0">{new Date(log.timestamp).toLocaleTimeString()}</span>
          <span className={`shrink-0 font-medium ${log.level === 'ERROR' ? 'text-red-400' : log.level === 'WARN' ? 'text-yellow-400' : 'text-blue-400'}`}>{log.level}</span>
          <span className="text-foreground break-all">{log.message}</span>
        </div>
      ))}
    </div>
  );
}

function MetricsPanel({ data }: { data: any }) {
  const charts: { title: string; points: any[]; color: string }[] = [];
  if (data?.cpu) {
    const points = Array.isArray(data.cpu) ? data.cpu.flatMap((s: any) => s.dataPoints || []) : [];
    if (points.length) charts.push({ title: 'CPU Usage (%)', points, color: '#f59e0b' });
  }
  if (data?.memory) {
    const points = Array.isArray(data.memory) ? data.memory.flatMap((s: any) => s.dataPoints || []) : [];
    if (points.length) charts.push({ title: 'Memory Usage (%)', points, color: '#8b5cf6' });
  }
  if (data?.errorRate) {
    const points = Array.isArray(data.errorRate) ? data.errorRate.flatMap((s: any) => s.dataPoints || []) : [];
    if (points.length) charts.push({ title: 'Error Rate (%)', points, color: '#ef4444' });
  }
  if (data?.requestRate) {
    const points = Array.isArray(data.requestRate) ? data.requestRate.flatMap((s: any) => s.dataPoints || []) : [];
    if (points.length) charts.push({ title: 'Request Rate (req/s)', points, color: '#10b981' });
  }

  if (!charts.length) return <p className="text-sm text-muted-foreground">No metrics data</p>;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {charts.map((c) => (
        <MetricsChart key={c.title} data={c.points} title={c.title} color={c.color} />
      ))}
    </div>
  );
}

function GitPanel({ data }: { data: any }) {
  const commits = data?.recentCommits || [];
  const deployments = data?.recentDeployments || [];

  return (
    <div className="space-y-4">
      {commits.length > 0 && (
        <div className="overflow-x-auto">
          <h4 className="text-xs font-medium text-muted-foreground uppercase mb-2">Recent Commits</h4>
          <table className="w-full text-xs">
            <thead><tr className="border-b border-border">
              <th className="text-left py-2 px-3 text-muted-foreground font-medium">SHA</th>
              <th className="text-left py-2 px-3 text-muted-foreground font-medium">Author</th>
              <th className="text-left py-2 px-3 text-muted-foreground font-medium">Message</th>
              <th className="text-left py-2 px-3 text-muted-foreground font-medium">Date</th>
            </tr></thead>
            <tbody>
              {commits.map((c: any, i: number) => (
                <tr key={i} className="border-b border-border/50">
                  <td className="py-2 px-3 font-mono text-primary">{(c.sha || c.shortSha || '').slice(0, 7)}</td>
                  <td className="py-2 px-3">{c.author}</td>
                  <td className="py-2 px-3 text-foreground max-w-xs truncate">{c.message}</td>
                  <td className="py-2 px-3 text-muted-foreground">{new Date(c.timestamp).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {deployments.length > 0 && (
        <div className="overflow-x-auto">
          <h4 className="text-xs font-medium text-muted-foreground uppercase mb-2">Recent Deployments</h4>
          <table className="w-full text-xs">
            <thead><tr className="border-b border-border">
              <th className="text-left py-2 px-3 text-muted-foreground font-medium">Version</th>
              <th className="text-left py-2 px-3 text-muted-foreground font-medium">Deployer</th>
              <th className="text-left py-2 px-3 text-muted-foreground font-medium">Date</th>
            </tr></thead>
            <tbody>
              {deployments.map((d: any, i: number) => (
                <tr key={i} className="border-b border-border/50">
                  <td className="py-2 px-3 font-mono">{d.version}</td>
                  <td className="py-2 px-3">{d.deployer}</td>
                  <td className="py-2 px-3 text-muted-foreground">{new Date(d.timestamp).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
