import pandas as pd
import sys
import json
import os

sys.path.append('d:/Hackathon_Proj/GrowGuruAI/growthguru-ai/backend')

from validation.column_mapper import build_column_mapping
from main import calculate_kpis
from insights import derive_business_insights

csv_data = """Product Name,Category,Units Sold,Revenue,Profit Margin (%),Current Stock,Customer Rating,Seasonality
Espresso,Beverage,850,2550,75,500,4.6,All Year
Latte,Beverage,1200,4800,70,400,4.8,All Year
Iced Caramel Macchiato,Beverage,900,4050,65,300,4.7,Summer
Cold Brew,Beverage,600,2700,70,150,4.5,Summer
Hot Chocolate,Beverage,400,1600,60,200,4.8,Winter
Avocado Toast,Food,450,4050,55,30,4.4,All Year
Blueberry Muffin,Food,700,2100,60,15,4.2,All Year
Croissant,Food,800,2400,65,10,4.6,All Year
Chicken Pesto Panini,Food,350,3150,45,25,4.7,All Year
Vegan Wrap,Food,150,1350,50,40,3.9,All Year
Matcha Latte,Beverage,200,1100,65,100,4.1,All Year
Chai Tea Latte,Beverage,550,2200,68,250,4.5,Winter
Bagel with Cream Cheese,Food,600,1800,70,20,4.3,All Year
Turkey Club Sandwich,Food,280,2660,45,35,4.5,All Year
Lemon Loaf Slice,Food,420,1470,62,12,4.4,All Year
Protein Protein Shake,Beverage,180,1260,55,80,4.0,Summer
Mixed Berry Smoothie,Beverage,320,1920,50,90,4.3,Summer
Almond Biscotti,Food,250,625,75,150,4.2,All Year
Quiche Lorraine,Food,120,960,40,15,4.6,All Year
Oatmeal Bowl,Food,190,1140,65,40,4.1,Winter
"""

with open('test.csv', 'w') as f:
    f.write(csv_data)

try:
    df = pd.read_csv('test.csv')
    print("Columns before map:", df.columns.tolist())
    mapped = build_column_mapping(df.columns.tolist())
    print("Mapped columns:", mapped)
    
    kpis = calculate_kpis(df)
    print("KPIs:", kpis)
    
    insights = derive_business_insights(df, kpis, "Cafe")
    print("Insights:", insights)
    
except Exception as e:
    print(f"ERROR: {type(e).__name__} - {e}")
