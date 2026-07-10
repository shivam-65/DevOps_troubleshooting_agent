import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { IncidentForm } from '@/components/incidents/IncidentForm';

describe('IncidentForm', () => {
  it('renders form fields', () => {
    render(<IncidentForm onSubmit={vi.fn()} onCancel={vi.fn()} />);
    expect(screen.getByPlaceholderText('Brief incident title')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Detailed description of the incident')).toBeInTheDocument();
  });

  it('disables submit when title is empty', () => {
    render(<IncidentForm onSubmit={vi.fn()} onCancel={vi.fn()} />);
    expect(screen.getByText('Create Incident')).toBeDisabled();
  });

  it('calls onCancel when cancel clicked', () => {
    const onCancel = vi.fn();
    render(<IncidentForm onSubmit={vi.fn()} onCancel={onCancel} />);
    fireEvent.click(screen.getByText('Cancel'));
    expect(onCancel).toHaveBeenCalledOnce();
  });

  it('shows Creating... when loading', () => {
    render(<IncidentForm onSubmit={vi.fn()} onCancel={vi.fn()} loading={true} />);
    expect(screen.getByText('Creating...')).toBeInTheDocument();
  });
});
