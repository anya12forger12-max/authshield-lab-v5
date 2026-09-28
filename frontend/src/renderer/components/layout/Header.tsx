import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useAppStore } from '../../store/appStore';
import { Breadcrumbs } from './Breadcrumbs';
import { cn } from '../../utils/cn';
import type { UserRole } from '../../types';

export function Header() {
  const {
    searchOpen,
    setSearchOpen,
    searchQuery,
    setSearchQuery,
    theme,
    toggleTheme,
    notifications,
    unreadNotificationCount,
    markAllNotificationsRead,
    currentMode,
    setCurrentMode,
    user,
  } = useAppStore();

  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [modeMenuOpen, setModeMenuOpen] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const notifRef = useRef<HTMLDivElement>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const modeMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (searchOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [searchOpen]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setNotificationsOpen(false);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setUserMenuOpen(false);
      }
      if (modeMenuRef.current && !modeMenuRef.current.contains(e.target as Node)) {
        setModeMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearchKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Escape') {
        setSearchOpen(false);
        setSearchQuery('');
      }
    },
    [setSearchOpen, setSearchQuery]
  );

  const modes: { value: UserRole; label: string }[] = [
    { value: 'demo', label: 'Demo' },
    { value: 'student', label: 'Student' },
    { value: 'instructor', label: 'Instructor' },
    { value: 'administrator', label: 'Administrator' },
    { value: 'developer', label: 'Developer' },
  ];

  return (
    <header
      aria-label="Main header"
      className="h-16 flex items-center justify-between px-6 border-b border-[var(--color-border)] bg-[var(--color-surface)]"
    >
      <div className="flex items-center gap-4 flex-1 min-w-0">
        <Breadcrumbs />
      </div>

      <div className="flex items-center gap-2">
        <div className="relative" ref={modeMenuRef}>
          <button
            onClick={() => setModeMenuOpen(!modeMenuOpen)}
            className="px-3 py-1.5 text-[var(--font-size-xs)] font-medium rounded-[var(--radius-md)] bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)] hover:bg-[var(--color-border-subtle)] capitalize transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-focus-ring)]"
            aria-label={`Current mode: ${currentMode}. Change mode.`}
            aria-expanded={modeMenuOpen}
          >
            {currentMode}
          </button>
          {modeMenuOpen && (
            <div className="absolute right-0 top-full mt-1 w-40 bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded-[var(--radius-md)] shadow-[var(--shadow-lg)] py-1 z-50">
              {modes.map((mode) => (
                <button
                  key={mode.value}
                  onClick={() => {
                    setCurrentMode(mode.value);
                    setModeMenuOpen(false);
                  }}
                  className={cn(
                    'w-full text-left px-3 py-2 text-sm transition-colors',
                    currentMode === mode.value
                      ? 'bg-[var(--color-primary-subtle)] text-[var(--color-primary)]'
                      : 'text-[var(--color-text-primary)] hover:bg-[var(--color-surface-sunken)]'
                  )}
                >
                  {mode.label}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="relative">
          <button
            onClick={() => setSearchOpen(!searchOpen)}
            className="p-2 rounded-[var(--radius-md)] text-[var(--color-text-muted)] hover:bg-[var(--color-surface-sunken)] hover:text-[var(--color-text-primary)] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-focus-ring)]"
            aria-label="Toggle search"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
          </button>
          {searchOpen && (
            <div className="absolute right-0 top-full mt-1 w-80">
              <input
                ref={searchInputRef}
                type="search"
                placeholder="Search AuthShield Lab..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={handleSearchKeyDown}
                className="w-full h-10 px-4 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--color-focus-ring)]"
                aria-label="Search"
              />
            </div>
          )}
        </div>

        <button
          onClick={toggleTheme}
          className="p-2 rounded-[var(--radius-md)] text-[var(--color-text-muted)] hover:bg-[var(--color-surface-sunken)] hover:text-[var(--color-text-primary)] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-focus-ring)]"
          aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark' || theme === 'high-contrast-dark' ? (
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <circle cx="12" cy="12" r="5" /><line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" /><line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" /><line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" /><line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
            </svg>
          ) : (
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          )}
        </button>

        <div className="relative" ref={notifRef}>
          <button
            onClick={() => setNotificationsOpen(!notificationsOpen)}
            className="relative p-2 rounded-[var(--radius-md)] text-[var(--color-text-muted)] hover:bg-[var(--color-surface-sunken)] hover:text-[var(--color-text-primary)] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-focus-ring)]"
            aria-label={`Notifications${unreadNotificationCount > 0 ? `, ${unreadNotificationCount} unread` : ''}`}
            aria-expanded={notificationsOpen}
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
            {unreadNotificationCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-[var(--color-danger)] text-white text-[9px] font-bold rounded-full flex items-center justify-center" aria-hidden="true">
                {unreadNotificationCount > 99 ? '99+' : unreadNotificationCount}
              </span>
            )}
          </button>
          {notificationsOpen && (
            <div className="absolute right-0 top-full mt-1 w-80 bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded-[var(--radius-lg)] shadow-[var(--shadow-lg)] z-50">
              <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border-subtle)]">
                <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">Notifications</h3>
                {unreadNotificationCount > 0 && (
                  <button
                    onClick={markAllNotificationsRead}
                    className="text-xs text-[var(--color-primary)] hover:underline"
                  >
                    Mark all read
                  </button>
                )}
              </div>
              <div className="max-h-64 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="px-4 py-6 text-center text-sm text-[var(--color-text-muted)]">
                    No notifications
                  </div>
                ) : (
                  notifications.slice(0, 10).map((notif) => (
                    <div
                      key={notif.id}
                      className={cn(
                        'px-4 py-3 border-b border-[var(--color-border-subtle)] last:border-0',
                        !notif.read && 'bg-[var(--color-primary-subtle)]/30'
                      )}
                    >
                      <p className="text-sm font-medium text-[var(--color-text-primary)]">{notif.title}</p>
                      <p className="text-xs text-[var(--color-text-muted)] mt-0.5">{notif.message}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        <div className="relative" ref={userMenuRef}>
          <button
            onClick={() => setUserMenuOpen(!userMenuOpen)}
            className="flex items-center gap-2 p-1 rounded-[var(--radius-md)] hover:bg-[var(--color-surface-sunken)] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-focus-ring)]"
            aria-label="User menu"
            aria-expanded={userMenuOpen}
          >
            <div className="w-8 h-8 rounded-full bg-[var(--color-primary-subtle)] flex items-center justify-center">
              <span className="text-[var(--font-size-sm)] font-semibold text-[var(--color-primary)]">
                {user?.displayName?.charAt(0)?.toUpperCase() || 'U'}
              </span>
            </div>
          </button>
          {userMenuOpen && (
            <div className="absolute right-0 top-full mt-1 w-48 bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded-[var(--radius-md)] shadow-[var(--shadow-lg)] py-1 z-50">
              <div className="px-3 py-2 border-b border-[var(--color-border-subtle)]">
                <p className="text-sm font-medium text-[var(--color-text-primary)]">{user?.displayName}</p>
                <p className="text-xs text-[var(--color-text-muted)]">{user?.email}</p>
              </div>
              <button className="w-full text-left px-3 py-2 text-sm text-[var(--color-text-primary)] hover:bg-[var(--color-surface-sunken)] transition-colors">
                Profile
              </button>
              <button className="w-full text-left px-3 py-2 text-sm text-[var(--color-text-primary)] hover:bg-[var(--color-surface-sunken)] transition-colors">
                Preferences
              </button>
              <div className="border-t border-[var(--color-border-subtle)] mt-1 pt-1">
                <button className="w-full text-left px-3 py-2 text-sm text-[var(--color-danger)] hover:bg-[var(--color-danger-subtle)] transition-colors">
                  Sign out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
