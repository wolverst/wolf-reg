import os
import json
import time
from datetime import datetime, timezone
from google import genai
from supabase import create_client

print("Starting scraper script...")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY or not GEMINI_API_KEY:
    raise ValueError("Missing one or more required environment variables (Secrets)!")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

def generate_with_retry(prompt):
    models_to_try = ["gemini-3.8-flash", "gemini-3.8-flash-lite"]
    
    for model_name in models_to_try:
        for attempt in range(3):
            try:
                print(f"Attempt {attempt + 1} using {model_name}...")
                response = ai_client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                return response.text
            except Exception as e:
                print(f"Temporary error on {model_name}: {e}")
                if attempt < 2:
                    time.sleep(10)
                    
    raise RuntimeError("All model attempts failed due to temporary server load.")

def run_pipeline():
    prompt = """
    Generate 1 realistic Indian renewable energy policy update (MNRE, CERC, or SECI).
    Return ONLY valid JSON with these exact keys:
    id, source, title, sector, date, summary
    """
    
    raw_json = generate_with_retry(prompt)
    print("Received response from Gemini.")

    record = json.loads(raw_json)
    record["updated_at"] = datetime.now(timezone.utc).isoformat()

    print(f"Upserting policy {record['id']} into Supabase...")
    result = supabase.table("policies").upsert(record).execute()
    print("Successfully synced policy to Supabase!", result)

if __name__ == "__main__":
    run_pipeline()
