from typing import Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    kb_id: Optional[str] = None  # knowledge base to use for RAG (optional)
    message: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str
