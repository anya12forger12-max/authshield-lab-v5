import type { Theme } from '../types';

export interface ThemeColors {
  primary: string;
  'primary-hover': string;
  'primary-active': string;
  'primary-subtle': string;
  secondary: string;
  'secondary-hover': string;
  'secondary-active': string;
  'secondary-subtle': string;
  success: string;
  'success-subtle': string;
  warning: string;
  'warning-subtle': string;
  danger: string;
  'danger-subtle': string;
  info: string;
  'info-subtle': string;
  background: string;
  surface: string;
  'surface-elevated': string;
  'surface-sunken': string;
  'text-primary': string;
  'text-secondary': string;
  'text-muted': string;
  'text-inverse': string;
  border: string;
  'border-subtle': string;
  'border-strong': string;
  'focus-ring': string;
  overlay: string;
  accent: string;
  'accent-subtle': string;
}

export interface ThemeTypography {
  fontFamily: { body: string; mono: string; display: string };
  fontSize: { xs: string; sm: string; base: string; lg: string; xl: string; '2xl': string };
  fontWeight: { normal: number; medium: number; semibold: number; bold: number };
  lineHeight: { tight: string; normal: string; relaxed: string };
}

export interface ThemeSpacing {
  xs: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
}

export interface ThemeAnimations {
  duration: { fast: string; normal: string; slow: string };
  easing: { default: string; in: string; out: string; inOut: string };
  reduceMotion: boolean;
}

export interface ThemeConfig {
  name: Theme;
  colors: ThemeColors;
  typography: ThemeTypography;
  spacing: ThemeSpacing;
  radius: { sm: string; md: string; lg: string; full: string };
  shadows: { sm: string; md: string; lg: string; focus: string };
  animations: ThemeAnimations;
}

const commonTypography: ThemeTypography = {
  fontFamily: {
    body: 'Inter, system-ui, -apple-system, sans-serif',
    mono: 'JetBrains Mono, Fira Code, monospace',
    display: 'Inter, system-ui, -apple-system, sans-serif',
  },
  fontSize: {
    xs: '0.75rem',
    sm: '0.875rem',
    base: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
  },
  fontWeight: { normal: 400, medium: 500, semibold: 600, bold: 700 },
  lineHeight: { tight: '1.25', normal: '1.5', relaxed: '1.75' },
};

const commonSpacing: ThemeSpacing = {
  xs: '0.25rem',
  sm: '0.5rem',
  md: '1rem',
  lg: '1.5rem',
  xl: '2rem',
  '2xl': '3rem',
};

const commonRadius = { sm: '0.25rem', md: '0.5rem', lg: '0.75rem', full: '9999px' };

export const lightTheme: ThemeConfig = {
  name: 'light',
  colors: {
    primary: '#2563eb',
    'primary-hover': '#1d4ed8',
    'primary-active': '#1e40af',
    'primary-subtle': '#eff6ff',
    secondary: '#475569',
    'secondary-hover': '#334155',
    'secondary-active': '#1e293b',
    'secondary-subtle': '#f1f5f9',
    success: '#16a34a',
    'success-subtle': '#f0fdf4',
    warning: '#d97706',
    'warning-subtle': '#fffbeb',
    danger: '#dc2626',
    'danger-subtle': '#fef2f2',
    info: '#0891b2',
    'info-subtle': '#ecfeff',
    background: '#f8fafc',
    surface: '#ffffff',
    'surface-elevated': '#ffffff',
    'surface-sunken': '#f1f5f9',
    'text-primary': '#0f172a',
    'text-secondary': '#475569',
    'text-muted': '#94a3b8',
    'text-inverse': '#ffffff',
    border: '#e2e8f0',
    'border-subtle': '#f1f5f9',
    'border-strong': '#cbd5e1',
    'focus-ring': 'rgba(37, 99, 235, 0.5)',
    overlay: 'rgba(0, 0, 0, 0.5)',
    accent: '#7e22ce',
    'accent-subtle': '#faf5ff',
  },
  typography: commonTypography,
  spacing: commonSpacing,
  radius: commonRadius,
  shadows: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
    focus: '0 0 0 3px rgba(37, 99, 235, 0.5)',
  },
  animations: {
    duration: { fast: '150ms', normal: '250ms', slow: '400ms' },
    easing: { default: 'cubic-bezier(0.4, 0, 0.2, 1)', in: 'cubic-bezier(0.4, 0, 1, 1)', out: 'cubic-bezier(0, 0, 0.2, 1)', inOut: 'cubic-bezier(0.4, 0, 0.2, 1)' },
    reduceMotion: false,
  },
};

