import { cn } from '@/lib/utils';

const statusStyles: Record<string, string> = {
  OPEN: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  INVESTIGATING: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  IN_PROGRESS: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  EXECUTING: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  PENDING: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/30',
  PROPOSED: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/30',
  RESOLVED: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  COMPLETED: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  APPROVED: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  CLOSED: 'bg-slate-500/10 text-slate-400 border-slate-500/30',
  FAILED: 'bg-red-500/10 text-red-400 border-red-500/30',
  REJECTED: 'bg-red-500/10 text-red-400 border-red-500/30',
};

export function StatusBadge({ status, className }: { status: string; className?: string }) {
  return (
    <span className={cn(
      'inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border',
      statusStyles[status] || 'bg-zinc-500/10 text-zinc-400 border-zinc-500/30',
      className
    )}>
      {status.replace(/_/g, ' ')}
    </span>
  );
}
