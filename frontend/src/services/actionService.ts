import api from './api';
import type { Action, CreateActionRequest } from '@/types/action';
import type { PagedResponse } from '@/types/common';

export const actionService = {
  getAll: async (params: Record<string, any> = {}): Promise<PagedResponse<Action>> => {
    const { data } = await api.get('/actions', { params });
    return data;
  },
  getById: async (id: string): Promise<Action> => {
    const { data } = await api.get(`/actions/${id}`);
    return data;
  },
  create: async (req: CreateActionRequest): Promise<Action> => {
    const { data } = await api.post('/actions', req);
    return data;
  },
  approve: async (id: string, approvedBy: string): Promise<Action> => {
    const { data } = await api.post(`/actions/${id}/approve`, { approvedBy });
    return data;
  },
  reject: async (id: string, reason?: string): Promise<Action> => {
    const { data } = await api.post(`/actions/${id}/reject`, { reason });
    return data;
  },
  execute: async (id: string): Promise<Action> => {
    const { data } = await api.post(`/actions/${id}/execute`);
    return data;
  },
};
