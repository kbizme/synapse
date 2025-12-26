from fastapi import APIRouter
from app.agents import agents
from app.schemas.chat import ChatRequest, ChatResponse
from app.core import memory

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    completion = agents.get_completion(request.message)
    return ChatResponse(reply=completion)


@router.post("/reset")
def reset():
    memory.reset_memory()
    return {"status": "ok"}
