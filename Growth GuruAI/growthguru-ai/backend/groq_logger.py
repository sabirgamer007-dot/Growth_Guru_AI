import time
import uuid
import groq.resources.chat.completions

original_create = groq.resources.chat.completions.Completions.create

def count_tokens(text):
    if isinstance(text, int):
        return text // 4
    if not text:
        return 0
    return len(str(text)) // 4

def intercepted_create(self, **kwargs):
    messages = kwargs.get("messages", [])
    max_tokens = kwargs.get("max_tokens", 0)
    
    import inspect
    stack = inspect.stack()
    feature_name = "Unknown"
    python_file = "Unknown"
    function_name = "Unknown"
    
    for frame_info in stack:
        filename = frame_info.filename
        if "groq_client.py" in filename and "generate_growthguru_response" in frame_info.function:
            feature_name = "Growth Plan"
            python_file = "groq_client.py"
            function_name = frame_info.function
            break
        elif "scenario_simulator.py" in filename:
            feature_name = "Scenario Simulator"
            python_file = "scenario_simulator.py"
            function_name = frame_info.function
            break
        elif "groq_validator.py" in filename:
            feature_name = "CSV Validator"
            python_file = "groq_validator.py"
            function_name = frame_info.function
            break

    system_prompt = ""
    user_prompt = ""
    history_chars = 0
    
    print("\n==================================================")
    print(f"REQUEST ID: {uuid.uuid4().hex[:8]}")
    print(f"Timestamp: {time.time()}")
    print(f"Feature Name: {feature_name}")
    print(f"Python File: {python_file}")
    print(f"Function Name: {function_name}")
    print()

    for i, msg in enumerate(messages):
        role = msg.get("role", "")
        content = str(msg.get("content", ""))
        
        if role == "system":
            system_prompt += content
        elif role == "user":
            user_prompt += content
        elif role == "assistant":
            history_chars += len(content)

        print(f"Message {i+1}")
        print(f"Role: {role}")
        print(f"Characters: {len(content)}")
        print(f"Estimated Tokens: {count_tokens(content)}")
        print()

    business_insights_chars = 0
    csv_chars = 0
    additional_context_chars = 0
    
    if "Business Insights:" in user_prompt:
        parts = user_prompt.split("Business Insights:")
        additional_context_chars += len(parts[0])
        rest = parts[1]
        
        if "Available Product Names:" in rest:
            bi_part, rest = rest.split("Available Product Names:")
            business_insights_chars = len(bi_part)
            
            if "Sample Data:" in rest:
                prod_part, rest = rest.split("Sample Data:")
                additional_context_chars += len(prod_part)
                
                if "TASK" in rest:
                    csv_part, rest = rest.split("TASK")
                    csv_chars = len(csv_part)
                    additional_context_chars += len(rest)
    
    print(f"System Prompt Characters\n{len(system_prompt)}")
    print(f"System Prompt Estimated Tokens\n{count_tokens(system_prompt)}")
    print()
    print(f"User Prompt Characters\n{len(user_prompt)}")
    print(f"User Prompt Estimated Tokens\n{count_tokens(user_prompt)}")
    print()
    print(f"Business Summary Characters\n{business_insights_chars}")
    print(f"Business Summary Estimated Tokens\n{count_tokens(business_insights_chars)}")
    print()
    print(f"CSV Characters\n{csv_chars}")
    print(f"CSV Estimated Tokens\n{count_tokens(csv_chars)}")
    print()
    print(f"Conversation History Characters\n{history_chars}")
    print(f"Conversation History Estimated Tokens\n{count_tokens(history_chars)}")
    print()
    print(f"Additional Context Characters\n{additional_context_chars}")
    print(f"Additional Context Estimated Tokens\n{count_tokens(additional_context_chars)}")
    print()
    
    total_chars = len(system_prompt) + len(user_prompt) + history_chars
    print(f"TOTAL INPUT CHARACTERS\n{total_chars}")
    print(f"TOTAL ESTIMATED INPUT TOKENS\n{count_tokens(total_chars)}")
    print()
    print(f"Configured max_completion_tokens\n{max_tokens}")
    print("==================================================\n")

    sizes = {
        "System Prompt": len(system_prompt),
        "Business Summary": business_insights_chars,
        "Available Products List (Additional)": (additional_context_chars if "Available Product Names" in user_prompt else 0),
        "Sample Data (CSV)": csv_chars,
    }
    
    largest_key = max(sizes, key=sizes.get)
    largest_val = sizes[largest_key]
    percentage = (largest_val / total_chars) * 100 if total_chars > 0 else 0
    print(f"Largest contributor: {largest_key}")
    print(f"Percentage of total tokens: {percentage:.1f}%\n")
    
    print("--- Duplicate Context Detection ---")
    if "Business Insights:" in user_prompt and "Business Insights:" in system_prompt:
        print("Business Summary is duplicated in System and User prompts.")
    else:
        print("No duplicate context detected between system and user prompts.")

    # Call the actual Groq API!
    return original_create(self, **kwargs)

# Apply Monkey Patch
groq.resources.chat.completions.Completions.create = intercepted_create
print(">>> Groq API Token Forensic Logger Active <<<")
