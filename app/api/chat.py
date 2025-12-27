from fastapi import APIRouter, HTTPException, status
from app.agents import agents
from app.schemas.chat import ChatRequest, ChatResponse, ChatResetRequest
from app.core.memory import ChatManager
from app.core.chat_service import ChatService
from app.core.persistence.repositories import ChatRepository, MessageRepository
from app.core.persistence.db_sessions import get_session



router = APIRouter()



@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    completion = ChatService().handle_user_message(chat_id=request.chat_id, prompt=request.message)
    return ChatResponse(chat_id=request.chat_id, reply=completion)


@router.get("/chat/{chat_id}")
def get_chat(chat_id: str):
    with get_session() as session:
        assert session is not None
        chat = ChatRepository.get_by_id(db_session=session, chat_id=chat_id)
        if chat is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        chat_messages = MessageRepository.get_messages_by_chat_id(db_session=session, chat_id=chat_id)
        results = {"status": "ok", "id": chat_id, 'chat_title': chat.title, "messages": [
                                                            {"role": message.role, 
                                                             "content": message.content
                                                            } for message in chat_messages
                                                        ]
                    }
    return results
    

@router.post("/reset")
def reset(request: ChatResetRequest):
    ChatManager().reset_chat(request.chat_id)
    return {"status": "ok"}


@router.get("/all-chats")
def all_chats():
    with get_session() as session:
        assert session is not None
        chats =  ChatRepository.get_all(db_session=session)
        results = {"status": "ok", "chats": [ 
                                    {"id": chat.id, "title": chat.title, "updated_at": chat.updated_at}
                                    for chat in chats]
                                    }

    return results