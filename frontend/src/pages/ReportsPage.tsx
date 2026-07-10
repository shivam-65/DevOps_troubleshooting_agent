import { useEffect, useState, useCallback } from 'react';
import { FileText, Download } from 'lucide-react';
import { reportService } from '@/services/reportService';
import type { Report } from '@/types/report';
import { usePagination } from '@/hooks/usePagination';
import { LoadingState } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { EmptyState } from '@/components/shared/EmptyState';
import { format } from 'date-fns';

export function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const { pagination, setPage, updateFromResponse } = usePagination();

  const fetchReports = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await reportService.getAll({ page: pagination.page, size: pagination.size });
      setReports(res.content);
      updateFromResponse(res);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.size, updateFromResponse]);

  useEffect(() => { fetchReports(); }, [fetchReports]);

  const handleExport = async (id: string, fmt: string) => {
    try {
      const blob = await reportService.exportReport(id, fmt);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report-${id}.${fmt.toLowerCase()}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch { /* ignore */ }
  };

  return (
    <div className="space-y-5">
      <h2 className="text-lg font-semibold text-foreground">Reports</h2>

      {loading ? <LoadingState /> : error ? <ErrorState error={error} onRetry={fetchReports} /> :
        reports.length === 0 ? (
          <EmptyState icon={<FileText className="h-10 w-10" />} title="No reports generated"
            description="Reports are generated from incident investigations. Navigate to an incident and click Generate Report." />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Reports List */}
            <div className="lg:col-span-1 space-y-2">
              {reports.map((report) => (
                <div key={report.id} onClick={() => setSelectedReport(report)}
                  className={`bg-card border rounded-lg p-4 cursor-pointer transition-colors ${selectedReport?.id === report.id ? 'border-primary' : 'border-border hover:border-primary/30'}`}>
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-primary/10 rounded-md flex-shrink-0">
                      <FileText className="h-4 w-4 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-foreground truncate">{report.title}</h4>
                      <p className="text-xs text-muted-foreground mt-0.5">{format(new Date(report.generatedAt), 'MMM d, yyyy HH:mm')}</p>
                    </div>
                  </div>
                </div>
              ))}
              {pagination.totalPages > 1 && (
                <div className="flex justify-center gap-2 pt-2">
                  <button disabled={pagination.page === 0} onClick={() => setPage(pagination.page - 1)}
                    className="px-2 py-1 text-xs rounded-md bg-muted hover:bg-secondary disabled:opacity-30 transition-colors">Prev</button>
                  <span className="text-xs text-muted-foreground self-center">{pagination.page + 1}/{pagination.totalPages}</span>
                  <button disabled={pagination.page >= pagination.totalPages - 1} onClick={() => setPage(pagination.page + 1)}
                    className="px-2 py-1 text-xs rounded-md bg-muted hover:bg-secondary disabled:opacity-30 transition-colors">Next</button>
                </div>
              )}
            </div>

            {/* Report Detail */}
            <div className="lg:col-span-2">
              {selectedReport ? (
                <div className="bg-card border border-border rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-base font-medium text-foreground">{selectedReport.title}</h3>
                    <div className="flex gap-2">
                      <button onClick={() => handleExport(selectedReport.id, 'JSON')}
                        className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-medium bg-muted hover:bg-secondary text-foreground transition-colors">
                        <Download className="h-3 w-3" /> JSON
                      </button>
                      <button onClick={() => handleExport(selectedReport.id, 'PDF')}
                        className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-medium bg-muted hover:bg-secondary text-foreground transition-colors">
                        <Download className="h-3 w-3" /> PDF
                      </button>
                    </div>
                  </div>
                  {selectedReport.metadata && (
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
                      {Object.entries(selectedReport.metadata).map(([key, val]) => (
                        <div key={key} className="bg-muted rounded-md p-3">
                          <span className="text-xs text-muted-foreground uppercase">{key.replace(/([A-Z])/g, ' $1')}</span>
                          <p className="text-sm text-foreground mt-0.5">{Array.isArray(val) ? val.join(', ') : String(val)}</p>
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="prose prose-invert max-w-none">
                    <pre className="bg-muted rounded-lg p-4 text-xs text-foreground overflow-x-auto whitespace-pre-wrap font-mono">{selectedReport.content}</pre>
                  </div>
                </div>
              ) : (
                <div className="bg-card border border-border rounded-lg p-12 text-center">
                  <FileText className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">Select a report to view its content</p>
                </div>
              )}
            </div>
          </div>
        )}
    </div>
  );
}
