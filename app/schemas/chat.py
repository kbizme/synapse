from pydantic import BaseModel


class ChatRequest(BaseModel):    
    """ User message sent to the chat agent."""
    chat_id: str
    message: str
