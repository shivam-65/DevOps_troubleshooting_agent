import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { usePagination } from '@/hooks/usePagination';

describe('usePagination', () => {
  it('initializes with default values', () => {
    const { result } = renderHook(() => usePagination());
    expect(result.current.pagination.page).toBe(0);
    expect(result.current.pagination.size).toBe(20);
    expect(result.current.pagination.totalElements).toBe(0);
    expect(result.current.pagination.totalPages).toBe(0);
  });

  it('initializes with custom size', () => {
    const { result } = renderHook(() => usePagination(10));
    expect(result.current.pagination.size).toBe(10);
  });

  it('sets page correctly', () => {
    const { result } = renderHook(() => usePagination());
    act(() => { result.current.setPage(3); });
    expect(result.current.pagination.page).toBe(3);
  });

  it('resets page to 0 when size changes', () => {
    const { result } = renderHook(() => usePagination());
    act(() => { result.current.setPage(5); });
    act(() => { result.current.setSize(50); });
    expect(result.current.pagination.page).toBe(0);
    expect(result.current.pagination.size).toBe(50);
  });

  it('updates from response', () => {
    const { result } = renderHook(() => usePagination());
    act(() => {
      result.current.updateFromResponse({ page: 2, size: 20, totalElements: 100, totalPages: 5 });
    });
    expect(result.current.pagination.page).toBe(2);
    expect(result.current.pagination.totalElements).toBe(100);
    expect(result.current.pagination.totalPages).toBe(5);
  });
});
