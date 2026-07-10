import { useState, useCallback } from 'react';
import type { PaginationState } from '@/types/common';

export function usePagination(initialSize = 20) {
  const [pagination, setPagination] = useState<PaginationState>({
    page: 0,
    size: initialSize,
    totalElements: 0,
    totalPages: 0,
  });

  const setPage = useCallback((page: number) => {
    setPagination((prev) => ({ ...prev, page }));
  }, []);

  const setSize = useCallback((size: number) => {
    setPagination((prev) => ({ ...prev, size, page: 0 }));
  }, []);

  const updateFromResponse = useCallback((response: { page: number; size: number; totalElements: number; totalPages: number }) => {
    setPagination({
      page: response.page,
      size: response.size,
      totalElements: response.totalElements,
      totalPages: response.totalPages,
    });
  }, []);

  return { pagination, setPage, setSize, updateFromResponse };
}
