import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load .env from project root (two levels up from this file)
_env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(_env_path)

from app.routes.convert import router as convert_router
from app.routes.export import router as export_router
from app.routes.tex_export import router as tex_export_router
from app.routes import tex
from app.db.base import Base
from app.db.session import engine

app = FastAPI()

def _auth_env_ready() -> None:
    if os.getenv("AUTH_DEV_BYPASS", "").lower() in {"1", "true", "yes"}:
        return
    if not os.getenv("CLERK_SECRET_KEY"):
        raise RuntimeError("CLERK_SECRET_KEY is required for authentication")
    if not os.getenv("CLERK_ISSUER"):
        raise RuntimeError("CLERK_ISSUER is required for authentication")
    if not os.getenv("CLERK_AUDIENCE"):
        raise RuntimeError("CLERK_AUDIENCE is required for authentication")


@app.on_event("startup")
def _startup():
    _auth_env_ready()
    # Auto-create database tables if they don't exist
    import app.db.models  # noqa: F401 — ensure models are registered
    Base.metadata.create_all(bind=engine)


# CORS


frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ROUTERS


app.include_router(convert_router, prefix="/api")
app.include_router(export_router, prefix="/api")
app.include_router(tex.router)  # tex routes already include /api
app.include_router(tex_export_router, prefix="/api")


# ERROR HANDLERS


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail},
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, _exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"},
    )



@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
