import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app.routes.convert import router as convert_router
from app.routes.export import router as export_router
from app.routes import tex

# Load environment variables FIRST
load_dotenv()

app = FastAPI()


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
