import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

class AnalysisRequest(BaseModel):
    query: str

@app.get("/")
def home():
    return FileResponse("dashboard.html")

@app.get("/api")
def api_status():
    return {"status": "online", "system": "AI Strategic Studio"}

@app.post("/api/analyze")
def analyze(request: AnalysisRequest):
    q = request.query.strip()
    if not q:
        return {"status": "error", "message": "موضوع تحلیل وارد نشده است."}

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "status": "error",
            "message": "کلید OPENAI_API_KEY در Render تنظیم نشده است."
        }

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
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
        return {"status": "error", "message": "خطا در اتصال به موتور AI."}
