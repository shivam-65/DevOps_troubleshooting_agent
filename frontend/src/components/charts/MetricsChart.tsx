import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

interface Props {
  data: { timestamp: string; value: number }[];
  title: string;
  yAxisLabel?: string;
  color?: string;
}

export function MetricsChart({ data, title, yAxisLabel, color = '#6366f1' }: Props) {
  if (!data.length) return null;
  return (
    <div className="bg-card border border-border rounded-lg p-5">
      <h3 className="text-sm font-medium text-foreground mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2e303a" />
          <XAxis dataKey="timestamp" tick={{ fill: '#9ca3af', fontSize: 10 }} axisLine={false} tickLine={false}
            tickFormatter={(v) => new Date(v).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} />
          <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} axisLine={false} tickLine={false} label={yAxisLabel ? { value: yAxisLabel, angle: -90, position: 'insideLeft', fill: '#9ca3af', fontSize: 10 } : undefined} />
          <Tooltip contentStyle={{ backgroundColor: '#1a1b23', border: '1px solid #2e303a', borderRadius: '6px', color: '#e4e4e7', fontSize: '12px' }}
            labelFormatter={(v) => new Date(v).toLocaleString()} />
          <Area type="monotone" dataKey="value" stroke={color} fill={color} fillOpacity={0.1} strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
