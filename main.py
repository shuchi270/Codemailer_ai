print("CodeMailer AI started successfully!")


# ------Detection of code language------
from dotenv import load_dotenv
load_dotenv()

import os
api_key = os.getenv("OPENROUTER_API_KEY")
print("Using API Key from .env:", api_key)

from pygments.lexers import guess_lexer_for_filename
from ai_analyzer import analyze_code
from report_generator import generate_report

def main():
    print("🚀 CodeMailer AI started successfully!")
    
    file_path = "test.py" # Ensure this file exists!
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found.")
        return

    # Read the code
    with open(file_path, "r") as f:
        code = f.read()

    # Detect language for local logs
    try:
        lexer = guess_lexer_for_filename(file_path, code)
        print(f"📂 Detected local language: {lexer.name}")
    except:
        print("📂 Local language detection failed (using AI instead).")

    print("🤖 Analyzing code with AI... please wait.")
    
    # Run the AI Analysis
    result = analyze_code(code)
    generate_report(result)
    
    print("\n" + "="*50)
    print("AI ANALYSIS RESULT:")
    print("="*50)
    print(result)
    print("="*50)
    print("Report generated: report.html")
    print("="*50)

if __name__ == "__main__":
    main()
    