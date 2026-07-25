"""
GrowthGuru AI — FastAPI Application
=====================================
Main entry point for the backend server.
Configures CORS, defines API routes, and wires up the Groq client.

Run with:
    uvicorn main:app --reload --port 8000
"""

import os
import uuid
import pandas as pd
import groq_logger
from dotenv import load_dotenv
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from groq_client import (
    generate_growthguru_response,
    generate_growthguru_response_stream,
)
from schemas import (
    ChatRequest,
    ChatResponse,
    AnalyzeRequest,
    GrowthPlanRequest,
    ValidateAlignmentRequest,
    SimulateImpactRequest
)
from storage import storage
from validation import validate_csv_structure, validate_business_alignment
from validation.column_mapper import build_column_mapping
from scenario_simulator import generate_scenario_impact
from insights import derive_business_insights
import json

# ---------------------------------------------------------------------------
# Load environment variables from .env file
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Global Logging Configuration
# ---------------------------------------------------------------------------
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ---------------------------------------------------------------------------
# FastAPI App Initialization
# ---------------------------------------------------------------------------
app = FastAPI(
    title="GrowthGuru AI",
    description="AI-powered Social Media Marketing Assistant for small businesses.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------------------
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
allowed_origins = [origin.strip() for origin in FRONTEND_URL.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global Exception Handler
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all handler to prevent the server from returning raw stack traces."""
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error_code": "HTTP_ERROR",
                "message": str(exc.detail) if exc.detail is not None else "HTTP error",
            }
        )
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error_code": "INTERNAL_ERROR",
            "message": f"Internal server error: {str(exc)}",
        },
    )

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------
def calculate_kpis(df: pd.DataFrame) -> dict:
    # Normalize headers using the centralized mapper
    col_map = build_column_mapping(df.columns.tolist())
    df = df.rename(columns=col_map)
    
    # Required columns for KPI
    if not {'Product_Name', 'Quantity', 'Total_Revenue'}.issubset(df.columns):
        raise ValueError("Missing required columns: Product_Name, Quantity, Total_Revenue")

    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0) # type: ignore
    df['Total_Revenue'] = pd.to_numeric(df['Total_Revenue'], errors='coerce').fillna(0) # type: ignore

    total_sales_count = int(df['Quantity'].sum()) # type: ignore
    total_revenue = float(df['Total_Revenue'].sum()) # type: ignore
    
    product_stats = df.groupby('Product_Name').agg({'Total_Revenue': 'sum'}).reset_index()
    product_stats = product_stats.sort_values(by='Total_Revenue', ascending=False)
    
    best_selling_product = product_stats.iloc[0]['Product_Name'] if not product_stats.empty else "N/A"
    lowest_selling_product = product_stats.iloc[-1]['Product_Name'] if not product_stats.empty else "N/A"
    
    # Product data list for charts
    product_data = []
    if 'Category' in df.columns:
        cat_stats = df.groupby(['Product_Name', 'Category']).agg({'Total_Revenue': 'sum', 'Quantity': 'sum'}).reset_index()
        cat_stats = cat_stats.sort_values(by='Total_Revenue', ascending=False)
        for _, row in cat_stats.iterrows():
            product_data.append({
                "name": str(row['Product_Name']),
                "category": str(row['Category']),
                "quantity": int(row['Quantity']), # type: ignore
                "revenue": float(row['Total_Revenue']) # type: ignore
            })
    else:
        for _, row in product_stats.iterrows():
            product_data.append({
                "name": str(row['Product_Name']),
                "revenue": float(row['Total_Revenue']), # type: ignore
                "quantity": 0, # Cannot compute total units cleanly without joining, mock 0
                "category": ""
            })

    return {
        "total_sales_count": total_sales_count,
        "total_revenue": total_revenue,
        "best_selling_product": str(best_selling_product),
        "lowest_selling_product": str(lowest_selling_product),
        "product_data": product_data
    }

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "GrowthGuru AI", "version": "1.0.0"}


@app.post("/upload", tags=["Hackathon API"])
async def upload_csv(file: UploadFile = File(...)):
    """Uploads and validates the raw sales CSV file."""
    if not file.filename or not file.filename.endswith('.csv'):
        return JSONResponse(status_code=400, content={
            "status": "error",
            "error_code": "VALIDATION_ERROR",
            "message": "Invalid file type. Please upload a .csv file."
        })
    
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        return JSONResponse(status_code=413, content={
            "status": "error",
            "error_code": "FILE_TOO_LARGE",
            "message": "File exceeds 5MB limit."
        })
    
    is_valid, reason, df = validate_csv_structure(contents)
    if not is_valid:
        return JSONResponse(status_code=422, content={
            "status": "error",
            "error_code": "VALIDATION_ERROR",
            "message": reason
        })
    
    file_id = str(uuid.uuid4())
    storage.save(file_id, df)
    
    return JSONResponse(status_code=200, content={
        "status": "success",
        "message": "File uploaded and validated successfully.",
        "file_id": file_id
    })

@app.post("/validate-alignment", tags=["Hackathon API"])
async def validate_alignment(request: ValidateAlignmentRequest):
    df = storage.get(request.file_id)
    if df is None:
        return JSONResponse(status_code=404, content={
            "status": "error",
            "error_code": "FILE_NOT_FOUND",
            "message": "File ID has expired or does not exist."
        })
    
    try:
        # Stage 1: Trust verification execution
        csv_bytes = df.head(5).to_csv(index=False).encode('utf-8')
        is_valid, reason, validated_df = validate_csv_structure(csv_bytes)
        if not is_valid:
            return JSONResponse(status_code=422, content={
                "status": "error",
                "error_code": "CORRUPTED_DATA",
                "message": f"Stored dataset is corrupted: {reason}"
            })
            
        result = validate_business_alignment(validated_df, request.business_type)
        return JSONResponse(status_code=200, content={
            "status": "success",
            "data": result
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "error_code": "INTERNAL_ERROR",
            "message": str(e)
        })


@app.post("/analyze", tags=["Hackathon API"])
async def analyze_data(request: AnalyzeRequest):
    """Aggregates the uploaded CSV data and extracts KPIs."""
    df = storage.get(request.file_id)
    if df is None:
        return JSONResponse(status_code=404, content={
            "status": "error",
            "error_code": "FILE_NOT_FOUND",
            "message": "File ID has expired or does not exist. Please upload the file again."
        })
    
    try:
        kpis = calculate_kpis(df)
        # Frontend expects totalSales and bestSeller to map properly based on API spec.
        # But we'll follow API spec format for the return.
        return JSONResponse(status_code=200, content={
            "status": "success",
            "data": {
                "total_sales_count": kpis["total_sales_count"],
                "total_revenue": kpis["total_revenue"],
                "best_selling_product": kpis["best_selling_product"],
                "lowest_selling_product": kpis["lowest_selling_product"],
                "product_data": kpis["product_data"] # Added for charts
            }
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "error_code": "INTERNAL_ERROR",
            "message": str(e)
        })


@app.post("/generate-growth-plan", tags=["Hackathon API"])
def generate_plan(request: GrowthPlanRequest):
    """Generates AI growth strategy and marketing content."""
    df = storage.get(request.file_id)
    if df is None:
        return JSONResponse(status_code=404, content={
            "status": "error",
            "error_code": "FILE_NOT_FOUND",
            "message": "File ID has expired or does not exist. Please upload the file again."
        })
    
    try:
        # Token Optimization: Do not slice the dataframe here so KPI calculations are correct.
        kpis = calculate_kpis(df)
        
        business_insights = derive_business_insights(df, kpis, request.business_profile.business_type)
        insights_json = json.dumps(business_insights, indent=2)
        
        available_products = ", ".join([p['name'] for p in kpis.get('product_data', [])])
        
        # Token Optimization: Slice the pandas DataFrame immediately before prompt injection.
        sample_data = df.head(5).to_dict(orient="records")
        sample_data_json = json.dumps(sample_data, indent=2)
        
        user_prompt = f"""Business Profile:
- Name: {request.business_profile.business_name}
- Goal: {request.business_profile.business_goals}

Business Insights:
{insights_json}

Available Product Names:
{available_products}

Sample Data:
{sample_data_json}

TASK

Generate a practical business growth strategy prioritizing the opportunities identified in the insights.

Business Facts:
- This business sells ONLY the products listed above.
- Recommendations must not reference products outside this list.
- If confidence is low, avoid making strong recommendations. Prefer cautious wording such as "consider testing" instead of definitive advice."""

        result = generate_growthguru_response(user_prompt)
        
        # If parsing completely failed, groq_client returns {"error": ..., "status": 500}
        if result.get("status") == 500:
            return JSONResponse(status_code=500, content=result)
        
        if result.get("success"):
            # Save context for future AI tasks (like scenario simulation)
            storage.save_context(request.file_id, {
                "business_profile": request.business_profile.model_dump(),
                "growth_plan": result["data"]
            })
            
            return JSONResponse(status_code=200, content={
                "status": "success",
                "data": result["data"]
            })
        else:
            status_code = result.get("status", 500)
            error_code = "RATE_LIMIT_ERROR" if status_code == 429 else "GROQ_API_ERROR"
            return JSONResponse(status_code=status_code, content={
                "status": "error",
                "error_code": error_code,
                "message": result.get("error", "Unknown error")
            })
            
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "error_code": "INTERNAL_ERROR",
            "message": str(e)
        })

@app.post("/simulate-impact", tags=["Hackathon API"])
def simulate_impact(request: SimulateImpactRequest):
    """Simulates the business impact of the generated growth plan."""
    df = storage.get(request.file_id)
    context = storage.get_context(request.file_id)
    
    if df is None or context is None:
        return JSONResponse(status_code=404, content={
            "status": "error",
            "error_code": "FILE_NOT_FOUND",
            "message": "Session data has expired. Please regenerate your growth plan first."
        })
    
    try:
        kpis = calculate_kpis(df)
        business_profile = context["business_profile"]
        growth_plan = context["growth_plan"]
        
        business_insights = derive_business_insights(df, kpis, business_profile['business_type'])
        insights_json = json.dumps(business_insights, indent=2)
        
        # Build prompt using compact tokens
        user_prompt = f"""BUSINESS PROFILE:
- Type: {business_profile['business_type']}
- KPIs: {kpis['total_sales_count']} transactions, {kpis['total_revenue']} revenue

BUSINESS INSIGHTS & CONFIDENCE:
{insights_json}

GENERATED GROWTH PLAN:
{growth_plan.get('plan', growth_plan.get('growth_plan', ''))}"""

        result = generate_scenario_impact(user_prompt)
        
        if result["success"]:
            return JSONResponse(status_code=200, content={
                "status": "success",
                "data": result["data"]
            })
        else:
            status_code = result.get("status", 500)
            error_code = "RATE_LIMIT_ERROR" if status_code == 429 else "GROQ_API_ERROR"
            return JSONResponse(status_code=status_code, content={
                "status": "error",
                "error_code": error_code,
                "message": result["error"]
            })
            
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "error_code": "INTERNAL_ERROR",
            "message": str(e)
        })

# Keep original chat endpoints just in case
@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    result = generate_growthguru_response(request.user_prompt)
    status_code = 200 if result["success"] else 500
    return JSONResponse(content=result, status_code=status_code)

@app.post("/api/chat/stream", tags=["Chat"])
async def chat_stream(request: ChatRequest):
    return StreamingResponse(
        generate_growthguru_response_stream(request.user_prompt),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
