import json
import re
from typing import Any

def extract_and_parse_json(response_text: str) -> Any:
    import json
    import re
    
    text = response_text.strip()
    
    # 1. Fast path for clean responses
    clean_text = text
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()
    
    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        pass

    # 2. Try to extract markdown block anywhere
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Aggressive search for JSON object using a stack to find balanced braces
    start = -1
    stack = 0
    for i, char in enumerate(response_text):
        if char == '{':
            if stack == 0:
                start = i
            stack += 1
        elif char == '}':
            stack -= 1
            if stack == 0 and start != -1:
                candidate = response_text[start:i+1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    pass # Keep looking
                start = -1 # Reset after finding a balanced pair

    # 4. Fallback to greedy regex requested by user
    match = re.search(r'\{[\s\S]*\}', response_text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
            
    return None

test_strings = [
    """Here is the output { wait what? }:
```json
{
    "plan": "Test"
}
```
Thanks!""",
    """Some text
{
    "plan": "Test"
}
Some other text {that breaks}
"""
]

for i, s in enumerate(test_strings):
    res = extract_and_parse_json(s)
    print(f"Test {i}: {'SUCCESS' if res else 'FAILED'} - {res}")
