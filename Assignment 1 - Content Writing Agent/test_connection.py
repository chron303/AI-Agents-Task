"""
Quick API connection test.
Run with: python test_connection.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL")

    if not api_key:
        print("✗ GEMINI_API_KEY not set in .env")
        sys.exit(1)
    if not model:
        print("✗ GEMINI_MODEL not set in .env")
        sys.exit(1)

    print(f"  API key: {'*' * (len(api_key) - 4) + api_key[-4:]}")
    print(f"  Model:   {model}")

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents="Say exactly: Connection successful"
        )
        print(f"\n✓ Connection successful!")
        print(f"  Response: {response.text.strip()}")
    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Testing Gemini API connection...")
    test_connection()
