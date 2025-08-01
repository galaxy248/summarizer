from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse

from app.api import api_router

app = FastAPI(
    version="1.0.0",
    title="Summarizer",
    description="AI-powered content summarization service"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

ui_directory = Path(__file__).parent / "ui"
app.mount("/static", StaticFiles(directory=str(ui_directory)), name="static")

app.include_router(api_router)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return FileResponse(str(ui_directory / "dashboard.html"))

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return FileResponse(str(ui_directory / "login.html"))

@app.get("/signup", response_class=HTMLResponse)
async def signup_page():
    return FileResponse(str(ui_directory / "signup.html"))

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    return FileResponse(str(ui_directory / "dashboard.html"))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Summarizer API"}
