import { useState, useEffect } from 'react';
import type { CreateIncidentRequest, IncidentSeverity } from '@/types/incident';
import { scenarioService, type Scenario } from '@/services/scenarioService';

interface Props {
  onSubmit: (data: CreateIncidentRequest) => void;
  onCancel: () => void;
  loading?: boolean;
}

const severities: IncidentSeverity[] = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

export function IncidentForm({ onSubmit, onCancel, loading }: Props) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [severity, setSeverity] = useState<IncidentSeverity>('MEDIUM');
  const [services, setServices] = useState('');
  const [assignee, setAssignee] = useState('');
  const [tags, setTags] = useState('');
  
  // Scenario selection
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<string>('');
  const [loadingScenarios, setLoadingScenarios] = useState(false);
  const [activateScenario, setActivateScenario] = useState(false);

  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        setLoadingScenarios(true);
        const data = await scenarioService.getAll();
        setScenarios(data);
      } catch (error) {
        console.error('Failed to fetch scenarios:', error);
      } finally {
        setLoadingScenarios(false);
      }
    };
    fetchScenarios();
  }, []);

  const handleScenarioChange = (scenarioId: string) => {
    setSelectedScenario(scenarioId);
    const scenario = scenarios.find(s => s.id === scenarioId);
    
    if (scenario) {
      // Pre-populate form fields based on scenario
      setTitle(scenario.name);
      setDescription(scenario.description);
      setServices(scenario.targetServices.join(', '));
      // Set severity based on scenario type
      if (scenario.id.includes('crash') || scenario.id.includes('oom')) {
        setSeverity('CRITICAL');
      } else if (scenario.id.includes('error')) {
        setSeverity('HIGH');
      } else {
        setSeverity('MEDIUM');
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('[IncidentForm] Submitting:', { title, description, severity, selectedScenario });
    
    // Activate scenario if selected and checkbox is checked
    if (selectedScenario && activateScenario) {
      const targetServices = services ? services.split(',').map((s) => s.trim()).filter(Boolean) : [];
      
      if (targetServices.length === 0) {
        alert('Please specify at least one affected service to activate the scenario.');
        return;
      }
      
      try {
        await scenarioService.activate(selectedScenario, { targetServices });
        console.log('[IncidentForm] Scenario activated:', selectedScenario, 'for services:', targetServices);
      } catch (error) {
        console.error('[IncidentForm] Failed to activate scenario:', error);
        alert('Failed to activate scenario. Please check if the simulator is running.');
        return;
      }
    }
    
    const data = {
      title,
      description,
      severity,
      affectedServices: services ? services.split(',').map((s) => s.trim()).filter(Boolean) : [],
      assignee: assignee || undefined,
      tags: tags ? tags.split(',').map((t) => t.trim()).filter(Boolean) : [],
    };
    console.log('[IncidentForm] Form data:', data);
    onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Scenario Selection */}
      <div>
        <label className="block text-sm font-medium text-foreground mb-1">Select Scenario (Optional)</label>
        <select 
          value={selectedScenario} 
          onChange={(e) => handleScenarioChange(e.target.value)}
          disabled={loadingScenarios}
          className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <option value="">-- Select a predefined scenario --</option>
          {loadingScenarios ? (
            <option value="" disabled>Loading scenarios...</option>
          ) : (
            scenarios.map((scenario) => (
              <option key={scenario.id} value={scenario.id}>
                {scenario.name} - {scenario.description}
              </option>
            ))
          )}
        </select>
        <p className="text-xs text-muted-foreground mt-1">
          Selecting a scenario will auto-populate incident details
        </p>
      </div>

      {selectedScenario && (
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="activateScenario"
            checked={activateScenario}
            onChange={(e) => setActivateScenario(e.target.checked)}
            className="h-4 w-4 rounded border-border text-primary focus:ring-primary"
          />
          <label htmlFor="activateScenario" className="text-sm text-foreground cursor-pointer">
            Activate this scenario in simulator
          </label>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-foreground mb-1">Title *</label>
        <input value={title} onChange={(e) => setTitle(e.target.value)} required
          className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          placeholder="Brief incident title" />
      </div>
      <div>
        <label className="block text-sm font-medium text-foreground mb-1">Description *</label>
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} required rows={3}
          className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary resize-none"
          placeholder="Detailed description of the incident" />
      </div>
      <div>
        <label className="block text-sm font-medium text-foreground mb-1">Severity *</label>
        <select value={severity} onChange={(e) => setSeverity(e.target.value as IncidentSeverity)}
          className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary">
          {severities.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium text-foreground mb-1">Affected Services</label>
        <input value={services} onChange={(e) => setServices(e.target.value)}
          className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          placeholder="Comma-separated: payment-api, checkout-service" />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-foreground mb-1">Assignee</label>
          <input value={assignee} onChange={(e) => setAssignee(e.target.value)}
            className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            placeholder="john.doe" />
        </div>
        <div>
          <label className="block text-sm font-medium text-foreground mb-1">Tags</label>
          <input value={tags} onChange={(e) => setTags(e.target.value)}
            className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            placeholder="Comma-separated tags" />
        </div>
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <button type="button" onClick={onCancel} disabled={loading}
          className="px-4 py-2 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-secondary disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          Cancel
        </button>
        <button 
          type="submit" 
          disabled={loading || !title || !description}
          onClick={() => console.log('[IncidentForm] Submit button clicked', { loading, title: !!title, description: !!description })}
          className="px-4 py-2 rounded-md text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          {loading ? 'Creating...' : 'Create Incident'}
        </button>
      </div>
    </form>
  );
}
