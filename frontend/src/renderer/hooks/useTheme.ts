import { useCallback, useEffect, useState } from 'react';
import { useAppStore } from '../store/appStore';
import { getTheme, applyTheme } from '../themes/theme-engine';
import type { Theme } from '../types';

export function useTheme() {
  const { theme, setTheme: setStoreTheme } = useAppStore((state) => ({
    theme: state.theme,
    setTheme: state.setTheme,
  }));
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('dark');

  const setTheme = useCallback(
    (newTheme: Theme) => {
      setStoreTheme(newTheme);
      const config = getTheme(newTheme);
      applyTheme(config);
      setResolvedTheme(config.name.includes('dark') ? 'dark' : 'light');
    },
    [setStoreTheme]
  );

  const toggleTheme = useCallback(() => {
    const next: Theme = theme === 'dark' ? 'light' : theme === 'light' ? 'dark' : theme;
    setTheme(next);
  }, [theme, setTheme]);

  useEffect(() => {
    const config = getTheme(theme);
    applyTheme(config);
    setResolvedTheme(config.name.includes('dark') ? 'dark' : 'light');
  }, [theme]);

  useEffect(() => {
    if (theme !== 'system') return;
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent) => {
      const resolved = e.matches ? 'dark' : 'light';
      setResolvedTheme(resolved);
      applyTheme(getTheme(resolved));
    };
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [theme]);

  return { theme, resolvedTheme, setTheme, toggleTheme };
}
