import { AlertTriangle, ArrowRight, Upload, X } from 'lucide-react';

export default function MismatchModal({ 
  isOpen, 
  onClose, 
  validationData, 
  onChangeBusiness, 
  onUploadAnother, 
  onKeepCurrent 
}) {
  if (!isOpen || !validationData) return null;

  const {
    detected_business,
    selected_business,
    reason,
    confidence,
    groq_used
  } = validationData;

  const isSmartRecovery = confidence >= 95 && detected_business && detected_business !== selected_business;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-surface border border-surface-border rounded-lg shadow-2xl max-w-md w-full overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="flex items-start justify-between p-lg border-b border-surface-border">
          <div className="flex items-center gap-sm">
            <div className="p-xs rounded-full bg-danger/10">
              <AlertTriangle className="w-6 h-6 text-danger" />
            </div>
            <h2 className="text-h2 text-text-main">Data Mismatch Detected</h2>
          </div>
          <button onClick={onClose} className="text-text-muted hover:text-text-main transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-lg space-y-md">
          <div className="space-y-xs">
            <p className="text-body text-text-muted">
              We analyzed your CSV file and found that it does not appear to match your selected business type.
            </p>
            <div className="flex justify-between items-center bg-background p-sm rounded-md text-small">
              <span className="text-text-muted">Selected: <strong className="text-text-main">{selected_business}</strong></span>
              {detected_business && detected_business !== selected_business && (
                <span className="text-primary font-medium">Detected: {detected_business}</span>
              )}
            </div>
          </div>

          <div className="bg-primary/5 border border-primary/20 rounded-button p-sm">
            <p className="text-small text-text-main font-medium mb-xs">Reason:</p>
            <p className="text-small text-text-muted leading-relaxed">{reason}</p>
          </div>

          {isSmartRecovery && (
            <div className="bg-success/10 border border-success/20 rounded-button p-sm">
              <p className="text-small text-success-light">
                <strong>Smart Recovery:</strong> We confidently detected this as a {detected_business}. 
                Would you like to switch your profile automatically and continue?
              </p>
            </div>
          )}
          
          {groq_used && (
            <p className="text-[10px] text-text-muted/50 text-right uppercase tracking-wider">
              Verified by AI
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="p-lg border-t border-surface-border bg-background/50 flex flex-col gap-sm">
          {isSmartRecovery ? (
            <>
              <button 
                onClick={() => onChangeBusiness(detected_business)}
                className="w-full btn btn-primary flex items-center justify-center gap-xs"
              >
                Switch to {detected_business} <ArrowRight className="w-4 h-4" />
              </button>
              <div className="flex gap-sm">
                <button onClick={onUploadAnother} className="flex-1 btn btn-outline flex items-center justify-center gap-xs">
                  <Upload className="w-4 h-4" /> New CSV
                </button>
                <button onClick={onKeepCurrent} className="flex-1 btn btn-outline text-text-muted">
                  Keep Current
                </button>
              </div>
            </>
          ) : (
            <>
              <button onClick={() => onChangeBusiness()} className="w-full btn btn-primary">
                Change Business Type
              </button>
              <button onClick={onUploadAnother} className="w-full btn btn-outline flex items-center justify-center gap-xs">
                <Upload className="w-4 h-4" /> Upload Another CSV
              </button>
            </>
          )}
        </div>

      </div>
    </div>
  );
}
