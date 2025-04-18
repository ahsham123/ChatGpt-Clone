import uuid
from openai import AsyncOpenAI
from typing import Optional
from app.config import settings
from app.services.history_service import HistoryService


client = AsyncOpenAI(api_key=settings.openai_api_key)
# openai.api_key = settings.openai_api_key

history_service = HistoryService()

from app.services.kb_service import KnowledgeBaseService

kbs = KnowledgeBaseService()


async def get_chat_response(
    user_id: str,
    session_id: Optional[str],
    message: str,
    kb_id: Optional[str] = None,
):
    if session_id is None:
        session_id = str(uuid.uuid4())

    previous = await history_service.get_messages(user_id, session_id)
    messages = [{"role": m.role, "content": m.content} for m in previous]

    # User custom system prompt
    custom_prompt = await history_service.get_system_prompt(user_id, session_id)
    if custom_prompt:
        messages.insert(0, {"role": "system", "content": custom_prompt})
    # Knowledge‑base retrieval for RAG
    if kb_id:
        try:
            context_chunks = await kbs.retrieve(user_id, kb_id, message, top_k=3)
            context_text = "\n".join(context_chunks)
            system_prompt = (
                "You are an assistant with access to the following context extracted "
                "from the user's documents. Use it to answer the user.\n\n" + context_text
            )
            messages.insert(0, {"role": "system", "content": system_prompt})
        except Exception as e:
            # just ignore retrieval errors – fallback to no context
            print("KB retrieval failed", e)

    messages.append({"role": "user", "content": message})

    response = await client.chat.completions.create(
        model="gpt-4.1",
        messages=messages
    )
    reply = response.choices[0].message.content

    await history_service.save_message(user_id, session_id, "user", message)
    await history_service.save_message(user_id, session_id, "assistant", reply)

    return session_id, reply
