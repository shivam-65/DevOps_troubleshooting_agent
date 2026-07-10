import { cn } from '@/lib/utils';

export function ConnectionStatus({ connected }: { connected: boolean }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className={cn('h-2 w-2 rounded-full', connected ? 'bg-emerald-400' : 'bg-red-400')} />
      <span className="text-xs text-muted-foreground">{connected ? 'Live' : 'Disconnected'}</span>
    </div>
  );
}
