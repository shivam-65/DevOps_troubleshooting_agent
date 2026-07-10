import api from './api';
import type { Investigation } from '@/types/investigation';
import type { Evidence } from '@/types/evidence';

export const investigationService = {
  getByIncident: async (incidentId: string): Promise<Investigation[]> => {
    const { data } = await api.get(`/incidents/${incidentId}/investigations`);
    return data;
  },
  getById: async (incidentId: string, invId: string): Promise<Investigation> => {
    const { data } = await api.get(`/incidents/${incidentId}/investigations/${invId}`);
    return data;
  },
  trigger: async (incidentId: string, options?: Record<string, any>): Promise<Investigation> => {
    const { data } = await api.post(`/incidents/${incidentId}/investigations`, options || {});
    return data;
  },
  getEvidence: async (incidentId: string, invId: string): Promise<Evidence[]> => {
    const { data } = await api.get(`/incidents/${incidentId}/investigations/${invId}/evidence`);
    return data;
  },
};
