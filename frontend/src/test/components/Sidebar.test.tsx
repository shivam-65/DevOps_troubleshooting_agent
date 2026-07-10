import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Sidebar } from '@/components/layout/Sidebar';

describe('Sidebar', () => {
  it('renders navigation items when expanded', () => {
    render(
      <MemoryRouter>
        <Sidebar collapsed={false} onToggle={vi.fn()} />
      </MemoryRouter>
    );
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Incidents')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();
    expect(screen.getByText('Reports')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('hides labels when collapsed', () => {
    render(
      <MemoryRouter>
        <Sidebar collapsed={true} onToggle={vi.fn()} />
      </MemoryRouter>
    );
    expect(screen.queryByText('Dashboard')).toBeNull();
    expect(screen.queryByText('Incidents')).toBeNull();
  });

  it('shows app title when expanded', () => {
    render(
      <MemoryRouter>
        <Sidebar collapsed={false} onToggle={vi.fn()} />
      </MemoryRouter>
    );
    expect(screen.getByText('Incident Commander')).toBeInTheDocument();
  });

  it('calls onToggle when toggle button clicked', () => {
    const onToggle = vi.fn();
    render(
      <MemoryRouter>
        <Sidebar collapsed={false} onToggle={onToggle} />
      </MemoryRouter>
    );
    // The toggle button is the last button in the sidebar
    const buttons = screen.getAllByRole('button');
    fireEvent.click(buttons[buttons.length - 1]);
    expect(onToggle).toHaveBeenCalledOnce();
  });
});
