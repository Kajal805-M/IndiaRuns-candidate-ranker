from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from core.config import settings
from api.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME, 
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Backend API for the Intelligent Candidate Discovery Platform",
    version="1.0.0"
)

# Configure CORS for the frontend (Optimized/Secured for PoC deployment)
# In a true production environment, replace "*" with the explicit Vercel/frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow Netlify and Vercel
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["System"])
def health_check():
    """
    Health check endpoint to verify API uptime.
    """
    return {"status": "ok", "message": f"{settings.PROJECT_NAME} API is running."}

if __name__ == "__main__":
    # Optimized for local development. Production should use the uvicorn CLI with --workers.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
