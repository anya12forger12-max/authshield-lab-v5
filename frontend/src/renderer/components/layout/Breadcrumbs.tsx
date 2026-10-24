import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { navigationConfig } from '../../navigation/navigationConfig';
import { cn } from '../../utils/cn';

function findNavItemByPath(path: string, items = navigationConfig): { label: string; path: string } | null {
  for (const item of items) {
    if (item.path === path) {
      return { label: item.label, path: item.path };
    }
    if (item.children) {
      const found = findNavItemByPath(path, item.children);
      if (found) return found;
    }
  }
  return null;
}

function generateBreadcrumbs(pathname: string): { label: string; path: string; isCurrent: boolean }[] {
  if (pathname === '/dashboard') {
    return [{ label: 'Dashboard', path: '/dashboard', isCurrent: true }];
  }

  const segments = pathname.split('/').filter(Boolean);
  const crumbs: { label: string; path: string; isCurrent: boolean }[] = [];

  for (let i = 0; i < segments.length; i++) {
    const path = `/${  segments.slice(0, i + 1).join('/')}`;
    const navItem = findNavItemByPath(path);

    crumbs.push({
      label: navItem?.label || segments[i].charAt(0).toUpperCase() + segments[i].slice(1).replace(/-/g, ' '),
      path,
      isCurrent: i === segments.length - 1,
    });
  }

  return crumbs;
}

export function Breadcrumbs() {
  const location = useLocation();
  const crumbs = generateBreadcrumbs(location.pathname);

  if (crumbs.length <= 1) return null;

  return (
    <nav aria-label="Breadcrumb" className="min-w-0">
      <ol className="flex items-center gap-1 text-[var(--font-size-sm)] min-w-0">
        {crumbs.map((crumb, index) => {
          const isLast = index === crumbs.length - 1;
          const isMiddle = crumbs.length > 4 && index > 0 && index < crumbs.length - 2 && !isLast;

          if (isMiddle) {
            if (index === 1) {
              return (
                <React.Fragment key={crumb.path}>
                  <li aria-hidden="true" className="text-[var(--color-text-muted)]">
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="1" fill="currentColor" />
                      <circle cx="19" cy="12" r="1" fill="currentColor" />
                      <circle cx="5" cy="12" r="1" fill="currentColor" />
                    </svg>
                  </li>
                  <li>
                    <span className="text-[var(--color-text-muted)]" aria-hidden="true">
                      ...
                    </span>
                  </li>
                </React.Fragment>
              );
            }
            return null;
          }

          return (
            <li key={crumb.path} className="flex items-center gap-1 min-w-0">
              {index > 0 && (
                <svg
                  className="w-4 h-4 shrink-0 text-[var(--color-text-muted)]"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  aria-hidden="true"
                >
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              )}
              {isLast ? (
                <span
                  className="font-medium text-[var(--color-text-primary)] truncate"
                  aria-current="page"
                >
                  {crumb.label}
                </span>
              ) : (
                <Link
                  to={crumb.path}
                  className={cn(
                    'text-[var(--color-text-muted)] hover:text-[var(--color-primary)] transition-colors truncate',
                    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-focus-ring)] focus-visible:ring-offset-1 rounded'
                  )}
                >
                  {crumb.label}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
