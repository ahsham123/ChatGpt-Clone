from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class MessageHistory(BaseModel):
    session_id: str
    user_id: str
    role: str
    content: str
    timestamp: datetime


# A lightweight summary of a chat session – useful for populating a sidebar
# with the list of conversations without downloading the full history of every
# session. It only contains the identifier of the session, the content of the
# most recent message in that session (could be user or assistant), and the
# timestamp of that message so that the client can order sessions
# chronologically.


class SessionSummary(BaseModel):
    session_id: str
    last_message: str
    timestamp: datetime