export const darkTheme: ThemeConfig = {
  name: 'dark',
  colors: {
    primary: '#60a5fa',
    'primary-hover': '#93c5fd',
    'primary-active': '#3b82f6',
    'primary-subtle': 'rgba(59, 130, 246, 0.1)',
    secondary: '#94a3b8',
    'secondary-hover': '#cbd5e1',
    'secondary-active': '#e2e8f0',
    'secondary-subtle': 'rgba(148, 163, 184, 0.1)',
    success: '#4ade80',
    'success-subtle': 'rgba(74, 222, 128, 0.1)',
    warning: '#fbbf24',
    'warning-subtle': 'rgba(251, 191, 36, 0.1)',
    danger: '#f87171',
    'danger-subtle': 'rgba(248, 113, 113, 0.1)',
    info: '#22d3ee',
    'info-subtle': 'rgba(34, 211, 238, 0.1)',
    background: '#0f172a',
    surface: '#1e293b',
    'surface-elevated': '#273549',
    'surface-sunken': '#020617',
    'text-primary': '#f1f5f9',
    'text-secondary': '#94a3b8',
    'text-muted': '#475569',
    'text-inverse': '#0f172a',
    border: '#334155',
    'border-subtle': '#1e293b',
    'border-strong': '#475569',
    'focus-ring': 'rgba(96, 165, 250, 0.5)',
    overlay: 'rgba(0, 0, 0, 0.7)',
    accent: '#c084fc',
    'accent-subtle': 'rgba(192, 132, 252, 0.1)',
  },
  typography: commonTypography,
  spacing: commonSpacing,
  radius: commonRadius,
  shadows: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.3)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -2px rgba(0, 0, 0, 0.3)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -4px rgba(0, 0, 0, 0.3)',
    focus: '0 0 0 3px rgba(96, 165, 250, 0.5)',
  },
  animations: {
    duration: { fast: '150ms', normal: '250ms', slow: '400ms' },
    easing: { default: 'cubic-bezier(0.4, 0, 0.2, 1)', in: 'cubic-bezier(0.4, 0, 1, 1)', out: 'cubic-bezier(0, 0, 0.2, 1)', inOut: 'cubic-bezier(0.4, 0, 0.2, 1)' },
    reduceMotion: false,
  },
};

export const highContrastDarkTheme: ThemeConfig = {
  name: 'high-contrast-dark',
  colors: {
    primary: '#6db3f2',
    'primary-hover': '#9dcdf7',
    'primary-active': '#4a9fe8',
    'primary-subtle': 'rgba(109, 179, 242, 0.15)',
    secondary: '#c0cad8',
    'secondary-hover': '#dde4ec',
    'secondary-active': '#eef1f5',
    'secondary-subtle': 'rgba(192, 202, 216, 0.15)',
    success: '#5ce88a',
    'success-subtle': 'rgba(92, 232, 138, 0.15)',
    warning: '#ffd666',
    'warning-subtle': 'rgba(255, 214, 102, 0.15)',
    danger: '#ff7878',
    'danger-subtle': 'rgba(255, 120, 120, 0.15)',
    info: '#4de0f0',
    'info-subtle': 'rgba(77, 224, 240, 0.15)',
    background: '#000000',
    surface: '#1a1a1a',
    'surface-elevated': '#2a2a2a',
    'surface-sunken': '#0a0a0a',
    'text-primary': '#ffffff',
    'text-secondary': '#d0d0d0',
    'text-muted': '#808080',
    'text-inverse': '#000000',
    border: '#555555',
    'border-subtle': '#333333',
    'border-strong': '#777777',
    'focus-ring': 'rgba(109, 179, 242, 0.7)',
    overlay: 'rgba(0, 0, 0, 0.85)',
    accent: '#d8a0ff',
    'accent-subtle': 'rgba(216, 160, 255, 0.15)',
  },
  typography: commonTypography,
  spacing: { xs: '0.25rem', sm: '0.5rem', md: '1rem', lg: '1.5rem', xl: '2rem', '2xl': '3rem' },
  radius: { sm: '0.25rem', md: '0.5rem', lg: '0.75rem', full: '9999px' },
  shadows: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.5)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.6), 0 2px 4px -2px rgba(0, 0, 0, 0.5)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.6), 0 4px 6px -4px rgba(0, 0, 0, 0.5)',
    focus: '0 0 0 4px rgba(109, 179, 242, 0.7)',
  },
  animations: {
    duration: { fast: '150ms', normal: '250ms', slow: '400ms' },
    easing: { default: 'cubic-bezier(0.4, 0, 0.2, 1)', in: 'cubic-bezier(0.4, 0, 1, 1)', out: 'cubic-bezier(0, 0, 0.2, 1)', inOut: 'cubic-bezier(0.4, 0, 0.2, 1)' },
    reduceMotion: false,
  },
};

