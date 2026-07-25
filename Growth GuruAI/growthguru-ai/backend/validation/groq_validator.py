from typing import Dict, Any

from groq_client import execute_groq_json_call

def validate_via_groq(business_type: str, headers: list, sample_json: str, row_count: int) -> Dict[str, Any]:
    """
    Stage 3: AI Fallback Validation
    Uses the unified LLM pipeline with fallback logic to determine if the CSV matches the business type.
    """
    system_prompt = """You are an expert semantic business classifier.
Your ONLY task is determining whether the uploaded CSV belongs to the selected business.

RULES:
- Never classify a business from a single product. Use overall context.
- Ignore isolated outlier rows, capitalization, and minor spelling mistakes.
- Prefer conservative classification when confidence is low.

Return STRICT JSON ONLY. Do not wrap the JSON in markdown blocks. No explanations.
Schema:
{
  "match": boolean,
  "confidence": number,
  "selected_business": string,
  "detected_business": string (MUST be one of: "Cafe", "Bakery", "Boutique", "Clothing Store", "Shoe Store", "Salon", "Cosmetic Store", "Electronics Shop", or "Unknown"),
  "reason": string,
  "warnings": [string],
  "recommendation": string,
  "matched_keywords": [string],
  "unexpected_keywords": [string]
}

If confidence is below 70, set reason to exactly: "Unable to confidently determine business category."
"""

    user_prompt = f"""Selected Business: {business_type}
Total Row Count: {row_count}
CSV Headers: {headers}
Representative Sample Rows:
{sample_json}
"""

    result = execute_groq_json_call(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=250,
        temperature=0.1,
        feature_name="CSV Validator"
    )

    if result.get("success"):
        data = result["data"]
        # Ensure schema compliance
        return {
            "match": bool(data.get("match", False)),
            "confidence": int(data.get("confidence", 0)),
            "selected_business": data.get("selected_business", business_type),
            "detected_business": data.get("detected_business", ""),
            "reason": data.get("reason", ""),
            "warnings": data.get("warnings", []),
            "recommendation": data.get("recommendation", ""),
            "matched_keywords": data.get("matched_keywords", []),
            "unexpected_keywords": data.get("unexpected_keywords", [])
        }
    else:
        # Fail gracefully
        error_msg = result.get("error", "AI Validation failed to process the request.")
        return {
            "match": False,
            "confidence": 0,
            "selected_business": business_type,
            "detected_business": "Unknown",
            "reason": error_msg,
            "warnings": [error_msg],
            "recommendation": "Please ensure your CSV is properly formatted."
        }
