import api from './api';
import type { Report, GenerateReportRequest } from '@/types/report';
import type { PagedResponse } from '@/types/common';

export const reportService = {
  getAll: async (params: Record<string, any> = {}): Promise<PagedResponse<Report>> => {
    const { data } = await api.get('/reports', { params });
    return data;
  },
  getById: async (id: string): Promise<Report> => {
    const { data } = await api.get(`/reports/${id}`);
    return data;
  },
  generate: async (req: GenerateReportRequest): Promise<Report> => {
    const { data } = await api.post('/reports', req);
    return data;
  },
  exportReport: async (id: string, format: string): Promise<Blob> => {
    const { data } = await api.get(`/reports/${id}/export`, {
      params: { format },
      responseType: 'blob',
    });
    return data;
  },
};
