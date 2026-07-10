import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorState } from '@/components/shared/ErrorState';

describe('ErrorState', () => {
  it('displays error message', () => {
    render(<ErrorState error="Network error" />);
    expect(screen.getByText('Network error')).toBeInTheDocument();
  });

  it('displays heading', () => {
    render(<ErrorState error="error" />);
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('calls onRetry when button clicked', () => {
    const onRetry = vi.fn();
    render(<ErrorState error="error" onRetry={onRetry} />);
    fireEvent.click(screen.getByText('Try Again'));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it('does not render retry button when onRetry is not provided', () => {
    render(<ErrorState error="error" />);
    expect(screen.queryByText('Try Again')).toBeNull();
  });
});
