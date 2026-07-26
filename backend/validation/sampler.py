import pandas as pd

def get_representative_sample(df: pd.DataFrame, max_rows: int = 10) -> str:
    """
    Stage 3 Helper: Representative Sampler
    Extracts a highly diverse subset of the dataset to maximize Groq accuracy 
    while strictly minimizing token consumption.
    """
    if len(df) <= max_rows:
        return df.to_json(orient="records")

    # Group by category if it exists to ensure diverse sampling
    sampled = pd.DataFrame()
    
    if 'Category' in df.columns:
        # Get 1 row from each unique category first
        unique_cats = df.drop_duplicates(subset=['Category'])
        sampled = pd.concat([sampled, unique_cats.head(max_rows)])
        
    # If we still have room, add rows based on unique products
    if len(sampled) < max_rows and 'Product_Name' in df.columns:
        remaining = max_rows - len(sampled)
        # Filter out ones already sampled
        already_sampled = sampled.index if not sampled.empty else []
        candidates = df.drop(index=already_sampled, errors='ignore').drop_duplicates(subset=['Product_Name'])
        sampled = pd.concat([sampled, candidates.head(remaining)])
        
    # If still room (e.g. they only sell 1 product in 1 category but many rows), just sample randomly
    if len(sampled) < max_rows:
        remaining = max_rows - len(sampled)
        already_sampled = sampled.index if not sampled.empty else []
        candidates = df.drop(index=already_sampled, errors='ignore')
        if not candidates.empty:
            sampled = pd.concat([sampled, candidates.sample(min(remaining, len(candidates)))])

    # Truncate any long text columns to save tokens
    for col in sampled.columns:
        if sampled[col].dtype == 'object':
            sampled[col] = sampled[col].astype(str).str.slice(0, 100)

    return sampled.to_json(orient="records")
