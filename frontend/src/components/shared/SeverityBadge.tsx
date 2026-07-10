import { cn } from '@/lib/utils';

const severityStyles: Record<string, string> = {
  CRITICAL: 'bg-red-500/10 text-red-400 border-red-500/30',
  HIGH: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
  MEDIUM: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
  LOW: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
};

export function SeverityBadge({ severity, className }: { severity: string; className?: string }) {
  return (
    <span className={cn(
      'inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border',
      severityStyles[severity] || 'bg-zinc-500/10 text-zinc-400 border-zinc-500/30',
      className
    )}>
      {severity}
    </span>
  );
}
