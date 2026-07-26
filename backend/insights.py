import pandas as pd
from validation.column_mapper import build_column_mapping
from config import LOW_MARGIN_THRESHOLD, OVERSTOCK_RATIO_THRESHOLD, UNDERSTOCK_RATIO_THRESHOLD

def derive_business_insights(df: pd.DataFrame, kpis: dict, business_type: str) -> dict:
    """
    Derives structured, highly-specific business insights from backend KPIs,
    ranked by priority, category-aware, and deduplicated into executive summaries.
    """
    product_data = kpis.get("product_data", [])
    
    insights_dict = {
        "business_type": business_type,
        "summary": {},
        "products": {
            "best": kpis.get("best_selling_product", "N/A"),
            "medium": [p['name'] for p in product_data if p.get('performance_segment') == 'medium'],
            "worst": kpis.get("lowest_selling_product", "N/A")
        },
        "opportunities": [],
        "inventory": {
            "risk": [],
            "healthy": []
        },
        "confidence": {
            "inventory": "high" if any(p.get('inventory_coverage_ratio') is not None for p in product_data) else "none",
            "pricing": "high" if any('profit_margin' in p for p in product_data) else "medium",
            "bundling": "high", 
            "retention": "low"
        }
    }
    
    best_seller_name = kpis.get("best_selling_product")
    best_seller = next((p for p in product_data if p['name'] == best_seller_name), None)

    # Categories for portfolio insights
    categories = {}
    for p in product_data:
        cat = p.get('category')
        if cat and p.get('integrity_status') != 'critical':
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(p)
            
    critical_products = []
    profit_candidates = []
    growth_candidates = []
    overstocked_candidates = []
    understocked_candidates = []
    
    for p in product_data:
        name = p.get('name')
        integrity = p.get('integrity_status', 'valid')
        margin = p.get('profit_margin')
        perf = p.get('performance_segment')
        rating = p.get('customer_rating')
        ratio = p.get('inventory_coverage_ratio')
        contribution = p.get('revenue_contribution', 0)
        
        if integrity == 'critical':
            critical_products.append(p)
            continue
            
        if margin is not None and margin < 0:
            profit_candidates.append(p)
            
        # Growth Candidate Selection
        if perf == 'medium' and (margin is None or margin >= 0) and rating is not None and rating >= 4.0 and contribution > 0:
            growth_candidates.append(p)
                
        if ratio is not None:
            if ratio > OVERSTOCK_RATIO_THRESHOLD:
                overstocked_candidates.append(p)
                insights_dict["inventory"]["risk"].append(name)
            elif ratio < UNDERSTOCK_RATIO_THRESHOLD:
                understocked_candidates.append(p)
                insights_dict["inventory"]["risk"].append(name)
            else:
                insights_dict["inventory"]["healthy"].append(name)

    final_insights = []

    # 1. Consolidated Critical Integrity
    if len(critical_products) == 1:
        name = critical_products[0]['name']
        issues = critical_products[0].get('integrity_issues', [])
        issue_msgs = ", ".join([i.get('message', '') for i in issues])
        final_insights.append(f"{name} has critical data integrity issues ({issue_msgs}). Resolve these issues before relying on AI recommendations or marketing decisions.")
    elif len(critical_products) > 1:
        names = ", ".join([p['name'] for p in critical_products])
        final_insights.append(f"{len(critical_products)} products contain critical data integrity issues ({names}). Resolve these issues before relying on AI recommendations or marketing decisions.")

    # 2. Profitability (Highest priority only)
    if profit_candidates:
        profit_candidates.sort(key=lambda x: x.get('revenue_contribution', 0), reverse=True)
        top_profit = profit_candidates[0]
        margin = top_profit.get('profit_margin')
        final_insights.append(f"{top_profit['name']} contributes meaningful revenue but operates at a {margin:.1f}% profit margin. Review pricing, supplier costs, or promotions before investing in additional marketing.")

    # 3. Growth Opportunity (Highest priority only, 1 bundle max)
    if growth_candidates:
        growth_candidates.sort(key=lambda x: x.get('revenue_contribution', 0), reverse=True)
        top_growth = growth_candidates[0]
        name = top_growth['name']
        rating = top_growth.get('customer_rating')
        contribution = top_growth.get('revenue_contribution', 0)
        cat = top_growth.get('category')
        
        bundle_target = None
        if cat and cat in categories:
            same_cat = [other['name'] for other in categories[cat] if other['name'] != name]
            if same_cat:
                bundle_target = same_cat[0]
                
        if bundle_target:
            final_insights.append(f"{name} has a {rating:.1f} customer rating and contributes {contribution:.1f}% of revenue. Bundling it with {bundle_target} could increase average order value while preserving margins.")
        else:
            final_insights.append(f"{name} has a {rating:.1f} customer rating and contributes {contribution:.1f}% of revenue. Promote it selectively to elevate it to top-performer status without eroding margins.")

    # 4. Inventory (One highest-impact insight)
    if overstocked_candidates or understocked_candidates:
        top_overstock = max(overstocked_candidates, key=lambda x: x.get('inventory_coverage_ratio', 0)) if overstocked_candidates else None
        top_understock = min(understocked_candidates, key=lambda x: x.get('inventory_coverage_ratio', 0)) if understocked_candidates else None
        
        if top_overstock:
            name = top_overstock['name']
            ratio = top_overstock.get('inventory_coverage_ratio', 0)
            final_insights.append(f"{name} has extremely high inventory relative to sales (coverage ratio {ratio:.1f}). Consider bundle offers or controlled clearance to improve inventory turnover.")
        elif top_understock:
            name = top_understock['name']
            ratio = top_understock.get('inventory_coverage_ratio', 0)
            final_insights.append(f"{name} is dangerously understocked (coverage ratio {ratio:.1f}). Replenish stock immediately to avoid missed sales opportunities.")

    # 5. Portfolio Insight
    if categories:
        cat_stats = []
        for cat, prods in categories.items():
            cat_rev = sum(p.get('revenue', 0) for p in prods)
            margins = [p.get('profit_margin') for p in prods if p.get('profit_margin') is not None]
            avg_margin = sum(margins) / len(margins) if margins else 0
            cat_stats.append({'cat': cat, 'rev': cat_rev, 'margin': avg_margin})
            
        cat_stats.sort(key=lambda x: x['rev'], reverse=True)
        top_rev_cat = cat_stats[0]['cat']
        
        cat_stats.sort(key=lambda x: x['margin'], reverse=True)
        top_margin_cat = cat_stats[0]['cat']
        
        if top_rev_cat != top_margin_cat:
            final_insights.append(f"\"{top_rev_cat}\" products generate the largest share of revenue, while \"{top_margin_cat}\" delivers the strongest margins. Increasing {top_margin_cat} attachment rates could improve overall profitability.")
        else:
            total_rev = kpis.get('total_revenue', 0)
            cat_pct = (cat_stats[0]['rev'] / total_rev * 100) if total_rev > 0 else 0
            final_insights.append(f"\"{top_rev_cat}\" is your strongest category, driving {cat_pct:.1f}% of total revenue and maintaining top margins. Focus on expanding this product line.")

    # Fallback to ensure enough insights (aim for 5-6)
    if len(final_insights) < 5 and best_seller:
        contribution = best_seller.get('revenue_contribution', 0)
        final_insights.append(f"{best_seller['name']} is your market leader, contributing {contribution:.1f}% of total revenue. It requires no additional marketing spend.")

    # Apply deduplication and enforce 6 max
    seen = set()
    deduped = []
    for insight in final_insights:
        if insight not in seen:
            deduped.append(insight)
            seen.add(insight)

    insights_dict["opportunities"] = deduped[:6]
    
    return insights_dict
