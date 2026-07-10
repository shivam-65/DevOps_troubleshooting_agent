import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ConnectionStatus } from '@/components/shared/ConnectionStatus';

describe('ConnectionStatus', () => {
  it('shows Live when connected', () => {
    render(<ConnectionStatus connected={true} />);
    expect(screen.getByText('Live')).toBeInTheDocument();
  });

  it('shows Disconnected when not connected', () => {
    render(<ConnectionStatus connected={false} />);
    expect(screen.getByText('Disconnected')).toBeInTheDocument();
  });
});
