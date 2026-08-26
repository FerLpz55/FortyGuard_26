from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/chat")
async def chat(current_user: User = Depends(get_current_user)) -> dict:
    """Agent chat endpoint."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Agent endpoints deferred to BE-09/BE-10")

@router.post("/execute")
async def execute(current_user: User = Depends(get_current_user)) -> dict:
    """Agent execute endpoint."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Agent endpoints deferred to BE-09/BE-10")

@router.get("/status")
async def status_endpoint(current_user: User = Depends(get_current_user)) -> dict:
    """Agent status endpoint."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Agent endpoints deferred to BE-09/BE-10")
