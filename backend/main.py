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
from validation.integrity_checker import check_business_integrity
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
def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    col_map = build_column_mapping(df.columns.tolist())
    df = df.rename(columns=col_map)
    df = check_business_integrity(df)
    return df

def calculate_kpis(df: pd.DataFrame) -> dict:
    
    # Required columns for KPI
    if not {'Product_Name', 'Quantity', 'Total_Revenue'}.issubset(df.columns):
        raise ValueError("Missing required columns: Product_Name, Quantity, Total_Revenue")

    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0) # type: ignore
    df['Total_Revenue'] = pd.to_numeric(df['Total_Revenue'], errors='coerce').fillna(0) # type: ignore

    if 'Profit_Margin' in df.columns:
        df['Profit_Margin'] = pd.to_numeric(df['Profit_Margin'], errors='coerce').fillna(0)
    
    if 'Stock' in df.columns:
        df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0)
        
    if 'Customer_Rating' in df.columns:
        df['Customer_Rating'] = pd.to_numeric(df['Customer_Rating'], errors='coerce').fillna(0)

    # Define aggregations per column
    agg_funcs: dict = {'Total_Revenue': 'sum', 'Quantity': 'sum'}
    if 'Profit_Margin' in df.columns:
        agg_funcs['Profit_Margin'] = 'mean'
    if 'Stock' in df.columns:
        agg_funcs['Stock'] = 'sum'
    if 'Customer_Rating' in df.columns:
        agg_funcs['Customer_Rating'] = 'mean'
    if 'Category' in df.columns:
        agg_funcs['Category'] = 'first'
        
    if 'integrity_status' in df.columns:
        def agg_status(statuses):
            if 'critical' in statuses.values:
                return 'critical'
            if 'warning' in statuses.values:
                return 'warning'
            return 'valid'
        agg_funcs['integrity_status'] = agg_status
        
    if 'integrity_issues' in df.columns:
        def agg_issues(issues_lists):
            merged = []
            for issues in issues_lists:
                merged.extend(issues)
            unique_issues = {i['code']: i for i in merged}
            return list(unique_issues.values())
        agg_funcs['integrity_issues'] = agg_issues
        
    product_stats = df.groupby('Product_Name').agg(agg_funcs).reset_index()
    product_stats = product_stats.sort_values(by='Total_Revenue', ascending=False)
    
    total_sales_count = int(product_stats['Quantity'].sum())
    total_revenue = float(product_stats['Total_Revenue'].sum())
    
    # Compute Profit Metrics
    total_profit = 0.0
    if 'Profit_Margin' in product_stats.columns:
        product_stats['Profit'] = product_stats['Total_Revenue'] * (product_stats['Profit_Margin'] / 100.0)
        total_profit = float(product_stats['Profit'].sum())
        overall_profit_margin = (total_profit / total_revenue * 100.0) if total_revenue != 0 else 0.0
    else:
        product_stats['Profit'] = 0.0
        overall_profit_margin = 0.0

    # Compute Revenue Contribution
    if total_revenue != 0:
        product_stats['Revenue_Contribution'] = (product_stats['Total_Revenue'] / total_revenue * 100.0)
    else:
        product_stats['Revenue_Contribution'] = 0.0

    best_selling_product = product_stats.iloc[0]['Product_Name'] if not product_stats.empty else "N/A"
    lowest_selling_product = product_stats.iloc[-1]['Product_Name'] if not product_stats.empty else "N/A"
    
    top_q = product_stats['Total_Revenue'].quantile(0.80) if not product_stats.empty else 0
    bottom_q = product_stats['Total_Revenue'].quantile(0.20) if not product_stats.empty else 0

    product_data = []
    for _, row in product_stats.iterrows():
        rev = float(row['Total_Revenue'])
        qty = int(row['Quantity'])
        
        if rev > top_q:
            perf_seg = 'best'
        elif rev <= bottom_q:
            perf_seg = 'worst'
        else:
            perf_seg = 'medium'

        p_data: dict[str, float | int | str | None] = {
            "name": str(row['Product_Name']),
            "revenue": rev,
            "quantity": qty,
            "revenue_contribution": float(row['Revenue_Contribution']),
            "performance_segment": perf_seg
        }
        if 'Category' in product_stats.columns:
            p_data['category'] = str(row['Category'])
        else:
            p_data['category'] = ""
            
        if 'Profit_Margin' in product_stats.columns:
            p_data['profit_margin'] = float(row['Profit_Margin'])
            p_data['profit'] = float(row['Profit'])
            
        if 'Stock' in product_stats.columns:
            stk = float(row['Stock'])
            p_data['stock'] = stk
            if qty > 0:
                p_data['inventory_coverage_ratio'] = stk / qty
                p_data['inventory_status'] = "available"
            else:
                if stk > 0:
                    p_data['inventory_coverage_ratio'] = None
                    p_data['inventory_status'] = "no_sales"
                else:
                    p_data['inventory_coverage_ratio'] = 0.0
                    p_data['inventory_status'] = "out_of_stock"
            
        if 'Customer_Rating' in product_stats.columns:
            p_data['customer_rating'] = float(row['Customer_Rating'])
            
        if 'integrity_status' in product_stats.columns:
            p_data['integrity_status'] = str(row['integrity_status'])
            p_data['integrity_issues'] = row['integrity_issues']
            
        product_data.append(p_data)

    return {
        "total_sales_count": total_sales_count,
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "overall_profit_margin": overall_profit_margin,
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
        df = preprocess_dataframe(df)
        kpis = calculate_kpis(df)
        insights = derive_business_insights(df, kpis, "General")
        
        return JSONResponse(status_code=200, content={
            "status": "success",
            "data": {
                "total_sales_count": kpis["total_sales_count"],
                "total_revenue": kpis["total_revenue"],
                "total_profit": kpis["total_profit"],
                "overall_profit_margin": kpis["overall_profit_margin"],
                "best_selling_product": kpis["best_selling_product"],
                "lowest_selling_product": kpis["lowest_selling_product"],
                "product_data": kpis["product_data"],
                "insights": insights
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
        df = preprocess_dataframe(df)
        kpis = calculate_kpis(df)
        
        business_insights = derive_business_insights(df, kpis, request.business_profile.business_type)
        # Build AI Context Builder structured object
        
        # Calculate integrity summary
        critical_count = sum(1 for p in kpis.get("product_data", []) if p.get("integrity_status") == "critical")
        warning_count = sum(1 for p in kpis.get("product_data", []) if p.get("integrity_status") == "warning")
        integrity_summary = {
            "total_critical_issues": critical_count,
            "total_warning_issues": warning_count,
            "overall_health": "critical" if critical_count > 0 else ("warning" if warning_count > 0 else "valid")
        }

        ai_context = {
            "business_summary": {
                "name": request.business_profile.business_name,
                "goal": request.business_profile.business_goals,
                "type": request.business_profile.business_type
            },
            "kpis": {
                "total_sales_count": kpis.get("total_sales_count"),
                "total_revenue": kpis.get("total_revenue"),
                "total_profit": kpis.get("total_profit"),
                "overall_profit_margin": kpis.get("overall_profit_margin")
            },
            "products": kpis.get("product_data", []),
            "business_insights": business_insights,
            "integrity_summary": integrity_summary
        }
        
        ai_context_json = json.dumps(ai_context, indent=2)
        
        user_prompt = f"""Business Context:
{ai_context_json}

TASK

Generate a practical business growth strategy prioritizing the opportunities identified in the insights.

Business Facts:
- This business sells ONLY the products listed in the context.
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
        df = preprocess_dataframe(df)
        kpis = calculate_kpis(df)
        business_profile = context["business_profile"]
        growth_plan = context["growth_plan"]
        
        business_insights = derive_business_insights(df, kpis, business_profile['business_type'])
        insights_json = json.dumps(business_insights, indent=2)
        
        # Build prompt using compact tokens
        user_prompt = f"""BUSINESS PROFILE:
- Type: {business_profile['business_type']}
- KPIs: {kpis['total_sales_count']} transactions, {kpis['total_revenue']} revenue, {kpis['total_profit']} profit, {kpis['overall_profit_margin']:.1f}% margin

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
