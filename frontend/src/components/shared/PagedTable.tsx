import { ChevronLeft, ChevronRight } from 'lucide-react';
import type { PaginationState } from '@/types/common';

interface Column<T> {
  header: string;
  accessor: (row: T) => React.ReactNode;
  className?: string;
}

interface PagedTableProps<T> {
  columns: Column<T>[];
  data: T[];
  pagination: PaginationState;
  onPageChange: (page: number) => void;
  onSizeChange?: (size: number) => void;
  onRowClick?: (row: T) => void;
  keyExtractor: (row: T) => string;
}

export function PagedTable<T>({ columns, data, pagination, onPageChange, onSizeChange, onRowClick, keyExtractor }: PagedTableProps<T>) {
  return (
    <div>
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-muted/50">
              {columns.map((col, i) => (
                <th key={i} className={`px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider ${col.className || ''}`}>
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-12 text-center text-muted-foreground">
                  No data available
                </td>
              </tr>
            ) : (
              data.map((row) => (
                <tr key={keyExtractor(row)} onClick={() => onRowClick?.(row)}
                  className={`hover:bg-muted/30 transition-colors ${onRowClick ? 'cursor-pointer' : ''}`}>
                  {columns.map((col, j) => (
                    <td key={j} className={`px-4 py-3 ${col.className || ''}`}>
                      {col.accessor(row)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      {pagination.totalPages > 0 && (
        <div className="flex items-center justify-between mt-4 px-1">
          <div className="text-sm text-muted-foreground">
            {pagination.totalElements} total · Page {pagination.page + 1} of {pagination.totalPages}
          </div>
          <div className="flex items-center gap-2">
            {onSizeChange && (
              <select value={pagination.size} onChange={(e) => onSizeChange(Number(e.target.value))}
                className="bg-card border border-border rounded-md px-2 py-1 text-sm text-foreground">
                {[10, 20, 50].map((s) => (
                  <option key={s} value={s}>{s} / page</option>
                ))}
              </select>
            )}
            <button disabled={pagination.page === 0} onClick={() => onPageChange(pagination.page - 1)}
              className="p-1.5 rounded-md hover:bg-muted disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button disabled={pagination.page >= pagination.totalPages - 1} onClick={() => onPageChange(pagination.page + 1)}
              className="p-1.5 rounded-md hover:bg-muted disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
