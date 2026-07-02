from fastapi import APIRouter
from api.routes import candidates, ai, analytics

api_router = APIRouter()

# Attach module routers
api_router.include_router(candidates.router, prefix="/candidates", tags=["Candidates"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Copilot & Explanations"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
