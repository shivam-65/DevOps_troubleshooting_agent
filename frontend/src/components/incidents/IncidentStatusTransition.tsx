import { Play, CheckCircle, RotateCcw, XCircle } from 'lucide-react';
import type { Incident } from '@/types/incident';

interface Props {
  incident: Incident;
  onTransition: (status: string) => void;
  loading?: boolean;
}

export function IncidentStatusTransition({ incident, onTransition, loading }: Props) {
  const buttons: { label: string; status: string; icon: React.ReactNode; className: string }[] = [];

  switch (incident.status) {
    case 'OPEN':
      buttons.push({ label: 'Start Investigation', status: 'INVESTIGATING', icon: <Play className="h-3.5 w-3.5" />, className: 'bg-amber-600 hover:bg-amber-700 text-white' });
      buttons.push({ label: 'Close', status: 'CLOSED', icon: <XCircle className="h-3.5 w-3.5" />, className: 'bg-slate-600 hover:bg-slate-700 text-white' });
      break;
    case 'INVESTIGATING':
      buttons.push({ label: 'Mark Resolved', status: 'RESOLVED', icon: <CheckCircle className="h-3.5 w-3.5" />, className: 'bg-emerald-600 hover:bg-emerald-700 text-white' });
      buttons.push({ label: 'Reopen', status: 'OPEN', icon: <RotateCcw className="h-3.5 w-3.5" />, className: 'bg-blue-600 hover:bg-blue-700 text-white' });
      break;
    case 'RESOLVED':
      buttons.push({ label: 'Close', status: 'CLOSED', icon: <XCircle className="h-3.5 w-3.5" />, className: 'bg-slate-600 hover:bg-slate-700 text-white' });
      buttons.push({ label: 'Reopen Investigation', status: 'INVESTIGATING', icon: <RotateCcw className="h-3.5 w-3.5" />, className: 'bg-amber-600 hover:bg-amber-700 text-white' });
      break;
  }

  if (buttons.length === 0) return null;

  return (
    <div className="flex items-center gap-2">
      {buttons.map((btn) => (
        <button key={btn.status} onClick={() => onTransition(btn.status)} disabled={loading}
          className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors disabled:opacity-50 ${btn.className}`}>
          {btn.icon}
          {btn.label}
        </button>
      ))}
    </div>
  );
}
