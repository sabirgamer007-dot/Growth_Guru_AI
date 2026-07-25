/**
 * GrowthGuru AI — API Service Layer
 * ====================================
 * Centralized API client using axios.
 * All backend communication goes through this module.
 *
 * Endpoints used by the frontend:
 *   POST /upload                — Upload CSV file; returns file_id
 *   POST /validate-alignment    — Validate CSV matches selected business type
 *   POST /generate-growth-plan  — Generate AI growth plan + captions + hashtags
 *   POST /simulate-impact       — Generate GrowthLens scenario simulation
 *   POST /analyze               — (available) Aggregate KPIs server-side; KPIs are also
 *                                  computed client-side via csvParser.js
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60s — Groq generation can take time
});

/**
 * Upload a CSV file to the backend.
 *
 * @param {File} file - The CSV File object from the input
 * @returns {Promise<{ success: boolean, data: { file_id: string } | null, error: string | null }>}
 */
export async function uploadCSV(file) {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    return {
      success: true,
      data: response.data,
      error: null,
    };
  } catch (error) {
    return {
      success: false,
      data: null,
      error: extractErrorMessage(error),
    };
  }
}

/**
 * Analyze uploaded CSV data and retrieve KPIs.
 *
 * @param {string} fileId - The file_id returned by /upload
 * @returns {Promise<{ success: boolean, data: Object | null, error: string | null }>}
 */
export async function analyzeData(fileId) {
  try {
    const response = await apiClient.post('/analyze', { file_id: fileId });

    return {
      success: true,
      data: response.data.data,
      error: null,
    };
  } catch (error) {
    return {
      success: false,
      data: null,
      error: extractErrorMessage(error),
    };
  }
}

/**
 * Generate AI growth plan, captions, and hashtags.
 *
 * @param {string} fileId - The file_id from /upload
 * @param {{ businessName: string, businessType: string, targetAudience: string, businessGoals: string }} businessProfile
 * @returns {Promise<{ success: boolean, data: Object | null, error: string | null }>}
 */
export async function generateGrowthPlan(fileId, businessProfile) {
  try {
    const response = await apiClient.post('/generate-growth-plan', {
      file_id: fileId,
      business_profile: {
        business_name: businessProfile.businessName,
        business_type: businessProfile.businessType,
        target_audience: businessProfile.targetAudience,
        business_goals: businessProfile.businessGoals,
      },
    });

    return {
      success: true,
      data: response.data.data,
      error: null,
    };
  } catch (error) {
    return {
      success: false,
      data: null,
      error: extractErrorMessage(error),
    };
  }
}

// Variable to track the active validation request
let activeValidationPromise = null;

/**
 * Validate if the uploaded CSV matches the selected business type.
 * Includes deduplication to prevent double-firing.
 *
 * @param {string} fileId - The file_id from /upload
 * @param {string} businessType - The selected business type
 * @returns {Promise<{ success: boolean, data: Object | null, error: string | null }>}
 */
export async function validateBusinessAlignment(fileId, businessType) {
  // 1. If a request is already in progress, return that exact same promise
  if (activeValidationPromise) {
    console.log("Validation already in progress. Preventing double-fire.");
    return activeValidationPromise;
  }

  // 2. Otherwise, start a new request and store the promise
  activeValidationPromise = (async () => {
    try {
      const response = await apiClient.post('/validate-alignment', {
        file_id: fileId,
        business_type: businessType,
      });

      return {
        success: true,
        data: response.data.data,
        error: null,
      };
    } catch (error) {
      return {
        success: false,
        data: null,
        error: extractErrorMessage(error),
      };
    } finally {
      // 3. Always clear the tracker when the request finishes (success or fail)
      activeValidationPromise = null;
    }
  })();

  return activeValidationPromise;
}

/**
 * Simulate the business impact of the generated growth plan.
 *
 * @param {string} fileId - The file_id from /upload
 * @returns {Promise<{ success: boolean, data: Object | null, error: string | null }>}
 */
export async function simulateImpact(fileId) {
  try {
    const response = await apiClient.post('/simulate-impact', {
      file_id: fileId,
    });

    return {
      success: true,
      data: response.data.data,
      error: null,
    };
  } catch (error) {
    return {
      success: false,
      data: null,
      error: extractErrorMessage(error),
    };
  }
}

/**
 * Extract a human-readable error message from an axios error.
 *
 * @param {Error} error
 * @returns {string}
 */
function extractErrorMessage(error) {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred. Please try again.';
}
