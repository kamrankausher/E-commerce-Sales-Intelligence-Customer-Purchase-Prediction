from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routers import analytics

app = FastAPI(
    title="E-commerce Growth Intelligence Platform API",
    description="API serving advanced e-commerce analytics.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analytics.router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
def health_check():
    return JSONResponse(content={"status": "ok", "message": "API is running successfully"})
