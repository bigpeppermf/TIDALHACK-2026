from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.convert import router as convert_router
from app.routes.export import router as export_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(convert_router, prefix="/api")
app.include_router(export_router, prefix="/api")

@app.get("/api/health")
def health():
    return {"status": "ok"}