export const highContrastLightTheme: ThemeConfig = {
  name: 'high-contrast-light',
  colors: {
    primary: '#0044cc',
    'primary-hover': '#003399',
    'primary-active': '#002266',
    'primary-subtle': 'rgba(0, 68, 204, 0.1)',
    secondary: '#333333',
    'secondary-hover': '#1a1a1a',
    'secondary-active': '#000000',
    'secondary-subtle': 'rgba(51, 51, 51, 0.1)',
    success: '#006600',
    'success-subtle': 'rgba(0, 102, 0, 0.1)',
    warning: '#996600',
    'warning-subtle': 'rgba(153, 102, 0, 0.1)',
    danger: '#cc0000',
    'danger-subtle': 'rgba(204, 0, 0, 0.1)',
    info: '#006699',
    'info-subtle': 'rgba(0, 102, 153, 0.1)',
    background: '#ffffff',
    surface: '#f5f5f5',
    'surface-elevated': '#ffffff',
    'surface-sunken': '#e8e8e8',
    'text-primary': '#000000',
    'text-secondary': '#222222',
    'text-muted': '#555555',
    'text-inverse': '#ffffff',
    border: '#555555',
    'border-subtle': '#999999',
    'border-strong': '#333333',
    'focus-ring': 'rgba(0, 68, 204, 0.6)',
    overlay: 'rgba(0, 0, 0, 0.6)',
    accent: '#660099',
    'accent-subtle': 'rgba(102, 0, 153, 0.1)',
  },
  typography: commonTypography,
  spacing: { xs: '0.25rem', sm: '0.5rem', md: '1rem', lg: '1.5rem', xl: '2rem', '2xl': '3rem' },
  radius: { sm: '0.25rem', md: '0.5rem', lg: '0.75rem', full: '9999px' },
  shadows: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.15)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -2px rgba(0, 0, 0, 0.15)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -4px rgba(0, 0, 0, 0.15)',
    focus: '0 0 0 4px rgba(0, 68, 204, 0.6)',
  },
  animations: {
    duration: { fast: '150ms', normal: '250ms', slow: '400ms' },
    easing: { default: 'cubic-bezier(0.4, 0, 0.2, 1)', in: 'cubic-bezier(0.4, 0, 1, 1)', out: 'cubic-bezier(0, 0, 0.2, 1)', inOut: 'cubic-bezier(0.4, 0, 0.2, 1)' },
    reduceMotion: false,
  },
};

const themes: Record<Theme, ThemeConfig> = {
  light: lightTheme,
  dark: darkTheme,
  system: lightTheme,
  'high-contrast-dark': highContrastDarkTheme,
  'high-contrast-light': highContrastLightTheme,
};

export function getTheme(theme: Theme): ThemeConfig {
  if (theme === 'system') {
    return getSystemTheme();
  }
  return themes[theme] ?? lightTheme;
}

function getSystemTheme(): ThemeConfig {
  if (typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return darkTheme;
  }
  return lightTheme;
}

function applyColorsToElement(element: HTMLElement, colors: ThemeColors): void {
  const root = element;
  for (const [key, value] of Object.entries(colors)) {
    root.style.setProperty(`--color-${key}`, value);
  }
}

function applyTypographyToElement(element: HTMLElement, typography: ThemeTypography): void {
  const root = element;
  for (const [key, value] of Object.entries(typography.fontFamily)) {
    root.style.setProperty(`--font-family-${key}`, value);
  }
  for (const [key, value] of Object.entries(typography.fontSize)) {
    root.style.setProperty(`--font-size-${key}`, value);
  }
  for (const [key, value] of Object.entries(typography.lineHeight)) {
    root.style.setProperty(`--line-height-${key}`, String(value));
  }
}

function applySpacingToElement(element: HTMLElement, spacing: ThemeSpacing): void {
  for (const [key, value] of Object.entries(spacing)) {
    element.style.setProperty(`--spacing-${key}`, value);
  }
}

