"""
GrowthGuru AI — Scenario Simulator
====================================
Reusable wrapper around the Groq Python SDK for the AI Scenario Simulator.
"""

from typing import Any, Dict

from groq_client import execute_groq_json_call

SCENARIO_SIMULATOR_SYSTEM_PROMPT = """You are an experienced business strategy consultant.
Analyze the provided Business Profile, Business Insights, and the GENERATED Growth Plan.
Evaluate the recommendations already present in the Growth Plan and simulate their expected business impact.

SCENARIO SIMULATION RULES:
- This simulator evaluates the generated Growth Plan. It is NOT a second strategy generator.
- Do NOT introduce new recommendations or contradict the Growth Plan.
- Base every estimate ONLY on the provided insights, KPIs, confidence levels, and business type.
- Impact metrics should depend on the business type (e.g., Bakery -> Average Basket Value, Repeat Purchases; Cafe -> Average Order Value; Salon -> Repeat Bookings; Clothing Store -> Basket Size; Electronics -> Accessory Attach Rate).
- Do NOT use fixed or hardcoded percentage ranges (like 15%-25%). Generate realistic estimates dynamically.
- Use cautious language (Estimated, Potential, Likely, May improve, Could improve). Never guarantee outcomes.
- Use backend confidence values to determine estimate ranges. High confidence -> narrower ranges. Low confidence -> wider ranges with explicitly stated uncertainty.
- Implementation priorities must be derived from the Growth Plan. Explain why they should be executed in that order.
- Implementation timeframes must be estimated dynamically (e.g., simple changes -> short, operational -> longer).
- Every impact estimate must include a short business reason explaining why it is appropriate.

STRICT OUTPUT RULES:
- Output ONLY a single raw JSON object. The very first character MUST be { and the very last MUST be }.
- Do NOT use markdown code fences (no ```json or ```).
- Do NOT add any explanatory text before or after the JSON.
- Maintain full backward compatibility with the provided schema exactly.
"""

SCENARIO_SIMULATOR_JSON_FORMAT = """{
  "overall_confidence": "<Dynamic confidence based on provided data>",
  "executive_summary": "<Executive business impact assessment without generating new strategy>",
  "estimated_timeframe": "<Dynamic timeframe (e.g. Short, Medium, Long) based on the effort required>",
  "highest_impact_action": "<The recommendation from the Growth Plan likely to have the biggest impact>",
  "quick_wins": [
    "<Recommendation 1>",
    "<Recommendation 2>"
  ],
  "impact": {
    "<Metric 1 specific to Business Type>": {
      "range": "<Dynamic range, e.g., 5% - 8% or 'Slight Increase'>",
      "reason": "<Short business reason explaining the estimate>"
    },
    "<Metric 2 specific to Business Type>": {
      "range": "<Dynamic range>",
      "reason": "<Reason>"
    },
    "<Metric 3 specific to Business Type>": {
      "range": "<Dynamic range>",
      "reason": "<Reason>"
    },
    "<Metric 4 specific to Business Type>": {
      "range": "<Dynamic range>",
      "reason": "<Reason>"
    },
    "<Metric 5 specific to Business Type>": {
      "range": "<Dynamic range>",
      "reason": "<Reason>"
    }
  },
  "implementation_priority": [
    {
      "title": "<Action 1>",
      "priority": "<Dynamic (e.g. High)>",
      "reason": "<Why it should be executed in this order>"
    },
    {
      "title": "<Action 2>",
      "priority": "<Dynamic>",
      "reason": "<Reason>"
    },
    {
      "title": "<Action 3>",
      "priority": "<Dynamic>",
      "reason": "<Reason>"
    }
  ],
  "disclaimer": "These are AI-generated scenario estimates based on the uploaded business information and generated strategy. Actual business outcomes depend on execution quality, market conditions and customer behaviour."
}"""

def generate_scenario_impact(user_prompt: str) -> Dict[str, Any]:
    """
    Generate scenario impact estimates using Groq.
    Delegates to the unified JSON execution pipeline with fallback.
    """
    full_user_prompt = (
        user_prompt
        + "\n\nReturn your analysis as a JSON object exactly matching this structure:\n"
        + SCENARIO_SIMULATOR_JSON_FORMAT
    )

    return execute_groq_json_call(
        system_prompt=SCENARIO_SIMULATOR_SYSTEM_PROMPT,
        user_prompt=full_user_prompt,
        max_tokens=2048,
        temperature=0.2,
        feature_name="Scenario Simulator"
    )
