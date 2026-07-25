/**
 * GrowthGuru AI — AI Growth Coach Screen
 * ========================================
 * Screen 4 per UI/UX spec §8.
 * Displays AI-generated growth plan, product-specific captions, and targeted hashtags.
 * Captions and hashtags are tied to specific products from the sales data.
 */

import { useState, useRef } from 'react';
import {
  Sparkles,
  Copy,
  Check,
  RefreshCw,
  AlertCircle,
  Target,
  MessageSquare,
  Hash,
} from 'lucide-react';
import { generateGrowthPlan, validateBusinessAlignment } from '../services/api';
import MismatchModal from '../components/MismatchModal';
import ScenarioSimulator from '../components/ScenarioSimulator';

export default function GrowthCoachScreen({ businessProfile, setBusinessProfile, kpis, fileId, growthData, setGrowthData, scenarioData, setScenarioData, onNavigate }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [hashtagsCopied, setHashtagsCopied] = useState(false);
  const [validationData, setValidationData] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  /**
   * Generate growth plan via the backend API.
   * Falls back to client-side mock if backend is unavailable.
   */
  const handleGenerate = async () => {
    executeGeneration(businessProfile.businessType);
  };

  const isGeneratingRef = useRef(false);

  const executeGeneration = async (currentBusinessType) => {
    if (isGeneratingRef.current) return;
    isGeneratingRef.current = true;
    setLoading(true);
    setError(null);
    setGrowthData(null);

    try {
      if (!fileId) {
        throw new Error("Missing file data. Please upload your CSV again.");
      }

      // 1. Validate Alignment first
      const valResult = await validateBusinessAlignment(fileId, currentBusinessType);

      if (!valResult.success) {
        throw new Error(valResult.error || "Failed to validate dataset.");
      }

      if (!valResult.data.match) {
        setValidationData(valResult.data);
        setIsModalOpen(true);
        setLoading(false);
        isGeneratingRef.current = false;
        return; // Stop generation
      }

      // 2. Generate Growth Plan if valid
      const result = await generateGrowthPlan(fileId, { ...businessProfile, businessType: currentBusinessType });

      if (result.success && result.data) {
        setGrowthData(result.data);
      } else {
        throw new Error(result.error || 'Failed to generate growth plan from AI.');
      }
    } catch (err) {
      setError(err.message || 'Failed to generate growth plan. Please try again.');
    } finally {
      setLoading(false);
      isGeneratingRef.current = false;
    }
  };

  /**
   * Copy text to clipboard.
   */
  const copyToClipboard = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    }
  };

  /**
   * Copy all hashtags to clipboard.
   */
  const copyAllHashtags = async () => {
    if (!growthData?.hashtags) return;
    const allHashtags = growthData.hashtags.join(' ');
    try {
      await navigator.clipboard.writeText(allHashtags);
      setHashtagsCopied(true);
      setTimeout(() => setHashtagsCopied(false), 2000);
    } catch {
      const textarea = document.createElement('textarea');
      textarea.value = allHashtags;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setHashtagsCopied(true);
      setTimeout(() => setHashtagsCopied(false), 2000);
    }
  };

  /**
   * Render the growth plan text with basic markdown heading support.
   */
  const renderPlanText = (text) => {
    if (!text) return null;

    return text.split('\n').map((line, idx) => {
      const trimmed = line.trim();
      if (trimmed.startsWith('### ')) {
        return (
          <h3 key={idx} className="text-base font-semibold text-text-main mt-md mb-xs first:mt-0">
            {trimmed.replace('### ', '')}
          </h3>
        );
      }
      if (trimmed === '') {
        return <div key={idx} className="h-2" />;
      }
      // Handle inline bold (**text**)
      const parts = trimmed.split(/(\*\*[^*]+\*\*)/g);
      return (
        <p key={idx} className="text-body text-text-muted leading-relaxed">
          {parts.map((part, pIdx) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              return (
                <span key={pIdx} className="text-text-main font-medium">
                  {part.slice(2, -2)}
                </span>
              );
            }
            // Handle inline "quoted text"
            return part.split(/("[^"]+")/g).map((segment, sIdx) => {
              if (segment.startsWith('"') && segment.endsWith('"')) {
                return (
                  <span key={sIdx} className="text-primary font-medium">
                    {segment}
                  </span>
                );
              }
              return segment;
            });
          })}
        </p>
      );
    });
  };

  // Empty state — no KPIs available
  if (!kpis) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-64px-48px)] text-center">
        <Sparkles className="w-12 h-12 text-text-muted mb-sm" />
        <h2 className="text-h2 text-text-main mb-xs">No Data Available</h2>
        <p className="text-body text-text-muted max-w-md">
          Complete your business profile and upload sales data first to generate a personalized
          growth strategy.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-md">
      {/* Header + Action Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-sm">
        <div>
          <h2 className="text-h1 text-text-main">Your Custom Growth Strategy</h2>
          <p className="text-body text-text-muted mt-xxs">
            AI-powered recommendations based on{' '}
            <span className="text-text-main">{businessProfile?.businessName || 'your'}</span>'s sales data.
          </p>
        </div>

        <button
          className="btn-primary flex items-center gap-xs whitespace-nowrap flex-shrink-0"
          onClick={handleGenerate}
          disabled={loading}
        >
          {loading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              Generating...
            </>
          ) : growthData ? (
            <>
              <RefreshCw className="w-4 h-4" />
              Regenerate
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Generate Growth Plan
            </>
          )}
        </button>
      </div>

      {/* Error State */}
      {error && (
        <div className="flex items-start gap-xs p-sm rounded-button bg-danger/10 border border-danger/20">
          <AlertCircle className="w-4 h-4 text-danger flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-small text-danger">{error}</p>
            <button
              className="text-small text-danger underline mt-xxs hover:no-underline"
              onClick={handleGenerate}
            >
              Try again
            </button>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="space-y-md">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card p-lg animate-pulse">
              <div className="h-5 w-48 bg-text-muted/10 rounded mb-md" />
              <div className="space-y-xs">
                <div className="h-3 w-full bg-text-muted/10 rounded" />
                <div className="h-3 w-5/6 bg-text-muted/10 rounded" />
                <div className="h-3 w-4/6 bg-text-muted/10 rounded" />
              </div>
            </div>
          ))}
          <p className="text-center text-body text-text-muted">
            Generating your personalized growth strategy...
          </p>
        </div>
      )}

      {/* Generated Content */}
      {growthData && !loading && (
        <div className="space-y-md">
          {/* Card 1: AI Growth Plan */}
          <div className="card p-lg">
            <div className="flex items-center gap-xs mb-md">
              <div className="p-xs rounded-button bg-primary/10">
                <Target className="w-5 h-5 text-primary" />
              </div>
              <h2 className="text-h2 text-text-main">GrowthEngine™</h2>
            </div>
            <div className="pl-1">
              {renderPlanText(growthData.growth_plan || growthData.plan)}
            </div>
          </div>

          {/* AI Scenario Simulator placed immediately after the Growth Plan summary */}
          <ScenarioSimulator fileId={fileId} scenarioData={scenarioData} setScenarioData={setScenarioData} />

          {/* Card 2: Product-Specific Captions */}
          <div className="card p-lg">
            <div className="flex items-center gap-xs mb-md">
              <div className="p-xs rounded-button bg-secondary/10">
                <MessageSquare className="w-5 h-5 text-secondary" />
              </div>
              <div>
                <h2 className="text-h2 text-text-main">Social Media Captions</h2>
                <p className="text-small text-text-muted mt-xxs">
                  Tailored to promote "{kpis?.bestSeller}" and boost sales of "{kpis?.worstSeller}"
                </p>
              </div>
            </div>

            <div className="space-y-sm">
              {growthData.captions?.map((caption, idx) => (
                <div
                  key={idx}
                  className="bg-bg border border-border rounded-card p-sm group relative"
                >
                  <p className="text-body text-text-main leading-relaxed pr-8">{caption}</p>
                  <button
                    className="absolute top-sm right-sm text-text-muted hover:text-primary transition-colors"
                    onClick={() => copyToClipboard(caption, `caption-${idx}`)}
                    title="Copy caption"
                    aria-label={`Copy caption ${idx + 1}`}
                  >
                    {copiedIndex === `caption-${idx}` ? (
                      <Check className="w-4 h-4 text-primary" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Card 3: Product-Specific Hashtags */}
          <div className="card p-lg">
            <div className="flex items-center justify-between mb-md">
              <div className="flex items-center gap-xs">
                <div className="p-xs rounded-button bg-primary/10">
                  <Hash className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-h2 text-text-main">Hashtag Suggestions</h2>
                  <p className="text-small text-text-muted mt-xxs">
                    Targeted to "{businessProfile?.businessType}" and "{kpis?.bestSeller}"
                  </p>
                </div>
              </div>
              <button
                className="btn-secondary text-small flex items-center gap-xxs py-1.5 px-3"
                onClick={copyAllHashtags}
                aria-label="Copy all hashtags"
              >
                {hashtagsCopied ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-primary" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    Copy All
                  </>
                )}
              </button>
            </div>

            <div className="flex flex-wrap gap-xs">
              {growthData.hashtags?.map((tag, idx) => (
                <button
                  key={idx}
                  className="bg-bg border border-border rounded-button px-sm py-xs text-body text-primary
                             hover:bg-primary/5 hover:border-primary/30 transition-colors cursor-pointer"
                  onClick={() => copyToClipboard(tag, `hashtag-${idx}`)}
                  title={`Copy ${tag}`}
                >
                  {copiedIndex === `hashtag-${idx}` ? (
                    <span className="text-primary flex items-center gap-xxs">
                      <Check className="w-3 h-3" /> Copied
                    </span>
                  ) : (
                    tag
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Initial state — no data generated yet, button not clicked */}
      {!growthData && !loading && !error && (
        <div className="card p-xl flex flex-col items-center justify-center text-center">
          <Sparkles className="w-16 h-16 text-primary/30 mb-md" />
          <h2 className="text-h2 text-text-main mb-xs">
            Your Growth Strategy Awaits
          </h2>
          <p className="text-body text-text-muted max-w-md mb-md">
            Click "Generate Growth Plan" above to get AI-powered growth recommendations,
            product-specific social media captions for "{kpis?.bestSeller}", and targeted hashtags
            for your {businessProfile?.businessType || 'business'}.
          </p>
          <div className="flex flex-wrap justify-center gap-xs text-small text-text-muted">
            <span className="bg-bg border border-border rounded-button px-sm py-xxs">
              📈 3-Step Growth Strategy
            </span>
            <span className="bg-bg border border-border rounded-button px-sm py-xxs">
              📝 Product-Specific Captions
            </span>
            <span className="bg-bg border border-border rounded-button px-sm py-xxs">
              #️⃣ Targeted Hashtags
            </span>
          </div>
        </div>
      )}

      <MismatchModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        validationData={validationData}
        onChangeBusiness={(newType) => {
          setIsModalOpen(false);
          if (newType) {
            setBusinessProfile(prev => ({ ...prev, businessType: newType }));
            executeGeneration(newType); // Smart Recovery auto-continue
          } else {
            onNavigate('home');
          }
        }}
        onUploadAnother={() => {
          setIsModalOpen(false);
          onNavigate('upload');
        }}
        onKeepCurrent={() => {
          setIsModalOpen(false);
        }}
      />
    </div>
  );
}
