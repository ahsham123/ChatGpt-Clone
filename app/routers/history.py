from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
# Import both models
from app.models.history import MessageHistory, SessionSummary
from app.services.history_service import HistoryService
from pydantic import BaseModel, Field
from app.services.auth_service import get_current_user
from app.models.user import UserInDB

router = APIRouter(prefix="/history", tags=["history"])
history_service = HistoryService()


# ------------------------- System prompt endpoints ---------------------- #


class PromptUpdate(BaseModel):
    prompt: str = Field(..., description="New system prompt to set for the session")


@router.get("/{session_id}/prompt")
async def get_system_prompt(session_id: str, current_user: UserInDB = Depends(get_current_user)):
    prompt = await history_service.get_system_prompt(current_user.id, session_id)
    return {"prompt": prompt}


@router.put("/{session_id}/prompt")
async def set_system_prompt(
    session_id: str,
    body: PromptUpdate,
    current_user: UserInDB = Depends(get_current_user),
):
    await history_service.set_system_prompt(current_user.id, session_id, body.prompt)
    return {"status": "ok"}

@router.get("/", response_model=List[MessageHistory])
async def get_history(
    session_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        messages = await history_service.get_messages(current_user.id, session_id, skip, limit)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------- Delete a session ------------------------------ #


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete all messages belonging to the given session for current user."""
    try:
        deleted = await history_service.delete_session(current_user.id, session_id)
        if deleted == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"deleted": deleted}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# New endpoint that returns a concise list of sessions for the current user.


@router.get("/sessions", response_model=List[SessionSummary])
async def list_sessions(
    limit: int = Query(100, ge=1),
    current_user: UserInDB = Depends(get_current_user)
):
    """Return up to `limit` sessions for the authenticated user ordered by
    most recent activity. The client can use this to populate the sidebar.
    """
    try:
        sessions = await history_service.get_sessions(current_user.id, limit)
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
