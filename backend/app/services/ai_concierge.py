import os
import httpx
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("catalog_maker.ai_concierge")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

async def ai_search_and_recommend(query: str, products_context: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Leverages Gemini / Groq free-tier LLM API to interpret customer's natural language request
    (e.g., 'I want a traditional red carpet for a 10x12 living room with floral patterns under 1 lakh')
    and returns matched product IDs with tailored styling recommendations.
    """
    # Build compact context of available products
    compact_catalog = [
        {
            "id": p["id"],
            "name": p["name"],
            "price": p["price"],
            "category": p["category_name"],
            "material": p.get("material", ""),
            "origin": p.get("origin", "")
        }
        for p in products_context[:40]
    ]

    prompt = f"""You are a luxury artisan carpet consultant for Rajdhani Artisans.
Customer Request: "{query}"

Here is the current carpet catalog:
{json.dumps(compact_catalog)}

Respond with a valid JSON object only with this exact structure:
{{
  "recommendation_text": "A friendly, expert 2-sentence recommendation explaining which styles fit their request",
  "matched_product_ids": ["id1", "id2", "id3"]
}}
"""

    if GEMINI_API_KEY:
        try:
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"response_mime_type": "application/json"}
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(endpoint, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(raw_text)
        except Exception as e:
            logger.warning(f"Gemini API query failed, falling back to smart scoring: {e}")

    # Fallback smart semantic scoring if no external API key is configured
    query_words = set(query.lower().split())
    scored = []
    for p in compact_catalog:
        score = 0
        text = f"{p['name']} {p['category']} {p.get('material', '')} {p.get('origin', '')}".lower()
        for w in query_words:
            if w in text:
                score += 1
        if score > 0:
            scored.append((score, p["id"]))

    scored.sort(key=lambda x: x[0], reverse=True)
    matched_ids = [s[1] for s in scored[:4]] if scored else [compact_catalog[0]["id"], compact_catalog[1]["id"]]

    return {
        "recommendation_text": f"Based on your preference for '{query}', we selected these handcrafted pieces known for their exceptional weave density and enduring artisan character.",
        "matched_product_ids": matched_ids
    }
