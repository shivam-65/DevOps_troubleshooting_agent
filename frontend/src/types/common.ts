export interface PagedResponse<T> {
  content: T[];
  page: number;
  size: number;
  totalElements: number;
  totalPages: number;
}

export interface PaginationState {
  page: number;
  size: number;
  totalElements: number;
  totalPages: number;
}

export interface WebSocketEvent<T> {
  eventType: string;
  entityId: string;
  timestamp: string;
  data: T;
}

export interface TimelineEvent {
  id: string;
  type: string;
  title: string;
  description: string | null;
  timestamp: string;
  icon: string;
}

export interface AgentStep {
  name: string;
  status: 'waiting' | 'running' | 'done' | 'error';
  duration: number | null;
}
