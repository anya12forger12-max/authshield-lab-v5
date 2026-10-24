import type React from 'react';
import { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react';
import { useAppStore } from '../store/appStore';
import { getTheme, applyTheme } from '../themes/theme-engine';
import type { AccessibilityPreferences } from '../types';

interface AnnounceFunction {
  (message: string, priority?: 'polite' | 'assertive'): void;
}

interface AppContextValue {
  announce: AnnounceFunction;
  accessibility: AccessibilityPreferences;
}

const AppContext = createContext<AppContextValue | null>(null);

export function useAppContext(): AppContextValue {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
}

export function AppProvider({ children }: { children: React.ReactNode }) {
  const { theme, accessibility } = useAppStore();
  const [announcer, setAnnouncer] = useState<{ message: string; priority: 'polite' | 'assertive' }>({
    message: '',
    priority: 'polite',
  });
  const announceTimeoutRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const announce: AnnounceFunction = useCallback((message, priority = 'polite') => {
    if (announceTimeoutRef.current) {
      clearTimeout(announceTimeoutRef.current);
    }
    setAnnouncer({ message: '', priority });
    requestAnimationFrame(() => {
      setAnnouncer({ message, priority });
      announceTimeoutRef.current = setTimeout(() => {
        setAnnouncer({ message: '', priority });
      }, 1000);
    });
  }, []);

  useEffect(() => {
    const config = getTheme(theme);
    applyTheme(config);
  }, [theme]);

  useEffect(() => {
    const root = document.documentElement;
    if (accessibility.reducedMotion) {
      root.style.setProperty('--duration-fast', '0ms');
      root.style.setProperty('--duration-normal', '0ms');
      root.style.setProperty('--duration-slow', '0ms');
    } else {
      root.style.removeProperty('--duration-fast');
      root.style.removeProperty('--duration-normal');
      root.style.removeProperty('--duration-slow');
    }
  }, [accessibility.reducedMotion]);

  useEffect(() => {
    const fontSizeMap: Record<string, string> = {
      small: '14px',
      medium: '16px',
      large: '18px',
      'extra-large': '20px',
    };
    document.documentElement.style.fontSize = fontSizeMap[accessibility.fontSize] || '16px';
  }, [accessibility.fontSize]);

  useEffect(() => {
    const spacingMap: Record<string, string> = {
      compact: '0.85',
      normal: '1',
      relaxed: '1.15',
    };
    document.documentElement.style.lineHeight = spacingMap[accessibility.spacing] || '1';
  }, [accessibility.spacing]);

  const value: AppContextValue = { announce, accessibility };

  return (
    <AppContext.Provider value={value}>
      {children}
      <div
        role="status"
        aria-live={announcer.priority}
        aria-atomic="true"
        className="sr-only"
      >
        {announcer.message}
      </div>
    </AppContext.Provider>
  );
}
