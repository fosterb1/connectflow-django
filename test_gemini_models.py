import os
import google.generativeai as genai
from decouple import config

def test_gemini():
    api_key = config('GEMINI_API_KEY', default='')
    if not api_key:
        print("FAIL: No GEMINI_API_KEY found")
        return

    first_key = api_key.split(',')[0].strip()
    genai.configure(api_key=first_key)
    
    models = ['gemini-1.5-flash-8b', 'gemini-1.5-flash', 'gemini-1.5-pro']
    
    for m in models:
        try:
            print(f"Testing model: {m}...")
            model = genai.GenerativeModel(m)
            response = model.generate_content("Hello, respond with 'OK'")
            print(f"  Result: {response.text.strip()}")
        except Exception as e:
            print(f"  FAIL for {m}: {str(e)}")

if __name__ == "__main__":
    test_gemini()
