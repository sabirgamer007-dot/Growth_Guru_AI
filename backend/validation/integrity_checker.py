import pandas as pd
import numpy as np
import math

def check_business_integrity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluates business rules deterministically and attaches structured integrity metadata 
    to each row.
    
    Returns the DataFrame with two new columns: 'integrity_status' and 'integrity_issues'.
    """
    
    statuses = []
    issues_list = []
    
    for idx, row in df.iterrows():
        issues = []
        status = "valid"
        
        # Helper to safely get numeric values, treating NaN as None
        def get_val(col_name):
            if col_name not in df.columns:
                return None
            val = row[col_name]
            if pd.isna(val):
                return None
            return float(val) if isinstance(val, (int, float, np.number)) else None

        revenue = get_val('Total_Revenue')
        quantity = get_val('Quantity')
        stock = get_val('Stock')
        rating = get_val('Customer_Rating')
        profit_margin = get_val('Profit_Margin')
        price = get_val('Price')
        
        # 1. Critical Checks
        
        # Required fields missing or NaN
        if pd.isna(row.get('Product_Name', np.nan)) or revenue is None or quantity is None:
            issues.append({"code": "MISSING_REQUIRED_DATA", "severity": "critical", "message": "Required fields (Product_Name, Quantity, Total_Revenue) are missing or invalid."})
            status = "critical"
            
        # Revenue < 0
        if revenue is not None and revenue < 0:
            issues.append({"code": "NEGATIVE_REVENUE", "severity": "critical", "message": "Revenue cannot be negative."})
            status = "critical"
            
        # Stock < 0
        if stock is not None and stock < 0:
            issues.append({"code": "NEGATIVE_STOCK", "severity": "critical", "message": "Stock cannot be negative."})
            status = "critical"
            
        # Customer Rating > 5 or < 1
        if rating is not None and (rating > 5.0 or rating < 1.0) and rating != 0:
            issues.append({"code": "INVALID_RATING", "severity": "critical", "message": f"Customer rating ({rating}) is outside the valid range (1-5)."})
            status = "critical"
            
        # Quantity == 0 AND Revenue > 0
        if quantity is not None and revenue is not None and quantity == 0 and revenue > 0:
            issues.append({"code": "ZERO_QTY_WITH_REVENUE", "severity": "critical", "message": "Units sold is 0 but revenue is generated."})
            status = "critical"
            
        # Revenue mismatch: Quantity * Price ≈ Revenue
        if quantity is not None and price is not None and revenue is not None:
            expected_revenue = quantity * price
            if expected_revenue != 0:
                diff_pct = abs(expected_revenue - revenue) / abs(expected_revenue)
                if diff_pct > 0.05: # > 5% mismatch
                    issues.append({"code": "REVENUE_MISMATCH", "severity": "critical", "message": "Quantity * Price does not match Total Revenue."})
                    status = "critical"
            else:
                if revenue > 0.01: # If expected is 0 but revenue is > 0
                    issues.append({"code": "REVENUE_MISMATCH", "severity": "critical", "message": "Quantity * Price is 0 but Total Revenue is > 0."})
                    status = "critical"

        # Inf values
        for col in ['Total_Revenue', 'Quantity', 'Stock', 'Profit_Margin', 'Customer_Rating', 'Price']:
            val = get_val(col)
            if val is not None and math.isinf(val):
                issues.append({"code": "INFINITE_VALUE", "severity": "critical", "message": f"Infinite value detected in {col}."})
                status = "critical"
                
        # 2. Warning Checks
        
        # Negative Profit Margin
        if profit_margin is not None and profit_margin < 0:
            issues.append({"code": "NEGATIVE_MARGIN", "severity": "warning", "message": "Product has a negative profit margin."})
            if status == "valid": status = "warning"
            
        # Revenue == 0
        if revenue is not None and revenue == 0:
            issues.append({"code": "ZERO_REVENUE", "severity": "warning", "message": "Product generated zero revenue."})
            if status == "valid": status = "warning"
            
        # Stock == 0
        if stock is not None and stock == 0:
            issues.append({"code": "ZERO_STOCK", "severity": "warning", "message": "Product is out of stock."})
            if status == "valid": status = "warning"

        statuses.append(status)
        issues_list.append(issues)
        
    df = df.copy()
    df['integrity_status'] = statuses
    df['integrity_issues'] = issues_list
    
    return df
