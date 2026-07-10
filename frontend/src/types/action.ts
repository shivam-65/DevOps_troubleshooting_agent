export type ActionStatus = 'PROPOSED' | 'APPROVED' | 'EXECUTING' | 'COMPLETED' | 'FAILED' | 'REJECTED';
export type ActionType = 'RESTART_SERVICE' | 'SCALE_UP' | 'ROLLBACK_DEPLOYMENT' | 'RUN_SCRIPT' | 'APPLY_CONFIG_CHANGE' | 'CLEAR_CACHE' | 'FAILOVER' | 'CUSTOM';

export interface Action {
  id: string;
  investigationId: string;
  incidentId: string;
  type: ActionType;
  status: ActionStatus;
  title: string;
  description: string | null;
  command: string | null;
  targetService: string | null;
  parameters: Record<string, any> | null;
  risk: string | null;
  estimatedImpact: string | null;
  executionResult: any | null;
  approvedBy: string | null;
  approvedAt: string | null;
  executedAt: string | null;
  completedAt: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface CreateActionRequest {
  investigationId: string;
  incidentId: string;
  type: ActionType;
  title: string;
  description?: string;
  command?: string;
  targetService?: string;
  parameters?: Record<string, any>;
  risk?: string;
  estimatedImpact?: string;
}

export interface ActionFilters {
  status?: ActionStatus | '';
  type?: ActionType | '';
  incidentId?: string;
  search?: string;
}
