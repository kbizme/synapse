from pydantic import BaseModel



class ChatRequest(BaseModel):    
    """ User message sent to the chat agent."""
    message: str


class ChatResponse(BaseModel):
    """ Agent reply sent to the user."""
    reply: str
    
