from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routers import analytics
import logging

# Configure basic logging for the application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="E-commerce Growth Intelligence Platform API",
    description="API serving advanced e-commerce analytics.",
    version="1.0.0"
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (Modify for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include analytics routes
app.include_router(analytics.router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify the API is running."""
    return JSONResponse(content={"status": "ok", "message": "API is running successfully"})
