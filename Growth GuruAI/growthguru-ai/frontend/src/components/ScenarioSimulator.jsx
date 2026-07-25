import { useState } from 'react';
import {
  TrendingUp,
  Activity,
  Users,
  Target,
  Zap,
  Clock,
  ShieldAlert,
  BarChart2,
  Award,
  AlertCircle
} from 'lucide-react';
import { simulateImpact } from '../services/api';

export default function ScenarioSimulator({ fileId, scenarioData, setScenarioData }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  // scenarioData is lifted to App.jsx — it persists across SPA navigation

  const handleSimulate = async () => {
    if (!fileId) return;
    setLoading(true);
    setError(null);
    setScenarioData(null);
    
    try {
      const result = await simulateImpact(fileId);
      if (result.success && result.data) {
        setScenarioData(result.data);
      } else {
        throw new Error(result.error || 'Failed to simulate impact.');
      }
    } catch (err) {
      setError(err.message || 'Failed to generate scenario simulation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!scenarioData && !loading) {
    return (
      <div className="card p-lg mt-lg border-2 border-primary/20 bg-primary/5 flex flex-col items-center justify-center text-center">
        <div className="p-sm rounded-full bg-primary/10 mb-sm">
          <TrendingUp className="w-8 h-8 text-primary" />
        </div>
        <h2 className="text-h2 text-text-main mb-xs">
          GrowthLens™
        </h2>
        <p className="text-body text-text-muted max-w-lg mb-md">
          Discover the potential business impact of implementing your custom growth strategy. 
          Our AI analyzes your strategy to provide conservative, scenario-based estimates.
        </p>
        
        {error && (
          <div className="flex items-start gap-xs p-sm rounded-button bg-danger/10 border border-danger/20 mb-md w-full max-w-lg">
            <AlertCircle className="w-4 h-4 text-danger flex-shrink-0 mt-0.5" />
            <p className="text-small text-danger text-left">{error}</p>
          </div>
        )}

        <button
          className="btn-primary flex items-center gap-xs px-lg py-sm text-base font-semibold"
          onClick={handleSimulate}
        >
          <Activity className="w-5 h-5" />
          Simulate Business Impact
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="card p-lg mt-lg space-y-md animate-pulse border-2 border-primary/10">
        <div className="flex flex-col items-center justify-center py-xl">
          <div className="relative">
            <div className="w-16 h-16 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
            <TrendingUp className="w-6 h-6 text-primary absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
          </div>
          <h3 className="text-h3 text-text-main mt-md">AI is analyzing your business strategy...</h3>
          <p className="text-body text-text-muted mt-xs">Running scenario simulations based on your data</p>
        </div>
        
        <div className="h-4 w-32 bg-text-muted/10 rounded mb-md" />
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-md">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="h-32 bg-text-muted/10 rounded-card" />
          ))}
        </div>
      </div>
    );
  }

  // Helper to map impact keys to UI details
  const getImpactDetails = (key) => {
    const details = {
      customer_reach: { title: "Customer Reach", icon: <Users className="w-5 h-5 text-blue-500" /> },
      customer_engagement: { title: "Customer Engagement", icon: <Activity className="w-5 h-5 text-purple-500" /> },
      sales_conversion: { title: "Sales Conversion", icon: <Target className="w-5 h-5 text-green-500" /> },
      repeat_customers: { title: "Repeat Customers", icon: <Zap className="w-5 h-5 text-orange-500" /> },
      brand_visibility: { title: "Brand Visibility", icon: <Award className="w-5 h-5 text-yellow-500" /> }
    };
    return details[key] || { title: key, icon: <TrendingUp className="w-5 h-5 text-primary" /> };
  };

  const priorityColors = {
    High: "bg-danger/10 text-danger border-danger/20",
    Medium: "bg-warning/10 text-warning border-warning/20",
    Low: "bg-success/10 text-success border-success/20"
  };

  return (
    <div className="card p-lg mt-lg space-y-lg border-2 border-primary/10">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-md pb-md border-b border-border">
        <div className="flex items-center gap-sm">
          <div className="p-sm rounded-full bg-primary/10">
            <TrendingUp className="w-6 h-6 text-primary" />
          </div>
          <div>
            <h2 className="text-h2 text-text-main">GrowthLens™</h2>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-small text-text-muted font-medium flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" /> {scenarioData.estimated_timeframe}
              </span>
              <span className="text-small text-text-muted">•</span>
              <span className="text-small text-text-muted font-medium">
                Confidence: {scenarioData.overall_confidence}
              </span>
            </div>
          </div>
        </div>
        <button
          className="btn-secondary text-small py-1.5 px-3"
          onClick={handleSimulate}
        >
          Recalculate
        </button>
      </div>

      {/* Executive Summary & Highest Impact */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-md">
        <div className="md:col-span-2 bg-bg border border-border rounded-card p-md">
          <h3 className="text-small font-semibold text-text-muted uppercase tracking-wider mb-sm">Executive Summary</h3>
          <p className="text-body text-text-main leading-relaxed">
            {scenarioData.executive_summary}
          </p>
        </div>
        <div className="bg-primary/5 border border-primary/20 rounded-card p-md flex flex-col justify-center">
          <h3 className="text-small font-semibold text-primary uppercase tracking-wider mb-sm flex items-center gap-1">
            <Zap className="w-4 h-4" /> Highest Impact Action
          </h3>
          <p className="text-base font-medium text-text-main">
            {scenarioData.highest_impact_action}
          </p>
        </div>
      </div>

      {/* Impact Cards */}
      <div>
        <h3 className="text-h3 text-text-main mb-md flex items-center gap-xs">
          <BarChart2 className="w-5 h-5 text-text-muted" /> Estimated Impact
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-sm">
          {Object.entries(scenarioData.impact).map(([key, data]) => {
            const { title, icon } = getImpactDetails(key);
            return (
              <div key={key} className="bg-bg border border-border rounded-card p-md hover:border-primary/30 transition-colors">
                <div className="flex items-center justify-between mb-sm">
                  <div className="flex items-center gap-xs">
                    {icon}
                    <span className="font-semibold text-text-main text-small">{title}</span>
                  </div>
                  <span className="font-bold text-lg text-text-main px-2 py-1 bg-primary/10 text-primary rounded-button whitespace-nowrap">
                    {data.range}
                  </span>
                </div>
                <p className="text-small text-text-muted leading-relaxed">
                  {data.reason}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
        {/* Quick Wins */}
        <div>
          <h3 className="text-h3 text-text-main mb-md flex items-center gap-xs">
            <Award className="w-5 h-5 text-text-muted" /> Quick Wins
          </h3>
          <ul className="space-y-sm">
            {scenarioData.quick_wins.map((win, idx) => (
              <li key={idx} className="flex items-start gap-sm bg-bg border border-border p-sm rounded-card">
                <div className="w-6 h-6 rounded-full bg-success/20 text-success flex items-center justify-center flex-shrink-0 text-small font-bold">
                  {idx + 1}
                </div>
                <p className="text-body text-text-main pt-0.5">{win}</p>
              </li>
            ))}
          </ul>
        </div>

        {/* Implementation Priority */}
        <div>
          <h3 className="text-h3 text-text-main mb-md flex items-center gap-xs">
            <Target className="w-5 h-5 text-text-muted" /> Implementation Priority
          </h3>
          <div className="space-y-sm">
            {scenarioData.implementation_priority.map((item, idx) => (
              <div key={idx} className="bg-bg border border-border p-sm rounded-card">
                <div className="flex justify-between items-start mb-xs gap-sm">
                  <h4 className="font-semibold text-text-main text-body leading-tight">{item.title}</h4>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-semibold border flex-shrink-0 ${priorityColors[item.priority] || 'bg-bg text-text-main border-border'}`}>
                    {item.priority}
                  </span>
                </div>
                <p className="text-small text-text-muted">{item.reason}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="bg-text-muted/5 p-sm rounded-card flex items-start gap-sm">
        <ShieldAlert className="w-5 h-5 text-text-muted flex-shrink-0 mt-0.5" />
        <p className="text-small text-text-muted italic leading-relaxed">
          {scenarioData.disclaimer || "These are AI-generated scenario estimates based on the uploaded business information and generated strategy. Actual business outcomes depend on execution quality, market conditions and customer behaviour."}
        </p>
      </div>

    </div>
  );
}
