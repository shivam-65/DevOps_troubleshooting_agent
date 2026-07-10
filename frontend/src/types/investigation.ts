import type { Action } from './action';
import type { Evidence } from './evidence';

export type InvestigationStatus = 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';

export interface Investigation {
  id: string;
  incidentId: string;
  status: InvestigationStatus;
  summary: string | null;
  rootCause: string | null;
  confidence: number | null;
  aiModelUsed: string | null;
  evidence?: Evidence[];
  actions?: Action[];
  startedAt: string | null;
  completedAt: string | null;
  createdAt: string;
  updatedAt: string;
}
