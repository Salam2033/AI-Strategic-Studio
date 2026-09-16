from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

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
    return {
        "status": "ok",
        "query": q,
        "analysis": {
            "summary": "موضوع برای تحلیل راهبردی دریافت شد.",
            "political": "نیازمند داده و منابع معتبر برای تحلیل سیاسی.",
            "economic": "نیازمند داده‌های اقتصادی مرتبط.",
            "security": "نیازمند داده‌های امنیتی و رویدادی مرتبط.",
            "next_step": "در مرحله بعد موتور AI به این API متصل می‌شود."
        }
    }
