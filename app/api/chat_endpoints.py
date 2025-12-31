from fastapi import APIRouter, HTTPException, status, Form, File, UploadFile
from app.schemas.chat import ChatRequest
from app.core.chat_service import ChatService
from app.core.vector_service import VectorService
from app.core.persistence.repositories import ChatRepository, MessageRepository, DocumentRepository
from app.core.persistence.db_sessions import get_session
from fastapi.responses import StreamingResponse



router = APIRouter()



@router.post("/chat")
def chat_stream(request: ChatRequest) -> StreamingResponse:
    stream = ChatService().handle_user_message(chat_id=request.chat_id, prompt=request.message)
    return StreamingResponse(stream, media_type="text/plain")



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
        results = {
            "status": "ok", 
            "id": chat_id, 
            'chat_title': chat.title, 
            "messages": [
                    {
                        "role": message.role, 
                        "content": message.content,
                        "tool_calls": message.tool_calls
                    } for message in chat_messages
                ]
            }
    return results



@router.get("/all-chats")
def all_chats():
    with get_session() as session:
        assert session is not None
        chats =  ChatRepository.get_all(db_session=session)
        results = {
            "status": "ok", 
            "chats": [ 
                    {"id": chat.id, 
                        "title": chat.title, 
                        "updated_at": chat.updated_at
                        } for chat in chats
                ]
            }
    # returning the chat lists
    return results



@router.post("/upload-and-query")
async def upload_and_query(chat_id: str = Form(...), 
                           message: str = Form(...), 
                           file: UploadFile = File(...)) -> StreamingResponse:
    # ingesting the file into CharomaDB
    file_content = await file.read()
    vector_service = VectorService()
    
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="File must need to have a name.")
    try:
        file_path = await vector_service.ingest_file(file_content=file_content,
                                                    filename=file.filename,
                                                    chat_id=chat_id)
        with get_session() as session:
            assert session is not None
            chat = ChatRepository.get_by_id(db_session=session, chat_id=chat_id)
            if not chat:
                ChatRepository.create(db_session=session, chat_id=chat_id, title=message[:60])
                
            # saving the uploaded document
            DocumentRepository.create(db_session=session,
                                        chat_id=chat_id,
                                        filename=file.filename,
                                        collection_name=f'chat_{chat_id}',
                                        file_path=file_path)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Failed to process docuemnt: {str(e)}")
    
    # calling the chat service
    stream = ChatService().handle_user_message(chat_id=chat_id, prompt=message)
    return StreamingResponse(stream, media_type="text/plain")