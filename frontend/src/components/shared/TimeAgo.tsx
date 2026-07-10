import { formatDistanceToNow, format } from 'date-fns';

export function TimeAgo({ date }: { date: string | null }) {
  if (!date) return <span className="text-muted-foreground">—</span>;
  const d = new Date(date);
  return (
    <span title={format(d, 'PPpp')} className="text-muted-foreground text-sm">
      {formatDistanceToNow(d, { addSuffix: true })}
    </span>
  );
}
