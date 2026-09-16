from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/")
def home():
    return FileResponse("dashboard.html")

@app.get("/api")
def api_status():
    return {
        "status": "online",
        "system": "AI Strategic Studio"
    }
