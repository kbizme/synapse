from fastapi import APIRouter
from app.agents import agents
from app.schemas.chat import ChatRequest, ChatResponse, ChatResetRequest
from app.core.memory import ChatManager
from app.core.chat_service import ChatService



router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    completion = ChatService().handle_user_message(chat_id=request.chat_id, prompt=request.message)
    return ChatResponse(chat_id=request.chat_id, reply=completion)


@router.post("/reset")
def reset(request: ChatResetRequest):
    ChatManager().reset_chat(request.chat_id)
    return {"status": "ok"}
