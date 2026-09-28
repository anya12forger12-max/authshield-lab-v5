import { useAppStore } from '../../store/appStore';
import { Card, CardBody, CardHeader, CardTitle } from '../../components/common/Card';

const stats = [
  { label: 'Total Users', value: '1,247', change: '+12%', trend: 'up' as const, color: 'primary' as const },
  { label: 'Active Sessions', value: '89', change: '+5%', trend: 'up' as const, color: 'success' as const },
  { label: 'Attacks Run', value: '3,412', change: '+23%', trend: 'up' as const, color: 'warning' as const },
  { label: 'Threats Blocked', value: '2,981', change: '-2%', trend: 'down' as const, color: 'danger' as const },
];

const quickActions = [
  { label: 'Run Attack Scenario', description: 'Launch a new attack simulation', color: 'bg-[var(--color-danger-subtle)] text-[var(--color-danger)]' },
  { label: 'View Audit Logs', description: 'Review recent activity', color: 'bg-[var(--color-info-subtle)] text-[var(--color-info)]' },
  { label: 'Generate Report', description: 'Create security report', color: 'bg-[var(--color-success-subtle)] text-[var(--color-success)]' },
  { label: 'Learning Modules', description: 'Continue training', color: 'bg-[var(--color-warning-subtle)] text-[var(--color-warning)]' },
];

const recentActivity = [
  { id: '1', action: 'Brute force attack completed', time: '2 minutes ago', severity: 'warning' as const },
  { id: '2', action: 'New user registered: student_004', time: '5 minutes ago', severity: 'info' as const },
  { id: '3', action: 'Rate limiting rule triggered', time: '12 minutes ago', severity: 'danger' as const },
  { id: '4', action: 'Session hijack defense activated', time: '18 minutes ago', severity: 'success' as const },
  { id: '5', action: 'Learning module completed', time: '25 minutes ago', severity: 'info' as const },
];

const severityColors: Record<string, string> = {
  info: 'bg-[var(--color-info-subtle)] text-[var(--color-info)]',
  success: 'bg-[var(--color-success-subtle)] text-[var(--color-success)]',
  warning: 'bg-[var(--color-warning-subtle)] text-[var(--color-warning)]',
  danger: 'bg-[var(--color-danger-subtle)] text-[var(--color-danger)]',
};

export function DashboardPage() {
  const currentMode = useAppStore((s) => s.currentMode);

  return (
    <div className="space-y-6">
      <section aria-labelledby="welcome-heading">
        <h1 id="welcome-heading" className="text-2xl font-bold text-[var(--color-text-primary)]">
          Welcome to AuthShield Lab
        </h1>
        <p className="text-[var(--color-text-secondary)] mt-1">
          Currently in <span className="font-semibold capitalize">{currentMode}</span> mode. Here&apos;s your security overview.
        </p>
      </section>

      <section aria-labelledby="stats-heading">
        <h2 id="stats-heading" className="sr-only">Statistics</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat) => (
            <Card key={stat.label}>
              <CardBody>
                <p className="text-[var(--font-size-sm)] text-[var(--color-text-muted)]">{stat.label}</p>
                <p className="text-[var(--font-size-2xl)] font-bold text-[var(--color-text-primary)] mt-1">{stat.value}</p>
                <p className={`text-[var(--font-size-xs)] mt-1 font-medium ${
                  stat.trend === 'up' ? 'text-[var(--color-success)]' : 'text-[var(--color-danger)]'
                }`}>
                  {stat.change} from last week
                </p>
              </CardBody>
            </Card>
          ))}
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-2" aria-labelledby="actions-heading">
          <Card>
            <CardHeader>
              <CardTitle as="h2">Quick Actions</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {quickActions.map((action) => (
                  <button
                    key={action.label}
                    className="flex items-center gap-3 p-3 rounded-[var(--radius-md)] border border-[var(--color-border)] hover:border-[var(--color-primary)] hover:shadow-[var(--shadow-sm)] transition-all text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-focus-ring)]"
                  >
                    <div className={`w-10 h-10 rounded-[var(--radius-md)] flex items-center justify-center ${action.color}`}>
                      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                        <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-[var(--color-text-primary)]">{action.label}</p>
                      <p className="text-xs text-[var(--color-text-muted)]">{action.description}</p>
                    </div>
                  </button>
                ))}
              </div>
            </CardBody>
          </Card>
        </section>

        <section aria-labelledby="activity-heading">
          <Card className="h-full">
            <CardHeader>
              <CardTitle as="h2">Recent Activity</CardTitle>
            </CardHeader>
            <CardBody>
              <ul className="space-y-3">
                {recentActivity.map((item) => (
                  <li key={item.id} className="flex items-start gap-3">
                    <span className={`mt-1 w-2 h-2 rounded-full shrink-0 ${severityColors[item.severity]}`} aria-hidden="true" />
                    <div className="min-w-0">
                      <p className="text-sm text-[var(--color-text-primary)] truncate">{item.action}</p>
                      <p className="text-xs text-[var(--color-text-muted)]">{item.time}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </CardBody>
          </Card>
        </section>
      </div>

      <section aria-labelledby="score-heading">
        <Card>
          <CardHeader>
            <CardTitle as="h2">Security Score</CardTitle>
          </CardHeader>
          <CardBody>
            <div className="flex items-center gap-6">
              <div className="relative w-20 h-20">
                <svg className="w-20 h-20 -rotate-90" viewBox="0 0 80 80" aria-hidden="true">
                  <circle cx="40" cy="40" r="35" fill="none" stroke="var(--color-border)" strokeWidth="8" />
                  <circle cx="40" cy="40" r="35" fill="none" stroke="var(--color-success)" strokeWidth="8" strokeDasharray="220" strokeDashoffset="44" strokeLinecap="round" />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-lg font-bold text-[var(--color-success)]">80</span>
                </div>
              </div>
              <div>
                <p className="text-lg font-semibold text-[var(--color-text-primary)]">Good</p>
                <p className="text-sm text-[var(--color-text-secondary)]">
                  Your security posture is strong. Consider enabling additional defenses for critical assets.
                </p>
              </div>
            </div>
          </CardBody>
        </Card>
      </section>
    </div>
  );
}
