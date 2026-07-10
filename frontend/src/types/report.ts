export type ReportFormat = 'JSON' | 'PDF';

export interface ReportMetadata {
  incidentDuration: string;
  severity: string;
  affectedServices: string[];
  rootCause: string;
  actionsExecuted: number;
  actionsProposed: number;
}

export interface Report {
  id: string;
  incidentId: string;
  title: string;
  content: string;
  format: ReportFormat;
  metadata: ReportMetadata | null;
  generatedAt: string;
  createdAt: string;
}

export interface GenerateReportRequest {
  incidentId: string;
  title: string;
  format: ReportFormat;
}
