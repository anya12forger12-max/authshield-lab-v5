import { useCallback, useRef, useEffect, type RefObject } from 'react';

interface UseKeyboardNavOptions {
  orientation?: 'horizontal' | 'vertical' | 'both';
  loop?: boolean;
  typeAhead?: boolean;
}

interface UseKeyboardNavReturn {
  handleKeyDown: (e: React.KeyboardEvent) => void;
  focusItem: (index: number) => void;
  focusedIndex: number;
}

export function useKeyboardNav(
  containerRef: RefObject<HTMLElement>,
  _itemCount: number,
  options: UseKeyboardNavOptions = {}
): UseKeyboardNavReturn {
  const { orientation = 'vertical', loop = true, typeAhead = true } = options;
  const focusedIndexRef = useRef(0);
  const typeAheadBufferRef = useRef('');
  const typeAheadTimeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const getFocusableItems = useCallback((): HTMLElement[] => {
    if (!containerRef.current) return [];
    return Array.from(
      containerRef.current.querySelectorAll('[data-keyboard-item]')
    ) as HTMLElement[];
  }, [containerRef]);

  const focusItem = useCallback(
    (index: number) => {
      const items = getFocusableItems();
      if (items.length === 0) return;

      const clampedIndex = loop
        ? ((index % items.length) + items.length) % items.length
        : Math.max(0, Math.min(index, items.length - 1));

      focusedIndexRef.current = clampedIndex;
      items[clampedIndex]?.focus();
    },
    [getFocusableItems, loop]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      const items = getFocusableItems();
      if (items.length === 0) return;

      const currentFocus = items.findIndex(
        (item) => item === document.activeElement || item.contains(document.activeElement)
      );
      const currentIndex = currentFocus >= 0 ? currentFocus : focusedIndexRef.current;

      let nextIndex: number | null = null;

      switch (e.key) {
        case 'ArrowDown':
          if (orientation === 'vertical' || orientation === 'both') {
            e.preventDefault();
            nextIndex = currentIndex + 1;
          }
          break;

        case 'ArrowUp':
          if (orientation === 'vertical' || orientation === 'both') {
            e.preventDefault();
            nextIndex = currentIndex - 1;
          }
          break;

        case 'ArrowRight':
          if (orientation === 'horizontal' || orientation === 'both') {
            e.preventDefault();
            nextIndex = currentIndex + 1;
          }
          break;

        case 'ArrowLeft':
          if (orientation === 'horizontal' || orientation === 'both') {
            e.preventDefault();
            nextIndex = currentIndex - 1;
          }
          break;

        case 'Home':
          e.preventDefault();
          nextIndex = 0;
          break;

        case 'End':
          e.preventDefault();
          nextIndex = items.length - 1;
          break;

        case 'Enter':
        case ' ':
          e.preventDefault();
          items[currentIndex]?.click();
          break;

        default:
          if (typeAhead && e.key.length === 1 && !e.ctrlKey && !e.altKey && !e.metaKey) {
            if (typeAheadTimeoutRef.current) clearTimeout(typeAheadTimeoutRef.current);
            typeAheadBufferRef.current += e.key.toLowerCase();

            const matchIndex = items.findIndex((item) => {
              const text = item.textContent?.toLowerCase().trim() ?? '';
              return text.startsWith(typeAheadBufferRef.current);
            });

            if (matchIndex >= 0) {
              e.preventDefault();
              nextIndex = matchIndex;
            }

            typeAheadTimeoutRef.current = setTimeout(() => {
              typeAheadBufferRef.current = '';
            }, 500);
          }
          break;
      }

      if (nextIndex !== null) {
        focusItem(nextIndex);
      }
    },
    [getFocusableItems, focusItem, orientation, typeAhead]
  );

  useEffect(() => {
    return () => {
      if (typeAheadTimeoutRef.current) clearTimeout(typeAheadTimeoutRef.current);
    };
  }, []);

  return {
    handleKeyDown,
    focusItem,
    focusedIndex: focusedIndexRef.current,
  };
}
