from sqlalchemy.orm import Session
from app.core.persistence.models import Chat, Message



class ChatRepository:
    @staticmethod
    def get_by_id(db_session: Session, chat_id: str):
        return db_session.query(Chat).filter(Chat.id == chat_id).one_or_none()
    
    
    @staticmethod
    def create(db_session: Session, chat_id: str, title: str | None) -> Chat:
        chat = Chat(id=chat_id, title=title)
        db_session.add(chat)
        return chat


class MessageRepository:
    @staticmethod
    def create(db_session: Session, chat_id: str, role: str, content: str) -> Message:
        message = Message(chat_id=chat_id, role=role, content=content)
        db_session.add(message)
        return message
    
    
    @staticmethod
    def get_by_chat_id(db_session: Session, chat_id: str) -> list[Message]:
        return (db_session
                .query(Message)
                .filter(Message.chat_id == chat_id)
                .order_by(Message.created_at.asc(), Message.id.asc())
                .all()
            )