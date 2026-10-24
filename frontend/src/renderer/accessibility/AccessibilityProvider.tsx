import type React from 'react';
import { createContext, useContext, useEffect, useCallback, useRef, useState } from 'react';
import { useAppStore } from '../store/appStore';
import type { AccessibilityPreferences } from '../types';

interface AccessibilityContextValue {
  preferences: AccessibilityPreferences;
  updatePreferences: (updates: Partial<AccessibilityPreferences>) => void;
  announce: (message: string, priority?: 'polite' | 'assertive') => void;
  registerShortcut: (id: string, handler: (e: KeyboardEvent) => void, keys: string[]) => void;
  unregisterShortcut: (id: string) => void;
}

const AccessibilityContext = createContext<AccessibilityContextValue | null>(null);

export function useAccessibility(): AccessibilityContextValue {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within AccessibilityProvider');
  }
  return context;
}

export function getAccessibilityPrefs(): AccessibilityPreferences {
  try {
    const stored = localStorage.getItem('authshield-accessibility');
    if (stored) {
      return JSON.parse(stored) as AccessibilityPreferences;
    }
  } catch {
    // fall through to defaults
  }
  return {
    highContrast: false,
    reducedMotion: window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false,
    fontSize: 'medium',
    keyboardNav: true,
    screenReader: false,
    dyslexiaFont: false,
    spacing: 'normal',
  };
}

export function updateAccessibilityPrefs(prefs: AccessibilityPreferences): void {
  localStorage.setItem('authshield-accessibility', JSON.stringify(prefs));
}

export function AccessibilityProvider({ children }: { children: React.ReactNode }) {
  const storePrefs = useAppStore((s) => s.accessibility);
  const updateStorePrefs = useAppStore((s) => s.updateAccessibility);
  const [preferences, setPreferences] = useState<AccessibilityPreferences>(storePrefs);
  const [announcerMessage, setAnnouncerMessage] = useState('');
  const [announcerPriority, setAnnouncerPriority] = useState<'polite' | 'assertive'>('polite');
  const shortcutsRef = useRef<Map<string, { handler: (e: KeyboardEvent) => void; keys: string[] }>>(new Map());
  const announceTimeoutRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    if (announceTimeoutRef.current) clearTimeout(announceTimeoutRef.current);
    setAnnouncerMessage('');
    setAnnouncerPriority(priority);
    requestAnimationFrame(() => {
      setAnnouncerMessage(message);
      announceTimeoutRef.current = setTimeout(() => setAnnouncerMessage(''), 1500);
    });
  }, []);

  const updatePreferences = useCallback(
    (updates: Partial<AccessibilityPreferences>) => {
      setPreferences((prev) => {
        const next = { ...prev, ...updates };
        updateStorePrefs(next);
        updateAccessibilityPrefs(next);
        return next;
      });
    },
    [updateStorePrefs]
  );

  const registerShortcut = useCallback(
    (id: string, handler: (e: KeyboardEvent) => void, keys: string[]) => {
      shortcutsRef.current.set(id, { handler, keys });
    },
    []
  );

  const unregisterShortcut = useCallback((id: string) => {
    shortcutsRef.current.delete(id);
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      for (const [, shortcut] of shortcutsRef.current) {
        const keyCombo = [];
        if (e.ctrlKey) keyCombo.push('ctrl');
        if (e.altKey) keyCombo.push('alt');
        if (e.shiftKey) keyCombo.push('shift');
        if (e.metaKey) keyCombo.push('meta');
        keyCombo.push(e.key.toLowerCase());

        const comboStr = keyCombo.join('+');
        if (shortcut.keys.includes(comboStr)) {
          e.preventDefault();
          shortcut.handler(e);
        }
      }
    };

    if (preferences.keyboardNav) {
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [preferences.keyboardNav]);

  useEffect(() => {
    const mql = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handler = (e: MediaQueryListEvent) => {
      updatePreferences({ reducedMotion: e.matches });
    };
    mql.addEventListener('change', handler);
    return () => mql.removeEventListener('change', handler);
  }, [updatePreferences]);

  useEffect(() => {
    const mql = window.matchMedia('(prefers-contrast: more)');
    const handler = (e: MediaQueryListEvent) => {
      updatePreferences({ highContrast: e.matches });
    };
    mql.addEventListener('change', handler);
    return () => mql.removeEventListener('change', handler);
  }, [updatePreferences]);

  const value: AccessibilityContextValue = {
    preferences,
    updatePreferences,
    announce,
    registerShortcut,
    unregisterShortcut,
  };

  return (
    <AccessibilityContext.Provider value={value}>
      {children}
      <div
        role="status"
        aria-live={announcerPriority}
        aria-atomic="true"
        className="sr-only"
      >
        {announcerMessage}
      </div>
    </AccessibilityContext.Provider>
  );
}
