import type React from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { SkipNavigation } from '../../accessibility/SkipNavigation';
import { useAppStore } from '../../store/appStore';
import { cn } from '../../utils/cn';

interface AppLayoutProps {
  children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const sidebarCollapsed = useAppStore((s) => s.sidebarCollapsed);

  return (
    <div className="flex h-screen overflow-hidden bg-[var(--color-background)]">
      <SkipNavigation />

      <Sidebar />

      <div
        className={cn(
          'flex flex-col flex-1 min-w-0 transition-all duration-[var(--transition-normal)]',
          sidebarCollapsed ? 'ml-16' : 'ml-64'
        )}
      >
        <Header />

        <main
          id="main-content"
          role="main"
          className="flex-1 overflow-y-auto p-6"
          tabIndex={-1}
        >
          {children}
        </main>
      </div>
    </div>
  );
}
