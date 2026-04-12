import requests
try:
    response = requests.get("https://openrouter.ai/api/v1/models", timeout=5)
    print("Connection Successful! Status:", response.status_code)
except Exception as e:
    print("Connection Failed:", e)