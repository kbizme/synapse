from fastapi import APIRouter
from app.agents import agents
from app.schemas.chat import ChatRequest, ChatResponse, ChatResetRequest
from app.core import memory

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    completion = agents.get_completion(chat_id=request.chat_id, 
                                       prompt=request.message)
    return ChatResponse(chat_id=request.chat_id, reply=completion)


@router.post("/reset")
def reset(request: ChatResetRequest):
    chat_manager = memory.ChatManager()
    chat_manager.reset_chat(request.chat_id)
    return {"status": "ok"}