export function applyTheme(config: ThemeConfig): void {
  const root = document.documentElement;
  root.setAttribute('data-theme', config.name);
  applyColorsToElement(root, config.colors);
  applyTypographyToElement(root, config.typography);
  applySpacingToElement(root, config.spacing);

  for (const [key, value] of Object.entries(config.radius)) {
    root.style.setProperty(`--radius-${key}`, value);
  }
  for (const [key, value] of Object.entries(config.shadows)) {
    root.style.setProperty(`--shadow-${key}`, value);
  }
  for (const [key, value] of Object.entries(config.animations.duration)) {
    root.style.setProperty(`--duration-${key}`, value);
  }
  for (const [key, value] of Object.entries(config.animations.easing)) {
    root.style.setProperty(`--easing-${key}`, value);
  }
}

function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? { r: parseInt(result[1], 16), g: parseInt(result[2], 16), b: parseInt(result[3], 16) }
    : null;
}

function rgbToHex(r: number, g: number, b: number): string {
  return `#${  [r, g, b].map((x) => Math.round(Math.min(255, Math.max(0, x))).toString(16).padStart(2, '0')).join('')}`;
}

function getLuminance(r: number, g: number, b: number): number {
  const [rs, gs, bs] = [r, g, b].map((c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

function getContrastRatio(hex1: string, hex2: string): number {
  const rgb1 = hexToRgb(hex1);
  const rgb2 = hexToRgb(hex2);
  if (!rgb1 || !rgb2) return 1;
  const l1 = getLuminance(rgb1.r, rgb1.g, rgb1.b);
  const l2 = getLuminance(rgb2.r, rgb2.g, rgb2.b);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

function ensureContrast(accent: string, background: string, minRatio = 4.5): string {
  const ratio = getContrastRatio(accent, background);
  if (ratio >= minRatio) return accent;

  const rgb = hexToRgb(accent);
  if (!rgb) return accent;

  const bgRgb = hexToRgb(background);
  if (!bgRgb) return accent;

  let best = accent;
  let bestRatio = ratio;

  for (let factor = 0.5; factor <= 2; factor += 0.05) {
    const candidate = rgbToHex(rgb.r * factor, rgb.g * factor, rgb.b * factor);
    const candidateRatio = getContrastRatio(candidate, background);
    if (candidateRatio >= minRatio && Math.abs(candidateRatio - minRatio) < Math.abs(bestRatio - minRatio)) {
      best = candidate;
      bestRatio = candidateRatio;
    }
  }

  return bestRatio >= minRatio ? best : accent;
}

export function customizeAccent(baseTheme: ThemeConfig, accentColor: string): ThemeConfig {
  const adjustedAccent = ensureContrast(accentColor, baseTheme.colors.background);
  const adjustedAccentSubtle = `${accentColor  }1a`;

  return {
    ...baseTheme,
    colors: {
      ...baseTheme.colors,
      accent: adjustedAccent,
      'accent-subtle': adjustedAccentSubtle,
    },
  };
}

export { themes };

export class ThemeProvider {
  private currentTheme: Theme = 'dark';
  private listeners: Set<(theme: ThemeConfig) => void> = new Set();
  private mediaQuery: MediaQueryList | null = null;

  constructor() {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('authshield-theme') as Theme | null;
      this.currentTheme = stored && themes[stored] ? stored : 'dark';
      this.mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      this.mediaQuery.addEventListener('change', this.handleSystemChange);
    }
  }

  private handleSystemChange = (): void => {
    if (this.currentTheme === 'system') {
      this.emitChange();
    }
  };

  private emitChange(): void {
    const config = getTheme(this.currentTheme);
    applyTheme(config);
    this.listeners.forEach((listener) => listener(config));
  }

  getTheme(): Theme {
    return this.currentTheme;
  }

  setTheme(theme: Theme): void {
    this.currentTheme = theme;
    if (typeof window !== 'undefined') {
      localStorage.setItem('authshield-theme', theme);
    }
    this.emitChange();
  }

  getResolvedTheme(): 'light' | 'dark' {
    const config = getTheme(this.currentTheme);
    return config.name.includes('dark') ? 'dark' : 'light';
  }

  subscribe(listener: (theme: ThemeConfig) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  destroy(): void {
    this.listeners.clear();
    this.mediaQuery?.removeEventListener('change', this.handleSystemChange);
  }
}
