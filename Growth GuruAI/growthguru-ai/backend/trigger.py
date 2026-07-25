import urllib.request
import json
import uuid

BASE_URL = "http://localhost:8000"

print("1. Uploading CSV...")
csv_content = b"""Transaction ID,Date,Product Name,Category,Quantity Sold,Price per Unit,Total Sales
1,2023-01-01,Test Coffee,Beverage,10,5.0,50.0
2,2023-01-01,Test Pastry,Food,5,4.0,20.0
"""
boundary = uuid.uuid4().hex
body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="test_real.csv"\r\n'
    f"Content-Type: text/csv\r\n\r\n"
).encode('utf-8') + csv_content + f"\r\n--{boundary}--\r\n".encode('utf-8')

req = urllib.request.Request(f"{BASE_URL}/upload", data=body)
req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')

with urllib.request.urlopen(req) as response:
    upload_res = json.loads(response.read().decode())
    print(f"Upload Status: {response.status}")
    file_id = upload_res.get("file_id")
    print(f"File ID: {file_id}")

print("\n2. Analyzing data...")
req_analyze = urllib.request.Request(f"{BASE_URL}/analyze", data=json.dumps({"file_id": file_id}).encode(), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req_analyze) as res:
    print("Analyzed.")

print("\n3. Generating Growth Plan...")
payload = {
    "file_id": file_id,
    "business_profile": {
        "business_name": "Test Cafe",
        "business_type": "Cafe",
        "target_audience": "Locals",
        "business_goals": "Increase weekend sales"
    }
}
req_plan = urllib.request.Request(f"{BASE_URL}/generate-growth-plan", data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req_plan) as response:
        print(f"Generate Plan Status: {response.status}")
        print("Success! Check the uvicorn terminal for the token breakdown.")
except urllib.error.HTTPError as e:
    print(f"Error: {e.code} {e.read()}")
