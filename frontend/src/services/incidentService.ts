import api from './api';
import type { Incident, CreateIncidentRequest, UpdateIncidentRequest } from '@/types/incident';
import type { PagedResponse } from '@/types/common';

export const incidentService = {
  getAll: async (params: Record<string, any> = {}): Promise<PagedResponse<Incident>> => {
    const { data } = await api.get('/incidents', { params });
    return data;
  },
  getById: async (id: string): Promise<Incident> => {
    const { data } = await api.get(`/incidents/${id}`);
    return data;
  },
  create: async (req: CreateIncidentRequest): Promise<Incident> => {
    const { data } = await api.post('/incidents', req);
    return data;
  },
  update: async (id: string, req: UpdateIncidentRequest): Promise<Incident> => {
    const { data } = await api.put(`/incidents/${id}`, req);
    return data;
  },
  delete: async (id: string): Promise<void> => {
    await api.delete(`/incidents/${id}`);
  },
};
