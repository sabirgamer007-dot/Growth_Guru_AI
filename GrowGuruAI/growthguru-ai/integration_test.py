import sys
import os
import json
import time

sys.path.append('d:/Hackathon_Proj/GrowGuruAI/growthguru-ai/backend')

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

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

def run_tests():
    print("=== 1. Testing /upload ===")
    response = client.post(
        "/upload",
        files={"file": ("test.csv", csv_data, "text/csv")}
    )
    print("Upload Status:", response.status_code)
    print("Upload Response:", response.json())
    assert response.status_code == 200, "Upload failed"
    file_id = response.json()["file_id"]

    time.sleep(2)
    print("\n=== 2. Testing /validate-alignment ===")
    response = client.post(
        "/validate-alignment",
        json={"file_id": file_id, "business_type": "Cafe"}
    )
    print("Validate Status:", response.status_code)
    print("Validate Response:", json.dumps(response.json(), indent=2))
    assert response.status_code == 200, "Validation failed"
    
    time.sleep(2)
    print("\n=== 3. Testing /analyze ===")
    response = client.post(
        "/analyze",
        json={"file_id": file_id}
    )
    print("Analyze Status:", response.status_code)
    print("Analyze Response:", json.dumps(response.json(), indent=2)[:500] + "...(truncated)")
    assert response.status_code == 200, "Analyze failed"

    time.sleep(2)
    print("\n=== 4. Testing /generate-growth-plan ===")
    business_profile = {
        "business_name": "Test Cafe",
        "business_type": "Cafe",
        "target_audience": "Locals and students",
        "business_goals": "Increase revenue and retention"
    }
    response = client.post(
        "/generate-growth-plan",
        json={"file_id": file_id, "business_profile": business_profile}
    )
    print("Growth Plan Status:", response.status_code)
    print("Growth Plan Response:", json.dumps(response.json(), indent=2))
    assert response.status_code == 200, "Growth Plan failed"

    time.sleep(2)
    print("\n=== 5. Testing /simulate-impact ===")
    response = client.post(
        "/simulate-impact",
        json={"file_id": file_id}
    )
    print("Simulate Impact Status:", response.status_code)
    print("Simulate Impact Response:", json.dumps(response.json(), indent=2))
    assert response.status_code in [200, 429], "Simulate Impact failed"
    
    print("\n✅ All tests passed successfully!")

if __name__ == "__main__":
    run_tests()
