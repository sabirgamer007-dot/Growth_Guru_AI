import {
  ShoppingCart,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Sparkles,
  Lightbulb,
  ArrowRight,
  Package,
  AlertTriangle,
  BarChart3,
} from 'lucide-react';
import KPICard from '../components/KPICard';
import SalesChart from '../components/SalesChart';

export default function DashboardScreen({ businessProfile, kpis, productData, onNavigateToCoach }) {
  const businessName = businessProfile?.businessName || 'Your Business';

  const insightsList = kpis?.insights?.opportunities || [];

  // Empty state
  if (!kpis) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-64px-48px)] text-center">
        <ShoppingCart className="w-12 h-12 text-text-muted mb-sm" />
        <h2 className="text-h2 text-text-main mb-xs">No Data Available</h2>
        <p className="text-body text-text-muted max-w-md">
          Upload your sales CSV file first to see your dashboard analytics and KPI overview.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-md">
      {/* Business Name Sub-header */}
      <p className="text-body text-text-muted">
        Overview for <span className="text-text-main font-medium">{businessName}</span>
      </p>

      {/* KPI Cards — 4 columns on desktop, 2 on tablet, 1 on mobile */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-md">
        <KPICard
          icon={ShoppingCart}
          label="Total Sales"
          value={kpis.totalSales.toLocaleString('en-IN')}
        />
        <KPICard
          icon={DollarSign}
          label="Total Revenue"
          value={`₹${kpis.totalRevenue.toLocaleString('en-IN')}`}
        />
        <KPICard
          icon={TrendingUp}
          label="Best Selling Product"
          value={kpis.bestSeller}
          trend="up"
        />
        <KPICard
          icon={TrendingDown}
          label="Lowest Selling Product"
          value={kpis.worstSeller}
          trend="down"
        />
      </div>

      {/* Middle Row — Chart (2/3) + Insights (1/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-md">
        {/* Sales Chart — spans 2 columns */}
        <div className="lg:col-span-2">
          <SalesChart data={productData} />
        </div>

        {/* Top Insights */}
        <div className="card p-md">
          <h2 className="text-h2 text-text-main mb-md">Top Insights</h2>

          {insightsList.length > 0 ? (
            <ul className="space-y-sm">
              {insightsList.map((insightText, idx) => {
                return (
                  <li key={idx} className="flex items-start gap-xs">
                    <div className="p-xxs rounded-button flex-shrink-0 mt-0.5 bg-primary/10">
                      <Sparkles className="w-5 h-5 text-primary" />
                    </div>
                    <p className="text-body text-text-muted leading-relaxed">{insightText}</p>
                  </li>
                );
              })}
            </ul>
          ) : (
            <p className="text-body text-text-muted">
              No insights are available for this analysis.
            </p>
          )}
        </div>
      </div>

      {/* Bottom Row — AI Growth Coach CTA */}
      <div className="card p-lg">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-sm">
          <div className="flex items-start gap-sm">
            <div className="p-xs rounded-button bg-primary/10 flex-shrink-0">
              <Sparkles className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h2 className="text-h2 text-text-main">Ready for AI-Powered Growth?</h2>
              <p className="text-body text-text-muted mt-xxs">
                Let our AI analyze your sales data and business profile to generate a tailored growth
                strategy, product-specific social media captions, and targeted hashtags.
              </p>
            </div>
          </div>
          <button
            className="btn-primary flex items-center gap-xs whitespace-nowrap flex-shrink-0"
            onClick={onNavigateToCoach}
          >
            Generate Growth Plan
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
