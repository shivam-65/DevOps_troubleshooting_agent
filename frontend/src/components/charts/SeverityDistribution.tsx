import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const COLORS: Record<string, string> = {
  CRITICAL: '#ef4444',
  HIGH: '#f97316',
  MEDIUM: '#eab308',
  LOW: '#3b82f6',
};

interface Props {
  data: { severity: string; count: number }[];
}

export function SeverityDistribution({ data }: Props) {
  if (!data.length) return null;
  return (
    <div className="bg-card border border-border rounded-lg p-5">
      <h3 className="text-sm font-medium text-foreground mb-4">Severity Distribution</h3>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie data={data} dataKey="count" nameKey="severity" cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={3} strokeWidth={0}>
            {data.map((entry) => (
              <Cell key={entry.severity} fill={COLORS[entry.severity] || '#6b7280'} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ backgroundColor: '#1a1b23', border: '1px solid #2e303a', borderRadius: '6px', color: '#e4e4e7' }} />
          <Legend wrapperStyle={{ fontSize: '12px', color: '#9ca3af' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
