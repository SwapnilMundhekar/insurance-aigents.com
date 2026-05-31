from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["frontend"])

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    html_path = Path(__file__).resolve().parents[1] / "static" / "index.html"
    html = html_path.read_text(encoding="utf-8")
    return HTMLResponse(
        content=html,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-Dashboard-Version": "README_HOMEPAGE_CHATBOT_V1"
        }
    )
