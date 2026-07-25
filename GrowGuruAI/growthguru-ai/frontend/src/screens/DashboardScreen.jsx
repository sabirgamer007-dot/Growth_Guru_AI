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

  /**
   * Generate dynamic, consultant-quality business insights from product data.
   * Produces up to 5 insights covering: market leader acknowledgment,
   * growth opportunities, revenue concentration risk, underperformer
   * assessment, and category strategy.
   */
  const generateInsights = () => {
    if (!kpis || !productData || productData.length === 0) return [];

    const insights = [];
    const totalRevenue = kpis.totalRevenue || 0;

    // --- Insight 1: Best seller acknowledgment (NOT a promotion recommendation) ---
    if (productData.length > 0 && totalRevenue > 0) {
      const topProduct = productData[0];
      const percentage = ((topProduct.revenue / totalRevenue) * 100).toFixed(0);
      insights.push({
        icon: TrendingUp,
        text: `"${topProduct.name}" is your market leader, contributing ${percentage}% of total revenue. It's performing well — no additional marketing spend needed here.`,
        type: 'positive',
      });
    }

    // --- Insight 2: Medium performer growth opportunity ---
    if (productData.length > 2) {
      const midProducts = productData.slice(1, -1);
      const midRevenue = midProducts.reduce((sum, p) => sum + p.revenue, 0);
      const midPercentage = ((midRevenue / totalRevenue) * 100).toFixed(0);
      const topMid = midProducts[0];
      insights.push({
        icon: Package,
        text: `Growth opportunity: ${midProducts.length} mid-tier product${midProducts.length > 1 ? 's' : ''} generate${midProducts.length === 1 ? 's' : ''} ${midPercentage}% of revenue. "${topMid.name}" has the highest untapped potential — consider targeted campaigns, bundles, or seasonal promotions.`,
        type: 'neutral',
      });
    }

    // --- Insight 3: Revenue concentration risk ---
    if (productData.length > 1 && totalRevenue > 0) {
      const topProduct = productData[0];
      const topPercentage = (topProduct.revenue / totalRevenue) * 100;
      if (topPercentage > 50) {
        insights.push({
          icon: AlertTriangle,
          text: `Revenue concentration risk: "${topProduct.name}" accounts for ${topPercentage.toFixed(0)}% of revenue. Diversifying sales across more products would reduce business vulnerability.`,
          type: 'warning',
        });
      } else {
        insights.push({
          icon: BarChart3,
          text: `Healthy revenue diversification — no single product exceeds 50% of total revenue. Focus on lifting mid-tier performers to accelerate overall growth.`,
          type: 'positive',
        });
      }
    }

    // --- Insight 4: Underperformer assessment ---
    if (productData.length > 1) {
      const worstProduct = productData[productData.length - 1];
      const worstPercentage = totalRevenue > 0 ? ((worstProduct.revenue / totalRevenue) * 100).toFixed(1) : '0';
      insights.push({
        icon: TrendingDown,
        text: `"${worstProduct.name}" contributes only ${worstPercentage}% of revenue (₹${worstProduct.revenue.toLocaleString('en-IN')}). Consider bundling it with your best seller or running a limited-time discount to test demand.`,
        type: 'warning',
      });
    }

    // --- Insight 5: Category strategy ---
    if (productData.length >= 3) {
      const categories = [...new Set(productData.map((p) => p.category).filter(Boolean))];
      if (categories.length > 1) {
        insights.push({
          icon: Lightbulb,
          text: `You operate across ${categories.length} categories (${categories.slice(0, 3).join(', ')}${categories.length > 3 ? '…' : ''}). Cross-category bundles and upselling between categories could significantly increase average order value.`,
          type: 'neutral',
        });
      } else {
        insights.push({
          icon: Lightbulb,
          text: `All ${productData.length} products are in the same category. Introducing a complementary product line could attract new customer segments and reduce revenue concentration risk.`,
          type: 'neutral',
        });
      }
    }

    return insights;
  };

  const insights = generateInsights();

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

          {insights.length > 0 ? (
            <ul className="space-y-sm">
              {insights.map((insight, idx) => {
                const InsightIcon = insight.icon;
                return (
                  <li key={idx} className="flex items-start gap-xs">
                    <div
                      className={`p-xxs rounded-button flex-shrink-0 mt-0.5 ${
                        insight.type === 'positive'
                          ? 'bg-primary/10'
                          : insight.type === 'warning'
                            ? 'bg-secondary/10'
                            : 'bg-text-muted/10'
                      }`}
                    >
                      <InsightIcon
                        className={`w-4 h-4 ${
                          insight.type === 'positive'
                            ? 'text-primary'
                            : insight.type === 'warning'
                              ? 'text-secondary'
                              : 'text-text-muted'
                        }`}
                      />
                    </div>
                    <p className="text-body text-text-muted leading-relaxed">{insight.text}</p>
                  </li>
                );
              })}
            </ul>
          ) : (
            <p className="text-body text-text-muted">
              Upload more data to unlock detailed insights.
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
