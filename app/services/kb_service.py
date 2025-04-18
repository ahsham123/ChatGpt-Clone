"""Knowledge base service – handles PDF ingestion and retrieval."""

import uuid
from datetime import datetime
from typing import List

from fastapi import UploadFile

from app.db import db
from app.config import settings

# Third‑party imports – we expect PyPDF2 to be installed. If missing, raise a
# clear error so that maintainers know which extra lib to add to
# requirements.txt.

try:
    import PyPDF2
except ImportError as exc:  # pragma: no cover
    raise ImportError("PyPDF2 must be installed to use the knowledge‑base features") from exc

from openai import AsyncOpenAI
import math


client = AsyncOpenAI(api_key=settings.openai_api_key)


class KnowledgeBaseService:
    """CRUD & search for PDF knowledge bases stored in MongoDB."""

    def __init__(self):
        self.kb_collection = db["knowledge_bases"]  # metadata documents
        self.chunk_collection = db["kb_chunks"]  # individual chunks with embeddings

    # ------------------------------ Ingestion ----------------------------- #

    async def ingest_pdf(self, user_id: str, file: UploadFile, chunk_size: int = 1000, overlap: int = 200) -> str:
        """Parse the uploaded PDF, chunk its text and embed each chunk.

        Returns the ID of the created knowledge base.
        """
        kb_id = str(uuid.uuid4())

        # Read PDF bytes and extract text
        pdf_reader = PyPDF2.PdfReader(file.file)
        pages_text = [page.extract_text() or "" for page in pdf_reader.pages]
        full_text = "\n".join(pages_text)

        # simple overlapping chunking by characters
        chunks = []
        start = 0
        while start < len(full_text):
            end = start + chunk_size
            chunk = full_text[start:end]
            chunks.append(chunk)
            start = end - overlap  # overlap for better continuity

        # Generate embeddings in batches (OpenAI can handle multiple inputs)
        embeddings_response = await client.embeddings.create(
            model="text-embedding-ada-002",
            input=chunks,
        )
        embeddings = [d.embedding for d in embeddings_response.data]

        now = datetime.utcnow()
        # Insert metadata doc
        await self.kb_collection.insert_one(
            {
                "_id": kb_id,
                "user_id": user_id,
                "filename": file.filename,
                "chunks": len(chunks),
                "created_at": now,
            }
        )

        # Insert chunks with embedding
        docs = [
            {
                "kb_id": kb_id,
                "user_id": user_id,
                "chunk_index": idx,
                "text": chunk,
                "embedding": emb,
            }
            for idx, (chunk, emb) in enumerate(zip(chunks, embeddings))
        ]
        if docs:
            await self.chunk_collection.insert_many(docs)

        return kb_id

    # ------------------------------ Retrieval ----------------------------- #

    async def retrieve(self, user_id: str, kb_id: str, query: str, top_k: int = 3) -> List[str]:
        """Return the *top_k* most similar chunks for the given query."""
        # Embed query
        q_emb_resp = await client.embeddings.create(model="text-embedding-ada-002", input=[query])
        q_emb = q_emb_resp.data[0].embedding

        # Fetch all chunks for kb (could be optimised with vector DB) – OK for small pdfs
        cursor = self.chunk_collection.find({"kb_id": kb_id, "user_id": user_id})
        chunks = await cursor.to_list(length=None)

        # Compute cosine similarity
        def cosine(a, b):
            dot = sum(i * j for i, j in zip(a, b))
            norm_a = math.sqrt(sum(i * i for i in a))
            norm_b = math.sqrt(sum(i * i for i in b))
            if norm_a == 0 or norm_b == 0:
                return -1
            return dot / (norm_a * norm_b)

        scored = [
            (cosine(q_emb, doc["embedding"]), doc["text"])
            for doc in chunks
        ]
        scored.sort(key=lambda t: t[0], reverse=True)
        top_chunks = [text for _score, text in scored[:top_k]]
        return top_chunks
