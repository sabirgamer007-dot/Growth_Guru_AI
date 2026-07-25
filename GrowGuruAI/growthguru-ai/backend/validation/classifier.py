import json
import math
import pandas as pd
from typing import Dict, Any, List,Tuple
import os

KEYWORDS_FILE = os.path.join(os.path.dirname(__file__), "keywords.json")

def load_keywords() -> dict:
    if not os.path.exists(KEYWORDS_FILE):
        return {}
    with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return text.strip().lower()

def score_dimension(words: List[str], target_keywords: List[str], synonyms: Dict[str, str], max_score: int) -> Tuple[float, List[str]]:
    """
    Scores a dimension using frequency normalization (diminishing returns).
    """
    matched = []
    freq = {}
    
    target_set = set([normalize_text(w) for w in target_keywords])
    
    for w in words:
        w_norm = normalize_text(w)
        # Apply synonyms
        if w_norm in synonyms:
            w_norm = synonyms[w_norm]
            
        if w_norm in target_set:
            freq[w_norm] = freq.get(w_norm, 0) + 1
            if w_norm not in matched:
                matched.append(w_norm)

    if not freq:
        return 0.0, []

    # Frequency normalization: log(1 + count) to prevent spam from inflating score
    raw_score = sum([math.log2(1 + count) for count in freq.values()])
    
    # We map raw_score to the max_score dimension. 
    # E.g. If they match 3 unique words well, they might get max score.
    # Cap at max_score
    scaled = min(max_score, raw_score * (max_score / 5.0)) # heuristic scaling
    
    return scaled, matched

def check_negatives(words: List[str], negative_keywords: List[str]) -> Tuple[float, List[str]]:
    neg_set = set([normalize_text(w) for w in negative_keywords])
    unexpected = []
    penalty = 0.0
    
    for w in words:
        w_norm = normalize_text(w)
        if w_norm in neg_set:
            if w_norm not in unexpected:
                unexpected.append(w_norm)
            penalty += 10.0 # Heavy penalty per unique negative word

    return min(penalty, 40.0), unexpected # Cap penalty at 40

def classify_business(df: pd.DataFrame, business_type: str) -> Dict[str, Any]:
    """
    Stage 2: Local Heuristic Classifier
    """
    db = load_keywords()
    profile = db.get(business_type)
    
    if not profile:
        # If business type not in local DB, we can't classify locally. Force AI fallback.
        return {
            "confidence": 50,
            "matched_keywords": [],
            "unexpected_keywords": [],
            "confidence_breakdown": {}
        }
        
    headers = [str(c) for c in df.columns]
    
    # Extract unique words from products
    if 'Product_Name' in df.columns:
        prod_words = " ".join(df['Product_Name'].dropna().astype(str).tolist()).split()
    else:
        prod_words = []
        
    # Categories
    if 'Category' in df.columns:
        cat_words = " ".join(df['Category'].dropna().astype(str).tolist()).split()
    else:
        cat_words = []

    syns = profile.get("synonyms", {})
    
    # Score dimensions (Weights: H=40, P=35, C=15)
    h_score, h_match = score_dimension(headers, profile.get("headers", []), syns, 40)
    p_score, p_match = score_dimension(prod_words, profile.get("products", []), syns, 35)
    c_score, c_match = score_dimension(cat_words, profile.get("categories", []), syns, 15)
    
    # Brand/Description omitted for simplicity if not in df, just pad remaining 10 points to products
    b_score, b_match = 0, [] # Would be 10 points if we had Brand column
    
    p_score += 10.0 # redistributing weight since we don't have description/brand columns strictly enforced
    
    # Negatives
    all_words = headers + prod_words + cat_words
    penalty, unexpected = check_negatives(all_words, profile.get("negative", []))

    total_confidence = max(0.0, min(100.0, (h_score + p_score + c_score + b_score) - penalty))
    matched_all = list(set(h_match + p_match + c_match + b_match))

    return {
        "confidence": int(total_confidence),
        "matched_keywords": matched_all,
        "unexpected_keywords": unexpected,
        "confidence_breakdown": {
            "headers": round(h_score, 1),
            "products": round(p_score, 1),
            "categories": round(c_score, 1),
            "brands": round(b_score, 1),
            "penalty": round(penalty, 1)
        }
    }
