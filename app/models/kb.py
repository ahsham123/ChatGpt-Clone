"""Models for Knowledge Base (PDF‑based RAG)."""

from typing import List, Optional
from pydantic import BaseModel, Field


class KBUploadResponse(BaseModel):
    kb_id: str = Field(..., description="Identifier of the created knowledge base")
    chunks: int = Field(..., description="Number of text chunks indexed")


class KBListItem(BaseModel):
    kb_id: str
    filename: str
    chunks: int
    created_at: str


class QueryRequest(BaseModel):
    kb_id: str
    query: str
    top_k: int = 3


class QueryResponse(BaseModel):
    kb_id: str
    query: str
    results: List[str]