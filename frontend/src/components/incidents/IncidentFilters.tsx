import { Search, ArrowUpDown } from 'lucide-react';
import type { IncidentFilters as IFilters } from '@/types/incident';

interface Props {
  filters: IFilters;
  onFilterChange: (filters: IFilters) => void;
}

export function IncidentFilters({ filters, onFilterChange }: Props) {
  return (
    <div className="flex flex-wrap gap-3 items-center">
      <div className="relative flex-1 min-w-[200px]">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <input value={filters.search || ''} onChange={(e) => onFilterChange({ ...filters, search: e.target.value })}
          className="w-full bg-muted border border-border rounded-md pl-9 pr-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          placeholder="Search incidents..." />
      </div>
      <select value={filters.status || ''} onChange={(e) => onFilterChange({ ...filters, status: e.target.value as any })}
        className="bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary">
        <option value="">All Status</option>
        <option value="OPEN">Open</option>
        <option value="INVESTIGATING">Investigating</option>
        <option value="RESOLVED">Resolved</option>
        <option value="CLOSED">Closed</option>
      </select>
      <select value={filters.severity || ''} onChange={(e) => onFilterChange({ ...filters, severity: e.target.value as any })}
        className="bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary">
        <option value="">All Severity</option>
        <option value="CRITICAL">Critical</option>
        <option value="HIGH">High</option>
        <option value="MEDIUM">Medium</option>
        <option value="LOW">Low</option>
      </select>
      <select value={filters.sortBy} onChange={(e) => onFilterChange({ ...filters, sortBy: e.target.value })}
        className="bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary">
        <option value="createdAt">Created Date</option>
        <option value="updatedAt">Updated Date</option>
        <option value="severity">Severity</option>
      </select>
      <button onClick={() => onFilterChange({ ...filters, sortDir: filters.sortDir === 'asc' ? 'desc' : 'asc' })}
        className="p-2 rounded-md bg-muted border border-border hover:bg-secondary transition-colors" title="Toggle sort direction">
        <ArrowUpDown className="h-4 w-4 text-muted-foreground" />
      </button>
    </div>
  );
}
