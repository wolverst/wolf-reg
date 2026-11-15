import os
import json
from datetime import datetime, timezone
from google import genai
from supabase import create_client

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_ROLE_KEY"]
)
ai_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def run_pipeline():
    prompt = """
    Generate 1 realistic Indian renewable energy policy update (MNRE, CERC, or SECI).
    Return ONLY valid JSON with these exact keys:
    id, source, title, sector, date, summary
    """
    response = ai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )

    record = json.loads(response.text)
    record["updated_at"] = datetime.now(timezone.utc).isoformat()

    supabase.table("policies").upsert(record).execute()
    print("Synced policy:", record["id"])

if __name__ == "__main__":
    run_pipeline()
