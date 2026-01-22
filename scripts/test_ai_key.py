import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "google/gemini-2.0-flash-exp:free"

if not API_KEY:
    print("❌ Error: OPENROUTER_API_KEY not found in environment.")
    exit(1)

print(f"Testing API Key: {API_KEY[:10]}...")
print(f"Target Model: {MODEL}")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "HTTP-Referer": "http://localhost:8501",
    "Content-Type": "application/json"
}

payload = {
    "model": MODEL,
    "messages": [
        {"role": "user", "content": "Say 'Hello World' if you can hear me."}
    ]
}

try:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload),
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Success! Response:")
        print(response.json()['choices'][0]['message']['content'])
    else:
        print("❌ API Request Failed:")
        print(response.text)

except Exception as e:
    print(f"❌ Exception: {e}")
