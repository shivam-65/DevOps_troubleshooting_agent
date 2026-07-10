import axios from 'axios';
import { config } from '@/config';

export interface Scenario {
  id: string;
  name: string;
  description: string;
  status: string;
  targetServices: string[];
  parameters: Record<string, any>;
}

export interface ScenarioActivationRequest {
  targetServices: string[];
  parameters?: Record<string, any>;
}

export interface ScenarioActivationResponse {
  id: string;
  status: string;
  targetServices: string[];
  activatedAt: string;
  message: string;
}

const simulatorApi = axios.create({
  baseURL: config.simulatorUrl,
  headers: { 'Content-Type': 'application/json' },
});

export const scenarioService = {
  async getAll(): Promise<Scenario[]> {
    const response = await simulatorApi.get('/api/scenarios');
    return response.data.scenarios;
  },

  async getById(scenarioId: string): Promise<Scenario> {
    const response = await simulatorApi.get(`/api/scenarios/${scenarioId}`);
    return response.data;
  },

  async activate(scenarioId: string, request: ScenarioActivationRequest): Promise<ScenarioActivationResponse> {
    const response = await simulatorApi.post(`/api/scenarios/${scenarioId}/activate`, request);
    return response.data;
  },

  async deactivate(scenarioId: string): Promise<any> {
    const response = await simulatorApi.post(`/api/scenarios/${scenarioId}/deactivate`);
    return response.data;
  },
};
