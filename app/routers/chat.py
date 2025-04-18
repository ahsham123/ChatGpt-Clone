from fastapi import APIRouter, HTTPException, Depends
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import get_chat_response, history_service, client
import uuid
from app.services.auth_service import get_current_user
from app.models.user import UserInDB

router = APIRouter(prefix="/chat", tags=["chat"])

# ---------------------------------------------------------------------------
# Standard non‑streaming endpoint (kept for backward compatibility)
# ---------------------------------------------------------------------------

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, current_user: UserInDB = Depends(get_current_user)):
    try:
        session_id, reply = await get_chat_response(
            current_user.id, request.session_id, request.message, request.kb_id
        )
        return ChatResponse(session_id=session_id, reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Streaming endpoint – returns chunks with partial assistant response so the
# client can render the reply token‑by‑token similar to ChatGPT.
# Each chunk is a JSON line (`\n` delimited) with one of the following shapes:
#   {"session_id": "id"}  – sent once at beginning if it was newly created.
#   {"token": "text"}     – delta token from OpenAI stream.
#   {"done": true}         – final message when complete.
# ---------------------------------------------------------------------------

from fastapi.responses import StreamingResponse
import json


@router.post("/stream")
async def chat_stream_endpoint(
    request: ChatRequest, current_user: UserInDB = Depends(get_current_user)
):
    """Stream assistant reply token‑by‑token using server‑sent JSON lines."""

    async def generator():
        # obtain or create session
        session_id, user_prompt = request.session_id, request.message
        if session_id is None:
            session_id = str(uuid.uuid4())
            # let client know which id to use going forward
            yield json.dumps({"session_id": session_id}) + "\n"

        # fetch previous messages and prepare prompt list
        previous = await history_service.get_messages(current_user.id, session_id)
        messages = [{"role": m.role, "content": m.content} for m in previous]

        # Custom system prompt (user‑defined)
        custom_prompt = await history_service.get_system_prompt(current_user.id, session_id)
        if custom_prompt:
            messages.insert(0, {"role": "system", "content": custom_prompt})

        # KB context if requested
        if request.kb_id:
            from app.services.kb_service import KnowledgeBaseService

            kb_service = KnowledgeBaseService()
            try:
                context_chunks = await kb_service.retrieve(current_user.id, request.kb_id, user_prompt, top_k=3)
                context_text = "\n".join(context_chunks)
                system_prompt = (
                    "You are an assistant with access to the following context extracted "
                    "from the user's documents. Use it to answer the user.\n\n" + context_text
                )
                messages.insert(0, {"role": "system", "content": system_prompt})
            except Exception as e:
                print("KB retrieve failed", e)

        messages.append({"role": "user", "content": user_prompt})

        # save user message immediately so that it appears in history even if
        # client disconnects later
        await history_service.save_message(current_user.id, session_id, "user", user_prompt)

        reply_text = ""

        # call OpenAI streaming
        response = await client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            stream=True,
        )

        async for chunk in response:
            token = chunk.choices[0].delta.content
            if token:
                reply_text += token
                print(token, end="", flush=True)
                yield json.dumps({"token": token}) + "\n"

        # finished – save assistant message
        await history_service.save_message(current_user.id, session_id, "assistant", reply_text)

        # tell client stream done
        yield json.dumps({"done": True}) + "\n"

    return StreamingResponse(generator(), media_type="application/json")
