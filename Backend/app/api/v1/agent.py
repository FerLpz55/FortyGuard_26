from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from app.api.deps import get_current_user
from app.models.user import User
from app.agents.core import get_agent_runner

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = 'default_session'

@router.post("/chat")
async def chat(request: ChatRequest, current_user: User = Depends(get_current_user)) -> dict:
    try:
        runner = get_agent_runner()
        response = runner.run(
            input_str=request.message,
            session_id=request.session_id
        )
        return {
            "status": "success",
            "response": response,
            "session_id": request.session_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el agente: {str(e)}"
        )

@router.post("/execute")
async def execute(request: ChatRequest, current_user: User = Depends(get_current_user)) -> dict:
    return await chat(request, current_user)

@router.get("/status")
async def status_endpoint(current_user: User = Depends(get_current_user)) -> dict:
    runner = get_agent_runner()
    return {
        "status": "active",
        "agent_name": runner.agent.name,
        "model": runner.agent.model,
        "tools_available": [tool.__name__ for tool in runner.agent.tools]
    }
