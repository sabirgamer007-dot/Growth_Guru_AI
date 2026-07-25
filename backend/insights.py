import pandas as pd
from validation.column_mapper import build_column_mapping

def derive_business_insights(df: pd.DataFrame, kpis: dict, business_type: str) -> dict:
    """
    Derives structured business insights from the uploaded dataset and computed KPIs.
    """
    # Normalize headers
    col_map = build_column_mapping(df.columns.tolist())
    norm_df = df.rename(columns=col_map)
    
    def has_col(c): return c in norm_df.columns
    
    insights = {
        "business_type": business_type,
        "summary": {},
        "products": {
            "best": kpis.get("best_selling_product", "N/A"),
            "medium": [],
            "worst": kpis.get("lowest_selling_product", "N/A")
        },
        "opportunities": [],
        "inventory": {
            "risk": [],
            "healthy": []
        },
        "confidence": {
            "inventory": "none",
            "pricing": "none",
            "bundling": "medium", # Because we can suggest bundles based on categories, but not transaction data
            "retention": "low"
        }
    }
    
    total_rev = kpis.get("total_revenue", 0)
    
    if has_col('Product_Name') and has_col('Quantity') and has_col('Total_Revenue'):
        norm_df['Quantity'] = pd.to_numeric(norm_df['Quantity'], errors='coerce').fillna(0)
        norm_df['Total_Revenue'] = pd.to_numeric(norm_df['Total_Revenue'], errors='coerce').fillna(0)
        
        prod_stats = norm_df.groupby('Product_Name').agg({'Total_Revenue': 'sum', 'Quantity': 'sum'}).reset_index()
        prod_stats = prod_stats.sort_values(by='Total_Revenue', ascending=False)
        
        if len(prod_stats) > 0:
            top_rev = prod_stats.iloc[0]['Total_Revenue']
            concentration = (top_rev / total_rev * 100) if total_rev > 0 else 0
            
            insights["summary"]["revenue_concentration"] = f"{concentration:.1f}% from top product"
            insights["summary"]["product_diversity"] = f"{len(prod_stats)} unique products sold"
            
            # Percentiles for products: Top 20%, Middle 60%, Bottom 20%
            if len(prod_stats) >= 3:
                top_q = prod_stats['Total_Revenue'].quantile(0.80)
                bottom_q = prod_stats['Total_Revenue'].quantile(0.20)
                
                medium_prods = prod_stats[(prod_stats['Total_Revenue'] > bottom_q) & (prod_stats['Total_Revenue'] <= top_q)]
                insights["products"]["medium"] = medium_prods['Product_Name'].tolist()[:10]
            else:
                insights["products"]["medium"] = prod_stats['Product_Name'].tolist()[1:-1] if len(prod_stats) > 2 else []
            
            # Growth opportunities
            if len(insights["products"]["medium"]) > 0:
                insights["opportunities"].append("Focus on medium-performing products for highest growth potential.")
            
            # Confidence logic for pricing
            if has_col('Price') or has_col('Profit_Margin'):
                if has_col('Price') and has_col('Profit_Margin'):
                    insights["confidence"]["pricing"] = "high"
                else:
                    insights["confidence"]["pricing"] = "medium"
            
            # Inventory logic
            if has_col('Stock'):
                insights["confidence"]["inventory"] = "high"
                norm_df['Stock'] = pd.to_numeric(norm_df['Stock'], errors='coerce').fillna(0)
                stock_stats = norm_df.groupby('Product_Name').agg({'Stock': 'mean'}).reset_index()
                
                merged = pd.merge(prod_stats, stock_stats, on='Product_Name')
                # Overstock: High stock, low sales (e.g. bottom 20% sales)
                # We use arbitrary logic based on relative volume since we don't have time span
                if not merged.empty:
                    merged['Stock_to_Sales'] = merged['Stock'] / merged['Quantity'].replace(0, 1)
                    risk_q = merged['Stock_to_Sales'].quantile(0.80)
                    healthy_q = merged['Stock_to_Sales'].quantile(0.20)
                    
                    overstock = merged[merged['Stock_to_Sales'] > risk_q]
                    healthy = merged[(merged['Stock_to_Sales'] <= risk_q) & (merged['Stock_to_Sales'] > healthy_q)]
                    
                    insights["inventory"]["risk"] = overstock['Product_Name'].tolist()[:5]
                    insights["inventory"]["healthy"] = healthy['Product_Name'].tolist()[:5]
                    
                    if len(insights["inventory"]["risk"]) > 0:
                        insights["opportunities"].append("Clear overstocked items to optimize inventory.")
            
            # Cross-selling/Bundle logic
            if has_col('Category'):
                insights["opportunities"].append("Suggest complementary products based on similar categories.")
    
    return insights
