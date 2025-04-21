from pydantic import BaseModel
from typing import List, Dict, Optional

class MessageHistory(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[MessageHistory]] = []

class ChatResponse(BaseModel):
    response: str
