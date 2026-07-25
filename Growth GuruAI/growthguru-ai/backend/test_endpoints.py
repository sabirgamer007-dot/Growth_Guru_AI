import json
import time
import pandas as pd
from io import BytesIO
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("1. Testing GET /")
response = client.get("/")
print("Response:", response.status_code, response.json())
assert response.status_code == 200

print("\n2. Testing POST /upload")
csv_data = "Transaction ID,Date,Product Name,Category,Quantity Sold,Price per Unit,Total Sales\n1,2023-01-01,Test Product,Test Category,10,5.0,50.0"
files = {'file': ('test.csv', BytesIO(csv_data.encode('utf-8')), 'text/csv')}
response = client.post("/upload", files=files)
print("Response:", response.status_code, response.json())
assert response.status_code == 200
file_id = response.json().get("file_id")

time.sleep(2)
print("\n3. Testing POST /validate-alignment")
response = client.post("/validate-alignment", json={"file_id": file_id, "business_type": "Retail"})
print("Response:", response.status_code, response.json())
assert response.status_code == 200

time.sleep(2)
print("\n4. Testing POST /analyze")
response = client.post("/analyze", json={"file_id": file_id})
print("Response:", response.status_code, response.json())
assert response.status_code == 200

time.sleep(2)
print("\n5. Testing POST /generate-growth-plan")
payload = {
    "file_id": file_id,
    "business_profile": {
        "business_name": "Test Business",
        "business_type": "Retail",
        "target_audience": "Everyone",
        "business_goals": "Increase sales"
    }
}
response = client.post("/generate-growth-plan", json=payload)
print("Response:", response.status_code, response.json() if response.status_code == 200 else response.text)

time.sleep(2)
print("\n6. Testing POST /simulate-impact")
response = client.post("/simulate-impact", json={"file_id": file_id})
print("Response:", response.status_code, response.json() if response.status_code == 200 else response.text)

time.sleep(2)
print("\n7. Testing POST /api/chat")
response = client.post("/api/chat", json={"user_prompt": "Hello"})
print("Response:", response.status_code)

time.sleep(2)
print("\n8. Testing POST /api/chat/stream")
response = client.post("/api/chat/stream", json={"user_prompt": "Hello"})
print("Response:", response.status_code)

print("\nAll endpoints tested.")
