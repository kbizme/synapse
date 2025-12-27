from sqlalchemy.orm import Session
from app.core.persistence.models import Chat, Message
from sqlalchemy.sql import func
from sqlalchemy import update



class ChatRepository:
    @staticmethod
    def get_by_id(db_session: Session, chat_id: str):
        return db_session.query(Chat).filter(Chat.id == chat_id).one_or_none()
    
    
    @staticmethod
    def get_all(db_session: Session):
        return db_session.query(Chat).order_by(Chat.updated_at.desc()).all()
    
    @staticmethod
    def create(db_session: Session, chat_id: str, title: str | None) -> Chat:
        chat = Chat(id=chat_id, title=title)
        db_session.add(chat)
        return chat
    
    @staticmethod
    def touch(db_session: Session, chat_id: str):
        db_session.execute(
            update(Chat)
            .where(Chat.id == chat_id)
            .values(updated_at=func.now())
        )
        
        
        
        

class MessageRepository:
    @staticmethod
    def create(db_session: Session, chat_id: str, role: str, content: str) -> Message:
        message = Message(chat_id=chat_id, role=role, content=content)
        db_session.add(message)
        return message
    
    
    @staticmethod
    def get_messages_by_chat_id(db_session: Session, chat_id: str) -> list[Message]:
        return (db_session
                .query(Message)
                .filter(Message.chat_id == chat_id)
                .order_by(Message.created_at.asc(), Message.id.asc())
                .all()
            )