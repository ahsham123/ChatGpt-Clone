from typing import List, Optional
from datetime import datetime
from app.db import db
from app.models.history import MessageHistory, SessionSummary

class HistoryService:
    def __init__(self):
        self.collection = db["messages"]

    async def save_message(self, user_id: str, session_id: str, role: str, content: str) -> None:
        doc = {
            "user_id": user_id,
            "session_id": session_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow()
        }
        await self.collection.insert_one(doc)

    async def get_messages(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[MessageHistory]:
        query = {"user_id": user_id}
        if session_id:
            query["session_id"] = session_id
        cursor = self.collection.find(query).sort("timestamp", 1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [MessageHistory(**doc) for doc in docs]

    async def delete_session(self, user_id: str, session_id: str) -> int:
        """Delete all messages for a given user/session. Returns deleted count."""
        res = await self.collection.delete_many({"user_id": user_id, "session_id": session_id})
        return res.deleted_count

    # ---------------------- System prompt helpers ---------------------- #

    def _meta_collection(self):
        return db["session_meta"]

    async def set_system_prompt(self, user_id: str, session_id: str, prompt: str):
        col = self._meta_collection()
        await col.update_one(
            {"user_id": user_id, "session_id": session_id},
            {"$set": {"system_prompt": prompt}},
            upsert=True,
        )

    async def get_system_prompt(self, user_id: str, session_id: str):
        doc = await self._meta_collection().find_one({"user_id": user_id, "session_id": session_id})
        return doc.get("system_prompt") if doc else None

    async def get_sessions(self, user_id: str, limit: int = 100) -> List[SessionSummary]:
        """Return a list of distinct sessions for the given user ordered by the
        timestamp of their most recent message (descending).

        It uses a MongoDB aggregation pipeline to group messages by session and
        pick the last (most recent) message in each session. The pipeline is
        designed to be efficient even when the total number of messages is
        large, because it leverages indexes (if present) and only returns the
        limited amount of data needed for a sidebar list.
        """
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$sort": {"timestamp": -1}  # newest messages first so $first gives us last message
            },
            {
                "$group": {
                    "_id": "$session_id",
                    "last_message": {"$first": "$content"},
                    "timestamp": {"$first": "$timestamp"},
                }
            },
            {"$sort": {"timestamp": -1}},
            {"$limit": limit},
        ]

        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=limit)
        return [SessionSummary(session_id=doc["_id"], last_message=doc["last_message"], timestamp=doc["timestamp"]) for doc in docs]
