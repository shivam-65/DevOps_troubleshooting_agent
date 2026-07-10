import { cn } from '@/lib/utils';

export function ConfidenceScore({ value, size = 48 }: { value: number | null; size?: number }) {
  if (value === null || value === undefined) return <span className="text-muted-foreground text-sm">N/A</span>;

  const percentage = Math.round(value * 100);
  const radius = (size - 6) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value * circumference);

  const color = value >= 0.8 ? 'text-emerald-400' : value >= 0.5 ? 'text-yellow-400' : 'text-red-400';
  const strokeColor = value >= 0.8 ? '#34d399' : value >= 0.5 ? '#facc15' : '#f87171';

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg className="transform -rotate-90" width={size} height={size}>
        <circle cx={size / 2} cy={size / 2} r={radius} stroke="#27272a" strokeWidth="4" fill="none" />
        <circle cx={size / 2} cy={size / 2} r={radius} stroke={strokeColor} strokeWidth="4" fill="none"
          strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round"
          className="transition-all duration-500" />
      </svg>
      <span className={cn('absolute text-xs font-bold', color)}>{percentage}%</span>
    </div>
  );
}
