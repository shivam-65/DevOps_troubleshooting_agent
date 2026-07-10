import { useState } from 'react';
import { useWebSocket } from '@/contexts/WebSocketContext';
import { ConnectionStatus } from '@/components/shared/ConnectionStatus';

export function SettingsPage() {
  const { connected } = useWebSocket();
  const [apiUrl, setApiUrl] = useState(import.meta.env.VITE_API_BASE_URL || '/api');
  const [wsUrl, setWsUrl] = useState(import.meta.env.VITE_WS_URL || '/ws');

  return (
    <div className="max-w-2xl space-y-6">
      <h2 className="text-lg font-semibold text-foreground">Settings</h2>

      {/* Connection Status */}
      <div className="bg-card border border-border rounded-lg p-5">
        <h3 className="text-sm font-medium text-foreground mb-3">Connection Status</h3>
        <div className="flex items-center gap-4">
          <ConnectionStatus connected={connected} />
          <span className="text-xs text-muted-foreground">WebSocket connection to the backend server</span>
        </div>
      </div>

      {/* API Configuration */}
      <div className="bg-card border border-border rounded-lg p-5">
        <h3 className="text-sm font-medium text-foreground mb-4">API Configuration</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-muted-foreground mb-1">API Base URL</label>
            <input value={apiUrl} onChange={(e) => setApiUrl(e.target.value)} readOnly
              className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground/70 cursor-not-allowed" />
            <p className="text-xs text-muted-foreground mt-1">Set via VITE_API_BASE_URL environment variable</p>
          </div>
          <div>
            <label className="block text-sm text-muted-foreground mb-1">WebSocket URL</label>
            <input value={wsUrl} onChange={(e) => setWsUrl(e.target.value)} readOnly
              className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground/70 cursor-not-allowed" />
            <p className="text-xs text-muted-foreground mt-1">Set via VITE_WS_URL environment variable</p>
          </div>
        </div>
      </div>

      {/* About */}
      <div className="bg-card border border-border rounded-lg p-5">
        <h3 className="text-sm font-medium text-foreground mb-2">About</h3>
        <p className="text-sm text-muted-foreground">
          AI-Powered DevOps Incident Commander is an intelligent incident management system that leverages AI to automatically
          investigate production incidents, identify root causes, and recommend remediation actions.
        </p>
        <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
          <div className="bg-muted rounded-md p-2">
            <span className="text-muted-foreground">Backend:</span>{' '}
            <span className="text-foreground">Spring Boot 3.3</span>
          </div>
          <div className="bg-muted rounded-md p-2">
            <span className="text-muted-foreground">AI Service:</span>{' '}
            <span className="text-foreground">FastAPI + Gemini</span>
          </div>
          <div className="bg-muted rounded-md p-2">
            <span className="text-muted-foreground">Frontend:</span>{' '}
            <span className="text-foreground">React 18 + TypeScript</span>
          </div>
          <div className="bg-muted rounded-md p-2">
            <span className="text-muted-foreground">Simulator:</span>{' '}
            <span className="text-foreground">FastAPI</span>
          </div>
        </div>
      </div>
    </div>
  );
}
