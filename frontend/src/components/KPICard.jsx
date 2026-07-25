/**
 * GrowthGuru AI — KPI Card Component
 * =====================================
 * Reusable stat card for the Dashboard.
 * Per UI/UX spec §6: #1E293B background, 1px border, 8px radius, no shadows.
 */

export default function KPICard({ icon: Icon, label, value, trend }) {
  // Product name values (strings) get a slightly smaller font to fit 2 lines gracefully
  const isProductName = typeof value === 'string' && isNaN(value.replace(/[₹,]/g, ''));

  return (
    <div className="card p-md">
      <div className="flex items-start justify-between mb-sm">
        <div className="p-xs rounded-button bg-primary/10">
          <Icon className="w-5 h-5 text-primary" />
        </div>
        {trend && (
          <span
            className={`text-small font-medium ${
              trend === 'up' ? 'text-primary' : trend === 'down' ? 'text-danger' : 'text-text-muted'
            }`}
          >
            {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '—'}
          </span>
        )}
      </div>
      <p className="text-small text-text-muted uppercase tracking-wider mb-xxs">
        {label}
      </p>
      <p
        className={`text-text-main font-bold leading-tight min-h-[2.2rem] ${
          isProductName ? 'text-[22px] line-clamp-2' : 'text-kpi'
        }`}
        title={typeof value === 'string' ? value : undefined}
      >
        {value}
      </p>
    </div>
  );
}
