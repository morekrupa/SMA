"""
Image Service: Handles image URL formatting, thumbnail generation, modern WebP query transforms,
and placeholder SVG generation for ultra-fast perceived page speed.
"""

import re
from typing import Optional, Dict

SVG_PLACEHOLDER = """<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600" fill="none">
  <rect width="600" height="600" fill="#1e2430"/>
  <rect x="20" y="20" width="560" height="560" rx="12" stroke="#334155" stroke-width="2" stroke-dasharray="8 8"/>
  <circle cx="300" cy="270" r="70" fill="#334155"/>
  <path d="M260 270L290 230L320 280L340 250L370 300H230L260 270Z" fill="#64748b"/>
  <text x="300" y="380" font-family="system-ui, -apple-system, sans-serif" font-size="20" font-weight="600" fill="#94a3b8" text-anchor="middle">Artisan Carpet Preview</text>
  <text x="300" y="415" font-family="system-ui, -apple-system, sans-serif" font-size="14" fill="#64748b" text-anchor="middle">Hand-Knotted High Resolution</text>
</svg>"""

def optimize_image_url(url: str, width: int = 600, quality: int = 80, format: str = "webp") -> str:
    """
    Appends or replaces image resizing query parameters for CDNs like Unsplash, Cloudflare, etc.
    """
    if not url:
        return "/static/images/placeholder.svg"
    
    # If it's an Unsplash image, inject width and modern webp compression
    if "images.unsplash.com" in url:
        clean_url = url.split("?")[0]
        return f"{clean_url}?auto=format&fit=crop&w={width}&q={quality}&fm={format}"
    
    return url

def get_thumbnail_and_full(url: str) -> Dict[str, str]:
    """
    Returns optimized thumbnail (w=400) and high-res lightbox view (w=1400)
    """
    return {
        "thumbnail": optimize_image_url(url, width=420, quality=75),
        "card": optimize_image_url(url, width=640, quality=80),
        "full": optimize_image_url(url, width=1400, quality=85),
    }
