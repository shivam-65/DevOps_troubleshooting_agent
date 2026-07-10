export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '/api',
  wsUrl: import.meta.env.VITE_WS_URL || '/ws',
  simulatorUrl: import.meta.env.VITE_SIMULATOR_URL || 'http://localhost:8001',
  defaultPageSize: 20,
  maxPageSize: 100,
  wsReconnectMaxDelay: 30000,
};
