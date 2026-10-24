import type React from 'react';
import { useState, useCallback, useMemo } from 'react';
import { cn } from '../../utils/cn';
import type { SortConfig, SortDirection } from '../../types';

export interface DataTableColumn<T> {
  id: string;
  header: string;
  accessorKey?: keyof T;
  accessorFn?: (row: T) => React.ReactNode;
  sortable?: boolean;
  className?: string;
  width?: string;
}

export interface DataTableProps<T> {
  columns: DataTableColumn<T>[];
  data: T[];
  caption?: string;
  sortable?: boolean;
  selectable?: boolean;
  onSelectionChange?: (selectedRows: T[]) => void;
  keyExtractor: (row: T) => string;
  emptyMessage?: string;
  loading?: boolean;
  className?: string;
  pageSize?: number;
  onPageChange?: (page: number) => void;
}

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  caption,
  sortable = true,
  selectable = false,
  onSelectionChange,
  keyExtractor,
  emptyMessage = 'No data available',
  loading = false,
  className,
  pageSize = 10,
  onPageChange,
}: DataTableProps<T>) {
  const [sort, setSort] = useState<SortConfig | null>(null);
  const [selectedKeys, setSelectedKeys] = useState<Set<string>>(new Set());
  const [currentPage, setCurrentPage] = useState(0);

  const totalPages = Math.ceil(data.length / pageSize);

  const handleSort = useCallback(
    (columnId: string) => {
      if (!sortable) return;
      setSort((prev) => {
        if (prev?.column === columnId) {
          const next: SortDirection = prev.direction === 'asc' ? 'desc' : 'asc';
          return { column: columnId, direction: next };
        }
        return { column: columnId, direction: 'asc' };
      });
    },
    [sortable]
  );

  const sortedData = useMemo(() => {
    if (!sort) return data;
    const column = columns.find((c) => c.id === sort.column);
    if (!column) return data;

    return [...data].sort((a, b) => {
      let aVal: unknown;
      let bVal: unknown;

      if (column.accessorFn) {
        aVal = column.accessorFn(a);
        bVal = column.accessorFn(b);
      } else if (column.accessorKey) {
        aVal = a[column.accessorKey];
        bVal = b[column.accessorKey];
      }

      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return 1;
      if (bVal == null) return -1;

      const comparison = String(aVal).localeCompare(String(bVal));
      return sort.direction === 'asc' ? comparison : -comparison;
    });
  }, [data, sort, columns]);

  const paginatedData = useMemo(() => {
    const start = currentPage * pageSize;
    return sortedData.slice(start, start + pageSize);
  }, [sortedData, currentPage, pageSize]);

  const handlePageChange = useCallback(
    (page: number) => {
      setCurrentPage(page);
      onPageChange?.(page);
    },
    [onPageChange]
  );

  const toggleAll = useCallback(() => {
    if (selectedKeys.size === paginatedData.length) {
      setSelectedKeys(new Set());
      onSelectionChange?.([]);
    } else {
      const newKeys = new Set(paginatedData.map(keyExtractor));
      setSelectedKeys(newKeys);
      onSelectionChange?.(paginatedData);
    }
  }, [paginatedData, selectedKeys.size, keyExtractor, onSelectionChange]);

  const toggleRow = useCallback(
    (row: T) => {
      const key = keyExtractor(row);
      setSelectedKeys((prev) => {
        const next = new Set(prev);
        if (next.has(key)) {
          next.delete(key);
        } else {
          next.add(key);
        }
        if (onSelectionChange) {
          const selected = paginatedData.filter((r) => next.has(keyExtractor(r)));
          onSelectionChange(selected);
        }
        return next;
      });
    },
    [paginatedData, keyExtractor, onSelectionChange]
  );

  const getSortIndicator = (columnId: string): string => {
    if (sort?.column !== columnId) return '';
    return sort.direction === 'asc' ? ' \u2191' : ' \u2193';
  };

  return (
    <div className={cn('w-full overflow-x-auto', className)}>
      <table
        className="w-full border-collapse text-[var(--font-size-sm)]"
        aria-label={caption || 'Data table'}
      >
        {caption && (
          <caption className="sr-only">{caption}</caption>
        )}
        <thead>
          <tr className="border-b border-[var(--color-border)]">
            {selectable && (
              <th className="w-10 px-3 py-2">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-focus-ring)]"
                  checked={selectedKeys.size === paginatedData.length && paginatedData.length > 0}
                  onChange={toggleAll}
                  aria-label="Select all rows"
                />
              </th>
            )}
            {columns.map((col) => (
              <th
                key={col.id}
                className={cn(
                  'px-3 py-2 text-left font-semibold text-[var(--color-text-secondary)] whitespace-nowrap',
                  col.sortable && sortable && 'cursor-pointer hover:text-[var(--color-text-primary)] select-none',
                  col.className
                )}
                style={col.width ? { width: col.width } : undefined}
                aria-sort={
                  sort?.column === col.id
                    ? sort.direction === 'asc'
                      ? 'ascending'
                      : 'descending'
                    : col.sortable
                    ? 'none'
                    : undefined
                }
                onClick={() => col.sortable && handleSort(col.id)}
                scope="col"
              >
                {col.header}
                {col.sortable && sortable && (
                  <span className="ml-1 inline-block" aria-hidden="true">
                    {getSortIndicator(col.id)}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {loading ? (
            <tr>
              <td
                colSpan={columns.length + (selectable ? 1 : 0)}
                className="px-3 py-8 text-center text-[var(--color-text-muted)]"
              >
                <div className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Loading...
                </div>
              </td>
            </tr>
          ) : paginatedData.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length + (selectable ? 1 : 0)}
                className="px-3 py-8 text-center text-[var(--color-text-muted)]"
              >
                {emptyMessage}
              </td>
            </tr>
          ) : (
            paginatedData.map((row) => {
              const key = keyExtractor(row);
              const isSelected = selectedKeys.has(key);
              return (
                <tr
                  key={key}
                  className={cn(
                    'border-b border-[var(--color-border-subtle)] hover:bg-[var(--color-surface-sunken)] transition-colors',
                    isSelected && 'bg-[var(--color-primary-subtle)]'
                  )}
                >
                  {selectable && (
                    <td className="w-10 px-3 py-2">
                      <input
                        type="checkbox"
                        className="h-4 w-4 rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-focus-ring)]"
                        checked={isSelected}
                        onChange={() => toggleRow(row)}
                        aria-label={`Select row ${key}`}
                      />
                    </td>
                  )}
                  {columns.map((col) => (
                    <td key={col.id} className={cn('px-3 py-2 text-[var(--color-text-primary)]', col.className)}>
                      {col.accessorFn
                        ? col.accessorFn(row)
                        : col.accessorKey
                        ? String(row[col.accessorKey] ?? '')
                        : null}
                    </td>
                  ))}
                </tr>
              );
            })
          )}
        </tbody>
      </table>

      {totalPages > 1 && (
        <nav className="flex items-center justify-between px-3 py-2 border-t border-[var(--color-border)]" aria-label="Pagination">
          <span className="text-[var(--font-size-sm)] text-[var(--color-text-muted)]">
            Showing {currentPage * pageSize + 1} to{' '}
            {Math.min((currentPage + 1) * pageSize, data.length)} of {data.length}
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 0}
              className="px-2 py-1 text-sm rounded border border-[var(--color-border)] hover:bg-[var(--color-surface-sunken)] disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-focus-ring)]"
              aria-label="Previous page"
            >
              Previous
            </button>
            {Array.from({ length: totalPages }, (_, i) => (
              <button
                key={i}
                onClick={() => handlePageChange(i)}
                className={cn(
                  'px-2 py-1 text-sm rounded border focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-focus-ring)]',
                  i === currentPage
                    ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary)]'
                    : 'border-[var(--color-border)] hover:bg-[var(--color-surface-sunken)]'
                )}
                aria-label={`Page ${i + 1}`}
                aria-current={i === currentPage ? 'page' : undefined}
              >
                {i + 1}
              </button>
            ))}
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage >= totalPages - 1}
              className="px-2 py-1 text-sm rounded border border-[var(--color-border)] hover:bg-[var(--color-surface-sunken)] disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-focus-ring)]"
              aria-label="Next page"
            >
              Next
            </button>
          </div>
        </nav>
      )}
    </div>
  );
}
