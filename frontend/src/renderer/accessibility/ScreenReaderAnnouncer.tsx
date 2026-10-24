import type React from 'react';
import { createContext, useContext, useState, useCallback, useRef, useEffect } from 'react';

interface ScreenReaderContextValue {
  announce: (message: string, priority?: 'polite' | 'assertive') => void;
}

const ScreenReaderContext = createContext<ScreenReaderContextValue | null>(null);

export function useScreenReader(): ScreenReaderContextValue {
  const context = useContext(ScreenReaderContext);
  if (!context) {
    throw new Error('useScreenReader must be used within ScreenReaderAnnouncer');
  }
  return context;
}

interface Announcement {
  id: number;
  message: string;
  priority: 'polite' | 'assertive';
}

let nextId = 0;

export function ScreenReaderAnnouncer({ children }: { children: React.ReactNode }) {
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const timeoutRefs = useRef<Map<number, ReturnType<typeof setTimeout>>>(new Map());

  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const id = nextId++;
    const announcement: Announcement = { id, message, priority };

    setAnnouncements((prev) => {
      if (priority === 'assertive') {
        return [announcement];
      }
      return [...prev, announcement];
    });

    const timeout = setTimeout(() => {
      setAnnouncements((prev) => prev.filter((a) => a.id !== id));
      timeoutRefs.current.delete(id);
    }, 2000);

    timeoutRefs.current.set(id, timeout);
  }, []);

  useEffect(() => {
    return () => {
      timeoutRefs.current.forEach((timeout) => clearTimeout(timeout));
      timeoutRefs.current.clear();
    };
  }, []);

  const value: ScreenReaderContextValue = { announce };

  const politeMessages = announcements.filter((a) => a.priority === 'polite');
  const assertiveMessages = announcements.filter((a) => a.priority === 'assertive');

  return (
    <ScreenReaderContext.Provider value={value}>
      {children}
      <div className="sr-only">
        <div role="log" aria-live="polite" aria-atomic="true" data-testid="sr-polite">
          {politeMessages.map((a) => (
            <span key={a.id}>{a.message}</span>
          ))}
        </div>
        <div role="log" aria-live="assertive" aria-atomic="true" data-testid="sr-assertive">
          {assertiveMessages.map((a) => (
            <span key={a.id}>{a.message}</span>
          ))}
        </div>
      </div>
    </ScreenReaderContext.Provider>
  );
}
