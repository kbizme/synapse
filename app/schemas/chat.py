from pydantic import BaseModel


class ChatRequest(BaseModel):    
    """ User message sent to the chat agent."""
    chat_id: str
    message: str


class ChatResponse(BaseModel):
    """ Agent reply sent to the user."""
    chat_id: str
    reply: str 
    

class ChatResetRequest(BaseModel):
    chat_id: str