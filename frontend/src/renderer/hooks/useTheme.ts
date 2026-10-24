import { useCallback, useEffect, useSyncExternalStore } from 'react';
import { useAppStore } from '../store/appStore';
import { getTheme, applyTheme } from '../themes/theme-engine';
import type { Theme } from '../types';

const DARK_QUERY = '(prefers-color-scheme: dark)';

function subscribeSystemScheme(onStoreChange: () => void) {
  if (typeof window === 'undefined') return () => {};
  const mediaQuery = window.matchMedia(DARK_QUERY);
  mediaQuery.addEventListener('change', onStoreChange);
  return () => mediaQuery.removeEventListener('change', onStoreChange);
}

function getSystemIsDark() {
  if (typeof window === 'undefined') return false;
  return window.matchMedia(DARK_QUERY).matches;
}

export function useTheme() {
  const { theme, setTheme: setStoreTheme } = useAppStore((state) => ({
    theme: state.theme,
    setTheme: state.setTheme,
  }));
  const systemIsDark = useSyncExternalStore(subscribeSystemScheme, getSystemIsDark, () => false);

  const resolvedTheme: 'light' | 'dark' =
    theme === 'system'
      ? systemIsDark
        ? 'dark'
        : 'light'
      : getTheme(theme).name.includes('dark')
        ? 'dark'
        : 'light';

  const setTheme = useCallback(
    (newTheme: Theme) => {
      setStoreTheme(newTheme);
      applyTheme(getTheme(newTheme));
    },
    [setStoreTheme]
  );

  const toggleTheme = useCallback(() => {
    const next: Theme = theme === 'dark' ? 'light' : theme === 'light' ? 'dark' : theme;
    setTheme(next);
  }, [theme, setTheme]);

  useEffect(() => {
    applyTheme(getTheme(theme));
  }, [theme, systemIsDark]);

  return { theme, resolvedTheme, setTheme, toggleTheme };
}
