/**
 * GrowthGuru AI — Upload CSV Screen
 * ====================================
 * Screen 2 per UI/UX spec §8.
 * Centered card with drag-and-drop area + "Use sample data" link.
 * Validates: .csv extension, max 5MB.
 * Parses CSV in-browser and calculates KPIs.
 */

import { useState, useRef, useCallback } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, ArrowRight } from 'lucide-react';
import { parseCSV, calculateKPIs, validateCSVHeaders } from '../utils/csvParser';
import { uploadCSV, validateBusinessAlignment } from '../services/api';
import MismatchModal from '../components/MismatchModal';

export default function UploadScreen({ businessProfile, setBusinessProfile, onDataReady, onNavigate }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [validationData, setValidationData] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [pendingData, setPendingData] = useState(null);
  const fileInputRef = useRef(null);

  const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB per API spec §4

  /**
   * Validate the selected file.
   */
  const validateFile = (file) => {
    if (!file.name.endsWith('.csv')) {
      return 'Invalid file type. Please upload a .csv file.';
    }
    if (file.size > MAX_FILE_SIZE) {
      return 'File size exceeds 5MB limit. Please upload a smaller file.';
    }
    return null;
  };

  /**
   * Process the CSV file: read, parse, calculate KPIs.
   */
  const processFile = useCallback(async (file) => {
    setError(null);
    setLoading(true);
    setSuccess(false);

    try {
      const text = await file.text();
      const { headers, rows } = parseCSV(text);

      // Validate required columns
      const validation = validateCSVHeaders(headers);
      if (!validation.valid) {
        throw new Error(`Missing required columns: ${validation.missing.join(', ')}`);
      }

      const uploadResult = await uploadCSV(file);
      if (!uploadResult.success) {
        throw new Error(uploadResult.error || "Failed to upload to backend");
      }
      const fileId = uploadResult.data.file_id;

      // Validate Alignment
      const valResult = await validateBusinessAlignment(fileId, businessProfile?.businessType);
      
      if (!valResult.success) {
        throw new Error(valResult.error || "Failed to validate dataset.");
      }

      const kpis = calculateKPIs(rows);
      const readyData = { rawRows: rows, kpis, headers, fileId };

      if (!valResult.data.match) {
        setValidationData(valResult.data);
        setPendingData(readyData);
        setIsModalOpen(true);
        setLoading(false);
        return; // Don't proceed to dashboard yet
      }

      setSuccess(true);
      setLoading(false);

      // Small delay so user sees the success state
      setTimeout(() => {
        onDataReady(readyData);
      }, 600);
    } catch (err) {
      setError(err.message || 'Failed to parse CSV file.');
      setLoading(false);
    }
  }, [onDataReady, businessProfile]);

  /**
   * Handle file selection (input or drop).
   */
  const handleFile = (file) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      setSelectedFile(null);
      return;
    }
    setError(null);
    setSelectedFile(file);
  };

  /**
   * Handle file input change.
   */
  const handleInputChange = (e) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  /**
   * Handle drag events.
   */
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  };

  /**
   * Handle "Upload CSV" button click — process the selected file.
   */
  const handleUpload = () => {
    if (selectedFile) {
      processFile(selectedFile);
    }
  };

  /**
   * Load sample data from public/sample_data.csv.
   */
  const handleUseSampleData = async () => {
    setError(null);
    setLoading(true);
    setSelectedFile(null);
    setSuccess(false);

    try {
      const response = await fetch('/sample_data.csv');
      if (!response.ok) throw new Error('Failed to load sample data.');
      const text = await response.text();
      const { headers, rows } = parseCSV(text);
      
      const blob = new Blob([text], { type: 'text/csv' });
      const file = new File([blob], 'sample_data.csv', { type: 'text/csv' });
      const uploadResult = await uploadCSV(file);
      if (!uploadResult.success) {
        throw new Error(uploadResult.error || "Failed to upload to backend");
      }
      const fileId = uploadResult.data.file_id;

      // Validate Alignment
      const valResult = await validateBusinessAlignment(fileId, businessProfile?.businessType);
      
      if (!valResult.success) {
        throw new Error(valResult.error || "Failed to validate dataset.");
      }

      const kpis = calculateKPIs(rows);
      const readyData = { rawRows: rows, kpis, headers, fileId };

      if (!valResult.data.match) {
        setValidationData(valResult.data);
        setPendingData(readyData);
        setIsModalOpen(true);
        setLoading(false);
        return; // Don't proceed to dashboard yet
      }

      setSuccess(true);
      setLoading(false);

      setTimeout(() => {
        onDataReady(readyData);
      }, 600);
    } catch (err) {
      setError(err.message || 'Failed to load sample data.');
      setLoading(false);
    }
  };

  return (
    <div className="flex items-start justify-center min-h-[calc(100vh-64px-48px)]">
      <div className="w-full max-w-[600px]">
        <div className="card p-lg">
          {/* Header */}
          <div className="flex items-center gap-xs mb-lg">
            <div className="p-xs rounded-button bg-primary/10">
              <Upload className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h2 className="text-h2 text-text-main">Upload Sales Data</h2>
              <p className="text-body text-text-muted mt-xxs">
                Upload your sales CSV file to generate insights and analytics.
              </p>
            </div>
          </div>

          {/* Drag & Drop Zone */}
          <div
            className={`
              border-2 border-dashed rounded-card p-xl
              flex flex-col items-center justify-center text-center
              transition-colors duration-200 cursor-pointer
              ${dragActive
                ? 'border-primary bg-primary/5'
                : error
                  ? 'border-danger/50'
                  : success
                    ? 'border-primary/50 bg-primary/5'
                    : 'border-border hover:border-text-muted/30'
              }
            `}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            role="button"
            tabIndex={0}
            aria-label="Drop CSV file here or click to browse"
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                fileInputRef.current?.click();
              }
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              className="hidden"
              onChange={handleInputChange}
              aria-hidden="true"
            />

            {loading ? (
              <>
                <div className="w-10 h-10 border-2 border-primary border-t-transparent rounded-full animate-spin mb-sm" />
                <p className="text-body text-text-muted">Processing your data...</p>
              </>
            ) : success ? (
              <>
                <CheckCircle className="w-10 h-10 text-primary mb-sm" />
                <p className="text-body text-primary font-medium">Data processed successfully!</p>
                <p className="text-small text-text-muted mt-xxs">Redirecting to dashboard...</p>
              </>
            ) : selectedFile ? (
              <>
                <FileText className="w-10 h-10 text-primary mb-sm" />
                <p className="text-body text-text-main font-medium">{selectedFile.name}</p>
                <p className="text-small text-text-muted mt-xxs">
                  {(selectedFile.size / 1024).toFixed(1)} KB — Ready to upload
                </p>
              </>
            ) : (
              <>
                <Upload className="w-10 h-10 text-text-muted mb-sm" />
                <p className="text-body text-text-main font-medium">
                  Drag and drop your CSV file here
                </p>
                <p className="text-small text-text-muted mt-xxs">
                  or click to browse. Maximum file size: 5MB
                </p>
              </>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-start gap-xs mt-sm p-sm rounded-button bg-danger/10 border border-danger/20">
              <AlertCircle className="w-4 h-4 text-danger flex-shrink-0 mt-0.5" />
              <p className="text-small text-danger">{error}</p>
            </div>
          )}

          {/* Actions */}
          <div className="mt-md space-y-sm">
            {/* Upload button */}
            <button
              className="btn-secondary w-full flex items-center justify-center gap-xs"
              onClick={handleUpload}
              disabled={!selectedFile || loading || success}
            >
              <Upload className="w-4 h-4" />
              Upload CSV
            </button>

            {/* Divider */}
            <div className="flex items-center gap-sm">
              <div className="flex-1 h-px bg-border" />
              <span className="text-small text-text-muted">or</span>
              <div className="flex-1 h-px bg-border" />
            </div>

            {/* Sample data link */}
            <button
              className="w-full text-center text-body text-primary hover:text-primary-hover transition-colors underline underline-offset-2 disabled:opacity-50"
              onClick={handleUseSampleData}
              disabled={loading || success}
            >
              Use sample data
            </button>
          </div>

          {/* CSV Format Hint */}
          <div className="mt-md p-sm rounded-button bg-bg border border-border">
            <p className="text-small text-text-muted">
              <span className="font-medium text-text-main">Required columns:</span>{' '}
              Product_Name, Quantity_Sold (or Quantity), Revenue (or Total_Revenue)
            </p>
          </div>
        </div>
      </div>

      <MismatchModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        validationData={validationData}
        onChangeBusiness={(newType) => {
          setIsModalOpen(false);
          if (newType) {
            setBusinessProfile(prev => ({ ...prev, businessType: newType }));
            setSuccess(true);
            setTimeout(() => {
              onDataReady(pendingData);
            }, 600);
          } else {
            onNavigate('home');
          }
        }}
        onUploadAnother={() => {
          setIsModalOpen(false);
          setSelectedFile(null);
          setPendingData(null);
          setError(null);
        }}
        onKeepCurrent={() => {
          setIsModalOpen(false);
        }}
      />
    </div>
  );
}
