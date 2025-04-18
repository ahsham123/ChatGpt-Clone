from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router
from app.routers.history import router as history_router
from app.routers.kb import router as kb_router
from fastapi.middleware.cors import CORSMiddleware


#CORS CONTROL


app = FastAPI(title="ChatGPT Clone API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(history_router)
app.include_router(kb_router)
