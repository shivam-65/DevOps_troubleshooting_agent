import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { EmptyState } from '@/components/shared/EmptyState';

describe('EmptyState', () => {
  it('renders title', () => {
    render(<EmptyState title="Nothing here" />);
    expect(screen.getByText('Nothing here')).toBeInTheDocument();
  });

  it('renders description', () => {
    render(<EmptyState title="Empty" description="No data available" />);
    expect(screen.getByText('No data available')).toBeInTheDocument();
  });

  it('renders action button', () => {
    render(<EmptyState title="Empty" action={<button>Create</button>} />);
    expect(screen.getByText('Create')).toBeInTheDocument();
  });
});
