import os
from pathlib import Path
import httpx
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

BASE_DIR = Path(__file__).parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path, override=True)

def analyze_code(code):
    """
    Sends code to OpenRouter for a deep dive analysis.
    Bypasses OpenAI library issues by using a direct HTTPS request.
    """
    
    # 1. Get the API Key and verify it exists
    api_key = os.getenv("OPENROUTER_API_KEY")
    print(f"🔑 Using API Key from .env: {'FOUND' if api_key else 'NOT FOUND'}")
    if not api_key:
        return f"❌ Error: OPENROUTER_API_KEY not found in .env file.\nScript Folder: {BASE_DIR} \nLooked for .env at: {env_path}"

    # 2. Configure the request
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000", # Required by some OpenRouter models
        "X-Title": "CodeMailer AI"
    }

    # 3. Build the prompt
    prompt = f"""
    Analyze the following code snippet. 
    Provide the response in this exact format:
    
    1. **Language Identification**: Identify the programming language.
    2. **Added Comments**: Provide a version of the code with helpful inline comments.
    3. **Bug Detection**: List any logic errors, syntax issues, or security risks.
    4. **Summary**: A brief overview of what this code does.
    5. **Workflow**: Explain the step-by-step logic of the execution.

    CODE:
    {code}
    """

    payload = {
        "model": "google/gemini-2.0-flash-001",
        "messages": [
            {"role": "system", "content": "You are a professional Senior Software Engineer and Code Auditor."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    # 4. Send the request
    try:
        # verify=False handles the macOS LibreSSL 'Connection Error'
        with httpx.Client(verify=False) as client:
            response = client.post(url, headers=headers, json=payload, timeout=45.0)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"❌ AI Error {response.status_code}: {response.text}"
                
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"