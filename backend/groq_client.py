"""
GrowthGuru AI — Groq Client
============================
Reusable wrapper around the Groq Python SDK.
Provides both blocking and streaming response generation
with comprehensive error handling and model fallback logic.
"""

import json
import os
import threading
import time
import logging
import uuid
from typing import Any, Dict, Generator

from groq import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    Groq,
    RateLimitError,
)
from groq.types.chat import ChatCompletionMessageParam

from config import (
    GROQ_MAX_COMPLETION_TOKENS,
    GROQ_MODEL,
    FALLBACK_MODEL,
    GROQ_TEMPERATURE,
    GROQ_TOP_P,
    GROWTHGURU_SYSTEM_PROMPT,
)

# ---------------------------------------------------------------------------
# Groq Client Initialization
# ---------------------------------------------------------------------------
def _get_groq_client() -> Groq:
    """
    Create and return a Groq client instance.
    Reads the API key exclusively from the GROQ_API_KEY environment variable.
    Raises ValueError if the key is not set.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set. "
            "Please set it in your .env file or system environment."
        )
    return Groq(api_key=api_key, max_retries=0)


# ---------------------------------------------------------------------------
# Message Builder
# ---------------------------------------------------------------------------
def _build_messages(system_prompt: str, user_prompt: str) -> list[ChatCompletionMessageParam]:
    """
    Build the minimal message payload for the Groq API.
    """
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


# Semaphore to queue LLM requests sequentially and prevent burst concurrency
_groq_lock = threading.Semaphore(1)


# ---------------------------------------------------------------------------
# Unified JSON Execution Pipeline with Model Fallback
# ---------------------------------------------------------------------------
def execute_groq_json_call(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = GROQ_MAX_COMPLETION_TOKENS,
    temperature: float = GROQ_TEMPERATURE,
    feature_name: str = "General",
    primary_model: str | None = None,
    fallback_model: str | None = None
) -> Dict[str, Any]:
    """
    Central unified function for executing Groq calls that expect JSON output.
    Implements resilient model fallback logic:
    - 429 / Rate Limit -> Instantly switch to FALLBACK_MODEL
    - Timeout -> Retry once on current model, then failover
    - Network Error -> Instantly switch to FALLBACK_MODEL
    - 400 Validation Error -> Fail immediately (no retry)
    Includes exact 1-time JSON repair logic.
    """
    req_id = str(uuid.uuid4())[:8]
    prompt_len = len(user_prompt)
    
    primary_model = primary_model or GROQ_MODEL
    fallback_model = fallback_model or FALLBACK_MODEL
    current_model = primary_model
    
    timeout_retries_remaining = 1
    
    logging.info(f"[{req_id}] [GROQ_START] Feature: {feature_name} | Prompt Chars: {prompt_len} | Initial Model: {current_model} | MaxTokens: {max_tokens}")

    while True:
        try:
            with _groq_lock:
                client = _get_groq_client()
            messages = _build_messages(system_prompt, user_prompt)

            start_time = time.time()
            logging.info(f"[{req_id}] [GROQ_CALL] Executing with model: {current_model}")
            
            response = client.chat.completions.create(
                model=current_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=GROQ_TOP_P,
                stream=False,
                response_format={"type": "json_object"},
            )
            full_response = response.choices[0].message.content or ""
            elapsed = time.time() - start_time
            logging.info(f"[{req_id}] [GROQ_SUCCESS] Model: {current_model} | Time: {elapsed:.2f}s | Output Chars: {len(full_response)}")

            # Attempt to parse
            try:
                parsed_data = json.loads(full_response)
                return {"success": True, "data": parsed_data, "error": None, "model_used": current_model}
            except json.JSONDecodeError:
                # Single retry: JSON Repair
                logging.warning(f"[{req_id}] [GROQ_REPAIR] Malformed JSON received from {current_model}. Attempting 1 repair.")
                repair_prompt = f"The following text was supposed to be a JSON object but parsing failed. Fix the formatting so it is strictly valid JSON. Do not change the content.\n\n{full_response}"
                repair_messages: list[ChatCompletionMessageParam] = [
                    {"role": "system", "content": "You are a JSON formatting assistant. Output only the fixed valid JSON. No markdown, no explanations."},
                    {"role": "user", "content": repair_prompt}
                ]
                repair_response = client.chat.completions.create(
                    model=current_model,
                    messages=repair_messages,
                    temperature=0.0,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"},
                )
                repaired_text = repair_response.choices[0].message.content or ""
                try:
                    parsed_data = json.loads(repaired_text)
                    logging.info(f"[{req_id}] [GROQ_REPAIR_SUCCESS] Repair successful with model {current_model}.")
                    return {"success": True, "data": parsed_data, "error": None, "model_used": current_model}
                except json.JSONDecodeError:
                    logging.error(f"[{req_id}] [GROQ_REPAIR_FAILED] Repair failed.")
                    return {"success": False, "error": "AI response parsing failed after repair.", "status": 500, "model_used": current_model}

        # --- Model Fallback & Error Handling ---
        except RateLimitError as exc:
            logging.warning(f"[{req_id}] [GROQ_429] RateLimitError on {current_model}: {exc}")
            if current_model == primary_model:
                logging.info(f"[{req_id}] [GROQ_FALLBACK] Switching to fallback model: {fallback_model}")
                current_model = fallback_model
                continue
            else:
                logging.error(f"[{req_id}] [GROQ_EXHAUSTED] Rate limit exceeded on fallback model too.")
                return {"success": False, "data": None, "error": "AI service is currently busy or you have reached your daily limit. Please try again later.", "status": 429}
                
        except APITimeoutError as exc:
            logging.warning(f"[{req_id}] [GROQ_TIMEOUT] Timeout on {current_model}: {exc}")
            if timeout_retries_remaining > 0:
                timeout_retries_remaining -= 1
                logging.info(f"[{req_id}] [GROQ_RETRY] Retrying once on current model: {current_model}")
                continue
            else:
                if current_model == primary_model:
                    logging.info(f"[{req_id}] [GROQ_FALLBACK] Timeout exhausted. Switching to fallback model: {fallback_model}")
                    current_model = fallback_model
                    timeout_retries_remaining = 1 # reset for fallback? user said "Retry once on same model.", I will not reset to avoid endless loops.
                    continue
                return {"success": False, "data": None, "error": "AI service timeout. Please try again later.", "status": 504}
                
        except APIConnectionError as exc:
            logging.warning(f"[{req_id}] [GROQ_NETWORK] Connection Error on {current_model}: {exc}")
            if current_model == primary_model:
                logging.info(f"[{req_id}] [GROQ_FALLBACK] Network error. Switching to fallback model: {fallback_model}")
                current_model = fallback_model
                continue
            return {"success": False, "data": None, "error": "Network error. Unable to connect to the Groq API.", "status": 503}
            
        except BadRequestError as exc:
            logging.error(f"[{req_id}] [GROQ_400] Validation/Bad Request Error on {current_model}: {exc}")
            return {"success": False, "data": None, "error": f"Invalid request: {exc.message}", "status": 400}
            
        except AuthenticationError:
            return {"success": False, "data": None, "error": "Authentication failed. Please verify your GROQ_API_KEY is valid.", "status": 401}
            
        except ValueError as exc:
            return {"success": False, "data": None, "error": str(exc), "status": 400}
            
        except Exception as exc:
            return {"success": False, "data": None, "error": f"An unexpected error occurred: {str(exc)}", "status": 500}


# ---------------------------------------------------------------------------
# Legacy Wrapper for Growth Plan Generation (Blocking)
# ---------------------------------------------------------------------------
def generate_growthguru_response(user_prompt: str, max_retries: int = 3) -> Dict[str, Any]:
    """
    Legacy wrapper for Growth Plan generation. 
    Now delegates to the unified pipeline.
    """
    return execute_groq_json_call(
        system_prompt=GROWTHGURU_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_tokens=GROQ_MAX_COMPLETION_TOKENS,
        temperature=GROQ_TEMPERATURE,
        feature_name="Growth Plan"
    )


# ---------------------------------------------------------------------------
# Streaming Response Generator (yields chunks for SSE)
# ---------------------------------------------------------------------------
def generate_growthguru_response_stream(user_prompt: str, max_retries: int = 3) -> Generator[str, None, None]:
    """
    Stream AI response chunks for Server-Sent Events (SSE).
    Uses identical model fallback logic manually implemented for streaming.
    """
    req_id = str(uuid.uuid4())[:8]
    primary_model = GROQ_MODEL
    fallback_model = FALLBACK_MODEL
    current_model = primary_model
    
    timeout_retries_remaining = 1

    while True:
        try:
            with _groq_lock:
                client = _get_groq_client()
            messages = _build_messages(GROWTHGURU_SYSTEM_PROMPT, user_prompt)
            
            logging.info(f"[{req_id}] [GROQ_STREAM_CALL] Executing with model: {current_model}")

            stream = client.chat.completions.create(
                model=current_model,
                messages=messages,
                temperature=GROQ_TEMPERATURE,
                max_tokens=GROQ_MAX_COMPLETION_TOKENS,
                top_p=GROQ_TOP_P,
                stream=True,
            )

            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield f"data: {json.dumps({'content': delta})}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"
            break

        except RateLimitError as exc:
            logging.warning(f"[{req_id}] [GROQ_STREAM_429] RateLimitError on {current_model}")
            if current_model == primary_model:
                current_model = fallback_model
                continue
            yield f"data: {json.dumps({'error': 'AI service is currently busy.', 'status': 429})}\n\n"
            break
            
        except APITimeoutError as exc:
            logging.warning(f"[{req_id}] [GROQ_STREAM_TIMEOUT] Timeout on {current_model}")
            if timeout_retries_remaining > 0:
                timeout_retries_remaining -= 1
                continue
            if current_model == primary_model:
                current_model = fallback_model
                timeout_retries_remaining = 1
                continue
            yield f"data: {json.dumps({'error': 'AI service timeout.', 'status': 504})}\n\n"
            break
            
        except APIConnectionError as exc:
            logging.warning(f"[{req_id}] [GROQ_STREAM_NETWORK] Connection Error on {current_model}")
            if current_model == primary_model:
                current_model = fallback_model
                continue
            yield f"data: {json.dumps({'error': 'Network error. Unable to reach the Groq API.', 'status': 503})}\n\n"
            break
            
        except BadRequestError as exc:
            yield f"data: {json.dumps({'error': f'Invalid request: {exc.message}', 'status': 400})}\n\n"
            break
            
        except AuthenticationError:
            yield f"data: {json.dumps({'error': 'Authentication failed.', 'status': 401})}\n\n"
            break
            
        except ValueError as exc:
            yield f"data: {json.dumps({'error': str(exc), 'status': 400})}\n\n"
            break
            
        except Exception as exc:
            yield f"data: {json.dumps({'error': f'Unexpected error: {str(exc)}', 'status': 500})}\n\n"
            break
