from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint for the application.
    """
    return {"status": "healthy", "version": "0.1.0"}
