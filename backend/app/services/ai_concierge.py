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
    Leverages Gemini / Groq free-tier LLM API to interpret customer's natural language lighting request
    (e.g., 'I need a dimmable warm table lamp for my bedside table with stone or ceramic base under 10000')
    and returns matched product IDs with tailored lighting recommendations.
    """
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

    prompt = f"""You are a luxury lighting designer and studio consultant for Lumina Studio (Designer Lamps & Ambient Lights).
Customer Request: "{query}"

Here is the current lighting catalog:
{json.dumps(compact_catalog)}

Respond with a valid JSON object only with this exact structure:
{{
  "recommendation_text": "A friendly, expert 2-sentence recommendation explaining which lamps and light temperatures suit their space and aesthetic",
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
        "recommendation_text": f"For your space matching '{query}', we recommend these handcrafted lamps engineered with soothing 2700K ambient color temperatures and premium tactile materials.",
        "matched_product_ids": matched_ids
    }
