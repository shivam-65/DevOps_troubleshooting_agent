import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ConfidenceScore } from '@/components/shared/ConfidenceScore';

describe('ConfidenceScore', () => {
  it('renders N/A for null value', () => {
    render(<ConfidenceScore value={null} />);
    expect(screen.getByText('N/A')).toBeInTheDocument();
  });

  it('renders percentage for valid value', () => {
    render(<ConfidenceScore value={0.85} />);
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  it('renders 100% for value of 1', () => {
    render(<ConfidenceScore value={1} />);
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('renders 0% for value of 0', () => {
    render(<ConfidenceScore value={0} />);
    expect(screen.getByText('0%')).toBeInTheDocument();
  });
});
