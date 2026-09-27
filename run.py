import uvicorn
import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"[STARTING] Catalog Maker on http://localhost:{port}...")
    print(f"[CATALOG] Customer Catalog: http://localhost:{port}/")
    print(f"[ADMIN] Admin Management Portal: http://localhost:{port}/admin")
    print(f"[DOCS] API Documentation: http://localhost:{port}/docs")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False, log_level="info")
