import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './contexts/AppContext';
import { ScreenReaderAnnouncer } from './accessibility/ScreenReaderAnnouncer';
import { AppLayout } from './components/layout/AppLayout';
import { DashboardPage } from './pages/dashboard/DashboardPage';

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">{title}</h1>
      <p className="text-[var(--color-text-secondary)]">
        This section is under construction. Check back soon.
      </p>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <ScreenReaderAnnouncer>
        <AppProvider>
          <AppLayout>
            <Routes>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/authentication" element={<PlaceholderPage title="Authentication" />} />
              <Route path="/authentication/*" element={<PlaceholderPage title="Authentication" />} />
              <Route path="/users" element={<PlaceholderPage title="Users" />} />
              <Route path="/sessions" element={<PlaceholderPage title="Sessions" />} />
              <Route path="/attacks" element={<PlaceholderPage title="Attacks" />} />
              <Route path="/defenses" element={<PlaceholderPage title="Defenses" />} />
              <Route path="/analytics" element={<PlaceholderPage title="Analytics" />} />
              <Route path="/audit" element={<PlaceholderPage title="Audit Logs" />} />
              <Route path="/timeline" element={<PlaceholderPage title="Security Timeline" />} />
              <Route path="/reports" element={<PlaceholderPage title="Reports" />} />
              <Route path="/learning" element={<PlaceholderPage title="Learning Center" />} />
              <Route path="/settings" element={<PlaceholderPage title="Settings" />} />
              <Route path="/help" element={<PlaceholderPage title="Help" />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </AppLayout>
        </AppProvider>
      </ScreenReaderAnnouncer>
    </BrowserRouter>
  );
}
