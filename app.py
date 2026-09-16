import os
import logging
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()
logger = logging.getLogger("uvicorn.error")

class AnalysisRequest(BaseModel):
    query: str


def get_openai_key():
    """Find a configured OpenAI key without exposing its value."""
    candidates = ["OPENAI_API_KEY", "OPENAI_API_KEY_2", "OPENAI_API_KEY_OLD"]
    for name in candidates:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip(), name

    for name, value in os.environ.items():
        if name.startswith("OPENAI_API_KEY_") and value and value.strip():
            return value.strip(), name
    return None, None


@app.on_event("startup")
def startup_diagnostics():
    key, key_name = get_openai_key()
    model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna").strip() or "gpt-5.6-luna"
    openai_names = sorted(name for name in os.environ if name.startswith("OPENAI_API_KEY"))
    # Safe diagnostics only: never log the secret value.
    logger.info(
        "OPENAI_RUNTIME_DIAGNOSTICS configured=%s source=%s key_length=%s variables=%s model=%s",
        bool(key), key_name or "NONE", len(key) if key else 0, openai_names, model
    )


@app.get("/")
def home():
    return FileResponse("dashboard.html")

@app.get("/api")
def api_status():
    key, key_name = get_openai_key()
    return {
        "status": "online",
        "system": "AI Strategic Studio",
        "openai_configured": bool(key),
        "openai_key_source": key_name,
        "model": os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
    }

@app.get("/api/diagnostics")
def diagnostics():
    key, key_name = get_openai_key()
    model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna").strip() or "gpt-5.6-luna"
    openai_names = sorted(name for name in os.environ if name.startswith("OPENAI_API_KEY"))
    return {
        "ok": bool(key),
        "key_source": key_name,
        "key_length": len(key) if key else 0,
        "key_variables_present": openai_names,
        "model": model
    }

@app.post("/api/analyze")
def analyze(request: AnalysisRequest):
    q = request.query.strip()
    if not q:
        return {"status": "error", "message": "موضوع تحلیل وارد نشده است."}

    api_key, key_name = get_openai_key()
    if not api_key:
        return {
            "status": "error",
            "message": "هیچ متغیر محیطی معتبر برای کلید OpenAI در زمان اجرا پیدا نشد.",
            "hint": "در Render باید OPENAI_API_KEY روی همین Web Service در runtime موجود باشد."
        }

    try:
        model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna").strip() or "gpt-5.6-luna"
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=model,
            instructions=(
                "تو موتور تحلیل راهبردی AI Strategic Studio هستی. "
                "پاسخ را به فارسی، بی‌طرف و تحلیلی ارائه کن. "
                "واقعیت، تحلیل و عدم قطعیت را از هم جدا کن و از ساختن منبع یا داده خودداری کن. "
                "موضوع را در چهار بخش خلاصه، سیاسی، اقتصادی و امنیتی بررسی کن."
            ),
            input=q
        )
        return {
            "status": "ok",
            "query": q,
            "analysis": {
                "summary": response.output_text,
                "political": "تحلیل سیاسی در متن بالا ارائه شده است.",
                "economic": "تحلیل اقتصادی در متن بالا ارائه شده است.",
                "security": "تحلیل امنیتی در متن بالا ارائه شده است.",
                "next_step": "موتور AI فعال است."
            }
        }
    except Exception as e:
        error_text = str(e).strip()
        return {
            "status": "error",
            "message": "خطا در موتور AI: " + (error_text[:500] if error_text else "خطای نامشخص"),
            "model": model,
            "key_source": key_name
        }
