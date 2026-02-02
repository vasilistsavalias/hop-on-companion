import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "google/gemini-2.0-flash-exp:free"

if not API_KEY:
    print("ERROR: OPENROUTER_API_KEY not found in environment.")
    raise SystemExit(1)

print(f"Testing API Key: {API_KEY[:10]}...")
print(f"Target Model: {MODEL}")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "HTTP-Referer": "http://localhost:8501",
    "Content-Type": "application/json",
}

payload = {
    "model": MODEL,
    "messages": [
        {"role": "user", "content": "Say 'Hello World' if you can hear me."}
    ],
}

try:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload),
        timeout=30,
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        print("SUCCESS: Response:")
        print(response.json()["choices"][0]["message"]["content"])
    else:
        print("ERROR: API Request Failed")
        print("Response Body:")
        print(response.text)

except Exception as e:
    print(f"ERROR: Exception: {e}")
