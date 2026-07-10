import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ConfirmDialog } from '@/components/shared/ConfirmDialog';

describe('ConfirmDialog', () => {
  it('does not render when closed', () => {
    render(<ConfirmDialog open={false} title="Delete" description="Are you sure?" onConfirm={vi.fn()} onCancel={vi.fn()} />);
    expect(screen.queryByText('Delete')).toBeNull();
  });

  it('renders title and description when open', () => {
    render(<ConfirmDialog open={true} title="Delete" description="Are you sure?" onConfirm={vi.fn()} onCancel={vi.fn()} />);
    expect(screen.getByText('Delete')).toBeInTheDocument();
    expect(screen.getByText('Are you sure?')).toBeInTheDocument();
  });

  it('calls onConfirm when confirm button clicked', () => {
    const onConfirm = vi.fn();
    render(<ConfirmDialog open={true} title="Test" description="Desc" onConfirm={onConfirm} onCancel={vi.fn()} />);
    fireEvent.click(screen.getByText('Confirm'));
    expect(onConfirm).toHaveBeenCalledOnce();
  });

  it('calls onCancel when cancel button clicked', () => {
    const onCancel = vi.fn();
    render(<ConfirmDialog open={true} title="Test" description="Desc" onConfirm={vi.fn()} onCancel={onCancel} />);
    fireEvent.click(screen.getByText('Cancel'));
    expect(onCancel).toHaveBeenCalledOnce();
  });

  it('uses custom confirm label', () => {
    render(<ConfirmDialog open={true} title="Test" description="Desc" confirmLabel="Yes, Delete" onConfirm={vi.fn()} onCancel={vi.fn()} />);
    expect(screen.getByText('Yes, Delete')).toBeInTheDocument();
  });
});
