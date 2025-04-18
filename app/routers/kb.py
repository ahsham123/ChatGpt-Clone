"""FastAPI router for PDF knowledge base operations."""

from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status

from app.services.kb_service import KnowledgeBaseService
from app.models.kb import KBUploadResponse, QueryRequest, QueryResponse, KBListItem
from app.services.auth_service import get_current_user
from app.models.user import UserInDB


router = APIRouter(prefix="/kb", tags=["knowledge_base"])
kbs = KnowledgeBaseService()


@router.post("/upload", response_model=KBUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(..., description="PDF file to ingest"),
    current_user: UserInDB = Depends(get_current_user),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    kb_id = await kbs.ingest_pdf(current_user.id, file)
    return KBUploadResponse(kb_id=kb_id, chunks=await kbs.chunk_collection.count_documents({"kb_id": kb_id}))


@router.post("/query", response_model=QueryResponse)
async def query_kb(request: QueryRequest, current_user: UserInDB = Depends(get_current_user)):
    texts = await kbs.retrieve(current_user.id, request.kb_id, request.query, request.top_k)
    return QueryResponse(kb_id=request.kb_id, query=request.query, results=texts)


@router.get("/list", response_model=List[KBListItem])
async def list_kb(current_user: UserInDB = Depends(get_current_user)):
    cursor = kbs.kb_collection.find({"user_id": current_user.id}).sort("created_at", -1)
    docs = await cursor.to_list(length=None)
    return [
        KBListItem(
            kb_id=doc["_id"],
            filename=doc["filename"],
            chunks=doc["chunks"],
            created_at=doc["created_at"].isoformat() + "Z",
        )
        for doc in docs
    ]
