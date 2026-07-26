"""GeoSafe AI – FastAPI Application Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers.api import router

settings = get_settings()

app = FastAPI(
    title="GeoSafe AI API",
    description="AI-Powered Property Safety & Risk Assessment Platform – India",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://innovahack-346r.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "GeoSafe AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }
