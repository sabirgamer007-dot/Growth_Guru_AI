import pandas as pd
from typing import Dict, Any
import time

from .classifier import classify_business
from .sampler import get_representative_sample
from .groq_validator import validate_via_groq
from .cache import validation_cache

def validate_business_alignment(df: pd.DataFrame, business_type: str) -> Dict[str, Any]:
    """
    The Decision Engine orchestrating Stage 2 and Stage 3 validation.
    Returns a unified schema for the frontend.
    """
    start_time = time.time()
    
    # 1. Gather context
    headers = list(df.columns)
    row_count = len(df)
    
    # 2. Stage 2: Local Classifier
    local_result = classify_business(df, business_type)
    confidence = local_result["confidence"]
    
    # Base response scaffold
    response = {
        "match": False,
        "confidence": confidence,
        "selected_business": business_type,
        "detected_business": business_type,
        "reason": "",
        "warnings": [],
        "recommendation": "",
        "matched_keywords": local_result["matched_keywords"],
        "unexpected_keywords": local_result["unexpected_keywords"],
        "confidence_breakdown": local_result.get("confidence_breakdown", {}),
        "groq_used": False,
        "cache_hit": False,
        "processing_time_ms": 0
    }

    # 3. Decision Logic based on Thresholds
    if confidence >= 90:
        # Direct Accept
        response["match"] = True
        response["reason"] = f"Locally verified as {business_type} with high confidence."
        
    elif confidence <= 30:
        # Direct Reject
        response["match"] = False
        response["reason"] = f"Local analysis strongly suggests this dataset does not belong to a {business_type}."
        if local_result["unexpected_keywords"]:
            response["reason"] += f" Found unexpected keywords: {', '.join(local_result['unexpected_keywords'])}."
            
    else:
        # Ambiguous (31-89) -> Stage 3: Groq Fallback
        
        # Build sampler & cache fingerprint
        sample_json = get_representative_sample(df, max_rows=15)
        fingerprint = validation_cache.generate_fingerprint(business_type, headers, sample_json, row_count)
        
        cached_result = validation_cache.get(fingerprint)
        if cached_result:
            # Cache Hit
            response.update(cached_result)
            response["cache_hit"] = True
            response["groq_used"] = False
        else:
            # Cache Miss -> Call Groq
            groq_result = validate_via_groq(business_type, headers, sample_json, row_count)
            
            # Smart Recovery mapping from Groq if match is false but confidence is high for something else
            # (Groq handles this via detected_business)
            
            response.update(groq_result)
            response["groq_used"] = True
            response["cache_hit"] = False
            
            # Save to cache
            validation_cache.set(fingerprint, groq_result)

    # 4. Finalize
    response["processing_time_ms"] = int((time.time() - start_time) * 1000)
    return response
