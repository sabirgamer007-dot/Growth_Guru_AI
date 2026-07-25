/**
 * GrowthGuru AI — Home Screen (Business Profile)
 * ================================================
 * Screen 1 per UI/UX spec §8.
 * Centered single-column form card (max-width 600px).
 * Captures: Business Name, Type (dropdown), Target Audience, Goals.
 */

import { useState } from 'react';
import { Building2, ArrowRight } from 'lucide-react';

const BUSINESS_TYPES = [
  'Cafe',
  'Bakery',
  'Boutique',
  'Clothing Store',
  'Shoe Store',
  'Salon',
  'Cosmetic Store',
  'Electronics Shop',
];

export default function HomeScreen({ businessProfile, setBusinessProfile, onContinue }) {
  const [errors, setErrors] = useState({});

  const handleChange = (field, value) => {
    setBusinessProfile((prev) => ({ ...prev, [field]: value }));
    // Clear error on change
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!businessProfile.businessName?.trim()) {
      newErrors.businessName = 'Business name is required.';
    }
    if (!businessProfile.businessType) {
      newErrors.businessType = 'Please select a business type.';
    }
    if (!businessProfile.targetAudience?.trim()) {
      newErrors.targetAudience = 'Target audience is required.';
    }
    if (!businessProfile.businessGoals?.trim()) {
      newErrors.businessGoals = 'Business goals are required.';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      onContinue();
    }
  };

  return (
    <div className="flex items-start justify-center min-h-[calc(100vh-64px-48px)]">
      <div className="w-full max-w-[600px]">
        <div className="card p-lg">
          {/* Header */}
          <div className="flex items-center gap-xs mb-lg">
            <div className="p-xs rounded-button bg-primary/10">
              <Building2 className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h2 className="text-h2 text-text-main">Tell us about your business</h2>
              <p className="text-body text-text-muted mt-xxs">
                This helps our AI tailor growth strategies specifically for you.
              </p>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-md" noValidate>
            {/* Business Name */}
            <div>
              <label htmlFor="businessName" className="label">
                Business Name
              </label>
              <input
                id="businessName"
                type="text"
                className={`input ${errors.businessName ? 'border-danger' : ''}`}
                placeholder="e.g., Urban Edge Boutique"
                value={businessProfile.businessName || ''}
                onChange={(e) => handleChange('businessName', e.target.value)}
                maxLength={500}
              />
              {errors.businessName && (
                <p className="text-small text-danger mt-xxs">{errors.businessName}</p>
              )}
            </div>

            {/* Business Type */}
            <div>
              <label htmlFor="businessType" className="label">
                Business Type
              </label>
              <select
                id="businessType"
                className={`input appearance-none ${errors.businessType ? 'border-danger' : ''} ${
                  !businessProfile.businessType ? 'text-text-muted' : ''
                }`}
                value={businessProfile.businessType || ''}
                onChange={(e) => handleChange('businessType', e.target.value)}
              >
                <option value="">Select your business type</option>
                {BUSINESS_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
              {errors.businessType && (
                <p className="text-small text-danger mt-xxs">{errors.businessType}</p>
              )}
            </div>

            {/* Target Audience */}
            <div>
              <label htmlFor="targetAudience" className="label">
                Target Audience
              </label>
              <input
                id="targetAudience"
                type="text"
                className={`input ${errors.targetAudience ? 'border-danger' : ''}`}
                placeholder="e.g., Gen Z and Millennials, working professionals"
                value={businessProfile.targetAudience || ''}
                onChange={(e) => handleChange('targetAudience', e.target.value)}
                maxLength={500}
              />
              {errors.targetAudience && (
                <p className="text-small text-danger mt-xxs">{errors.targetAudience}</p>
              )}
            </div>

            {/* Business Goals */}
            <div>
              <label htmlFor="businessGoals" className="label">
                Business Goals
              </label>
              <textarea
                id="businessGoals"
                className={`input resize-none ${errors.businessGoals ? 'border-danger' : ''}`}
                rows={4}
                placeholder="e.g., Increase weekend foot traffic and boost social media engagement."
                value={businessProfile.businessGoals || ''}
                onChange={(e) => handleChange('businessGoals', e.target.value)}
                maxLength={500}
              />
              {errors.businessGoals && (
                <p className="text-small text-danger mt-xxs">{errors.businessGoals}</p>
              )}
            </div>

            {/* Submit */}
            <button type="submit" className="btn-primary w-full flex items-center justify-center gap-xs">
              Continue
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
