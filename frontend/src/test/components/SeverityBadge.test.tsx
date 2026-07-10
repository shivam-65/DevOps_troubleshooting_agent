import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SeverityBadge } from '@/components/shared/SeverityBadge';

describe('SeverityBadge', () => {
  it('renders CRITICAL severity', () => {
    render(<SeverityBadge severity="CRITICAL" />);
    expect(screen.getByText('CRITICAL')).toBeInTheDocument();
  });

  it('renders HIGH severity', () => {
    render(<SeverityBadge severity="HIGH" />);
    expect(screen.getByText('HIGH')).toBeInTheDocument();
  });

  it('renders MEDIUM severity', () => {
    render(<SeverityBadge severity="MEDIUM" />);
    expect(screen.getByText('MEDIUM')).toBeInTheDocument();
  });

  it('renders LOW severity', () => {
    render(<SeverityBadge severity="LOW" />);
    expect(screen.getByText('LOW')).toBeInTheDocument();
  });
});
