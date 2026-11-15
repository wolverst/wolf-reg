import os
import json
from datetime import datetime, timezone
from google import genai
from supabase import create_client

print("Starting scraper script...")

# Verify environment variables exist before running
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY or not GEMINI_API_KEY:
    raise ValueError("Missing one or more required environment variables (Secrets)!")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

def run_pipeline():
    print("Sending prompt to Gemini 3.8 Flash...")
    prompt = """
    Generate 1 realistic Indian renewable energy policy update (MNRE, CERC, or SECI).
    Return ONLY valid JSON with these exact keys:
    id, source, title, sector, date, summary
    """
    
    response = ai_client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )
    print("Received response from Gemini.")

    record = json.loads(response.text)
    record["updated_at"] = datetime.now(timezone.utc).isoformat()

    print(f"Upserting policy {record['id']} into Supabase...")
    result = supabase.table("policies").upsert(record).execute()
    print("Successfully synced policy to Supabase!", result)

if __name__ == "__main__":
    run_pipeline()
